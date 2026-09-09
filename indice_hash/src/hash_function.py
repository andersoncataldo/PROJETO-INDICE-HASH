"""Funções hash usadas para mapear chaves aos buckets."""


def hash_djb2(chave: str, nb: int) -> int:
    """Calcula o endereço usando a função djb2."""
    if nb <= 0:
        raise ValueError("NB (número de buckets) deve ser maior que zero.")
    h = 5381
    for caractere in chave:
        h = (h * 33 + ord(caractere)) & 0xFFFFFFFF
    return h % nb


def hash_soma_simples(chave: str, nb: int) -> int:
    """Calcula o endereço pela soma dos códigos dos caracteres."""
    if nb <= 0:
        raise ValueError("NB (número de buckets) deve ser maior que zero.")
    return sum(ord(c) for c in chave) % nb


FUNCOES_HASH = {
    "djb2 (polinomial, recomendada)": hash_djb2,
    "Soma simples (ASCII mod NB)": hash_soma_simples,
}
