"""Testes do modelo de domínio (docs/03-classes.md)."""

from gerenciador_prompts.modelo import Prompt, id_da_colecao, preencher_look, variaveis_do_texto


def test_id_sem_acento_e_com_hifen():
    """O id da coleção nasce do nome: sem acento, minúsculo, com hífen."""
    assert id_da_colecao("Verão 2027") == "verao-2027"


def test_id_tira_espacos_das_pontas():
    """Espaços sobrando não mudam o id: "Verão 2027" e " Verão 2027 " são a mesma coleção."""
    assert id_da_colecao("  Inverno 2027 ") == "inverno-2027"


def test_prompt_nasce_como_rascunho():
    """Todo prompt salvo começa como rascunho; só o editor-chefe aprova (H04)."""
    prompt = Prompt(
        titulo="Editorial de praia",
        texto="A modelo veste {{look}}.",
        colecao="verao-2027",
        autor="rafa",
    )
    assert prompt.status == "rascunho"


# ── Fatia 3 · H03 ──────────────────────────────────────────────────────────


def test_troca_o_look_pela_peca():
    """O exemplo do slide 30: o teste que começou a fatia do RF04."""
    texto = "A modelo veste {{look}}, na praia."
    assert preencher_look(texto, "vestido midi") == "A modelo veste vestido midi, na praia."


def test_troca_com_cor_e_tecido():
    """A cor e o tecido entram depois da peça, separados por vírgula."""
    assert preencher_look("Veste {{ look }}.", "saia", "azul, linho") == "Veste saia, azul, linho."


def test_encontra_as_variaveis_sem_repetir():
    """As variáveis aparecem na ordem do texto, uma vez cada."""
    texto = "{{look}} na {{cena}}, de novo {{look}}"
    assert variaveis_do_texto(texto) == ["look", "cena"]
