from os import environ
import discord, youtube_dl
from discord.ext import commands

import Queue
import Song

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = Queue.Queue()
        self.extract = Song.Song()

        self.lastSong = None


    @commands.command(name="help", pass_context=True)
    async def help(self, ctx, args=None):
        embed = self.create_embed()
        command_names_list = sorted([x.name for x in ctx.bot.commands], key=str.lower)
        command_names_list.remove('help')

        print(command_names_list)

        if not args:
            embed.add_field(
                name="List of supported commands:",
                value="\n".join([str(i+1)+"- "+x.capitalize() for i,x in enumerate(command_names_list)]),
                inline=False
            )
            embed.add_field(
                name="Details",
                value="Type `-help <command name>` for more details about each command.",
                inline=False
            )
        elif args.lower() in command_names_list:

            embed.add_field(
                name="Command: " + args.capitalize(),
                value=ctx.bot.get_command(args).description
            )
        else:
            embed.add_field(
                name="",
                value="Don't think I got that command, boss!"
            )

        await ctx.send(embed=embed)

        return
    

    @commands.command(name="clear", description="Deletes 5 messages or an informed X number", pass_context=True)
    async def clear(self, ctx, amount=5):
        await ctx.channel.purge(limit=amount)
        print(f'Total deleted messages {amount}')
        return


    @commands.command(name="play", aliases=['p'], description="Play music over search or youtube url", pass_context=True)
    async def play(self, ctx, *, args: str):
        channel = await self._getChannel(ctx)

        if channel == None:
            return

        if len(args) == 0:
            await ctx.channel.send(embed=self.createEmbed("", "Type something there for me to look for"))
            return

        if ctx.voice_client == None:
            await channel.connect()
        else:
            if channel != ctx.voice_client.channel and ctx.voice_client.is_playing():
                await ctx.channel.send(embed=self.createEmbed("", "Is anyone listening now"))
                return
            else:
                await ctx.voice_client.move_to(channel)

        song = self.extract.verifyArgs(args)

        if ctx.voice_client.is_playing():
            if not type(song) == list:
                song.update({'author': ctx.author.name})
                self.queue.put_nowait(song)

                embed = self.create_embed(title="Add in playlist", description=f"{song['title'][0:60]}... | `{ctx.author.name}`" if len(song['title']) < 60 else f"{song['title'][0:len(song['title'])-1]} | `{ctx.author.name}`")
                await ctx.send(embed=embed, delete_after=5)
            else:
                for s in song:
                    s.update({'author': ctx.author.name})
                    self.queue.put_nowait(s)
                
                embed = self.create_embed(description=f"Add {len(song)} songs in playlist")
                await ctx.send(embed=embed, delete_after=5)
            
            return

        if not type(song) == list:
            self._play_song(ctx, song)
        else:
            self._play_song(ctx, song[0])

            playlist = song
            playlist.pop(0)

            song = song[0].update({'author': ctx.author.name})

            for s in playlist:
                    s.update({'author': ctx.author.name})
                    self.queue.put_nowait(s)

            embed = self.create_embed(description=f"Add {len(playlist)} songs in playlist")
            await ctx.send(embed=embed, delete_after=5)

        embed = self.create_embed(
            title="Now Playing",
            description=f"{song['title'[0:60]]}... | `{ctx.author.name}`" if len(song['title']) < 60 else f"{song['title'][0:len(song['title'])-1]} | `{ctx.author.name}`"
        ) 

        self.lastSong = song

        await ctx.send(embed=embed, delete_after=5)

        return


    @commands.command(name="skip", description="Skip to the next song in queue", pass_context=True)
    async def skip(self, ctx):
        channel = await self._getChannel(ctx)

        if channel == None:
            return

        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        return


    @commands.command(name="playlist", description="Returns the name of all songs in the queue", pass_context=True)
    async def playlist(self, ctx):
        playlist = list()
        pages = list()
        page = list()

        for indice, song in enumerate(self.queue.__iter__()):
            row = str(indice+1) + "-  " + song['title']

            page.append(row + f" | `{song['author']}`" if len(row) < 60 else row[0: 60] + f"... |  `{song['author']}`")

            if len(page) == 10 or indice+1 == len(self.queue):
                playlist.append(page)
                page = list()

        for indice, page in enumerate(playlist):
            countPages = f"Page({indice+1}/{len(playlist)})"
            embed = self.create_embed(title=f"{'Playlist:':<15}{countPages:>100}")
            embed.description = '\n'.join(page)
            pages.append(embed)

        message = await ctx.send(embed=pages[0], delete_after=len(playlist)*15)

        await message.add_reaction('⏮')
        await message.add_reaction('◀')
        await message.add_reaction('▶')
        await message.add_reaction('⏭')

        def check(reaction, user):
            return user == ctx.author

        i = 0
        reaction = None

        while True:
            if str(reaction) == '⏮':
                i = 0
                await message.edit(embed = pages[i])
            elif str(reaction) == '◀':
                if i > 0:
                    i -= 1
                    await message.edit(embed = pages[i])
            elif str(reaction) == '▶':
                if i < 2:
                    i += 1
                    await message.edit(embed = pages[i])
            elif str(reaction) == '⏭':
                i = len(pages)-1
                await message.edit(embed = pages[i])
            
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
                await message.remove_reaction(reaction, user)
            except:
                break


    @commands.command(name="remove", description="Remove a X song from the queue", pass_context=True)
    async def remove(self, ctx, index):
        channel = await self._getChannel(ctx)

        if channel == None:
            return

        try:
            index = int(index)-1
        except Exception as e:
            print(e)

        if ctx.voice_client.is_playing() and len(self.queue) >= index > 0 :
            song = f"{index+1}-  {self.queue[index]['title']}"
            
            self.queue.remove(index)

            embed = self.create_embed(title="Song removed:", description=song)

        await ctx.send(embed=embed)

        return


    @commands.command(name="resume", description="Play a paused song", pass_context=True)
    async def resume(self, ctx):
        channel = await self._getChannel(ctx)
        
        if channel == None:
            return
        
        if channel == ctx.voice_client.channel:
            if ctx.voice_client.is_paused():
                ctx.voice_client.resume()

                row = self.lastSong['title']

                await ctx.channel.send(embed=self.create_embed(
                    title='Playing Now: ', 
                    description=row + f" | `{self.lastSong['author']}`" if len(row) < 60 else row[0: 60] + f"... |  `{self.lastSong['author']}`"
                    )
                )
            else:
               await ctx.channel.send(embed=self.create_embed("", "There's nothing paused"))
        else:
            await ctx.channel.send(embed=self.create_embed("", "No music playing!"))
        
        return


    @commands.command(name="pause", description="Pause a song if it's playing", pass_context=True)
    async def pause(self, ctx):
        channel = await self._getChannel(ctx)
        
        if channel == None:
            return
        
        if channel == ctx.voice_client.channel:
            ctx.voice_client.pause()
        else:
            await ctx.channel.send(embed=self.create_embed("", "Don't try to pause the guys music"))
        
        return


    @commands.command(name='stop', description="Stop a song if it's playing", pass_context=True)
    async def stop(self, ctx):
        channel = await self._getChannel(ctx)
        
        if channel == None:
            return
        
        if channel == ctx.voice_client.channel:
            if not self.queue.empty():
                self.queue = Queue.Queue()
                self.lastSong = None
            ctx.voice_client.stop()
        else:
            await ctx.channel.send(embed=self.create_embed(description="Don't try to stop the guys' music, get on their channel and listen along"))

        return


    @commands.command(name='disconnect', aliases=['dc'] , description='Disconnect the bot from the channel', pass_context=True)
    async def disconnect(self, ctx):
        channel = await self._getChannel(ctx)
        
        if channel == None or ctx.voice_client == None:
            return
        
        if channel == ctx.voice_client.channel:
            if not self.queue.empty():
                self.queue = Queue.Queue()
                self.lastSong = None
            await ctx.voice_client.disconnect()
        else:
            await ctx.channel.send(embed=self.create_embed(description="Don't try to troll man, guys are listening"))
        
        return


    async def _getChannel(self, ctx):
        try:
            channel = ctx.message.author.voice.channel
        except AttributeError:
            await ctx.channel.send(f'Enter some channel there, bro')
            return
        else:
            return channel


    def _play_song(self, ctx, song):
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}

        ctx.voice_client.play(discord.FFmpegPCMAudio(song['formats'], executable=environ.get('FFMPEG_EXE'), **FFMPEG_OPTIONS), after=lambda e:  self._next_song(ctx))
        
        return
               
                
    def create_embed(self, title='', description='', color=0x19e2f0):
        embed = (discord.Embed(title=title,
                               description=description,
                               color=color)
                            )

        return embed
        

    def _next_song(self, ctx):
        if not self.queue.empty():
            song = self.queue.get_nowait()

            if not 'formats' in song.keys():
                song = self.extract.extractToUrl(song['url'])

            self.lastSong = song

            self._play_song(ctx, song)
        else:
            return None

            self.lastSong = None
