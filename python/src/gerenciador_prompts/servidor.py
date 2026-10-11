"""Servidor MCP do Gerenciador de Prompts da Fashion Co.

Walking skeleton: uma ferramenta com resposta fixa. As regras chegam fatia por fatia.
"""

from mcp.server.mcpserver import MCPServer

servidor = MCPServer("gerenciador-de-prompts-fashion-co")


@servidor.tool()
def listar_colecoes() -> str:
    """Lista as coleções da Fashion Co."""
    return "Ainda não há coleções."  # resposta fixa, por enquanto


if __name__ == "__main__":
    servidor.run(transport="streamable-http")
