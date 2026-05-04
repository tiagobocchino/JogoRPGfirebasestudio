import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Configura o caminho para o arquivo .env (na raiz do projeto)
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

class DatabaseService:
    def __init__(self):
        url: str = os.getenv("SUPABASE_URL", "").strip()
        # Limpa a URL caso ela tenha o sufixo /rest/v1/
        if url.endswith("/rest/v1/"):
            url = url.replace("/rest/v1/", "")
        # No Railway, as variáveis já vêm no os.environ. 
        # Só carregamos o .env se as variáveis essenciais NÃO existirem.
        if not os.getenv("SUPABASE_URL"):
            env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
            if os.path.exists(env_path):
                load_dotenv(dotenv_path=env_path)
                print("ℹ️ Carregando variáveis via arquivo .env")
            else:
                print("ℹ️ Arquivo .env não encontrado, usando variáveis de sistema.")
        else:
            print("ℹ️ Usando variáveis de ambiente do Sistema (Railway/Cloud)")
            
        self.url = os.getenv("SUPABASE_URL", "").strip()
        if self.url.endswith("/rest/v1/"):
            self.url = self.url.replace("/rest/v1/", "")
            
        # Aceita múltiplos nomes para a chave para facilitar o deploy
        self.key: str = (
            os.getenv("SUPABASE_SERVICE_ROLE_KEY") or 
            os.getenv("SUPABASE_KEY") or 
            os.getenv("SUPABASE_ANON_PUBLIC", "")
        ).strip()

        if not self.url:
            print("❌ ERRO: Variável SUPABASE_URL não encontrada no ambiente!")
        if not self.key:
            print("❌ ERRO: Nenhuma chave Supabase (SERVICE_ROLE ou ANON) encontrada!")
            
        if not self.url or not self.key:
            print("👉 Verifique as 'Variables' no painel do Railway.")
            return

        print(f"✅ Supabase configurado com URL: {self.url[:15]}...")
        self.supabase: Client = create_client(self.url, self.key)

    # --- Personagens ---
    def create_character(self, player_id: str, char_data: dict):
        # char_data deve conter: name, attributes, race, age, backstory
        hp = char_data.get("hp_max", 10)
        data = {
            "player_id": player_id,
            "name": char_data["name"],
            "race": char_data.get("race", "Humano"),
            "age": int(char_data.get("age", 20)),
            "backstory": char_data.get("backstory", ""),
            "hp_current": hp,
            "hp_max": hp,
            "attributes": char_data["attributes"],
            "tags": char_data.get("tags", []),
            "inventory": char_data.get("inventory", [])
        }
        return self.supabase.table("characters").insert(data).execute()

    def get_character(self, player_id: str):
        res = self.supabase.table("characters").select("*").eq("player_id", player_id).eq("is_active", True).execute()
        return res.data[0] if res.data else None

    # --- Sessões ---
    def get_or_create_session(self, channel_id: str, player_ids: list):
        res = self.supabase.table("game_sessions").select("*").eq("channel_id", channel_id).execute()
        if res.data:
            return res.data[0]
        
        new_session = {
            "channel_id": channel_id,
            "player_ids": player_ids,
            "history_log": [],
            "world_context": "Início da Jornada no Vale dos Ecos Perdidos"
        }
        return self.supabase.table("game_sessions").insert(new_session).execute().data[0]

    def update_session_history(self, session_id: str, history: list):
        return self.supabase.table("game_sessions").update({
            "history_log": history,
            "last_interaction": "now()"
        }).eq("id", session_id).execute()

    # --- Acesso ---
    def validate_invite(self, code: str, player_id: str):
        res = self.supabase.table("access_links").select("*").eq("code", code).eq("is_valid", True).execute()
        if res.data:
            invite = res.data[0]
            self.supabase.table("access_links").update({
                "is_valid": False,
                "used_by_id": player_id
            }).eq("id", invite["id"]).execute()
            return True
        return False
