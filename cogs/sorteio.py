import discord
from discord.ext import commands
from discord import app_commands
import asyncio

# ID do canal específico que você forneceu para o evento de sorteio
ID_CANAL_SORTEIO = 1512235024056062024

class EventoSorteio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # O evento começa desativado por padrão
        self.modo_sorteio_ativo = False
        print("🟢 [COG] Sistema de Menção de Eventos carregado!")

    # =========================================================================
    # DETECTOR DE ENTRADA DE MEMBROS (ON_MEMBER_JOIN)
    # =========================================================================
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # Se o modo de sorteio estiver desligado, o bot não faz nada
        if not self.modo_sorteio_ativo:
            return

        canal = self.bot.get_channel(ID_CANAL_SORTEIO)
        if not canal:
            print(f"❌ Erro no Evento: Canal com ID {ID_CANAL_SORTEIO} não encontrado.")
            return

        try:
            # Envia a mensagem mencionando o novo membro
            mensagem = await canal.send(content=f"{member.mention}")
            
            # Aguarda 1 segundo antes de apagar para garantir que o Discord processe a notificação
            await asyncio.sleep(1.0)
            
            # Apaga a mensagem logo em seguida (Menção Fantasma)
            await mensagem.delete()
            
        except discord.Forbidden:
            print(f"❌ Erro de Permissão: O bot não tem permissão para enviar ou deletar mensagens no canal {ID_CANAL_SORTEIO}.")
        except Exception as e:
            print(f"❌ Erro inesperado ao processar entrada de membro: {e}")

    # =========================================================================
    # COMANDO SLASH PARA ATIVAR/DESATIVAR O MODO DE SORTEIO
    # =========================================================================
    @app_commands.command(name="modo_sorteio", description="Ativa ou desativa as menções fantasmas automáticas para novos membros.")
    @app_commands.describe(status="Escolha se deseja ligar ou desligar o monitoramento de entrada.")
    @app_commands.choices(status=[
        app_commands.Choice(name="Ligar Modo Sorteio", value="ativar"),
        app_commands.Choice(name="Desligar Modo Sorteio", value="desativar")
    ])
    @app_commands.checks.has_permissions(manage_guild=True) # Apenas administradores/gerentes podem usar
    async def modo_sorteio(self, interaction: discord.Interaction, status: app_commands.Choice[str]):
        if status.value == "ativar":
            self.modo_sorteio_ativo = True
            await interaction.response.send_message(
                "🔥 **[EVENTO LIGADO]** O bot agora vai registrar e dar ping fantasma em todos os novos membros que entrarem no servidor!", 
                ephemeral=False
            )
        else:
            self.modo_sorteio_ativo = False
            await interaction.response.send_message(
                "❄️ **[EVENTO DESLIGADO]** O monitoramento de novos membros para o sorteio foi desativado.", 
                ephemeral=False
            )

    # Tratamento de erro caso alguém sem permissão tente usar o comando
    @modo_sorteio.error
    async def modo_sorteio_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(
                "❌ Você precisa da permissão de **Gerenciar Servidor** para alternar o status deste evento.", 
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(EventoSorteio(bot))