# 🌐 Multi-Language Translator Tool

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![PySide6](https://img.shields.io/badge/GUI-PySide6-green)
![API](https://img.shields.io/badge/API-Integration-orange)

## 📋 Sobre o Projeto
Aplicação Desktop desenvolvida em Python para tradução de textos em tempo real. O software consome APIs externas de tradução e oferece uma interface gráfica amigável (GUI) construída com **PySide6**.

O projeto demonstra a capacidade de integração de sistemas (consumo de APIs REST), manipulação de eventos de interface e tratamento de respostas JSON.

## 🚀 Funcionalidades
* **Suporte a Múltiplos Idiomas:** Tradução entre Português, Inglês, Espanhol, Francês, Alemão, Italiano, Japonês, Coreano, Russo e Chinês.
* **API Integration:** Conexão assíncrona com a API MyMemory/LibreTranslate.
* **Manipulação de Texto:** Ferramentas de clipboard (copiar/colar), limpeza rápida e inversão de idiomas.
* **Interface Personalizável:** Design responsivo com temas visuais.

## 🛠️ Tecnologias
* **Linguagem:** Python
* **Interface (GUI):** PySide6 (Qt for Python)
* **Requisições:** Requests Library
* **Tratamento de Dados:** JSON Parsing

## 📦 Como Rodar
```bash
# Clone o repositório
git clone [https://github.com/nikolasmrt/tradutor-de-linguagens](https://github.com/nikolasmrt/tradutor-de-linguagens)

# Instale as dependências
pip install requests PySide6

# Execute a aplicação
python main.py
