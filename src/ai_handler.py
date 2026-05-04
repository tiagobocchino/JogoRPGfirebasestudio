import os
import google.generativeai as genai
from dotenv import load_dotenv

# Configura o caminho para o arquivo .env (na raiz do projeto)
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

class AIService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
        
        # Carregar o System Prompt
        self.system_prompt = self._load_prompt()
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=self.system_prompt
        )

    def _load_prompt(self):
        try:
            # Tenta carregar o prompt do arquivo
            path = os.path.join(os.path.dirname(__file__), "gm_system_prompt.md")
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return "Você é um Mestre de RPG medieval."

    async def generate_response(self, user_message: str, history: list = None):
        """
        Gera uma resposta baseada no histórico da sessão.
        history format: [{"role": "user", "parts": ["..."]}, {"role": "model", "parts": ["..."]}]
        """
        chat = self.model.start_chat(history=history or [])
        response = await chat.send_message_async(user_message)
        return response.text

    def format_history_for_gemini(self, db_history: list):
        """Converte o formato do Supabase para o formato do Gemini"""
        formatted = []
        for entry in db_history:
            role = "user" if entry["role"] == "user" else "model"
            formatted.append({"role": role, "parts": [entry["content"]]})
        return formatted
