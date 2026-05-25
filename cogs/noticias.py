import discord
from discord.ext import commands, tasks
import feedparser
import datetime
from datetime import time

# =========================================================================
#                         CONFIGURAÇÕES DO SISTEMA
# =========================================================================
ID_CANAL_NOTICIAS = 1508516714181296219  # <-- ID do seu canal de notícias geek
ID_CARGO_ANIMES = 1489820094518530049    # <-- COLOQUE OQUI O ID DO CARGO PARA O PING DAS 12:00

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

                # Se a notícia for inédita, monta o Embed Laranja estilo Readybot
                if link not in self.noticias_enviadas:
                    self.noticias_enviadas.add(link)

                    autor = noticia.get('author', portal)
                    titulo = noticia.title
                    
                    # Limpa tags HTML simples que costumam vir no resumo
                    resumo = noticia.get('summary', 'Clique no link para ler a matéria completa.').split('<')[0]
                    if len(resumo) > 250:
                        resumo = resumo[:247] + "..."

                    # Criação do Embed Laranja
                    embed = discord.Embed(
                        title=titulo,
                        url=link,
                        description=resumo,
                        color=discord.Color.from_str("#FF4500"), # Laranja Vibrante Geek
                        timestamp=datetime.datetime.now()
                    )
                    
                    embed.set_author(name=autor)
                    
                    # Tenta extrair a imagem do post (suporta Crunchyroll e IGN)
                    if 'media_content' in noticia:
                        embed.set_image(url=noticia.media_content[0]['url'])
                    elif 'enclosures' in noticia and noticia.enclosures:
                        embed.set_image(url=noticia.enclosures[0].url)

                    embed.set_footer(text=f"Via {portal} • Atualizado")
                    
                    await canal.send(embed=embed)

            except Exception as e:
                print(f"❌ Erro ao puxar {portal}: {e}")

    # =========================================================================
    # 2. GIRO GEEK ESPECIAL (TODOS OS DIAS ÀS 12:00)
    # =========================================================================
    # Configura a rotina para rodar exatamente ao meio-dia (Horário do Servidor)
    @tasks.loop(time=time(hour=12, minute=0))
    async def giro_meio_dia(self):
        await self.bot.wait_until_ready()
        canal = self.bot.get_channel(ID_CANAL_NOTICIAS)
        if not canal:
            return

        # Busca o cargo para fazer o ping
        cargo_ping = canal.guild.get_role(ID_CARGO_ANIMES)
        mencao_cargo = cargo_ping.mention if cargo_ping else "@Animes"

        # Coleta as principais notícias recentes dos dois portais
        noticias_principais = []
        
        for portal, url in FONTES_RSS.items():
            try:
                feed = feedparser.parse(url)
                # Pega as 2 primeiras de cada portal para selecionar
                for i in range(min(2, len(feed.entries))):
                    noticias_principais.append((portal, feed.entries[i]))
            except:
                pass

        if not noticias_principais:
            return

        # Embed Super Especial e Robusto
        embed_especial = discord.Embed(
            title="🔥 NOTICIA GEEK DO DIA ESTÁ NO AR 🔥",
            description="Fique por dentro dos acontecimentos mais importantes sobre Animes, Mangás, Games e Cultura Pop de hoje!\n\n━━━━━━━ ● ━━━━━━━",
            color=discord.Color.from_str("#FF3300"), # Um tom de laranja ainda mais forte
            timestamp=datetime.datetime.now()
        )

        # Adiciona campos organizados (Fields) para cada notícia de destaque
        for idx, (portal, item) in enumerate(noticias_principais[:3], start=1):
            titulo = item.title
            link = item.link
            embed_especial.add_field(
                name=f"📌 DESTAQUE {idx} • {portal}",
                value=f"**[{titulo}]({link})**\n*Fique ligado nas atualizações dessa matéria.*\n\u200b",
                inline=False
            )

        # Imagem de destaque principal no embed especial (Pega a foto do primeiro item)
        primeira_noticia = noticias_principais[0][1]
        if 'media_content' in primeira_noticia:
            embed_especial.set_image(url=primeira_noticia.media_content[0]['url'])
        elif 'enclosures' in primeira_noticia and primeira_noticia.enclosures:
            embed_especial.set_image(url=primeira_noticia.enclosures[0].url)

        embed_especial.set_footer(text="Edição Especial Diária • Central de Notícias")
        
        # Envia dando o PING e anexando o embed de resumo recheado
        await canal.send(content=f"🔔 {mencao_cargo} **Horário Nobre! Veja o resumo das principais novidades:**", embed=embed_especial)

async def setup(bot):
    await bot.add_cog(NoticiasGeek(bot))