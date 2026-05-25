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

# CONFIGURAÇÃO DE IDS (Altere com os IDs reais do seu servidor)
ID_CANAL_NOTURNO = 1505414356479774720  # ID do seu chat madruga
ID_CANAL_GERAL = 1489820240576774307    # <-- SUBSTITUA PELO ID REAL DO SEU CHAT GERAL

class ChatNoturno(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Inicia as rotinas automáticas em segundo plano
        self.rotina_abrir.start()
        self.rotina_aviso_fechar.start()
        self.rotina_fechar.start()
        
        # Log de inicialização no console
        print("🟢 [COG] Sistema do Chat Noturno carregado com sucesso!")

    def cog_unload(self):
        # Para as rotinas caso a cog seja recarregada
        self.rotina_abrir.cancel()
        self.rotina_aviso_fechar.cancel()
        self.rotina_fechar.cancel()

    # ==================== ROTINAS AUTOMÁTICAS ====================

    # Rotina que roda todo dia às 21:00 (Abre e Torna Visível)
    @tasks.loop(time=HORARIO_ABRIR)
    async def rotina_abrir(self):
        canal = self.bot.get_channel(ID_CANAL_NOTURNO)
        general = self.bot.get_channel(ID_CANAL_GERAL)
        
        if canal:
            everyone = canal.guild.default_role
            # Define para VER o canal e ENVIAR mensagens
            await canal.set_permissions(everyone, view_channel=True, send_messages=True, read_message_history=True)
            
            embed = discord.Embed(
                title="<:kannapog:1503187985779265709> **CHAT BAGUNÇA DA MADRUGA ABERTO** <:kannapog:1503187985779265709> ",
                description="""<a:1n_b_seta:1502812597043593419> Chat encerra automaticamente as 6:00 AM
<a:1n_b_seta:1502812597043593419> Pode falar sobre o que quiser aqui!""",
                color=discord.Color.green()
            )
            await canal.send(embed=embed)
            print("O chat noturno foi aberto e tornado visível automaticamente.")
            
            # Envia o aviso lá no chat geral
            if general:
                embed_geral = discord.Embed(
                    title="<:kannapog:1503187985779265709> **MADRUGA LIBERADA!**",
                    description=f"O canal {canal.mention} acabou de ser aberto! Corre lá para jogar conversa fora.",
                    color=discord.Color.green()
                )
                await general.send(embed=embed_geral)

    # Rotina que roda todo dia às 05:30 (Aviso prévio)
    @tasks.loop(time=HORARIO_AVISO_FECHAR)
    async def rotina_aviso_fechar(self):
        canal = self.bot.get_channel(ID_CANAL_NOTURNO)
        
        if canal:
            embed = discord.Embed(
                title="<:emoji_33:1503190692099260492> **AVISO: O CHAT FECHA EM 30 MINUTOS** <:emoji_33:1503190692099260492>",
                description="""<a:1n_b_seta:1502812597043593419> O chat madruga será encerrado às **06:00 AM**!
Aproveitem os últimos minutos, pois o que acontece de madrugada fica de madrugada.""",
                color=discord.Color.gold()
            )
            await canal.send(embed=embed)
            print("Aviso de fechamento do chat noturno enviado.")

    # Rotina que roda todo dia às 06:00 da manhã (Fecha e Oculta)
    @tasks.loop(time=HORARIO_FECHAR)
    async def rotina_fechar(self):
        canal = self.bot.get_channel(ID_CANAL_NOTURNO)
        
        if canal:
            # Envia o embed avisando antes de sumir com o canal
            embed = discord.Embed(
                title="<:emoji_33:1503190692099260492> **CHAT ENCERRADO** <:emoji_33:1503190692099260492>",
                description="""<a:1n_b_seta:1502812597043593419> O chat fechou e abrirá novamente amanhã as 21:00!
O que acontece de madrugada fica de madrugada.""",
                color=discord.Color.red()
            )
            await canal.send(embed=embed)
            
            everyone = canal.guild.default_role
            # Modifica para NÃO ver o canal e NÃO enviar mensagens
            await canal.set_permissions(everyone, view_channel=False, send_messages=False)
            print("O chat noturno foi fechado e ocultado automaticamente.")

    @rotina_abrir.before_loop
    @rotina_aviso_fechar.before_loop
    @rotina_fechar.before_loop
    async def antes_da_rotina(self):
        await self.bot.wait_until_ready()

    # ==================== COMANDOS MANUAIS ====================

    # Comando para abrir manualmente
    @app_commands.command(name="noturno_abrir", description="Abre e torna visível o chat noturno manualmente.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def abrir_manual(self, interaction: discord.Interaction):
        canal = self.bot.get_channel(ID_CANAL_NOTURNO)
        general = self.bot.get_channel(ID_CANAL_GERAL)
        
        if not canal:
            await interaction.response.send_message("❌ Canal não encontrado. Verifique o ID configurado.", ephemeral=True)
            return

        everyone = canal.guild.default_role
        await canal.set_permissions(everyone, view_channel=True, send_messages=True, read_message_history=True)
        
        embed = discord.Embed(
            title="🔓 Chat Liberado Manualmente!",
            description=f"O chat noturno foi aberto e tornado visível mais cedo por {interaction.user.mention}.",
            color=discord.Color.green()
        )
        await canal.send(embed=embed)
        await interaction.response.send_message("✅ O canal foi aberto e tornado visível!", ephemeral=True)
        
        # Envia o aviso lá no chat geral indicando abertura manual
        if general:
            embed_geral = discord.Embed(
                title="<:kannapog:1503187985779265709> **MADRUGA LIBERADA MAIS CEDO!**",
                description=f"O canal {canal.mention} foi aberto antecipadamente por {interaction.user.mention}!",
                color=discord.Color.green()
            )
            await general.send(embed=embed_geral)

    # Comando para fechar manualmente
    @app_commands.command(name="noturno_fechar", description="Fecha e oculta o chat noturno manualmente.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def fechar_manual(self, interaction: discord.Interaction):
        canal = self.bot.get_channel(ID_CANAL_NOTURNO)
        if not canal:
            await interaction.response.send_message("❌ Canal não encontrado. Verifique o ID configurado.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🔒 Chat Fechado Manualmente!",
            description=f"O chat noturno foi fechado e ocultado antecipadamente por {interaction.user.mention}.",
            color=discord.Color.red()
        )
        await canal.send(embed=embed)

        everyone = canal.guild.default_role
        await canal.set_permissions(everyone, view_channel=False, send_messages=False)
        await interaction.response.send_message("✅ O canal foi fechado e ocultado com sucesso!", ephemeral=True)

    # Trata o erro caso alguém sem a permissão tente usar o comando
    @abrir_manual.error
    @fechar_manual.error
    async def comandos_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ Você não tem a permissão de **Gerenciar Canais** para usar este comando.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ChatNoturno(bot))