"""Testes do Servidor MCP (walking skeleton): a ferramenta é publicada e responde."""

import asyncio  # roda as funções assíncronas do SDK (list_tools, call_tool)

from gerenciador_prompts.servidor import (  # o código testado
    listar_colecoes,
    salvar_prompt,
    servidor,
)


def test_responde_sem_colecoes():
    """A função responde, chamada diretamente (sem o protocolo)."""
    assert listar_colecoes() == "Ainda não há coleções."


def test_resposta_segue_o_contrato():
    """Chamada pelo protocolo (tools/call), a resposta segue o Output Schema."""
    resultado = asyncio.run(servidor.call_tool("listar_colecoes", {}))
    assert resultado.structured_content == {"result": "Ainda não há coleções."}


def test_salva_na_colecao_como_rascunho():
    """H01: ao salvar, o sistema confirma a coleção e que o prompt entrou como rascunho."""
    resposta = salvar_prompt(
        titulo="Editorial de praia",
        texto="A modelo veste {{look}} na praia.",
        colecao="Verão 2027",
        autor="rafa",
    )
    assert 'coleção "Verão 2027"' in resposta
    assert "como rascunho" in resposta


def test_publica_as_ferramentas():
    """O servidor anuncia as ferramentas: é o que o Claude vê no tools/list."""
    ferramentas = asyncio.run(servidor.list_tools())
    assert sorted(f.name for f in ferramentas) == ["listar_colecoes", "salvar_prompt"]
