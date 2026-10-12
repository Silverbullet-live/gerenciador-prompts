"""Testes do repositório em memória."""

from gerenciador_prompts.modelo import Prompt
from gerenciador_prompts.repositorio import RepositorioEmMemoria


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


# ── Fatia 2 · H02 ──────────────────────────────────────────────────────────


def test_garantir_colecao_completa_sem_apagar():
    """Salvar de novo na mesma coleção não cria outra e não apaga o que já havia."""
    repo = RepositorioEmMemoria()
    primeira = repo.garantir_colecao("Verão 2027", temporada="verão")
    segunda = repo.garantir_colecao(" verão 2027 ", temporada="outra", ano=2027)
    assert primeira is segunda  # é o mesmo objeto: a mesma coleção
    assert segunda.temporada == "verão"  # o que já havia ficou
    assert segunda.ano == 2027  # o que faltava foi completado


def test_busca_do_mais_novo_para_o_mais_antigo():
    """O último prompt salvo aparece primeiro."""
    repo = RepositorioEmMemoria()
    antigo = repo.salvar_prompt(Prompt("A", "texto", "verao-2027", "rafa"))
    novo = repo.salvar_prompt(Prompt("B", "texto", "verao-2027", "rafa"))
    assert repo.buscar(colecao="verao-2027") == [novo, antigo]


def test_prompt_oculto_nao_aparece():
    """Ocultar no mural esconde o prompt da busca e da consulta pelo id."""
    repo = RepositorioEmMemoria()
    prompt = repo.salvar_prompt(Prompt("A", "texto", "verao-2027", "rafa"))
    prompt.oculto = True
    assert repo.buscar() == []
    assert repo.obter(prompt.id) is None
