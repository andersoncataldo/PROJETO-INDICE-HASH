"""
Módulo Função Hash
==================
Implementa a função hash que mapeia uma chave de busca (palavra em texto)
em um endereço de bucket (número de 0 a NB-1).

Foi escolhida uma função do tipo polinomial (semelhante ao algoritmo clássico
"djb2"), que distribui bem strings textuais e é simples de explicar/justificar
para a equipe: cada caractere da palavra contribui multiplicando um acumulador
por um número primo e somando o código ASCII/Unicode do caractere. O resultado
final é reduzido ao intervalo [0, NB) através do operador módulo.

djb2: h = 5381; para cada caractere c: h = h * 33 + ord(c)
"""


def hash_djb2(chave: str, nb: int) -> int:
    """Função hash polinomial (djb2) reduzida ao número de buckets NB."""
    if nb <= 0:
        raise ValueError("NB (número de buckets) deve ser maior que zero.")
    h = 5381
    for caractere in chave:
        h = (h * 33 + ord(caractere)) & 0xFFFFFFFF  # mantém em 32 bits
    return h % nb


def hash_soma_simples(chave: str, nb: int) -> int:
    """Função hash alternativa mais simples: soma dos códigos ASCII mod NB.
    Distribui pior que djb2 (mais colisões), disponível para fins de
    comparação/demonstração na interface."""
    if nb <= 0:
        raise ValueError("NB (número de buckets) deve ser maior que zero.")
    return sum(ord(c) for c in chave) % nb


FUNCOES_HASH = {
    "djb2 (polinomial, recomendada)": hash_djb2,
    "Soma simples (ASCII mod NB)": hash_soma_simples,
}
