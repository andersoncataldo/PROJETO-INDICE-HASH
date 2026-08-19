"""
Módulo Índice Hash
===================
Orquestra a construção do índice hash estático a partir das páginas de dados,
aplica a função hash a cada chave, insere nos buckets (tratando colisão e
overflow) e oferece busca indexada + cálculo de estatísticas.
"""

import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

from bucket import Bucket
from pagina import Pagina


@dataclass
class ResultadoBusca:
    encontrado: bool
    chave: str
    pagina: Optional[int]
    custo_acessos: int          # nº de buckets acessados (cadeia de overflow) + 1 (leitura da página)
    tempo_segundos: float
    endereco_bucket: int


@dataclass
class ResultadoTableScan:
    encontrado: bool
    chave: str
    pagina_encontrada: Optional[int]
    paginas_lidas: int           # custo = nº de páginas lidas até achar (ou até o fim)
    tempo_segundos: float
    log_paginas: List[int] = field(default_factory=list)  # ordem das páginas visitadas


class IndiceHash:
    def __init__(self, paginas: List[Pagina], fr: int,
                 funcao_hash: Callable[[str, int], int]):
        """
        paginas: lista de páginas já carregadas com os registros.
        fr: tamanho do bucket (nº máximo de tuplas endereçadas por bucket).
        funcao_hash: função hash(chave, nb) -> endereço do bucket.
        """
        self.paginas = paginas
        self.fr = fr
        self.funcao_hash = funcao_hash

        self.nr = sum(len(p) for p in paginas)  # cardinalidade da tabela
        self.nb = self._calcular_nb(self.nr, fr)

        self.buckets: List[Bucket] = [
            Bucket(id=i, capacidade_fr=fr) for i in range(self.nb)
        ]
        self._proximo_id_overflow = self.nb  # ids de overflow continuam a contagem

        # Estatísticas de construção
        self.total_colisoes = 0
        self.total_overflows = 0
        self.total_insercoes = 0

    @staticmethod
    def _calcular_nb(nr: int, fr: int) -> int:
        """NB deve satisfazer NB > NR / FR."""
        if fr <= 0:
            raise ValueError("FR (tamanho do bucket) deve ser maior que zero.")
        nb = nr // fr + 1  # garante estritamente maior que NR/FR
        return max(nb, 1)

    def _proximo_id_overflow_fn(self) -> int:
        novo_id = self._proximo_id_overflow
        self._proximo_id_overflow += 1
        return novo_id

    # ------------------------------------------------------------------
    # Construção do índice
    # ------------------------------------------------------------------
    def construir(self, callback_progresso=None) -> None:
        """
        Percorre página por página, aplica a função hash a cada chave e
        insere (chave, página) no bucket correspondente.
        """
        for pagina in self.paginas:
            for chave in pagina.registros:
                endereco = self.funcao_hash(chave, self.nb)
                bucket = self.buckets[endereco]
                houve_colisao, houve_overflow = bucket.inserir(
                    chave, pagina.numero, self._proximo_id_overflow_fn
                )
                self.total_insercoes += 1
                if houve_colisao:
                    self.total_colisoes += 1
                if houve_overflow:
                    self.total_overflows += 1

            if callback_progresso:
                callback_progresso(pagina.numero, len(self.paginas))

    # ------------------------------------------------------------------
    # Busca via índice
    # ------------------------------------------------------------------
    def buscar(self, chave: str) -> ResultadoBusca:
        inicio = time.perf_counter()
        endereco = self.funcao_hash(chave, self.nb)
        bucket = self.buckets[endereco]
        encontrado, pagina, custo_buckets = bucket.buscar(chave)
        # +1 representa o acesso de leitura da página de dados encontrada
        custo_total = custo_buckets + (1 if encontrado else 0)
        fim = time.perf_counter()
        return ResultadoBusca(
            encontrado=encontrado,
            chave=chave,
            pagina=pagina,
            custo_acessos=custo_total,
            tempo_segundos=fim - inicio,
            endereco_bucket=endereco,
        )

    # ------------------------------------------------------------------
    # Table scan
    # ------------------------------------------------------------------
    def table_scan(self, chave: str) -> ResultadoTableScan:
        inicio = time.perf_counter()
        log_paginas = []
        for pagina in self.paginas:
            log_paginas.append(pagina.numero)
            if chave in pagina.registros:
                fim = time.perf_counter()
                return ResultadoTableScan(
                    encontrado=True,
                    chave=chave,
                    pagina_encontrada=pagina.numero,
                    paginas_lidas=len(log_paginas),
                    tempo_segundos=fim - inicio,
                    log_paginas=log_paginas,
                )
        fim = time.perf_counter()
        return ResultadoTableScan(
            encontrado=False,
            chave=chave,
            pagina_encontrada=None,
            paginas_lidas=len(log_paginas),
            tempo_segundos=fim - inicio,
            log_paginas=log_paginas,
        )

    # ------------------------------------------------------------------
    # Estatísticas
    # ------------------------------------------------------------------
    def taxa_colisoes(self) -> float:
        if self.total_insercoes == 0:
            return 0.0
        return 100.0 * self.total_colisoes / self.total_insercoes

    def taxa_overflows(self) -> float:
        if self.total_insercoes == 0:
            return 0.0
        return 100.0 * self.total_overflows / self.total_insercoes

    def resumo(self) -> dict:
        return {
            "NR (nº de tuplas)": self.nr,
            "NB (nº de buckets)": self.nb,
            "FR (tuplas/bucket)": self.fr,
            "Nº de páginas": len(self.paginas),
            "Total de inserções": self.total_insercoes,
            "Colisões": self.total_colisoes,
            "Taxa de colisões (%)": round(self.taxa_colisoes(), 2),
            "Overflows": self.total_overflows,
            "Taxa de overflows (%)": round(self.taxa_overflows(), 2),
        }
