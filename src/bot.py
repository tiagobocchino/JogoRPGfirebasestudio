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
        intents.members = True # Necessário para o on_member_join
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

@bot.event
async def on_member_join(member):
    # Procura pelo canal de boas-vindas no servidor
    channel = discord.utils.get(member.guild.text_channels, name="🌟-portal-de-entrada")
    if channel:
        embed = discord.Embed(
            title=f"⚔️ Bem-vindo ao Vale, {member.display_name}!",
            description=(
                "Sua jornada pelas **Crônicas do Vale** começa aqui.\n\n"
                "**Como começar:**\n"
                "1️⃣ Vá até o canal <#ID_FICHAS> e use o comando `/ficha` para manifestar sua alma e atributos.\n"
                "2️⃣ Leia a mitologia em <#ID_LORE> para entender os perigos da Névoa.\n"
                "3️⃣ Escolha uma mesa na categoria **CRÔNICAS** e comece a narrar sua ação!\n\n"
                "*Que os Ecos te guiem...*"
            ),
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(content=f"O portal se abre para {member.mention}!", embed=embed)

@bot.tree.command(name="setup", description="Limpa o servidor e configura a estrutura final do RPG")
async def setup(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Você precisa ser administrador!", ephemeral=True)
    
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild

    # --- 0. LIMPEZA PROFUNDA (Wipe) ---
    print(f"Iniciando limpeza no servidor {guild.name}")
    for category in guild.categories:
        # Não apaga a categoria onde o comando foi dado para evitar erros de interação
        if interaction.channel.category and category.id == interaction.channel.category.id:
            continue
        for channel in category.channels:
            await channel.delete()
        await category.delete()

    # Apaga canais que estão fora de categorias (exceto o atual)
    for channel in guild.channels:
        if isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel)):
            if channel.id == interaction.channel.id: continue
            if channel.category: continue # Já tratado acima
            try: await channel.delete()
            except: pass

    # --- 1. COMECE AQUI E AJUDA ---
    cat_start = await guild.create_category("🚀 COMECE AQUI E AJUDA")
    start_ch = await guild.create_text_channel("🌟-comece-aqui", category=cat_start)
    help_ch = await guild.create_text_channel("❓-ajuda-e-suporte", category=cat_start)

    # --- 2. SALAS PARA JOGOS ---
    cat_games = await guild.create_category("🎮 SALAS PARA JOGOS")
    await guild.create_text_channel("⚔️-mesa-geral", category=cat_games)
    await guild.create_text_channel("🕯️-ordem-da-lamparina", category=cat_games)
    await guild.create_text_channel("⚒️-sindicato-do-ferro", category=cat_games)

    # --- 3. SALA DE PERSONAGEM ---
    cat_char = await guild.create_category("🧙 SALA DE PERSONAGEM")
    char_ch = await guild.create_text_channel("📜-criação-e-edição", category=cat_char)

    # --- 4. LOBBY E DESCONTRAÇÃO ---
    cat_lobby = await guild.create_category("🍻 LOBBY E DESCONTRAÇÃO")
    await guild.create_text_channel("💬-bate-papo", category=cat_lobby)
    await guild.create_text_channel("🎵-music-player", category=cat_lobby)
    await guild.create_voice_channel("🔊-taberna-voz", category=cat_lobby)

    # --- 5. COMUNIDADE ---
    cat_com = await guild.create_category("🤝 COMUNIDADE")
    invite_ch = await guild.create_text_channel("🎟️-convites", category=cat_com)

    # --- 6. REGRAS ---
    cat_rules = await guild.create_category("⚖️ REGRAS")
    rules_ch = await guild.create_text_channel("📜-regras-do-vale", category=cat_rules)

    # --- CONFIGURAÇÃO DE MENSAGENS ---

    # Mensagem de Boas-vindas e Passo a Passo (ONBOARDING)
    embed_start = discord.Embed(
        title="✨ BEM-VINDO ÀS CRÔNICAS DO VALE",
        description=(
            "Siga este passo a passo para iniciar sua jornada épica:\n\n"
            "**1️⃣ MANIFESTE SUA ALMA**\n"
            f"Vá até {char_ch.mention} e use o comando `/ficha`. Isso criará sua identidade no mundo.\n\n"
            "**2️⃣ CONHEÇA AS LEIS**\n"
            f"Leia as regras básicas em {rules_ch.mention}. O Vale é perigoso para os despreparados.\n\n"
            "**3️⃣ ESCOLHA SUA AVENTURA**\n"
            "Escolha uma das salas na categoria **SALAS PARA JOGOS** e comece a interagir com o Mestre!\n\n"
            "**4️⃣ TRAGA SEUS AMIGOS**\n"
            f"Gere convites em {invite_ch.mention} para expandir nossa irmandade."
        ),
        color=discord.Color.gold()
    )
    await start_ch.send(embed=embed_start)

    # Mensagem de Convites
    await invite_ch.send(
        embed=discord.Embed(title="Recrutamento", description="Clique abaixo para convidar aliados!", color=discord.Color.green()),
        view=InviteView()
    )

    await interaction.followup.send("✅ Servidor reorganizado com sucesso!", ephemeral=True)

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

    # O Mestre responde em qualquer canal das Salas de Jogos ou que comece com 'mesa-'
    is_rpg_channel = (
        message.channel.category and message.channel.category.name == "🎮 SALAS PARA JOGOS"
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
