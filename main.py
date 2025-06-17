
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QComboBox, QFileDialog, QMessageBox, QListWidget,
    QSpacerItem, QSizePolicy, QStackedWidget
)
from PySide6.QtGui import QIcon, QFontDatabase 
from PySide6.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve, QRunnable, QThreadPool, Signal
import sys
from datetime import datetime


from translator_logic import TranslatorWorker, IDIOMAS 

class TranslationTask(QRunnable):
    def __init__(self, worker, text, source_lang_code, target_lang_code, source_lang_name, target_lang_name):
        super().__init__()
        self.worker = worker
        self.text = text
        self.source_lang_code = source_lang_code
        self.target_lang_code = target_lang_code
        self.source_lang_name = source_lang_name
        self.target_lang_name = target_lang_name

    def run(self):
        self.worker.perform_translation(
            self.text, self.source_lang_code, self.target_lang_code,
            self.source_lang_name, self.target_lang_name
        )

class DetectionTask(QRunnable):
    def __init__(self, worker, text):
        super().__init__()
        self.worker = worker
        self.text = text

    def run(self):
        self.worker.perform_language_detection(self.text)


class TranslatorApp(QWidget):
    language_detected_ui_signal = Signal(str) 

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tradutor")
        self.setMinimumSize(800, 600)

        self.thread_pool = QThreadPool.globalInstance()
        self.thread_pool.setMaxThreadCount(2)

        self.worker = TranslatorWorker()
        self.worker.translation_finished.connect(self.handle_translation_result)
        self.worker.error_occurred.connect(self.handle_translation_error)
        
        self.worker.translation_finished.connect(self._handle_detection_result)
        self.language_detected_ui_signal.connect(self._update_detected_language_in_ui)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a2e; 
                color: #e0e0e0; 
                font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
                font-size: 14px;
            }
            QLineEdit, QTextEdit, QComboBox, QListWidget {
                background-color: #2c2c4d;
                border: 1px solid #4a4a7a;
                border-radius: 10px; 
                padding: 10px;
                color: #e0e0e0;
                selection-background-color: #4CAF50; 
                outline: none;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QListWidget:focus {
                border: 2px solid #FF3399; 
            }
            QPushButton {
                background-color: #FF3399; 
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 25px;
                font-weight: bold;
                text-transform: uppercase; 
                letter-spacing: 1px;
                
            }
            QPushButton:hover {
                background-color: #6600ff; 
            }
            QPushButton:pressed {
                background-color: #6600ff; 
            }
            QLabel {
                color: #B3E5FC; 
                font-weight: bold;
                padding-bottom: 5px;
            }
            QComboBox::drop-down {
                border: 0px;
                width: 25px; 
            }
            QComboBox::down-arrow {
                image: url(icons/arrow_down_cyan.png); 
                width: 16px;
                height: 16px;
            }
            QComboBox QAbstractItemView {
                background-color: #2c2c4d;
                border: 1px solid #4a4a7a;
                selection-background-color: #4CAF50; 
                color: #e0e0e0;
                border-radius: 8px;
            }
            QListWidget {
                border: 1px solid #4a4a7a;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3c3c5c; 
            }
            QListWidget::item:selected {
                background-color: #383861; 
                color: #00BCD4; 
                border-radius: 5px;
            }
            #loadingLabel {
                color: #4CAF50;
                font-weight: bold;
                font-size: 16px;
                text-align: center;
                padding: 10px;
            }
            #statusMessageLabel { 
                background-color: #3c3c4d; 
                color: #e0e0e0; 
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 13px;
                text-align: center;
                min-height: 25px; 
            }
            .warning_status { 
                color: #FFC107; 
            }
            .info_status { 
                color: #8BC34A; 
            }
        """)

        my_icon = QIcon()
        
        my_icon.addFile('images/logo.png') 
        self.setWindowIcon(my_icon)
        
        self.hist = []
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.start_translation_task)

        # Componentes da UI
        self.input_text = QLineEdit()
        self.input_text.setPlaceholderText("Digite o texto para traduzir...")
        self.input_text.textChanged.connect(self.agendar_traducao)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)

        self.lang_from = QComboBox()
        self.lang_to = QComboBox()
        self.populate_language_comboboxes()
        
        self.translate_btn = QPushButton("TRADUZIR")
        self.translate_btn.clicked.connect(self.start_translation_task)
        self.translate_btn.setIcon(QIcon('icons/translate_icon.png'))

        self.swap_btn = QPushButton("↔ INVERTER")
        self.swap_btn.clicked.connect(self.swap_languages)
        self.swap_btn.setIcon(QIcon('icons/swap_icon.png'))

        self.clear_btn = QPushButton("LIMPAR")
        self.clear_btn.clicked.connect(self.clear_fields)
        self.clear_btn.setIcon(QIcon('icons/clear_icon.png'))

        self.save_btn = QPushButton("SALVAR")
        self.save_btn.clicked.connect(self.salvar_traducao)
        self.save_btn.setIcon(QIcon('icons/save_icon.png'))

        self.copy_btn = QPushButton("COPIAR")
        self.copy_btn.clicked.connect(self.copiar_traducao)
        self.copy_btn.setIcon(QIcon('icons/copy_icon.png'))

        self.loading_label = QLabel("Traduzindo...")
        self.loading_label.setObjectName("loadingLabel")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.hide()

        self.hist_list = QListWidget()
        self.hist_list.setMaximumHeight(150)
        self.hist_list.itemClicked.connect(self.recarregar_hist)

        self.status_message_label = QLabel("")
        self.status_message_label.setObjectName("statusMessageLabel")
        self.status_message_label.setAlignment(Qt.AlignCenter)
        self.status_message_label.hide()

        self.status_timer = QTimer(self)
        self.status_timer.setSingleShot(True)
        self.status_timer.timeout.connect(self.status_message_label.hide)


        # Layout da UI
        main_layout = QVBoxLayout()

        main_layout.addWidget(QLabel("TEXTO DE ENTRADA:"))
        main_layout.addWidget(self.input_text)
        
        lang_selection_layout = QHBoxLayout()
        lang_selection_layout.addWidget(QLabel("DE:"))
        lang_selection_layout.addWidget(self.lang_from)
        lang_selection_layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        lang_selection_layout.addWidget(self.swap_btn)
        lang_selection_layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        lang_selection_layout.addWidget(QLabel("PARA:"))
        lang_selection_layout.addWidget(self.lang_to)
        main_layout.addLayout(lang_selection_layout)

        action_buttons_layout = QHBoxLayout()
        action_buttons_layout.addWidget(self.translate_btn)
        action_buttons_layout.addWidget(self.clear_btn)
        main_layout.addLayout(action_buttons_layout)

        translation_area_layout = QVBoxLayout()
        translation_area_layout.addWidget(QLabel("TRADUÇÃO:"))
        
        self.output_stacked_widget = QStackedWidget()
        self.output_stacked_widget.addWidget(self.output_text)
        self.output_stacked_widget.addWidget(self.loading_label)
        translation_area_layout.addWidget(self.output_stacked_widget)

        main_layout.addLayout(translation_area_layout)

        save_copy_layout = QHBoxLayout()
        save_copy_layout.addWidget(self.save_btn)
        save_copy_layout.addWidget(self.copy_btn)
        main_layout.addLayout(save_copy_layout)

        main_layout.addWidget(QLabel("HISTÓRICO DE TRADUÇÕES:"))
        main_layout.addWidget(self.hist_list)

        main_layout.addWidget(self.status_message_label)

        self.setLayout(main_layout)

        self.input_text.textChanged.connect(self.start_detection_task)

    def populate_language_comboboxes(self):
        self.lang_from.clear()
        self.lang_to.clear()
        
        for nome in IDIOMAS:
            self.lang_from.addItem(nome)
            self.lang_to.addItem(nome)
        
        self.lang_from.setCurrentText("Português")
        self.lang_to.setCurrentText("Inglês")

    def start_detection_task(self):
        text = self.input_text.text().strip()
        detection_task = DetectionTask(self.worker, text)
        self.thread_pool.start(detection_task)

    def _handle_detection_result(self, original_text, translated_text, source_lang_name, detected_lang_code):
        if not translated_text and not source_lang_name and detected_lang_code != "":
            self.language_detected_ui_signal.emit(detected_lang_code)
            
    def _update_detected_language_in_ui(self, detected_lang_code):
        if detected_lang_code != "indefinido":
            for nome, code in IDIOMAS.items():
                if code == detected_lang_code:
                    if self.lang_from.currentText() != nome:
                        self.lang_from.setCurrentText(nome)
                    break
        else:
            if self.input_text.text().strip() == "":
                self.lang_from.setCurrentText("Português")


    def agendar_traducao(self):
        self.timer.stop() 
        self.timer.start(1000)

    def start_translation_task(self):
        self.timer.stop()
        
        text = self.input_text.text().strip()
        if not text:
            self._mostrar_aviso("Digite algo para traduzir.") 
            return

        self.loading_label.setText("Traduzindo...")
        self.output_stacked_widget.setCurrentIndex(1)

        source_lang_name = self.lang_from.currentText()
        target_lang_name = self.lang_to.currentText()
        source_lang_code = IDIOMAS[source_lang_name]
        target_lang_code = IDIOMAS[target_lang_name]

        translation_task = TranslationTask(
            self.worker, text, source_lang_code, target_lang_code,
            source_lang_name, target_lang_name
        )
        self.thread_pool.start(translation_task)

    def handle_translation_result(self, original_text, translated_text, source_lang_name, target_lang_name):
        self.output_text.setPlainText(translated_text)
        self.output_stacked_widget.setCurrentIndex(0)

        if "Erro" in translated_text:
             self._mostrar_aviso(translated_text) 
             return
        
        if not translated_text or original_text == translated_text.strip():
            if not "Erro" in translated_text:
                self._mostrar_aviso("Tradução inválida ou igual ao original. Tente outros idiomas.")
            return

        hist_entry = f"{source_lang_name} ({original_text}) → {target_lang_name} ({translated_text})"
        if hist_entry not in self.hist:
            self.hist.append(hist_entry)
            self.hist_list.addItem(hist_entry)
        
        self._mostrar_info("Tradução concluída!")

    def handle_translation_error(self, message):
        self.output_stacked_widget.setCurrentIndex(0)
        self.output_text.setPlainText(f"Erro: {message}")
        self._mostrar_aviso(f"Erro na tradução: {message}") 

    def swap_languages(self):
        current_from_text = self.lang_from.currentText()
        current_to_text = self.lang_to.currentText()
        
        self.lang_from.setCurrentText(current_to_text)
        self.lang_to.setCurrentText(current_from_text)
        
        self.agendar_traducao()
        self._mostrar_info("Idiomas invertidos!")

    def clear_fields(self):
        self.input_text.clear()
        self.output_text.clear()
        self.input_text.setFocus()
        self.lang_from.setCurrentText("Português")
        self.lang_to.setCurrentText("Inglês")
        self._mostrar_info("Campos limpos.") 

    def salvar_traducao(self):
        entrada = self.input_text.text().strip()
        traducao = self.output_text.toPlainText().strip()
        
        if not traducao and not entrada:
            self._mostrar_aviso("Nada para salvar. Faça uma tradução primeiro ou digite um texto.") 
            return
        
        conteudo = f"--- Tradução {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n"
        conteudo += f"Idioma Origem: {self.lang_from.currentText()}\n"
        conteudo += f"Texto Original: {entrada}\n\n"
        conteudo += f"Idioma Destino: {self.lang_to.currentText()}\n"
        conteudo += f"Tradução: {traducao}\n"
        conteudo += "---------------------------------------\n\n"

        suggested_filename = f"traducao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        nome_arquivo, _ = QFileDialog.getSaveFileName(
            self, "Salvar Tradução", suggested_filename, "Arquivos de Texto (*.txt);;Todos os Arquivos (*)"
        )
        
        if nome_arquivo:
            try:
                with open(nome_arquivo, "a", encoding="utf-8") as f:
                    f.write(conteudo)
                self._mostrar_info("Tradução salva com sucesso!") 
            except Exception as e:
                self._mostrar_aviso(f"Erro ao salvar: {e}") 

    def copiar_traducao(self):
        traducao = self.output_text.toPlainText()
        if traducao:
            QApplication.clipboard().setText(traducao)
            self._mostrar_info("Tradução copiada para a área de transferência.") 
        else:
            self._mostrar_aviso("Nada para copiar.") 

    def recarregar_hist(self, item):
        full_text = item.text()
        try:
            parts = full_text.split(" → ", 1)
            
            origin_lang_part, original_text_part = parts[0].split(" (", 1)
            original_text = original_text_part[:-1]
            
            target_lang_part, translated_text_part = parts[1].split(" (", 1)
            translated_text = translated_text_part[:-1]

            self.input_text.setText(original_text)
            self.output_text.setPlainText(translated_text)
            
            self.lang_from.setCurrentText(origin_lang_part.strip())
            self.lang_to.setCurrentText(target_lang_part.strip())
            
            self._mostrar_info("Histórico carregado!") 

        except Exception as e:
            self._mostrar_aviso(f"Erro ao carregar histórico: Formato inválido. Erro: {e}")
            print(f"Erro ao parsear histórico: {full_text} -> {e}")

    
    def _mostrar_aviso(self, mensagem):
        self.status_message_label.setText(f"⚠️ {mensagem}")
        self.status_message_label.setStyleSheet("#statusMessageLabel { color: #FFC107; }") 
        self.status_message_label.show()
        self.status_timer.start(5000) 

    def _mostrar_info(self, mensagem):
        self.status_message_label.setText(f"✅ {mensagem}")
        self.status_message_label.setStyleSheet("#statusMessageLabel { color: #8BC34A; }") 
        self.status_message_label.show()
        self.status_timer.start(3000) 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = TranslatorApp()
    janela.show()
    sys.exit(app.exec())