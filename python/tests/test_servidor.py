"""Testes do Servidor MCP (walking skeleton): a ferramenta é publicada e responde."""

import asyncio  # roda as funções assíncronas do SDK (list_tools, call_tool)

from gerenciador_prompts.servidor import listar_colecoes, servidor  # o código testado


def test_publica_listar_colecoes():
    """O servidor anuncia a ferramenta: é o que o Claude vê no tools/list."""
    ferramentas = asyncio.run(servidor.list_tools())
    assert [f.name for f in ferramentas] == ["listar_colecoes"]


def test_responde_sem_colecoes():
    """A função responde, chamada diretamente (sem o protocolo)."""
    assert listar_colecoes() == "Ainda não há coleções."


def test_resposta_segue_o_contrato():
    """Chamada pelo protocolo (tools/call), a resposta segue o Output Schema."""
    resultado = asyncio.run(servidor.call_tool("listar_colecoes", {}))
    assert resultado.structured_content == {"result": "Ainda não há coleções."}
