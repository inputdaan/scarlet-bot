import os
import asyncio
import discord
from discord import app_commands
from discord.ext import commands

# --- CONFIGURAÇÕES DE CARGOS DO SEU SERVIDOR ---
# ⚠️ ID REAL DO CARGO GERAL DA SUA STAFF (MODERADOR/SUPORTE)
ID_CARGO_STAFF = 1489820037312151603          

# --- FUNÇÕES DE PERSISTÊNCIA DO CONTADOR ---

def get_next_ticket_id():
    filename = "ticket_counter.txt"
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write("1")
        return "001"
    
    with open(filename, "r") as f:
        try:
            current_id = int(f.read().strip())
        except ValueError:
            current_id = 1
            
    next_id = current_id + 1
    with open(filename, "w") as f:
        f.write(str(next_id))
        
    return f"{current_id:03d}"


# --- VIEWS DE CONTROLE DO TICKET ---

# 1. Painel que aparece APÓS o ticket ser fechado (Controles da Staff)
class StaffControlView(discord.ui.View):
    def __init__(self, creator_id: int = None):
        super().__init__(timeout=None)
        self.creator_id = creator_id 

    @discord.ui.button(label="Open", style=discord.ButtonStyle.success, emoji="🔓", custom_id="reopen_ticket_btn")
    async def reopen_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        channel = interaction.channel
        
        # Recupera o membro original da memória
        member = guild.get_member(self.creator_id) if self.creator_id else None
        
        # Fallback: se o bot reiniciou e perdeu a variável da memória, acha o dono buscando a primeira mensagem do canal
        if not member:
            async for msg in channel.history(limit=20, oldest_first=True):
                if msg.mentions:
                    member = msg.mentions[0]
                    break
        
        if member:
            # Devolve a permissão de ver e falar no canal para o usuário criador
            overwrite = channel.overwrites_for(member)
            overwrite.read_messages = True
            overwrite.send_messages = True
            await channel.set_permissions(member, overwrite=overwrite)
            
            await interaction.response.send_message(f"🔓 Ticket reaberto por {interaction.user.mention}. {member.mention} foi adicionado de volta!", ephemeral=False)
            await interaction.message.delete()
        else:
            await interaction.response.send_message("❌ Não foi possível reabrir automaticamente: usuário não encontrado. Adicione-o manualmente.", ephemeral=True)

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger, emoji="⛔", custom_id="delete_ticket_btn")
    async def delete_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("***Deletando o canal...***", ephemeral=False)
        await asyncio.sleep(2)
        await interaction.channel.delete()


# 2. Mensagem intermediária de Confirmação de Fechamento (Evita fechar sem querer)
# Fica sem custom_id fixo de propósito pois o timeout de 30 segundos impede que ela seja persistente
class ConfirmCloseView(discord.ui.View):
    def __init__(self, creator_id: int = None):
        super().__init__(timeout=30)
        self.creator_id = creator_id

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger, custom_id="confirm_close_yes")
    async def confirm_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel
        guild = interaction.guild
        cargo_staff = guild.get_role(ID_CARGO_STAFF)

        # Resgata o ID do criador se o bot reiniciou durante o processo
        creator_id = self.creator_id
        if not creator_id:
            async for msg in channel.history(limit=20, oldest_first=True):
                if msg.mentions:
                    creator_id = msg.mentions[0].id
                    break

        # Remove o acesso de leitura e escrita de quem abriu o ticket (membros comuns)
        for member, overwrite in channel.overwrites.items():
            if isinstance(member, discord.Member):
                is_staff = cargo_staff in member.roles if cargo_staff else False
                if not member.guild_permissions.administrator and not is_staff:
                    overwrite.read_messages = False
                    overwrite.send_messages = False
                    await channel.set_permissions(member, overwrite=overwrite)

        # Apaga a mensagem de confirmação vermelha
        await interaction.message.delete()

        # Envia no canal o aviso de quem fechou
        await interaction.channel.send(f"Ticket fechado por {interaction.user.mention}")
        
        staff_embed = discord.Embed(
            title="Ticket Fechado",
            description=f"Ticket Fechado por {interaction.user.mention}",
            color=discord.Color.yellow()
        )
        
        # Envia o painel final com as opções Open e Delete
        await channel.send(
            content="```Support team ticket controls```", 
            embed=staff_embed, 
            view=StaffControlView(creator_id=creator_id)
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, custom_id="confirm_close_no")
    async def confirm_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        await interaction.response.defer()


# 3. View inicial dentro do ticket aberto (Contém o botão Close original)
class TicketCloseView(discord.ui.View):
    def __init__(self, creator_id: int = None):
        super().__init__(timeout=None)
        self.creator_id = creator_id

    @discord.ui.button(label="Close", style=discord.ButtonStyle.secondary, emoji="🔒", custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        creator_id = self.creator_id
        if not creator_id:
            async for msg in interaction.channel.history(limit=10, oldest_first=True):
                if msg.mentions:
                    creator_id = msg.mentions[0].id
                    break
                    
        await interaction.response.send_message(
            content="⚠️ Você tem certeza que deseja fechar este ticket? Clique no botão abaixo para confirmar.", 
            view=ConfirmCloseView(creator_id=creator_id),
            ephemeral=False
        )


# 4. View do Painel Principal (Fica fixa no canal de suporte)
class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def create_ticket(self, interaction: discord.Interaction, topico: str, mensagem_boas_vindas: str, conteudo_texto: str):
        guild = interaction.guild
        user = interaction.user
        category = interaction.channel.category 

        ticket_id = get_next_ticket_id()
        
        # 💡 Nome formatado com o tópico à esquerda: ex: parceria-ticket-001
        channel_name = f"{topico}-ticket-{ticket_id}"

        # Permissões base do canal privado
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False), 
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True), 
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True) 
        }

        # Aplica permissões para a equipe de Staff verem o canal
        cargo_staff = guild.get_role(ID_CARGO_STAFF)
        if cargo_staff:
            overwrites[cargo_staff] = discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True)

        # Cria o canal focado na mesma categoria
        ticket_channel = await guild.create_text_channel(
            name=channel_name, 
            overwrites=overwrites,
            category=category
        )

        # Mensagem ephemeral que some sozinha após 30 segundos
        await interaction.response.send_message(f"✅ Seu ticket foi criado em {ticket_channel.mention}!", ephemeral=True, delete_after=30)

        embed = discord.Embed(
            title=f"Atendimento - {topico.capitalize()} (#\u200b{ticket_id})",
            description=mensagem_boas_vindas,
            color=discord.Color.green()
        )
        embed.set_footer(text="Clique no botão abaixo para encerrar o atendimento.")
        
        # Envia a mensagem com o conteúdo de texto dinâmico fora da embed
        await ticket_channel.send(content=conteudo_texto, embed=embed, view=TicketCloseView(creator_id=user.id))


    # --- BOTÕES DO PAINEL PRINCIPAL ---

    @discord.ui.button(label="Dúvida", style=discord.ButtonStyle.primary, emoji="❓", custom_id="btn_duvida")
    async def duvida_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(
            interaction, 
            topico="duvida", 
            mensagem_boas_vindas="O suporte irá responde-lo em breve.",
            conteudo_texto=f"{interaction.user.mention} Bem vindo! | <@&1489820036603445248> <@&1489820041456128130>" 
        )

    @discord.ui.button(label="Parceria", style=discord.ButtonStyle.success, emoji="🤝", custom_id="btn_parceria")
    async def parceria_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(
            interaction, 
            topico="parceria", 
            mensagem_boas_vindas="Envie a proposta da sua parceria.\nA nossa equipe irá analisar em breve.",
            conteudo_texto=f"{interaction.user.mention} Bem vindo! | <@&1489820042358161478> <@&1489820036603445248>" 
        )

    @discord.ui.button(label="Sugestão", style=discord.ButtonStyle.secondary, emoji="💡", custom_id="btn_sugestao")
    async def sugestao_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(
            interaction, 
            topico="sugestao", 
            mensagem_boas_vindas="Escreva sua sugestão abaixo.",
            conteudo_texto=f"{interaction.user.mention} Bem vindo! | <@&1489820036603445248>"
        )

    @discord.ui.button(label="Denúncia", style=discord.ButtonStyle.danger, emoji="🚨", custom_id="btn_denuncia")
    async def denuncia_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(
            interaction, 
            topico="denuncia", 
            mensagem_boas_vindas="Relate a sua denúncia com provas se possível.\nA Staff irá averiguar.",
            conteudo_texto=f"{interaction.user.mention} Nova denúncia registrada. | <@&1489820041456128130> <@&1489820034053177485> <@&1489820036603445248>"
        )


# --- CLASSE COG QUE GERENCIA ESTE ARQUIVO ---
class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="setup_tickets", description="Envia o painel fixo de tickets neste canal.")
    @app_commands.checks.has_permissions(administrator=True) 
    async def setup_tickets(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎫 Central de Atendimento",
            description="Precisa de ajuda ou quer falar com a Staff?\nEscolha a categoria abaixo para abrir um ticket privado.",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Sistema de tickets automática e segura.")
        
        await interaction.response.send_message("✅ Painel configurado com sucesso!", ephemeral=True)
        await interaction.channel.send(embed=embed, view=TicketPanelView())

    @setup_tickets.error
    async def setup_tickets_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ Você precisa ser um Administrador para usar este comando.", ephemeral=True)


# Função para o main.py carregar o arquivo
async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))
    
    # 💎 Registro persistente de todas as views sem limite de tempo (timeout=None)
    bot.add_view(TicketPanelView())
    bot.add_view(TicketCloseView())
    bot.add_view(StaffControlView())
