"""
Servidor MCP do Gerenciador de Prompts da Fashion Co.
Walking skeleton: ferramenta com resposta fixa + regras em fatias.
"""

# Que peça da arquitetura estou construindo: [Servidor MCP]
# Que biblioteca em Python usar para MCP: [SDK oficial mcp]
from mcp.server.mcpserver import MCPServer

# Como essa biblioteca cria um servidor: classe MCPServer --> SDK: py.sdk.modelcontextprotocol.io
servidor = MCPServer("gerenciador-de-prompts-fashion-co")


# Qual é a ferramenta: listar_colecoes
@servidor.tool()
def listar_colecoes() -> str:
    """Lista as coleções da Fashion Co."""
    return "Ainda não há coleções."  # resposta fixa, por enquanto


# Como o Claude chega até ela:  HTTP: streamable-http
if __name__ == "__main__":
    servidor.run(transport="streamable-http")
