"""Estruturas de entradas, buckets e encadeamento de overflow."""

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
        """Insere uma chave e informa se houve colisão ou overflow."""
        houve_colisao = len(self.entradas) > 0

        if not self.esta_cheio():
            self.entradas.append(Entrada(chave, pagina))
            return houve_colisao, False

        # Buckets cheios usam uma cadeia de overflow.
        if self.overflow is None:
            novo_id = proximo_id_overflow_fn()
            self.overflow = Bucket(id=novo_id, capacidade_fr=self.capacidade_fr,
                                    eh_bucket_overflow=True)
        self.overflow.inserir(chave, pagina, proximo_id_overflow_fn)
        return houve_colisao, True

    def buscar(self, chave: str) -> Tuple[bool, Optional[int], int]:
        """Busca uma chave e retorna resultado, página e custo em buckets."""
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
