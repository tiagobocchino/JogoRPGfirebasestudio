import discord
from discord.ui import Button, View, Modal, TextInput, Select

class CharacterCreationModal(Modal, title="Parte 1: Identidade do Herói"):
    name = TextInput(label="Nome do Herói", placeholder="Como serás chamado?", required=True)
    race = TextInput(label="Raça (Humano, Eco, Forjado, Silvestre)", placeholder="Deixe vazio para aleatório", required=False)
    age = TextInput(label="Idade", placeholder="Ex: 25 (Ou deixe vazio para aleatório)", required=False)
    history = TextInput(label="História", style=discord.TextStyle.paragraph, placeholder="Conte sua origem...", required=False)

    def __init__(self, callback):
        super().__init__()
        self.on_complete = callback

    async def on_submit(self, interaction: discord.Interaction):
        # Lógica de Randomização
        races = ["Humano", "Eco", "Forjado", "Silvestre"]
        final_race = self.race.value if self.race.value in races else races[0] # Simplificado
        final_age = self.age.value if self.age.value.isdigit() else "25"
        
        data = {
            "name": self.name.value,
            "race": final_race,
            "age": final_age,
            "history": self.history.value or "Um viajante misterioso vindo da Névoa."
        }
        await self.on_complete(interaction, data)

class CharacterDashboardView(View):
    def __init__(self, char_data, db):
        super().__init__(timeout=None)
        self.char_data = char_data
        self.db = db
        self.current_tab = "Habilidades"
        self.points = 6
        self.attrs = {"FOR": 10, "DES": 10, "CON": 10, "INT": 10, "SAB": 10, "CAR": 10}

    def generate_embed(self):
        embed = discord.Embed(title=f"Ficha de {self.char_data['name']}", color=0x7289da)
        embed.set_author(name=f"Raça: {self.char_data['race']} | Idade: {self.char_data['age']}")
        
        if self.current_tab == "Habilidades":
            content = "**Distribuição de Atributos**\n"
            content += f"Pontos Restantes: **{self.points}**\n\n"
            for attr, val in self.attrs.items():
                content += f"**{attr}:** {val}\n"
            embed.description = content
        elif self.current_tab == "Magias":
            embed.description = "**Ficha de Magias**\n\nNenhuma magia aprendida ainda. (Sistema de Resonância Arcaica ativo)"
        elif self.current_tab == "Itens":
            items_list = "🎒 **Inventário:**\n- Ração de Viagem (3 dias)\n- Pederneira e Isqueiro\n\n⚔️ **Equipamento:**\n"
            # Exemplo de itens por classe (poderia ser expandido)
            class_items = {
                "Vigilante": "- Arco Curto\n- Armadura de Couro",
                "Tecelão": "- Cajado Rúnico\n- Robe de Seda",
                "Baluarte": "- Espada Longa\n- Escudo de Ferro",
                "Devorador": "- Adaga de Prata\n- Capa Escura"
            }
            items_list += class_items.get(self.char_data.get("tags", [""])[0], "- Trajes de Camponês")
            embed.description = items_list
            embed.add_field(name="🛡️ Defesa (CA)", value="10 + DES", inline=True)
            embed.add_field(name="🔋 Carga", value="0 / 10 Slots", inline=True)
            
        return embed

    @discord.ui.button(label="Habilidades", style=discord.ButtonStyle.primary)
    async def tab_skills(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_tab = "Habilidades"
        await interaction.response.edit_message(embed=self.generate_embed(), view=self)

    @discord.ui.button(label="Magias", style=discord.ButtonStyle.primary)
    async def tab_spells(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_tab = "Magias"
        await interaction.response.edit_message(embed=self.generate_embed(), view=self)

    @discord.ui.button(label="Itens", style=discord.ButtonStyle.primary)
    async def tab_items(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_tab = "Itens"
        await interaction.response.edit_message(embed=self.generate_embed(), view=self)

    @discord.ui.button(label="FOR +", style=discord.ButtonStyle.secondary, row=1)
    async def for_plus(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.points > 0:
            self.attrs["FOR"] += 1
            self.points -= 1
            await interaction.response.edit_message(embed=self.generate_embed(), view=self)
        else:
            await interaction.response.send_message("Sem pontos!", ephemeral=True)

    @discord.ui.button(label="DES +", style=discord.ButtonStyle.secondary, row=1)
    async def des_plus(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.points > 0:
            self.attrs["DES"] += 1
            self.points -= 1
            await interaction.response.edit_message(embed=self.generate_embed(), view=self)
        else:
            await interaction.response.send_message("Sem pontos!", ephemeral=True)

    @discord.ui.button(label="SALVAR", style=discord.ButtonStyle.success, row=2)
    async def save_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Salvar no Supabase
        full_data = {
            **self.char_data,
            "attributes": self.attrs,
            "hp_max": 10 + (self.attrs["CON"] - 10),
            "level": 1
        }
        self.db.create_character(str(interaction.user.id), full_data)
        await interaction.response.edit_message(content="✅ Personagem salvo com sucesso!", embed=None, view=None)
