"""
Módulo Bucket
=============
Representa a estrutura que mapeia chaves de busca em endereços de página.

Tratamento de colisão: cada bucket comporta até FR entradas (chave, página).
Quando duas chaves diferentes são mapeadas para o mesmo bucket, isso é uma
COLISÃO, resolvida por encadeamento simples dentro do próprio bucket
(enquanto houver espaço).

Tratamento de overflow: quando um bucket já está com as FR posições ocupadas
e uma nova chave precisa ser inserida nele, ocorre OVERFLOW, resolvido por
encadeamento de buckets de transbordamento (overflow chaining) — um bucket
extra é criado e encadeado ao bucket original.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class Entrada:
    """Uma entrada dentro de um bucket: chave de busca + página onde está."""
    chave: str
    pagina: int


@dataclass
class Bucket:
    """Bucket de tamanho fixo FR, com suporte a encadeamento de overflow."""

    id: int
    capacidade_fr: int
    entradas: List[Entrada] = field(default_factory=list)
    overflow: Optional["Bucket"] = None
    eh_bucket_overflow: bool = False

    def esta_cheio(self) -> bool:
        return len(self.entradas) >= self.capacidade_fr

    def inserir(self, chave: str, pagina: int, proximo_id_overflow_fn) -> Tuple[bool, bool]:
        """
        Insere (chave, página) no bucket, tratando colisão e overflow.

        Retorna (houve_colisao, houve_overflow):
          - houve_colisao: True se o bucket já continha ao menos 1 entrada
            antes desta inserção (ou seja, duas chaves foram mapeadas ao
            mesmo bucket).
          - houve_overflow: True se foi necessário criar/usar um bucket de
            transbordamento porque este bucket já estava cheio.
        """
        houve_colisao = len(self.entradas) > 0

        if not self.esta_cheio():
            self.entradas.append(Entrada(chave, pagina))
            return houve_colisao, False

        # Bucket cheio -> overflow. Segue a cadeia até achar espaço.
        if self.overflow is None:
            novo_id = proximo_id_overflow_fn()
            self.overflow = Bucket(id=novo_id, capacidade_fr=self.capacidade_fr,
                                    eh_bucket_overflow=True)
        # Delegação recursiva na cadeia de overflow.
        self.overflow.inserir(chave, pagina, proximo_id_overflow_fn)
        return houve_colisao, True

    def buscar(self, chave: str) -> Tuple[bool, Optional[int], int]:
        """
        Busca uma chave neste bucket (e em sua cadeia de overflow, se houver).

        Retorna (encontrado, numero_da_pagina, custo_em_acessos_a_bucket).
        O custo conta quantos buckets (principal + overflow) precisaram ser
        acessados até encontrar (ou não encontrar) a chave.
        """
        for entrada in self.entradas:
            if entrada.chave == chave:
                return True, entrada.pagina, 1

        if self.overflow is not None:
            encontrado, pagina, custo_extra = self.overflow.buscar(chave)
            return encontrado, pagina, 1 + custo_extra

        return False, None, 1

    def contar_overflow_chain(self) -> int:
        """Conta quantos buckets de overflow estão encadeados a partir daqui."""
        if self.overflow is None:
            return 0
        return 1 + self.overflow.contar_overflow_chain()

    def total_entradas_na_cadeia(self) -> int:
        total = len(self.entradas)
        if self.overflow is not None:
            total += self.overflow.total_entradas_na_cadeia()
        return total
