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

**Fatias, uma história por vez** (`../docs/05-historias-de-usuario.md`), cada uma de ponta a ponta: teste → modelo → repositório → ferramenta. Cada fatia é **um commit**: para estudar, leia os commits na ordem (`git log --oneline -- python`) e, em cada um, o que mudou (`git show <commit>`).

| Fatia | História | O que entrou | Testes |
|---|---|---|---|
| esqueleto | | `servidor.py` com `listar_colecoes` fixa | 4 |
| 1 | H01 · Salvar prompt | `id_da_colecao`, `Prompt`, `RepositorioEmMemoria`, `salvar_prompt` | 10 |
| 2 | H02 · Buscar e listar | `Colecao`, busca e consulta, `listar_colecoes` de verdade, `buscar_prompts`, limites do RNF04, instruções para o Claude, `conftest.py` | 17 |
| 3 | H03 · Reusar trocando os looks | `Look`, `preencher_look`, `reusar_prompt`, erros com `ToolError` | 25 |
| 4 | H04 · Aprovar o padrão | um aprovado por coleção, `aprovar_prompt`, `obter_prompt`, `dotprompt.py` | 28 |
| 5 | H05 · Entregar à engenharia | `Entrega`, `entregar_colecao` com os bloqueios | 31 |
| 6 | Firestore e publicação | `repositorio_firestore.py`, escolha do repositório, `app.py` | 32 |

As sete ferramentas: `listar_colecoes`, `salvar_prompt`, `buscar_prompts`, `reusar_prompt`, `aprovar_prompt`, `obter_prompt`, `entregar_colecao`.

O SDK do MCP está na versão 2.x: o servidor é `MCPServer` (`from mcp.server.mcpserver import MCPServer`). Tutoriais antigos chamam a mesma classe de `FastMCP`.

## Onde os dados ficam: memória ou Firestore

O servidor conversa com um **repositório** e não sabe qual banco ele usa (`../docs/07-projeto.md`). Os dois repositórios têm os mesmos métodos:

| Repositório | Quando | Dados |
|---|---|---|
| `RepositorioEmMemoria` | padrão: testes e uso local | somem quando o servidor reinicia |
| `RepositorioFirestore` | com `REPOSITORIO=firestore` | ficam no Firestore; o mural lê os mesmos campos |

**Testar contra o Firestore sem tocar no banco real**, com o emulador (precisa de Java):

```bash
# terminal 1: o emulador (o arquivo .jar fica no cache da CLI do Firebase)
java -jar ~/.cache/firebase/emulators/cloud-firestore-emulator-*.jar --host 127.0.0.1 --port 8085

# terminal 2: os mesmos testes, agora gravando no emulador
FIRESTORE_EMULATOR_HOST=127.0.0.1:8085 GOOGLE_CLOUD_PROJECT=demo-gerenciador uv run pytest
```

O `firebase emulators:start` também funciona, mas a versão atual da CLI exige Java 21.

## Publicar (a decidir)

`app.py` transforma o servidor numa aplicação web sem estado, pronta para uma hospedagem ligar:

```bash
REPOSITORIO=firestore uv run uvicorn gerenciador_prompts.app:app --port 8000
```

**Ainda não publicado.** É uma decisão técnica nova, porque as Cloud Functions em Python usam outro modelo de aplicação (WSGI) que o do servidor MCP (ASGI):

| Opção | Como | Observação |
|---|---|---|
| **Cloud Run** | um contêiner com o `uvicorn` acima; o Firebase Hosting aponta `/mcp` para ele | roda o servidor como ele é; mesma URL pública de hoje |
| Cloud Functions (Python) | um adaptador ASGI → WSGI | menos peças novas, mas um adaptador no meio do caminho |

Em produção, defina `HOSTS_PERMITIDOS` com o endereço público (ver `app.py`).
