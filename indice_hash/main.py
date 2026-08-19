#!/usr/bin/env python3
"""
Trabalho de Banco de Dados — Índice Hash Estático
====================================================
Ponto de entrada da aplicação. Execute com:

    python3 main.py

Requisitos: Python 3.10+ (usa apenas a biblioteca padrão: tkinter, dataclasses).
No Linux, se o tkinter não estiver instalado, rode:
    sudo apt-get install python3-tk
"""

import os
import sys

# Garante que os módulos em src/ sejam encontrados independentemente de onde
# o script for chamado.
DIRETORIO_BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(DIRETORIO_BASE, "src"))

from gui import main  # noqa: E402

if __name__ == "__main__":
    main()
