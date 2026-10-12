"""
Servidor MCP do Gerenciador de Prompts da Fashion Co.
Walking skeleton: ferramenta com resposta fixa + regras em fatias.
"""

# Que peça da arquitetura estou construindo: [Servidor MCP]
# Que biblioteca em Python usar para MCP: [SDK oficial mcp]
from mcp.server.mcpserver import MCPServer

from gerenciador_prompts.modelo import Prompt, id_da_colecao
from gerenciador_prompts.repositorio import RepositorioEmMemoria

# Como essa biblioteca cria um servidor: classe MCPServer --> SDK: py.sdk.modelcontextprotocol.io
servidor = MCPServer("gerenciador-de-prompts-fashion-co")
repo = RepositorioEmMemoria()


# Qual é a ferramenta: listar_colecoes
@servidor.tool()
def listar_colecoes() -> str:
    """Lista as coleções da Fashion Co."""
    return "Ainda não há coleções."  # resposta fixa, por enquanto


# Fatia 1 · H01: salvar um prompt numa coleção
@servidor.tool()
def salvar_prompt(titulo: str, texto: str, colecao: str, autor: str = "anônimo") -> str:
    """Salva um prompt numa coleção. Entra como rascunho. Use {{look}} onde a peça muda."""
    prompt = Prompt(titulo=titulo, texto=texto, colecao=id_da_colecao(colecao), autor=autor)
    repo.salvar_prompt(prompt)
    return f'Prompt "{titulo}" salvo na coleção "{colecao}", como rascunho.'


# Como o Claude chega até ela:  HTTP: streamable-http
if __name__ == "__main__":
    servidor.run(transport="streamable-http")
