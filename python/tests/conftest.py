"""Preparação comum aos testes: o pytest carrega este arquivo sozinho."""

import pytest

import gerenciador_prompts.servidor as modulo_servidor
from gerenciador_prompts.repositorio import RepositorioEmMemoria


@pytest.fixture(autouse=True)
def repositorio_limpo(monkeypatch):
    """Cada teste começa com o repositório vazio, para um teste não sujar o outro.

    "autouse" quer dizer: vale para todos os testes, sem precisar pedir.
    O monkeypatch troca o repo do servidor por um novo e desfaz a troca no fim do teste.
    """
    novo = RepositorioEmMemoria()
    monkeypatch.setattr(modulo_servidor, "repo", novo)
    return novo
