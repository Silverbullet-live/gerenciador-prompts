"""Testes do repositório em memória."""

from gerenciador_prompts.repositorio import RepositorioEmMemoria

from gerenciador_prompts.modelo import Prompt


def test_salva_e_encontra_o_prompt():
    """O que foi salvo pode ser encontrado depois."""
    repo = RepositorioEmMemoria()
    prompt = Prompt(
        titulo="Editorial de praia",
        texto="A modelo veste {{look}}.",
        colecao="verao-2027",
        autor="rafa",
    )
    repo.salvar_prompt(prompt)
    assert repo.prompts == [prompt]
