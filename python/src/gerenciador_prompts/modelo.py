"""Modelo de domínio da Fashion Co. (docs/03-classes.md)."""

import re
import unicodedata
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

# Limites que implementam o requisito de segurança RNF04 (docs/01-requisitos.md).
LIMITES = {
    "titulo": 120,
    "texto": 4000,
    "colecao": 40,
    "apelido": 40,
    "peca": 80,
    "looks_por_pedido": 12,
    "resultados_busca": 20,
}


def novo_id() -> str:
    """Um id curto e aleatório, como "3f9a1c2e"."""
    return uuid.uuid4().hex[:8]


def agora() -> datetime:
    """A data e a hora de agora, em UTC (o mesmo relógio para todo o sistema)."""
    return datetime.now(UTC)


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


# Fatia 2 · H02: a coleção vira uma classe, para ser listada e filtrada.
@dataclass
class Colecao:
    """Uma das quatro trocas de coleção do ano."""

    id: str  # "verao-2027", derivado do nome
    nome: str  # "Verão 2027"
    temporada: str | None = None
    ano: int | None = None
    editor_responsavel: str | None = None
    criada_em: datetime = field(default_factory=agora)


@dataclass
class Prompt:
    """Um prompt de uma coleção (docs/03-classes.md)."""

    titulo: str
    texto: str
    colecao: str  # o id da coleção, ex.: "verao-2027"
    autor: str
    status: str = "rascunho"  # todo prompt nasce como rascunho
    # Fatia 2: para achar um prompt depois, ele precisa de um id e de uma data.
    id: str = field(default_factory=novo_id)
    criado_em: datetime = field(default_factory=agora)
    oculto: bool = False  # "ocultar" no mural esconde o cartão; o dado continua


@dataclass
class ResumoDaColecao:
    """O que o listar_colecoes mostra de cada coleção."""

    colecao: Colecao
    total_de_prompts: int
    aprovado: str | None = None  # o título do prompt aprovado, se houver


# ── Fatia 3 · H03: reusar trocando os looks ─────────────────────────────────

# {{look}}, {{ look }} ou {{ qualquer_nome }}: as variáveis de um prompt.
VARIAVEL = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")


def variaveis_do_texto(texto: str) -> list[str]:
    """As variáveis {{assim}} de um texto, na ordem em que aparecem, sem repetir."""
    nomes = []
    for nome in VARIAVEL.findall(texto):
        if nome not in nomes:
            nomes.append(nome)
    return nomes


def preencher_look(texto: str, peca: str, cor_e_tecido: str | None = None) -> str:
    """Troca o {{look}} pela peça: "A modelo veste {{look}}" vira "A modelo veste vestido midi"."""
    look = f"{peca}, {cor_e_tecido}" if cor_e_tecido else peca
    # lambda: a peça entra como texto puro, mesmo se tiver "\\" (que o re.sub leria como código)
    return re.sub(r"\{\{\s*look\s*\}\}", lambda _: look, texto)


@dataclass
class Look:
    """Uma peça da coleção, gerada a partir de um prompt trocando o {{look}}."""

    prompt_id: str
    colecao: str
    peca: str
    texto_gerado: str  # o prompt com o {{look}} já preenchido, pronto para a IA de imagem
    cor_e_tecido: str | None = None
    imagem_gerada: str | None = None  # RF06: a imagem aprovada (a v1 ainda não guarda, issue #5)
    entrega_id: str | None = None
    id: str = field(default_factory=novo_id)
    criado_em: datetime = field(default_factory=agora)
