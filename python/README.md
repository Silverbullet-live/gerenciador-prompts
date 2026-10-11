# Gerenciador de Prompts · Python

O servidor MCP do Gerenciador de Prompts da Fashion Co., em Python. A análise e o projeto (requisitos, casos de uso, modelo de domínio, decisões técnicas e arquitetura) estão em [`../docs`](../docs).

```bash
uv sync            # cria o ambiente (.venv) e instala as dependências
uv run pytest      # roda os testes
uv run ruff check  # confere o estilo
uv run python src/gerenciador_prompts/servidor.py   # sobe o servidor em http://127.0.0.1:8000/mcp
```

No VS Code, abra **esta pasta** (`app/python`): o interpretador do `.venv` e os testes já vêm configurados.

## Como o código é construído: walking skeleton de fatias verticais

**Esqueleto (feito):** `servidor.py` com uma ferramenta, `listar_colecoes`, que devolve uma resposta fixa. Prova que o ambiente roda e que o MCP conecta.

**Fatias, uma história por vez** (`../docs/05-historias-de-usuario.md`), cada uma de ponta a ponta: teste → modelo → repositório → ferramenta.

| Fatia | História | Arquivos que ela cria ou muda |
|---|---|---|
| 1 | H01 · Salvar prompt | `modelo.py`, `repositorio.py`, `servidor.py` |
| 2 | H02 · Buscar e listar | `repositorio.py`, `servidor.py` |
| 3 | H03 · Reusar trocando os looks | `modelo.py`, `servidor.py` |
| 4 | H04 · Aprovar o padrão | `repositorio.py`, `servidor.py` |
| 5 | H05 · Entregar à engenharia | `repositorio.py`, `servidor.py` |
| 6 | Firestore e publicação | `repositorio_firestore.py` |

O SDK do MCP está na versão 2.x: o servidor é `MCPServer` (`from mcp.server.mcpserver import MCPServer`). Tutoriais antigos chamam a mesma classe de `FastMCP`.
