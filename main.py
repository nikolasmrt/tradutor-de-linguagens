from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QFileDialog, QMessageBox, QListWidget
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer
import sys
from datetime import datetime

try:
    from googletrans import Translator as GoogleTranslator
    gtranslator = GoogleTranslator()
    USE_GOOGLE = True
except ImportError:
    USE_GOOGLE = False
    print("[INFO] Biblioteca 'googletrans' não instalada. Usando tradução mock.")

mock_translations = {
    ("pt", "en"): {"olá": "hello", "mundo": "world"},
    ("en", "pt"): {"hello": "olá", "world": "mundo"},
    ("pt", "es"): {"olá": "hola", "mundo": "mundo"},
    ("es", "pt"): {"hola": "olá", "mundo": "mundo"},
}

idiomas = {
    "Português": "pt",
    "Inglês": "en",
    "Espanhol": "es",
    "Francês": "fr",
    "Alemão": "de",
    "Italiano": "it",
    "Japonês": "ja",
    "Coreano": "ko",
    "Russo": "ru"
}

def traduzir(texto, origem, destino):
    if origem == destino:
        return texto
    if USE_GOOGLE:
        try:
            resultado = gtranslator.translate(texto, src=origem, dest=destino)
            return resultado.text
        except Exception as e:
            return f"Erro na tradução: {e}"
    else:
        palavras = texto.lower().split()
        traducao = []
        for palavra in palavras:
            t = mock_translations.get((origem, destino), {}).get(palavra, f"[{palavra}]")
            traducao.append(t)
        return " ".join(traducao)

class TranslatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tradutor Básico")
        self.setMinimumSize(600, 500)
        self.setStyleSheet("font-size: 14px;")

        my_icon = QIcon()
        my_icon.addFile('icone.ico')

        self.setWindowIcon(my_icon)
        
        self.hist = []
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.realizar_traducao)

        self.input_text = QLineEdit()
        self.input_text.setPlaceholderText("Digite o texto para traduzir")
        self.input_text.textChanged.connect(self.agendar_traducao)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)

        self.lang_from = QComboBox()
        self.lang_to = QComboBox()
        for nome in idiomas:
            self.lang_from.addItem(nome)
            self.lang_to.addItem(nome)
        self.lang_from.setCurrentText("Português")
        self.lang_to.setCurrentText("Inglês")

        self.translate_btn = QPushButton("🔁 Traduzir")
        self.translate_btn.clicked.connect(self.realizar_traducao)

        self.save_btn = QPushButton("💾 Salvar Tradução")
        self.save_btn.clicked.connect(self.salvar_traducao)

        self.copy_btn = QPushButton("📋 Copiar Tradução")
        self.copy_btn.clicked.connect(self.copiar_traducao)

        self.hist_list = QListWidget()
        self.hist_list.setMaximumHeight(100)
        self.hist_list.itemClicked.connect(self.recarregar_hist)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Texto de entrada:"))
        layout.addWidget(self.input_text)

        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("De:"))
        lang_layout.addWidget(self.lang_from)
        lang_layout.addWidget(QLabel("Para:"))
        lang_layout.addWidget(self.lang_to)
        layout.addLayout(lang_layout)

        layout.addWidget(self.translate_btn)
        layout.addWidget(QLabel("Tradução:"))
        layout.addWidget(self.output_text)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.copy_btn)
        layout.addLayout(btn_layout)

        layout.addWidget(QLabel("Histórico de Traduções:"))
        layout.addWidget(self.hist_list)

        self.setLayout(layout)

    def agendar_traducao(self):
        self.timer.start(1000)

    def realizar_traducao(self):
        texto = self.input_text.text().strip()
        if not texto:
            return
        origem = idiomas[self.lang_from.currentText()]
        destino = idiomas[self.lang_to.currentText()]
        resultado = traduzir(texto, origem, destino)

        if not resultado or resultado == texto:
            self._alerta("Tradução inválida ou igual ao original.")
            return

        self.output_text.setPlainText(resultado)
        hist_entry = f"{texto} → {resultado}"
        if hist_entry not in self.hist:
            self.hist.append(hist_entry)
            self.hist_list.addItem(hist_entry)

    def salvar_traducao(self):
        entrada = self.input_text.text().strip()
        traducao = self.output_text.toPlainText().strip()
        if not traducao:
            self._alerta("Nada para salvar. Faça uma tradução primeiro.")
            return
        conteudo = f"[Entrada]: {entrada}\n[Tradução]: {traducao}\n"
        nome_arquivo, _ = QFileDialog.getSaveFileName(self, "Salvar Tradução", f"traducao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "Text Files (*.txt)")
        if nome_arquivo:
            try:
                with open(nome_arquivo, "w", encoding="utf-8") as f:
                    f.write(conteudo)
                self._info("Tradução salva com sucesso!")
            except Exception as e:
                self._alerta(f"Erro ao salvar: {e}")

    def copiar_traducao(self):
        traducao = self.output_text.toPlainText()
        if traducao:
            QApplication.clipboard().setText(traducao)
            self._info("Tradução copiada para a área de transferência.")
        else:
            self._alerta("Nada para copiar.")

    def recarregar_hist(self, item):
        texto_original, traducao = item.text().split(" → ", 1)
        self.input_text.setText(texto_original)
        self.output_text.setPlainText(traducao)

    def _alerta(self, mensagem):
        QMessageBox.warning(self, "Aviso", mensagem)

    def _info(self, mensagem):
        QMessageBox.information(self, "Informação", mensagem)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = TranslatorApp()
    janela.show()
    sys.exit(app.exec())