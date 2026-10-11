"""Confere o ambiente: se este teste passa, o VS Code e o uv estão prontos."""

import sys


def test_python_311_ou_mais():
    assert sys.version_info >= (3, 11)


def test_sdk_do_mcp_instalado():
    # No SDK 2.x, o antigo FastMCP se chama MCPServer.
    from mcp.server.mcpserver import MCPServer

    assert MCPServer("teste").name == "teste"
