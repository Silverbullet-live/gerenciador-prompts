"""
Servidor MCP do Gerenciador de Prompts da Fashion Co.
Walking skeleton: ferramenta com resposta fixa + regras em fatias.
"""

from typing import Annotated

# Que peça da arquitetura estou construindo: [Servidor MCP]
# Que biblioteca em Python usar para MCP: [SDK oficial mcp]
from mcp.server.mcpserver import MCPServer
from pydantic import Field

from gerenciador_prompts.modelo import LIMITES, Prompt, id_da_colecao
from gerenciador_prompts.repositorio import RepositorioEmMemoria

# O que o Claude lê ao conectar: quando e como usar cada ferramenta.
INSTRUCOES = """\
Gerenciador de Prompts da Fashion Co. (marca fictícia, aula de Análise de Sistemas).
Os editores de moda guardam aqui os prompts que geram as imagens de cada coleção,
para não perdê-los, não reescrevê-los a cada troca de coleção e manter um padrão de qualidade.

- Salvar: use salvar_prompt quando a pessoa pedir para salvar, guardar ou registrar um prompt.
  Se ela falar em "categoria", trate como coleção. Se não disser a coleção, chame
  listar_colecoes e sugira uma existente. Se não disser um título, proponha um curto.
- Tudo aparece num mural público projetado em sala: nunca salve dados pessoais (nome completo,
  telefone, e-mail, documentos). Se o texto contiver algo assim, avise e peça para remover."""

# Como essa biblioteca cria um servidor: classe MCPServer --> SDK: py.sdk.modelcontextprotocol.io
servidor = MCPServer("gerenciador-de-prompts-fashion-co", instructions=INSTRUCOES)
repo = RepositorioEmMemoria()

# Os tipos dos parâmetros já trazem os limites do RNF04: o SDK recusa o que passar deles.
Titulo = Annotated[str, Field(min_length=1, max_length=LIMITES["titulo"])]
Texto = Annotated[str, Field(min_length=1, max_length=LIMITES["texto"])]
NomeDeColecao = Annotated[str, Field(min_length=1, max_length=LIMITES["colecao"])]
Apelido = Annotated[str, Field(min_length=1, max_length=LIMITES["apelido"])]


# Qual é a ferramenta: listar_colecoes (Fatia 2 · H02: deixa de ser fixa e lê o repositório)
@servidor.tool()
def listar_colecoes() -> str:
    """Lista as coleções, quantos prompts cada uma tem e qual é o prompt aprovado (o padrão)."""
    resumos = repo.resumo_das_colecoes()
    if not resumos:
        return "Ainda não há coleções."
    linhas = []
    for r in resumos:
        quando = " ".join(str(x) for x in (r.colecao.temporada, r.colecao.ano) if x)
        nome = f"{r.colecao.nome} ({quando})" if quando else r.colecao.nome
        padrao = f' · aprovado: "{r.aprovado}"' if r.aprovado else " · sem prompt aprovado"
        linhas.append(f"• {nome}: {r.total_de_prompts} prompt(s){padrao}")
    return "\n".join(linhas)


# Fatia 1 · H01: salvar um prompt numa coleção
@servidor.tool()
def salvar_prompt(
    titulo: Titulo,
    texto: Texto,
    colecao: NomeDeColecao,
    autor: Apelido = "anônimo",
    temporada: str | None = None,
    ano: int | None = None,
) -> str:
    """Salva um prompt numa coleção. Entra como rascunho. Use {{look}} onde a peça muda."""
    c = repo.garantir_colecao(colecao, temporada, ano, editor_responsavel=autor)
    prompt = Prompt(titulo=titulo.strip(), texto=texto, colecao=c.id, autor=autor.strip())
    repo.salvar_prompt(prompt)
    return (
        f'Prompt salvo com id {prompt.id} na coleção "{c.nome}", como rascunho. '
        "Já aparece no mural."
    )


# Fatia 2 · H02: buscar por coleção ou palavra
@servidor.tool()
def buscar_prompts(
    colecao: NomeDeColecao | None = None,
    termo: str | None = None,
    somente_aprovados: bool = False,
    limite: Annotated[int, Field(ge=1, le=LIMITES["resultados_busca"])] = 10,
) -> str:
    """Busca prompts por coleção e/ou palavra-chave. Pode trazer só os aprovados."""
    achados = repo.buscar(
        termo=termo.strip() if termo else None,
        colecao=id_da_colecao(colecao) if colecao else None,
        somente_aprovados=somente_aprovados,
        limite=limite,
    )
    if not achados:
        return "Nenhum prompt encontrado com esses critérios."
    return f"{len(achados)} prompt(s):\n" + "\n".join(resumo(p) for p in achados)


def resumo(p: Prompt) -> str:
    """Uma linha por prompt: id, título, coleção, autor, selo e um trecho do texto."""
    trecho = p.texto if len(p.texto) <= 160 else p.texto[:160] + "…"
    selo = " ★ aprovado" if p.status == "aprovado" else ""
    trecho = " ".join(trecho.split())  # junta as quebras de linha num texto corrido
    return f"• [{p.id}] {p.titulo} (coleção {p.colecao}, por {p.autor}){selo}\n  {trecho}"


# Como o Claude chega até ela:  HTTP: streamable-http
if __name__ == "__main__":
    servidor.run(transport="streamable-http")
