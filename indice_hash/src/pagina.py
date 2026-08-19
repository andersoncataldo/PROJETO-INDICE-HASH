"""
Módulo Página
=============
Representa a estrutura de divisão e alocação física da tabela na "mídia de
armazenamento" (simulada em memória). Cada página guarda um número limitado
de registros (tuplas), definido pelo tamanho da página escolhido pelo usuário.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Pagina:
    """Representa uma página física contendo um subconjunto de registros."""

    numero: int
    capacidade: int
    registros: List[str] = field(default_factory=list)

    def esta_cheia(self) -> bool:
        return len(self.registros) >= self.capacidade

    def adicionar_registro(self, chave: str) -> bool:
        """Adiciona um registro à página, se houver espaço."""
        if self.esta_cheia():
            return False
        self.registros.append(chave)
        return True

    def __len__(self) -> int:
        return len(self.registros)

    def __repr__(self) -> str:
        primeiros = self.registros[:3]
        resto = "..." if len(self.registros) > 3 else ""
        return (f"Página {self.numero} "
                f"({len(self.registros)}/{self.capacidade} registros) "
                f"[{', '.join(primeiros)}{resto}]")


def calcular_quantidade_paginas(total_registros: int, tamanho_pagina: int) -> int:
    """Calcula quantas páginas são necessárias para armazenar todos os
    registros, dado o tamanho (capacidade) de cada página."""
    if tamanho_pagina <= 0:
        raise ValueError("O tamanho da página deve ser maior que zero.")
    return -(-total_registros // tamanho_pagina)  # teto (ceil) sem usar math


def calcular_tamanho_pagina(total_registros: int, quantidade_paginas: int) -> int:
    """Calcula o tamanho (capacidade) de cada página, dado o número de
    páginas desejado pelo usuário (caminho inverso do parâmetro)."""
    if quantidade_paginas <= 0:
        raise ValueError("A quantidade de páginas deve ser maior que zero.")
    return -(-total_registros // quantidade_paginas)  # teto (ceil)


def paginar_registros(registros: List[str], tamanho_pagina: int) -> List[Pagina]:
    """Divide a lista de registros em páginas sequenciais, respeitando a
    ordem original do arquivo de dados."""
    paginas: List[Pagina] = []
    total = len(registros)
    num_paginas = calcular_quantidade_paginas(total, tamanho_pagina)

    idx = 0
    for num in range(num_paginas):
        pagina = Pagina(numero=num, capacidade=tamanho_pagina)
        fatia = registros[idx: idx + tamanho_pagina]
        for chave in fatia:
            pagina.adicionar_registro(chave)
        paginas.append(pagina)
        idx += tamanho_pagina

    return paginas
