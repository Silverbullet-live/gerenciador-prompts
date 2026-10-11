"""Testes do modelo de domínio (docs/03-classes.md)."""

from gerenciador_prompts.modelo import Prompt, id_da_colecao


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
