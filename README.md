# 🈂️ Tradutor Multilíngue com PySide6

Este é um aplicativo gráfico de tradução de textos desenvolvido em **Python** utilizando **PySide6**. Ele permite traduzir entre diversos idiomas, utilizando a API `googletrans` (quando disponível), com fallback para uma tradução mock offline.


---

## 🚀 Funcionalidades

- Tradução entre vários idiomas (Português, Inglês, Espanhol, Francês, Alemão, etc)
- Tradução automática após digitação (com debounce)
- Histórico de traduções realizadas
- Copiar tradução para área de transferência
- Salvar tradução em arquivo `.txt`
- Interface responsiva com PySide6
- Ícone personalizado

---

## 📦 Tecnologias e Bibliotecas

- [Python 3.x](https://www.python.org/)
- [PySide6](https://doc.qt.io/qtforpython/)
- [googletrans](https://py-googletrans.readthedocs.io/en/latest/) (opcional)
- Fallback de tradução offline com dicionário mock

---

## 🛠️ Instalação

### 1. Dependências

```bash
requirements 
pip install PySide6 googletrans==4.0.0-rc1

