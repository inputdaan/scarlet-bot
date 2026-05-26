import discord
from discord.ext import commands, tasks
from discord import app_commands
import feedparser
import datetime

# =========================================================================
#                         CONFIGURAÇÕES DO SISTEMA
# =========================================================================
ID_CANAL_NOTICIAS = 1508516714181296219  # ID do seu canal de notícias geek
ID_CARGO_ANIMES = 1489820094518530049    # ID do cargo para o ping das 12:00

# Define o fuso horário de Brasília (UTC-3) para corrigir o envio das 9h
UTC_MENOS_TRES = datetime.timezone(datetime.timedelta(hours=-3))
HORARIO_GIRO = datetime.time(hour=12, minute=0, second=0, tzinfo=UTC_MENOS_TRES)

# Fontes RSS em Português
FONTES_RSS = {
    "Crunchyroll": "https://www.crunchyroll.com/news/rss/brazil",
    "IGN Brasil": "https://br.ign.com/feed.xml"
}

class NoticiasGeek(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.noticias_enviadas = set() # Guarda links já enviados no dia para evitar duplicatas
        
        # Inicia as duas rotinas automáticas
        self.rotina_tempo_real.start()
        self.giro_meio_dia.start()
        print("🟢 [COG] Sistema de Notícias de Animes e Mundo Geek carregado!")

    def cog_unload(self):
        self.rotina_tempo_real.cancel()
        self.giro_meio_dia.cancel()

    # =========================================================================
    # 1. MONITORAMENTO EM TEMPO REAL (RODA A CADA 15 MINUTOS)
    # =========================================================================
    @tasks.loop(minutes=15.0)
    async def rotina_tempo_real(self):
        await self.bot.wait_until_ready()
        canal = self.bot.get_channel(ID_CANAL_NOTICIAS)
        if not canal:
            return

        for portal, url in FONTES_RSS.items():
            try:
                feed = feedparser.parse(url)
                if not feed.entries:
                    continue

                # Analisa a notícia mais recente do portal
                noticia = feed.entries[0]
                link = noticia.link

                # Se for a primeira execução do bot, popula a lista para não floodar
                if not self.noticias_enviadas:
                    for p_url in FONTES_RSS.values():
                        f = feedparser.parse(p_url)
                        if f.entries:
                            self.noticias_enviadas.add(f.entries[0].link)
                    return

                # Se a notícia for inédita, monta o Embed Laranja
                if link not in self.noticias_enviadas:
                    self.noticias_enviadas.add(link)

                    autor = noticia.get('author', portal)
                    titulo = noticia.title
                    
                    # Tenta buscar 'summary' e, se não achar (caso da IGN), busca 'description'
                    resumo_bruto = noticia.get('summary', noticia.get('description', 'Clique no link para ler a matéria completa.'))
                    
                    # Limpa tags HTML simples que costumam vir no resumo
                    resumo = resumo_bruto.split('<')[0].strip()
                    if len(resumo) > 250:
                        resumo = resumo[:247] + "..."

                    # Criação do Embed Laranja Vibrante Geek
                    embed = discord.Embed(
                        title=titulo,
                        url=link,
                        description=resumo,
                        color=discord.Color.from_str("#FF4500"), # 🟠 Mantido o Laranja aqui
                        timestamp=datetime.datetime.now(UTC_MENOS_TRES)
                    )
                    
                    embed.set_author(name=autor)
                    
                    # Tenta extrair a imagem do post (suporta Crunchyroll e IGN)
                    if 'media_content' in noticia:
                        embed.set_image(url=noticia.media_content[0]['url'])
                    elif 'enclosures' in noticia and noticia.enclosures:
                        embed.set_image(url=noticia.enclosures[0].url)

                    embed.set_footer(text=f"Via {portal} • Atualizado")
                    
                    # Define o nome da fonte em texto baseado no portal atual
                    fonte_texto = "Crunchyroll Noticias" if portal == "Crunchyroll" else "IGN Brasil"
                    
                    # Envia a mensagem com o texto da fonte fora da embed
                    await canal.send(content=f"📰 **{fonte_texto}**", embed=embed)

            except Exception as e:
                print(f"❌ Erro ao puxar {portal}: {e}")

    # =========================================================================
    # 2. GIRO GEEK ESPECIAL (TODOS OS DIAS ÀS 12:00 HORÁRIO DE BRASÍLIA)
    # =========================================================================
    @tasks.loop(time=HORARIO_GIRO)
    async def giro_meio_dia(self):
        await self.bot.wait_until_ready()
        canal = self.bot.get_channel(ID_CANAL_NOTICIAS)
        if not canal:
            return

        cargo_ping = canal.guild.get_role(ID_CARGO_ANIMES)
        mencao_cargo = cargo_ping.mention if cargo_ping else "@Animes"

        noticias_principais = []
        
        for portal, url in FONTES_RSS.items():
            try:
                feed = feedparser.parse(url)
                for i in range(min(2, len(feed.entries))):
                    noticias_principais.append((portal, feed.entries[i]))
            except:
                pass

        if not noticias_principais:
            return

        embed_especial = discord.Embed(
            title="🔥 NOTICIA GEEK DO DIA ESTÁ NO AR 🔥",
            description="Fique por dentro dos acontecimentos mais importantes sobre Animes, Mangás, Games e Cultura Pop de hoje!\n\n━━━━━━━ ● ━━━━━━━",
            color=discord.Color.from_str("#FF3300"),
            timestamp=datetime.datetime.now(UTC_MENOS_TRES)
        )

        for idx, (portal, item) in enumerate(noticias_principais[:3], start=1):
            titulo = item.title
            link = item.link
            embed_especial.add_field(
                name=f"📌 DESTAQUE {idx} • {portal}",
                value=f"**[{titulo}]({link})**\n*Fique ligado nas atualizações dessa matéria.*\n\u200b",
                inline=False
            )

        primeira_noticia = noticias_principais[0][1]
        if 'media_content' in primeira_noticia:
            embed_especial.set_image(url=primeira_noticia.media_content[0]['url'])
        elif 'enclosures' in primeira_noticia and primeira_noticia.enclosures:
            embed_especial.set_image(url=primeira_noticia.enclosures[0].url)

        embed_especial.set_footer(text="Edição Especial Diária • Central de Notícias")
        
        await canal.send(content=f"🔔 {mencao_cargo} **Horário Nobre! Veja o resumo das principais novidades:**", embed=embed_especial)

    # =========================================================================
    # 3. COMANDO DE TESTE MANUAL (COM VALIDAÇÃO DE PERMISSÕES)
    # =========================================================================
    @app_commands.command(name="testar_noticia", description="Força o envio da notícia mais recente da IGN para testar a formatação do embed laranja.")
    @app_commands.checks.has_permissions(manage_channels=True, manage_roles=True)
    async def testar_noticia(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔄 Conectando aos portais e gerando embed laranja de teste...", ephemeral=True)
        
        canal = self.bot.get_channel(ID_CANAL_NOTICIAS)
        if not canal:
            await interaction.followup.send(f"❌ Erro: Canal de texto com ID `{ID_CANAL_NOTICIAS}` não foi encontrado no servidor.", ephemeral=True)
            return

        try:
            feed = feedparser.parse(FONTES_RSS["IGN Brasil"])
            if not feed.entries:
                await interaction.followup.send("❌ Erro: O feed da IGN Brasil respondeu vazio no momento.", ephemeral=True)
                return

            noticia = feed.entries[0]
            autor = noticia.get('author', 'IGN Brasil')
            titulo = noticia.title
            
            resumo_bruto = noticia.get('summary', noticia.get('description', 'Clique no link para ler a matéria completa.'))
            resumo = resumo_bruto.split('<')[0].strip()
            if len(resumo) > 250:
                resumo = resumo[:247] + "..."

            # Monta o embed laranja exatamente igual à rotina oficial
            embed = discord.Embed(
                title=f"🧪 [TESTE] {titulo}",
                url=noticia.link,
                description=resumo,
                color=discord.Color.from_str("#FF4500"), # 🟠 Mantido o Laranja aqui no teste também
                timestamp=datetime.datetime.now(UTC_MENOS_TRES)
            )
            embed.set_author(name=autor)

            if 'media_content' in noticia:
                embed.set_image(url=noticia.media_content[0]['url'])
            elif 'enclosures' in noticia and noticia.enclosures:
                embed.set_image(url=noticia.enclosures[0].url)

            embed.set_footer(text="Teste Manual • Via IGN Brasil")

            await canal.send(content="📰 **IGN Brasil**", embed=embed)
            await interaction.followup.send("✅ O embed de teste foi gerado e enviado com sucesso no canal de notícias!", ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"❌ Ocorreu um erro ao processar o feed: {e}", ephemeral=True)

    @testar_noticia.error
    async def testar_noticia_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ Você precisa ter as permissões de **Gerenciar Canais** e **Gerenciar Cargos** para usar este comando.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(NoticiasGeek(bot))