"""Testes do Servidor MCP (walking skeleton): a ferramenta é publicada e responde."""

import asyncio  # roda as funções assíncronas do SDK (list_tools, call_tool)

from gerenciador_prompts.servidor import (  # o código testado
    buscar_prompts,
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
    assert sorted(f.name for f in ferramentas) == [
        "buscar_prompts",
        "listar_colecoes",
        "salvar_prompt",
    ]


# ── Fatia 2 · H02: buscar e listar ─────────────────────────────────────────


def salvar_exemplos():
    """Três prompts em duas coleções, como no teste de ponta a ponta da versão anterior."""
    salvar_prompt(
        titulo="Editorial de praia",
        texto="Foto editorial na praia, luz de fim de tarde. A modelo veste {{look}}.",
        colecao="Verão 2027",
        temporada="verão",
        ano=2027,
        autor="rafa",
    )
    salvar_prompt(
        titulo="Fundo de estúdio",
        texto="Foto de estúdio com fundo cinza, vestido vermelho de seda.",
        colecao="Verão 2027",
        autor="lu",
    )
    salvar_prompt(
        titulo="Lookbook de inverno", texto="Lookbook na neve com {{look}}.", colecao="Inverno 2027"
    )


def test_lista_colecoes_com_contagem():
    """listar_colecoes mostra cada coleção, quantos prompts tem e se já há um aprovado."""
    salvar_exemplos()
    lista = listar_colecoes()
    assert "Verão 2027 (verão 2027): 2 prompt(s) · sem prompt aprovado" in lista
    assert "Inverno 2027: 1 prompt(s)" in lista


def test_busca_por_colecao():
    """H02: a busca por coleção traz só os prompts dela, com o nome escrito de qualquer jeito."""
    salvar_exemplos()
    achados = buscar_prompts(colecao="verão 2027")
    assert "Editorial de praia" in achados
    assert "Fundo de estúdio" in achados
    assert "Lookbook de inverno" not in achados


def test_busca_por_palavra():
    """H02: a palavra pode estar no título ou no texto, com maiúsculas ou não."""
    salvar_exemplos()
    achados = buscar_prompts(termo="NEVE")
    assert achados.startswith("1 prompt(s):")
    assert "Lookbook de inverno" in achados


def test_busca_sem_resultado():
    """Quando nada combina, a resposta diz isso claramente."""
    assert buscar_prompts(termo="praia") == "Nenhum prompt encontrado com esses critérios."
