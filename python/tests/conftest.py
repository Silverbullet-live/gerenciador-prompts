"""Preparação comum aos testes: o pytest carrega este arquivo sozinho."""

import os

import httpx
import pytest

import gerenciador_prompts.servidor as modulo_servidor
from gerenciador_prompts.repositorio import RepositorioEmMemoria

# Fatia 6: com o emulador do Firestore ligado, os mesmos testes rodam contra o banco.
EMULADOR = os.environ.get("FIRESTORE_EMULATOR_HOST")
PROJETO = os.environ.get("GOOGLE_CLOUD_PROJECT", "demo-gerenciador")


def esvaziar_emulador():
    """Apaga tudo o que está no emulador (só existe no emulador, nunca no banco real)."""
    url = f"http://{EMULADOR}/emulator/v1/projects/{PROJETO}/databases/(default)/documents"
    httpx.delete(url).raise_for_status()


@pytest.fixture(autouse=True)
def repositorio_limpo(monkeypatch):
    """Cada teste começa com o repositório vazio, para um teste não sujar o outro.

    "autouse" quer dizer: vale para todos os testes, sem precisar pedir.
    O monkeypatch troca o repo do servidor por um novo e desfaz a troca no fim do teste.
    """
    if EMULADOR:
        from google.cloud import firestore

        from gerenciador_prompts.repositorio_firestore import RepositorioFirestore

        esvaziar_emulador()
        novo = RepositorioFirestore(firestore.Client(project=PROJETO))
    else:
        novo = RepositorioEmMemoria()
    monkeypatch.setattr(modulo_servidor, "repo", novo)
    return novo
