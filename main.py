from os import environ
from dotenv import load_dotenv

import discord
from discord.ext import commands
from commandsBot import Commands

class BotehTu(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(
                        command_prefix='-', 
                        case_insensitive=True,
                        activity=discord.Activity(name=" ", type=2),
                        help_command=None, 
                        intents=intents
                    )

    # Events
    async def on_ready(self):
        print('Bot is ON READY')

    async def on_member_join(self, member):
        channel_id = [c.id for c in self.guilds[0].text_channels]
        channel = self.get_channel(channel_id[0])
        await channel.send(f'Welcome {member.name}!')

    async def on_member_remove(self, member):
        channel_id = [c.id for c in self.guilds[0].text_channels]
        channel = self.get_channel(channel_id[0])
        await channel.send(f'{member.name}, goodbye my friend!')


if __name__ == "__main__":
    bot = BotehTu()
    bot.add_cog(Commands(bot))

    load_dotenv()

    bot.run(environ.get('BOT_TOKEN'))


    

