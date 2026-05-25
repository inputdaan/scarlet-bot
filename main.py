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
        
        # CARREGA O CHAT NOTURNO: Ativa o novo sistema que criamos
        try:
            await self.load_extension('cogs.chatnoturno')
            print("Cog do Chat Noturno carregada com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao carregar a Cog do Chat Noturno: {e}")
            
        # CARREGA O SISTEMA DE BOAS-VINDAS ALEATÓRIO
        try:
            await self.load_extension('cogs.boasvindas')
            print("Cog de Boas-Vindas carregada com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao carregar a Cog de Boas-Vindas: {e}")
        
        # CARREGA O SISTEMA DE NOTÍCIAS GEEK E ANIMES
        try:
            await self.load_extension('cogs.noticias')
            print("Cog de Notícias Geek carregada com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao carregar a Cog de Notícias Geek: {e}")
        
        # Sincroniza todos os comandos com o Discord (incluindo os novos do chat noturno e boas-vindas)
        try:
            synced = await self.tree.sync()
            print(f"🔄 Comandos Slash sincronizados globalmente! Total: {len(synced)} comandos.")
        except Exception as e:
            print(f"❌ Erro ao sincronizar comandos na árvore do Discord: {e}")

    async def on_ready(self):
        print(f'Bot logado com sucesso como {self.user.name}')
        await self.change_presence(activity=discord.Game(name="Chinko No Chistu"))

bot = MyBot()

if __name__ == "__main__":
    bot.run(TOKEN)