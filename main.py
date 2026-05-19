import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True  
intents.members = True          

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Carrega o arquivo de tickets dinamicamente da pasta cogs
        await self.load_extension('cogs.tickets')
        print("Cog de Tickets carregado com sucesso!")
        
        # Sincroniza os comandos com o Discord
        await self.tree.sync()
        print("Comandos Slash sincronizados globalmente!")

    async def on_ready(self):
        print(f'Bot logado com sucesso como {self.user.name}')
        await self.change_presence(activity=discord.Game(name="Chinko No Chistu"))

bot = MyBot()

if __name__ == "__main__":
    bot.run(TOKEN)