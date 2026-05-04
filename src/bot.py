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

@bot.tree.command(name="setup", description="Configura automaticamente os canais do RPG no servidor")
async def setup(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Você precisa ser administrador para usar este comando!", ephemeral=True)
    
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    
    # 1. Criar Categoria
    category = await guild.create_category("🏰 CRÔNICAS DO VALE")
    
    # 2. Criar Canais
    lobby = await guild.create_text_channel("🌟-lobby-de-entrada", category=category)
    music = await guild.create_text_channel("🎵-musica-ambiente", category=category)
    admin = await guild.create_text_channel("📜-administracao-e-ficha", category=category)
    mesa = await guild.create_text_channel("⚔️-mesa-testes", category=category)
    
    # 3. Mensagens Iniciais
    await lobby.send(f"## Bem-vindo ao Vale, viajante!\nEste é o seu ponto de partida. Aguarde aqui outros heróis.\n\nUse `/ficha` em {admin.mention} para começar.")
    await music.send(f"## Central de Som\nConecte-se a um canal de voz e use `/play [url]` para definir o clima da aventura.")
    await admin.send(f"## Terminal de Fichas\nUse `/ficha` aqui para criar ou editar seu personagem.")
    
    await interaction.followup.send("✅ Estrutura criada com sucesso!", ephemeral=True)

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

    if message.channel.name.startswith('mesa-'):
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
