"""Carregamento das chaves a partir de um arquivo de texto."""

from pathlib import Path
from typing import List, Optional


def carregar_palavras(caminho_arquivo: str, limite: Optional[int] = None) -> List[str]:
    """Lê as palavras do arquivo, opcionalmente limitando a quantidade."""
    caminho = Path(caminho_arquivo)
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo de dados não encontrado: {caminho_arquivo}")

    palavras: List[str] = []
    with caminho.open("r", encoding="utf-8") as f:
        for linha in f:
            palavra = linha.strip()
            if not palavra:
                continue
            palavras.append(palavra)
            if limite is not None and len(palavras) >= limite:
                break
    return palavras
