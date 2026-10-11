"""Modelo de domínio da Fashion Co. (docs/03-classes.md)."""

import unicodedata
from dataclasses import dataclass


def id_da_colecao(nome: str) -> str:
    """Transforma o nome da coleção no seu id: "Verão 2027" vira "verao-2027"."""
    texto = nome.strip()  # 1. tira os espaços das pontas
    texto = texto.lower()  # 2. passa para minúsculas
    texto = unicodedata.normalize("NFD", texto)  # 3a. separa cada letra do seu acento
    sem_acento = ""
    for letra in texto:  # 3b. passa por cada pedaço do texto
        if unicodedata.combining(letra) == 0:  #     se NÃO for acento…
            sem_acento = sem_acento + letra  #     …guarda
    texto = sem_acento
    texto = texto.replace(" ", "-")  # 4. espaços viram hífen
    return texto


@dataclass
class Prompt:
    """Um prompt de uma coleção (docs/03-classes.md)."""

    titulo: str
    texto: str
    colecao: str  # o id da coleção, ex.: "verao-2027"
    autor: str
    status: str = "rascunho"  # todo prompt nasce como rascunho
