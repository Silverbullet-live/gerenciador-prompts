"""Fatia 6: a aplicação web responde ao protocolo MCP, como na internet."""

import httpx
import pytest

from gerenciador_prompts.app import app

INICIAR = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "teste", "version": "1"},
    },
}


@pytest.mark.anyio
async def test_app_responde_initialize_com_host_publico():
    """Com um endereço público no cabeçalho Host, o aperto de mão funciona (sem sessão)."""
    transporte = httpx.ASGITransport(app=app)
    async with (
        app.router.lifespan_context(app),  # liga o gerenciador de sessões do MCP
        httpx.AsyncClient(transport=transporte, base_url="https://exemplo.run.app") as cliente,
    ):
        resposta = await cliente.post(
            "/mcp",
            json=INICIAR,
            headers={"Accept": "application/json, text/event-stream"},
        )
    assert resposta.status_code == 200
    assert resposta.json()["result"]["serverInfo"]["name"] == "gerenciador-de-prompts-fashion-co"


@pytest.fixture
def anyio_backend():
    return "asyncio"
