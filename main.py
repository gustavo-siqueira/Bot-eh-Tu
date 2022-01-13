import discord, random
from discord.ext import commands
from commandsBot import Commands
    
class BotéTu(commands.Bot):
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
        self.ready = ['Bot is ON READY']

    # Events
    async def on_ready(self):
        print(random.choice(self.ready))

    async def on_member_join(self, membesr):
        channel_id = [c.id for c in self.guilds[0].text_channels]
        channel = self.get_channel(channel_id[0])
        await channel.send(f'Welcome {member.name}!')

    async def on_member_remove(self, member):
        channel_id = [c.id for c in self.guilds[0].text_channels]
        channel = self.get_channel(channel_id[0])
        await channel.send(f'{member.name}, goodbye my friend!')


if __name__ == "__main__":
    bot = BotéTu()
    bot.add_cog(Commands(bot))

    token = str(input("Enter with your token: ").strip())

    bot.run(token)


    

