# Gerenciador de Prompts · Python

O servidor MCP do Gerenciador de Prompts da Fashion Co., em Python. A análise e o projeto (requisitos, casos de uso, modelo de domínio, decisões técnicas e arquitetura) estão em [`../docs`](../docs).

```bash
uv sync            # cria o ambiente (.venv) e instala as dependências
uv run pytest      # roda os testes
uv run ruff check  # confere o estilo
uv run python src/gerenciador_prompts/servidor.py   # sobe o servidor em http://127.0.0.1:8000/mcp
```

No VS Code, abra **esta pasta** (`app/python`): o interpretador do `.venv` e os testes já vêm configurados.

## Testar o servidor com o MCP Inspector

O endereço `/mcp` não é uma página web: aberto direto no navegador, ele responde `Missing session ID`, porque o navegador não faz o aperto de mão do protocolo. Quem faz é um cliente MCP, como o Inspector.

1. No primeiro terminal, suba o servidor: `uv run python src/gerenciador_prompts/servidor.py`.
2. Num segundo terminal, com o servidor ainda rodando no primeiro: `npx @modelcontextprotocol/inspector`.
3. Abra o endereço que ele mostrar, algo como `http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=...`, **com o token**, como aparece no terminal.
4. No Inspector:
   - **Transport Type:** Streamable HTTP;
   - **URL:** `http://127.0.0.1:8000/mcp`;
   - deixe a seção **Authentication** vazia (o servidor não tem login);
   - clique em **Connect**.
5. Na aba **Tools**: **List Tools**, escolha a ferramenta e **Run Tool**. O **History** mostra as mensagens trocadas (`initialize`, `tools/list`, `tools/call`).

Para desligar, `Ctrl+C` nos dois terminais.

**Erros comuns:** `Failed to fetch` quer dizer que o Inspector (terminal 2) foi desligado: rode de novo. `HTTP 401 Unauthorized` quer dizer que a aba do navegador usa o token de uma sessão anterior: o token muda a cada vez que o Inspector sobe, então abra o link novo do terminal.

## Como o código é construído: walking skeleton de fatias verticais

**Esqueleto:** `servidor.py` com uma ferramenta, `listar_colecoes`, que devolve uma resposta fixa. Prova que o ambiente roda e que o MCP conecta.

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
