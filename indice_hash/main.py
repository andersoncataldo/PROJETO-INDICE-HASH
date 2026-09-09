#!/usr/bin/env python3
"""Ponto de entrada da aplicação."""

import os
import sys

# Permite executar o script a partir de qualquer diretório.
DIRETORIO_BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(DIRETORIO_BASE, "src"))

from gui import main  # noqa: E402

if __name__ == "__main__":
    main()
