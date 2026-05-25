import discord
from discord.ext import tasks, commands
from discord import app_commands
import datetime

# Define o fuso horário de Brasília (UTC-3)
UTC_MENOS_TRES = datetime.timezone(datetime.timedelta(hours=-3))

# Define os horários exatos em que as tarefas vão rodar todo dia
HORARIO_ABRIR = datetime.time(hour=21, minute=0, second=0, tzinfo=UTC_MENOS_TRES)
HORARIO_AVISO_FECHAR = datetime.time(hour=5, minute=30, second=0, tzinfo=UTC_MENOS_TRES) # <-- 30 min antes de fechar
HORARIO_FECHAR = datetime.time(hour=6, minute=0, second=0, tzinfo=UTC_MENOS_TRES)

# CONFIGURAÇÃO DE ID (Altere com o ID do seu servidor)
ID_CANAL_NOTURNO = 1505414356479774720  # ID real do seu chat noturno

class ChatNoturno(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Inicia as rotinas automáticas em segundo plano
        self.rotina_abrir.start()
        self.rotina_aviso_fechar.start() # <-- Inicia a nova rotina de aviso
        self.rotina_fechar.start()

    def cog_unload(self):
        # Para as rotinas caso a cog seja recarregada
        self.rotina_abrir.cancel()
        self.rotina_aviso_fechar.cancel()
        self.rotina_fechar.cancel()

    # ==================== ROTINAS AUTOMÁTICAS ====================

    # Rotina que roda todo dia às 21:00
    @tasks.loop(time=HORARIO_ABRIR)
    async def rotina_abrir(self):
        canal = self.bot.get_channel(ID_CANAL_NOTURNO)
        
        if canal:
            everyone = canal.guild.default_role
            await canal.set_permissions(everyone, send_messages=True, read_message_history=True)
            
            embed = discord.Embed(
                title="<:kannapog:1503187985779265709> **CHAT BAGUNÇA DA MADRUGA ABERTO** <:kannapog:1503187985779265709> ",
                description="""<a:1n_b_seta:1502812597043593419> Chat encerra automaticamente as 6:00 AM
<a:1n_b_seta:1502812597043593419> Pode falar sobre o que quiser aqui!""",
                color=discord.Color.green()
            )
            await canal.send(embed=embed)
            print("O chat noturno foi aberto automaticamente pelo sistema.")

    # Rotina que roda todo dia às 05:30 (Aviso prévio)
    @tasks.loop(time=HORARIO_AVISO_FECHAR)
    async def rotina_aviso_fechar(self):
        canal = self.bot.get_channel(ID_CANAL_NOTURNO)
        
        if canal:
            embed = discord.Embed(
                title="<:emoji_33:1503190692099260492> **AVISO: O CHAT FECHA EM 30 MINUTOS** <:emoji_33:1503190692099260492>",
                description="""<a:1n_b_seta:1502812597043593419> O chat madruga será encerrado às **06:00 AM**!
Aproveitem os últimos minutos, pois o que acontece de madrugada fica de madrugada.""",
                color=discord.Color.gold() # Cor amarela/laranja para indicar aviso
            )
            await canal.send(embed=embed)
            print("Aviso de fechamento do chat noturno enviado.")

    # Rotina que roda todo dia às 06:00 da manhã
    @tasks.loop(time=HORARIO_FECHAR)
    async def rotina_fechar(self):
        canal = self.bot.get_channel(ID_CANAL_NOTURNO)
        
        if canal:
            everyone = canal.guild.default_role
            await canal.set_permissions(everyone, send_messages=False)
            
            embed = discord.Embed(
                title="<:emoji_33:1503190692099260492> **CHAT ENCERRADO** <:emoji_33:1503190692099260492>",
                description="""<a:1n_b_seta:1502812597043593419> O chat fechou e abrirá novamente amanhã as 21:00!
O que acontece de madrugada fica de madrugada.""",
                color=discord.Color.red()
            )
            await canal.send(embed=embed)
            print("O chat noturno foi fechado automaticamente pelo sistema.")

    @rotina_abrir.before_loop
    @rotina_aviso_fechar.before_loop
    @rotina_fechar.before_loop
    async def antes_da_rotina(self):
        await self.bot.wait_until_ready()

    # ==================== COMANDOS MANUAIS ====================

    # Comando para abrir manualmente
    @app_commands.command(name="noturno_abrir", description="Abre o chat noturno manualmente antes do horário padrão.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def abrir_manual(self, interaction: discord.Interaction):
        canal = self.bot.get_channel(ID_CANAL_NOTURNO)
        if not canal:
            await interaction.response.send_message("❌ Canal não encontrado. Verifique o ID configurado.", ephemeral=True)
            return

        everyone = canal.guild.default_role
        await canal.set_permissions(everyone, send_messages=True, read_message_history=True)
        
        embed = discord.Embed(
            title="🔓 Chat Liberado Manualmente!",
            description=f"O chat noturno foi aberto mais cedo por {interaction.user.mention}.",
            color=discord.Color.green()
        )
        await canal.send(embed=embed)
        await interaction.response.send_message("✅ O canal foi aberto com sucesso!", ephemeral=True)

    # Comando para fechar manualmente
    @app_commands.command(name="noturno_fechar", description="Fecha o chat noturno manualmente antes do horário padrão.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def fechar_manual(self, interaction: discord.Interaction):
        canal = self.bot.get_channel(ID_CANAL_NOTURNO)
        if not canal:
            await interaction.response.send_message("❌ Canal não encontrado. Verifique o ID configurado.", ephemeral=True)
            return

        everyone = canal.guild.default_role
        await canal.set_permissions(everyone, send_messages=False)
        
        embed = discord.Embed(
            title="🔒 Chat Fechado Manualmente!",
            description=f"O chat noturno foi fechado antecipadamente por {interaction.user.mention}.",
            color=discord.Color.red()
        )
        await canal.send(embed=embed)
        await interaction.response.send_message("✅ O canal foi fechado com sucesso!", ephemeral=True)

    # Trata o erro caso alguém sem a permissão tente burlar ou usar o comando
    @abrir_manual.error
    @fechar_manual.error
    async def comandos_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ Você não tem a permissão de **Gerenciar Canais** para usar este comando.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ChatNoturno(bot))