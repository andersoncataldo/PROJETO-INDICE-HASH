"""
Módulo Data Loader
===================
Responsável por carregar o arquivo de dados (words.txt, ~466 mil palavras,
uma por linha, todas únicas -> cada palavra é uma chave) para a memória.
"""

from pathlib import Path
from typing import List, Optional


def carregar_palavras(caminho_arquivo: str, limite: Optional[int] = None) -> List[str]:
    """
    Lê o arquivo de palavras e retorna uma lista de chaves (strings).

    limite: se informado, carrega apenas as N primeiras palavras (útil para
    testes rápidos ou para não sobrecarregar a interface gráfica com 466 mil
    linhas). Se None, carrega o arquivo inteiro.
    """
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
