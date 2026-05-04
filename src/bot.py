import os
import sys
import discord
from discord import app_commands
from discord.ext import commands
import random
from dotenv import load_dotenv

# Garante que a pasta 'src' está no path para o deploy
sys.path.append(os.path.dirname(__file__))

from database import DatabaseService
from ai_handler import AIService
from rpg_mechanics import RPGMechanics
from character_ui import CharacterCreationModal, CharacterDashboardView

# Configura o caminho para o arquivo .env (na raiz do projeto)
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

class RPG_Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.db = DatabaseService()
        self.ai = AIService()
        self.mechanics = RPGMechanics()

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Comandos sincronizados para {self.user}")

bot = RPG_Bot()

@bot.event
async def on_ready():
    print(f'Logado como {bot.user} (ID: {bot.user.id})')
    print('------')

# --- COMANDOS ---
@bot.tree.command(name="ficha", description="Cria ou edita sua ficha de personagem")
async def ficha(interaction: discord.Interaction):
    char_data = bot.db.get_character(str(interaction.user.id))
    
    # Se já existir um personagem (char_data não é None)
    if char_data:
        view = CharacterDashboardView(char_data, bot.db)
        await interaction.response.send_message("Sua ficha atual:", embed=view.generate_embed(), view=view, ephemeral=True)
    else:
        async def modal_callback(inter, data):
            view = CharacterDashboardView(data, bot.db)
            await inter.response.send_message(embed=view.generate_embed(), view=view, ephemeral=True)
        await interaction.response.send_modal(CharacterCreationModal(modal_callback))

class InviteView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Gerar Convite 🎟️", style=discord.ButtonStyle.success, custom_id="generate_invite")
    async def generate_invite(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Cria um convite válido por 24h para até 5 usos
        invite = await interaction.channel.create_invite(max_age=86400, max_uses=5, unique=True)
        await interaction.response.send_message(
            f"⚔️ **O Vale precisa de heróis!**\nAqui está o seu convite exclusivo para enviar aos seus aliados:\n{invite.url}\n\n*Válido por 24h para até 5 pessoas.*", 
            ephemeral=True
        )

@bot.tree.command(name="setup", description="Configura automaticamente os canais do RPG no servidor")
async def setup(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Você precisa ser administrador para usar este comando!", ephemeral=True)
    
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    
    # --- 1. CATEGORIA: CRÔNICAS DO VALE ---
    cat_rpg = await guild.create_category("🏰 CRÔNICAS DO VALE")
    
    # Salas de Aventura (Mestre IA responde aqui)
    lore = await guild.create_text_channel("📜-lore-e-mitologia", category=cat_rpg)
    mesa_geral = await guild.create_text_channel("⚔️-mesa-geral", category=cat_rpg)
    mesa_lamparina = await guild.create_text_channel("🕯️-ordem-da-lamparina", category=cat_rpg)
    mesa_ferro = await guild.create_text_channel("⚒️-sindicato-do-ferro", category=cat_rpg)
    mesa_sussurros = await guild.create_text_channel("🌫️-os-sussurrantes", category=cat_rpg)
    
    # --- 2. CATEGORIA: COMUNIDADE ---
    cat_com = await guild.create_category("🤝 COMUNIDADE")
    admin = await guild.create_text_channel("📜-fichas-e-regras", category=cat_com)
    convites = await guild.create_text_channel("🎟️-convites", category=cat_com)
    
    # --- 3. CONFIGURAÇÃO DE MENSAGENS INICIAIS ---
    
    # Mensagem de Lore
    embed_lore = discord.Embed(
        title="O Vale dos Ecos Perdidos",
        description=(
            "O mundo como conhecemos é apenas um eco de algo maior. "
            "A **Névoa Cinzenta** consome tudo, mas nas ruínas dos ancestrais, heróis encontram poder.\n\n"
            "Escolha seu caminho nas salas de aventura abaixo!"
        ),
        color=discord.Color.dark_purple()
    )
    await lore.send(embed=embed_lore)

    # Mensagem de Convites
    embed_invite = discord.Embed(
        title="Traga seus Aliados",
        description="Clique no botão abaixo para gerar um link de convite e fortalecer nossa irmandade no Vale!",
        color=discord.Color.green()
    )
    await convites.send(embed=embed_invite, view=InviteView())

    # Instrução de Fichas
    await admin.send(
        "## Terminal de Heróis\nUse o comando `/ficha` aqui para manifestar sua presença no Vale e criar sua ficha de personagem."
    )
    
    await interaction.followup.send("✅ Mundo expandido com sucesso!", ephemeral=True)

@bot.tree.command(name="play", description="Toca uma música no canal de voz")
async def play(interaction: discord.Interaction, url: str):
    if not interaction.user.voice:
        return await interaction.response.send_message("Você precisa estar em um canal de voz!", ephemeral=True)
    
    await interaction.response.send_message(f"🎵 Tentando tocar: {url}\n*(Nota: Requer FFmpeg instalado no servidor)*")
    # Lógica de conexão de voz seria implementada aqui

# 2. Comando de Rolagem Integrado
@bot.tree.command(name="rolar", description="Rola um dado (ex: 1d20+2)")
async def rolar(interaction: discord.Interaction, comando: str):
    num, faces, mod = bot.mechanics.parse_roll_command(comando)
    resultados = [random.randint(1, faces) for _ in range(num)]
    total = sum(resultados) + mod
    
    await interaction.response.send_message(f'🎲 **Rolagem:** {comando}\n**Dados:** {resultados} + {mod}\n**Total:** {total}')

# 3. Interação com o Mestre (IA Real)
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # O Mestre responde em qualquer canal das Crônicas ou que comece com 'mesa-'
    is_rpg_channel = (
        message.channel.category and message.channel.category.name == "🏰 CRÔNICAS DO VALE"
    ) or message.channel.name.startswith('mesa-')

    if is_rpg_channel and not message.content.startswith('!'):
        async with message.channel.typing():
            # 1. Obter ou Criar Sessão
            session = bot.db.get_or_create_session(str(message.channel.id), [str(message.author.id)])
            
            # 2. Obter Ficha do Jogador
            char = bot.db.get_character(str(message.author.id))
            char_context = f"\n[JOGADOR: {char['name']} | TAGS: {char['tags']} | ATRIBUTOS: {char['attributes']}]" if char else "\n[JOGADOR SEM FICHA]"
            
            # 3. Formatar Histórico para Gemini
            history = bot.ai.format_history_for_gemini(session["history_log"])
            
            # 4. Gerar Resposta
            user_input = f"{message.author.display_name} diz: {message.content} {char_context}"
            response_text = await bot.ai.generate_response(user_input, history)
            
            # 5. Atualizar Banco
            new_log = session["history_log"] + [
                {"role": "user", "content": user_input},
                {"role": "model", "content": response_text}
            ]
            bot.db.update_session_history(session["id"], new_log[-20:]) # Mantém as últimas 20 mensagens
            
            await message.reply(response_text)

    await bot.process_commands(message)

if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_TOKEN')
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Erro: DISCORD_TOKEN não encontrado no .env")
