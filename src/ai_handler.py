import os
import google.generativeai as genai
from dotenv import load_dotenv

# Configura o caminho para o arquivo .env (na raiz do projeto)
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

class AIService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if api_key:
            genai.configure(api_key=api_key)
        
        self.system_prompt = self._load_prompt()
        
        # DIAGNÓSTICO: Listar modelos disponíveis para esta chave
        print("🔍 Consultando modelos disponíveis para sua chave API...")
        try:
            available_models = [m.name for m in genai.list_models()]
            print(f"📋 Modelos encontrados: {available_models}")
        except Exception as list_e:
            print(f"❌ Erro ao listar modelos: {list_e}")

        # Tenta o modelo LITE primeiro (maior cota gratuita)
        models_to_try = [
            "gemini-2.0-flash-lite", 
            "gemini-2.0-flash", 
            "gemini-flash-latest", 
            "gemini-pro-latest"
        ]
        self.model = None
        
        for m_name in models_to_try:
            try:
                test_model = genai.GenerativeModel(
                    model_name=m_name,
                    system_instruction=self.system_prompt
                )
                # Não dá pra testar sem enviar mensagem, então vamos configurar o primeiro e torcer
                self.model = test_model
                self.current_model_name = m_name
                print(f"✅ Modelo {m_name} pré-selecionado.")
                break
            except Exception as e:
                print(f"❌ Falha ao configurar {m_name}: {e}")

    def _load_prompt(self):
        try:
            path = os.path.join(os.path.dirname(__file__), "gm_system_prompt.md")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            return "Você é um Mestre de RPG medieval no Vale dos Ecos Perdidos."
        except Exception:
            return "Você é um Mestre de RPG medieval."

    async def generate_response(self, user_message: str, history: list = None):
        if not self.model:
            return "Erro: O sistema de IA não foi configurado corretamente. Verifique sua chave API."

        try:
            chat = self.model.start_chat(history=history or [])
            response = await chat.send_message_async(user_message)
            return response.text
        except Exception as e:
            # Se o flash falhou no envio, tenta o pro como última chance
            if "gemini-1.5" in self.current_model_name:
                print(f"🔄 Erro no {self.current_model_name}, tentando fallback para gemini-pro...")
                fallback_model = genai.GenerativeModel(model_name="gemini-pro")
                chat = fallback_model.start_chat(history=history or [])
                response = await chat.send_message_async(f"{self.system_prompt}\n\nUsuário: {user_message}")
                return response.text
            raise e

    def format_history_for_gemini(self, db_history: list):
        """Converte o formato do Supabase para o formato do Gemini"""
        formatted = []
        for entry in db_history:
            role = "user" if entry["role"] == "user" else "model"
            formatted.append({"role": role, "parts": [entry["content"]]})
        return formatted
