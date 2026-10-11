"""Walking skeleton: o servidor publica a ferramenta e ela responde."""

import asyncio

from gerenciador_prompts.servidor import listar_colecoes, servidor


def test_publica_listar_colecoes():
    ferramentas = asyncio.run(servidor.list_tools())
    assert [f.name for f in ferramentas] == ["listar_colecoes"]


def test_responde_sem_colecoes():
    assert listar_colecoes() == "Ainda não há coleções."
