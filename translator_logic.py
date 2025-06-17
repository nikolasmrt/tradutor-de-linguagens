
from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool
import sys
import requests

MYMEMORY_API_URL = "https://api.mymemory.translated.net/get"

IDIOMAS = {
    "Português": "pt",
    "Inglês": "en",
    "Espanhol": "es",
    "Francês": "fr",
    "Alemão": "de",
    "Italiano": "it",
    "Japonês": "ja",
    "Coreano": "ko",
    "Russo": "ru",
    "Chinês (Simplificado)": "zh-cn",
    "Árabe": "ar",
    "Hindi": "hi"
}

class TranslatorWorker(QObject):
    translation_finished = Signal(str, str, str, str)
    error_occurred = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def perform_translation(self, text: str, source_lang_code: str, target_lang_code: str,
                            source_lang_name: str, target_lang_name: str):
        if not text.strip():
            self.error_occurred.emit("Nenhum texto para traduzir.")
            return

        if source_lang_code == target_lang_code:
            self.translation_finished.emit(text, text, source_lang_name, target_lang_name)
            return

        translated_text = ""
        try:
            params = {
                "q": text,
                "langpair": f"{source_lang_code}|{target_lang_code}",

            }
            response = requests.get(MYMEMORY_API_URL, params=params, timeout=10)
            response.raise_for_status() 

            data = response.json()

            if data and data.get("responseStatus") == 200:
                translated_text = data["responseData"]["translatedText"]
                if translated_text == "INVALID_LANG_PAIR":
                    self.error_occurred.emit("Combinação de idiomas inválida ou não suportada pela API.")
                    return
                if translated_text == text:
                    self.error_occurred.emit(f"Tradução falhou: A API retornou o texto original. Tente outro par de idiomas.")
                    return

            else:
                error_message = data.get("responseDetails", "Erro desconhecido na API MyMemory.")
                if data.get("responseStatus") == 403:
                    error_message = "Limite de uso da API MyMemory excedido ou acesso negado. Tente mais tarde."
                self.error_occurred.emit(f"Erro na tradução (API MyMemory): {error_message}")
                return

        except requests.exceptions.Timeout:
            self.error_occurred.emit("Tempo limite excedido na conexão com a API MyMemory. Verifique sua internet.")
            return
        except requests.exceptions.RequestException as e:
            self.error_occurred.emit(f"Erro de conexão com a API MyMemory: {e}")
            return
        except Exception as e:
            self.error_occurred.emit(f"Erro inesperado durante a tradução com MyMemory: {e}")
            return

        if not translated_text or translated_text.strip() == text.strip():
            self.error_occurred.emit("Tradução inválida ou igual ao original. Tente outros idiomas ou verifique a conexão.")
        else:
            self.translation_finished.emit(text, translated_text, source_lang_name, target_lang_name)

    def perform_language_detection(self, text: str):
        detected_lang_code = "indefinido"
  
        self.translation_finished.emit(text, "", "", detected_lang_code)