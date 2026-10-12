"""Testes do Servidor MCP (walking skeleton): a ferramenta é publicada e responde."""

import asyncio  # roda as funções assíncronas do SDK (list_tools, call_tool)

import pytest
from mcp.server.mcpserver.exceptions import ToolError

from gerenciador_prompts.servidor import (  # o código testado
    PedidoDeLook,
    aprovar_prompt,
    buscar_prompts,
    entregar_colecao,
    listar_colecoes,
    obter_prompt,
    reusar_prompt,
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
        "aprovar_prompt",
        "buscar_prompts",
        "entregar_colecao",
        "listar_colecoes",
        "obter_prompt",
        "reusar_prompt",
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


# ── Fatia 3 · H03: reusar trocando os looks ────────────────────────────────


def id_do_salvo(resposta: str) -> str:
    """Tira o id da resposta do salvar_prompt: "Prompt salvo com id 3f9a1c2e na…"."""
    return resposta.split("com id ")[1].split()[0]


def test_reusa_trocando_os_looks():
    """H03: um prompt por look, com o {{look}} preenchido pela peça, a cor e o tecido."""
    id = id_do_salvo(
        salvar_prompt(
            titulo="Editorial de praia",
            texto="Foto na praia. A modelo veste {{look}}. Corpo inteiro.",
            colecao="Verão 2027",
        )
    )
    resposta = reusar_prompt(
        id,
        [
            PedidoDeLook(peca="vestido midi", cor_e_tecido="verde-oliva, linho"),
            PedidoDeLook(peca="conjunto de alfaiataria", cor_e_tecido="areia, crepe"),
        ],
    )
    assert "A modelo veste vestido midi, verde-oliva, linho." in resposta
    assert "A modelo veste conjunto de alfaiataria, areia, crepe." in resposta
    assert "ainda é rascunho" in resposta  # avisa que não é o padrão aprovado


def test_avisa_ao_salvar_sem_look():
    """Ao salvar um prompt sem {{look}}, o sistema avisa que ele não poderá ser reusado."""
    resposta = salvar_prompt(titulo="Estúdio", texto="Vestido vermelho de seda.", colecao="Verão")
    assert "não tem {{look}}" in resposta


def test_recusa_reusar_prompt_sem_look():
    """Sem {{look}} não há onde trocar a peça: a ferramenta devolve um erro claro."""
    id = id_do_salvo(salvar_prompt(titulo="Estúdio", texto="Vestido de seda.", colecao="Verão"))
    with pytest.raises(ToolError, match="não tem {{look}}"):
        reusar_prompt(id, [PedidoDeLook(peca="saia")])


def test_recusa_id_inexistente():
    """Um id que não existe gera erro, e não uma resposta vazia."""
    with pytest.raises(ToolError, match="Não encontrei"):
        reusar_prompt("nao-existe", [PedidoDeLook(peca="saia")])


def test_reusar_pelo_protocolo():
    """Pelo protocolo (como o Claude chama), os looks chegam como JSON e viram PedidoDeLook."""
    id = id_do_salvo(salvar_prompt(titulo="Praia", texto="Veste {{look}}.", colecao="Verão"))
    resultado = asyncio.run(
        servidor.call_tool("reusar_prompt", {"id": id, "looks": [{"peca": "saia"}]})
    )
    assert "Veste saia." in resultado.structured_content["result"]


# ── Fatia 4 · H04: aprovar o padrão e exportar em .prompt ──────────────────


def test_um_so_aprovado_por_colecao():
    """H04: aprovar um prompt devolve o antigo padrão a rascunho."""
    praia = id_do_salvo(salvar_prompt(titulo="Praia", texto="Veste {{look}}.", colecao="Verão"))
    estudio = id_do_salvo(salvar_prompt(titulo="Estúdio", texto="Fundo cinza.", colecao="Verão"))
    aprovar_prompt(estudio, "chefe.ana")
    resposta = aprovar_prompt(praia, "chefe.ana")
    assert '"Praia" agora é o prompt aprovado' in resposta
    assert '"Estúdio", voltou a rascunho' in resposta
    aprovados = buscar_prompts(colecao="Verão", somente_aprovados=True)
    assert aprovados.startswith("1 prompt(s):")
    assert "Praia" in aprovados and "★ aprovado" in aprovados
    assert 'aprovado: "Praia"' in listar_colecoes()


def test_aprovar_id_inexistente():
    """Aprovar um id que não existe é erro."""
    with pytest.raises(ToolError, match="Não encontrei"):
        aprovar_prompt("nao-existe", "chefe.ana")


def test_exporta_em_dotprompt():
    """O .prompt traz modelo, temperatura, o {{look}} como entrada e quem aprovou."""
    id = id_do_salvo(
        salvar_prompt(
            titulo="Editorial de praia",
            texto="Foto na praia. A modelo veste {{look}}.",
            colecao="Verão 2027",
            autor="rafa",
            modelo="imagen-4",
            temperatura=0.4,
        )
    )
    aprovar_prompt(id, "chefe.ana")
    arquivo = obter_prompt(id)
    assert "Arquivo sugerido: verao-2027/editorial_de_praia.prompt" in arquivo
    assert "model: imagen-4\nconfig:\n  temperature: 0.4\n" in arquivo
    assert "    look: string, a peça com cor e tecido\n" in arquivo
    assert "  status: aprovado\n  aprovadoPor: chefe.ana\n  autor: rafa\n" in arquivo
    assert arquivo.rstrip().endswith("A modelo veste {{look}}.")


# ── Fatia 5 · H05: entregar à engenharia ───────────────────────────────────


def test_nao_entrega_sem_prompt_aprovado():
    """Sem padrão aprovado, não há o que entregar."""
    salvar_prompt(titulo="Praia", texto="Veste {{look}}.", colecao="Verão 2027")
    with pytest.raises(ToolError, match="ainda não tem prompt aprovado"):
        entregar_colecao("Verão 2027", "eng.joao")


def test_nao_entrega_sem_looks():
    """Issue #3: com o prompt aprovado mas sem looks, a entrega é recusada."""
    id = id_do_salvo(salvar_prompt(titulo="Outono", texto="Com {{look}}.", colecao="Outono 2027"))
    aprovar_prompt(id, "chefe.ana")
    with pytest.raises(ToolError, match="ainda não tem looks gerados"):
        entregar_colecao("Outono 2027", "eng.joao")


def test_entrega_o_prompt_aprovado_e_os_looks(repositorio_limpo):
    """H05: a entrega traz o .prompt aprovado e os looks, e cada look fica marcado com ela."""
    id = id_do_salvo(
        salvar_prompt(titulo="Editorial de praia", texto="Veste {{look}}.", colecao="Verão 2027")
    )
    aprovar_prompt(id, "chefe.ana")
    reusar_prompt(
        id,
        [
            PedidoDeLook(peca="vestido midi", cor_e_tecido="verde-oliva, linho"),
            PedidoDeLook(peca="conjunto de alfaiataria", cor_e_tecido="areia, crepe"),
        ],
    )
    resposta = entregar_colecao("Verão 2027", "eng.joao")
    assert "registrada para eng.joao" in resposta
    assert "Arquivo: verao-2027/editorial_de_praia.prompt" in resposta
    assert (
        "Looks enviados (2):\n• vestido midi (verde-oliva, linho)\n"
        "• conjunto de alfaiataria (areia, crepe)"
    ) in resposta
    assert "issue #5" in resposta  # é honesta sobre o que ainda não vai
    # O conftest entrega o repositório limpo como parâmetro: dá para olhar dentro dele.
    assert all(look.entrega_id for look in repositorio_limpo.looks)
