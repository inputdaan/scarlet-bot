import discord
from discord.ext import commands
from discord import app_commands
import random

# CONFIGURAÇÃO DE ID
ID_CANAL_GERAL = 1489820240576774307    # ID real do seu chat geral

# =========================================================================
#                    BANCO DE TEMPLATES DE BOAS-VINDAS
# =========================================================================
TEMPLATES_BOAS_VINDAS = [
    {
        "titulo": "💤  Seja bem-vindo(a) ao Restart!",
        "descricao": "Olá {membro}! <:kannapog:1503187985779265709>  Que bom ter você aqui no nosso cantinho. <:Akiss:1504819046435131446>  Aproveite para fazer novos amigos e divirta-se! \n\n <a:1n_b_seta:1502812597043593419> Não esqueça de ler as <#1502709340006514849> \n\n <a:1n_b_seta:1502812597043593419> Apresente-se no canal <#1506469646713356348> para a gente te conhecer melhor!",
        "banner": "https://i.imgur.com/vcRNNac.gif"
    },
    {
        "titulo": "✨  Um novo membro apareceu!",
        "descricao": "Olá {membro}!  <:1_tome:1501575350822633625>  Que bom ter você aqui no nosso cantinho. Aproveite para fazer novos amigos e divirta-se! \n\n <:zbranco:1504076517880369224> <a:1n_b_seta:1502812597043593419> Não esqueça de ler as <#1502709340006514849> \n\n <:Bamor:1504816461347164240> <a:1n_b_seta:1502812597043593419> Mande foto do seu pet no <#1489836142990983198>!",
        "banner": "https://i.imgur.com/nlPCY2v.jpeg"
    },
    {
        "titulo": "🐦  Bem Vindo(a) amostradinho!",
        "descricao": "Olá {membro}! Você chegou na nossa bagunça! <:Abeijao:1490160490511466577> Aproveite para fazer novos amigos e divirta-se! \n\n <:ALTRD_amarelo_MM_chocado:1508196452793450657> <a:1n_b_seta:1502812597043593419> Fique a vontade para assoviar <#1505632387940225125>! \n\n <:emoji_19:1508196442744029414> <a:1n_b_seta:1502812597043593419> Proibido Assoprar achando que ta assoviando!",
        "banner": "https://i.imgur.com/2ded1Fn.jpeg"
    },
    {
        "titulo": "🎉  Alerta de Novo Membro!",
        "descricao": "Olá {membro}! Agradecemos por ter entrado em nosso server!\n\n <a:notsopog:1503202349500334210> <a:1n_b_seta:1502812597043593419> Mande sua Arte no <#1489837308499857448> \n\n <:jheny4:1504842849903050912> <a:1n_b_seta:1502812597043593419> Caso esteja mal, e queira desabafar nos te ajudamos! <#1489820243529306193> ",
        "banner": "https://i.imgur.com/fkTgofu.gif"
    },
    {
        "titulo": "💚  Bem vindo lindão ou lindona!",
        "descricao": "Olá {membro}! <:sic_20:1507618090303754411>  Que bom ter você aqui no nosso manicômio! Aproveite para fazer novos amigos e web namorada(o) <:Ahihi:1490160711647756332>  \n\n <:bwhite:1507618065548972092> <:c_tracinhobranco:1490161387148677170> Fique a vontade para jogar <#1489820254677762179> \n\n <:blue_chef_kiss:1508183407799042281> <:c_tracinhobranco:1490161387148677170> Caso você goste de jogar nos mostre! <#1505029434397298728>  !",
        "banner": "https://i.imgur.com/BBYnXB7.jpeg"
    },
    {
        "titulo": "💥  Chegou mais um pra completar!",
        "descricao": "<a:Cat:1508183397384585216> Olá {membro}! <a:Cat:1508183397384585216>  Que bom ter você aqui no nosso cantinho. Aproveite para fazer novos amigos e divirta-se! \n\n <:Lux_scottchan:1503191980715409458> <a:1n_b_seta:1502812597043593419> Poste foto sua no <#1506455398683644105> caso você seja bonito(a)! \n\n <:alertadefofura:1503194749656498308> <a:1n_b_seta:1502812597043593419> Mande foto do seu pet no <#1489836142990983198>! <a:Cat1:1508183399758827580> ",
        "banner": "https://i.imgur.com/hq4JtzA.gif"
    },
    {
        "titulo": "🌸  Bem-vindo(a) a casa!",
        "descricao": "Olá {membro}! Que bom ter você aqui no nosso cantinho. Aproveite para fazer novos amigos e divirta-se! \n\n <:jheny4:1504842849903050912> <:c_tracinhobranco:1490161387148677170> Se apresente-se no <#1506469646713356348> !  \n\n <:br_gado:1507619463577468958> <:c_tracinhobranco:1490161387148677170>  Mande foto do seu pet no <#1489836142990983198>!",
        "banner": "https://i.imgur.com/jkQQ6bW.gif"
    }
]

class BoasVindas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("🟢 [COG] Sistema de Boas-Vindas Aleatório carregado!")

    # Evento disparado SEMPRE que alguém entra no servidor
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        canal = self.bot.get_channel(ID_CANAL_GERAL)
        
        if not canal:
            print(f"❌ Erro Boas-Vindas: O canal com ID {ID_CANAL_GERAL} não foi encontrado.")
            return

        template_escolhido = random.choice(TEMPLATES_BOAS_VINDAS)
        descricao_formatada = template_escolhido["descricao"].format(membro=member.mention)

        embed = discord.Embed(
            title=template_escolhido["titulo"], 
            description=descricao_formatada,
            color=discord.Color.blurple()
        )

        if template_escolhido["banner"]:
            embed.set_image(url=template_escolhido["banner"])

        embed.set_footer(
            text=f"Agora somos {member.guild.member_count} membros!",
            icon_url=member.guild.icon.url if member.guild.icon else None
        )

        await canal.send(content=f"{member.mention} **Seja Bem-Vindo(a)!**", embed=embed)

    # ==================== COMANDO DE TESTE MANUAL ====================
    @app_commands.command(name="testar_boas_vindas", description="Simula uma entrada falsa de boas-vindas para testar os banners e textos aleatórios.")
    @app_commands.checks.has_permissions(manage_channels=True, manage_roles=True)
    async def testar_boas_vindas(self, interaction: discord.Interaction):
        canal = self.bot.get_channel(ID_CANAL_GERAL)
        
        if not canal:
            await interaction.response.send_message(f"❌ Erro: Canal de texto com ID `{ID_CANAL_GERAL}` não configurado ou inacessível.", ephemeral=True)
            return

        # Avisa que o teste começou de forma silenciosa (só quem usou o comando vê a resposta inicial)
        await interaction.response.send_message("🔄 Simulando entrada de membro e gerando embed de teste...", ephemeral=True)

        # Escolhe um template de forma idêntica ao evento de entrada real
        template_escolhido = random.choice(TEMPLATES_BOAS_VINDAS)
        
        # Simula o texto marcando quem executou o comando para ver como fica
        descricao_formatada = template_escolhido["descricao"].format(membro=interaction.user.mention)

        embed = discord.Embed(
            title=f"🧪 [TESTE] {template_escolhido['titulo']}", 
            description=descricao_formatada,
            color=discord.Color.blurple()
        )

        if template_escolhido["banner"]:
            embed.set_image(url=template_escolhido["banner"])

        embed.set_footer(
            text=f"Agora somos {interaction.guild.member_count} membros! (Simulação de Teste)",
            icon_url=interaction.guild.icon.url if interaction.guild.icon else None
        )

        # Envia a mensagem completa simulada direto no chat geral
        await canal.send(content=f"{interaction.user.mention} **Seja Bem-Vindo(a)!** (Teste de Sistema)", embed=embed)

    # Trata o erro de falta de permissões do comando de teste
    @testar_boas_vindas.error
    async def testar_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ Você precisa ter as permissões de **Gerenciar Canais** e **Gerenciar Cargos** para rodar esse teste manual.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(BoasVindas(bot))