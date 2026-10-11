# Gerenciador de Prompts · versão Python

Porte do servidor MCP (hoje em TypeScript, em `../functions`) para Python. A análise e o projeto são os mesmos (`../docs`); muda só a implementação.

```bash
uv sync            # cria o ambiente (.venv) e instala as dependências
uv run pytest      # roda os testes
uv run ruff check  # confere o estilo
```

No VS Code, abra **esta pasta** (`app/python`): o interpretador do `.venv` e os testes já vêm configurados.

## Ordem do porte (segue o mapa de arquitetura, `../docs/07-projeto.md`)

1. `modelo.py`: Coleção, Prompt, Look, Entrega e a troca do `{{look}}`.
2. `repositorio.py`: a interface e a versão em memória.
3. `servidor_mcp.py`: as ferramentas, com `MCPServer` (SDK `mcp` 2.x; nos tutoriais antigos ele aparece como `FastMCP`).
4. Firestore e publicação.
