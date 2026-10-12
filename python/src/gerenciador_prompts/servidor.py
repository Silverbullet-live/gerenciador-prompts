"""
Servidor MCP do Gerenciador de Prompts da Fashion Co.
Walking skeleton: ferramenta com resposta fixa + regras em fatias.
"""

from typing import Annotated

# Que peça da arquitetura estou construindo: [Servidor MCP]
# Que biblioteca em Python usar para MCP: [SDK oficial mcp]
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import BaseModel, Field

from gerenciador_prompts.dotprompt import nome_do_arquivo, para_dotprompt
from gerenciador_prompts.modelo import (
    LIMITES,
    Look,
    Prompt,
    id_da_colecao,
    preencher_look,
    variaveis_do_texto,
)
from gerenciador_prompts.repositorio import RepositorioEmMemoria

# O que o Claude lê ao conectar: quando e como usar cada ferramenta.
INSTRUCOES = """\
Gerenciador de Prompts da Fashion Co. (marca fictícia, aula de Análise de Sistemas).
Os editores de moda guardam aqui os prompts que geram as imagens de cada coleção,
para não perdê-los, não reescrevê-los a cada troca de coleção e manter um padrão de qualidade.

- Salvar: use salvar_prompt quando a pessoa pedir para salvar, guardar ou registrar um prompt.
  Se ela falar em "categoria", trate como coleção. Se não disser a coleção, chame
  listar_colecoes e sugira uma existente. Se não disser um título, proponha um curto.
- {{look}}: quando o prompt descreve uma peça específica, sugira trocar a peça por {{look}}
  antes de salvar. Assim o prompt pode ser reusado em toda a coleção (reusar_prompt).
- Aprovar: aprovar_prompt é papel do editor-chefe. Cada coleção tem um único prompt aprovado.
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
IdDePrompt = Annotated[str, Field(min_length=1, max_length=64)]


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
    ano: Annotated[int, Field(ge=2000, le=2100)] | None = None,
    modelo: Annotated[str, Field(max_length=80)] | None = None,
    temperatura: Annotated[float, Field(ge=0, le=2)] | None = None,
) -> str:
    """Salva um prompt numa coleção. Entra como rascunho. Use {{look}} onde a peça muda."""
    c = repo.garantir_colecao(colecao, temporada, ano, editor_responsavel=autor)
    prompt = Prompt(
        titulo=titulo.strip(),
        texto=texto,
        colecao=c.id,
        autor=autor.strip(),
        modelo=modelo.strip() if modelo else None,
        temperatura=temperatura,
    )
    repo.salvar_prompt(prompt)
    # Fatia 3: avisar quando o prompt não poderá ser reusado.
    dica = ""
    if "look" not in variaveis_do_texto(texto):
        dica = " Dica: ele não tem {{look}}, então ainda não pode ser reusado trocando a peça."
    return (
        f'Prompt salvo com id {prompt.id} na coleção "{c.nome}", como rascunho. '
        f"Já aparece no mural.{dica}"
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


# Fatia 3 · H03: reusar trocando os looks
class PedidoDeLook(BaseModel):
    """Um look pedido pelo editor: a peça e, se quiser, a cor e o tecido."""

    peca: Annotated[str, Field(min_length=1, max_length=LIMITES["peca"])]
    cor_e_tecido: Annotated[str, Field(max_length=LIMITES["peca"])] | None = None


@servidor.tool()
def reusar_prompt(
    id: IdDePrompt,
    looks: Annotated[
        list[PedidoDeLook], Field(min_length=1, max_length=LIMITES["looks_por_pedido"])
    ],
) -> str:
    """Gera um prompt por look, trocando o {{look}} pela peça. Registra os looks da coleção."""
    prompt = repo.obter(id.strip())
    if prompt is None:
        raise ToolError(f'Não encontrei um prompt com id "{id}".')
    if "look" not in variaveis_do_texto(prompt.texto):
        raise ToolError(
            f'O prompt "{prompt.titulo}" não tem {{{{look}}}}: não há onde trocar a peça. '
            "Salve uma versão com {{look}} no lugar da peça."
        )
    novos = []
    for pedido in looks:
        peca = pedido.peca.strip()
        cor = pedido.cor_e_tecido.strip() if pedido.cor_e_tecido else None
        novos.append(
            Look(
                prompt_id=prompt.id,
                colecao=prompt.colecao,
                peca=peca,
                cor_e_tecido=cor,
                texto_gerado=preencher_look(prompt.texto, peca, cor),
            )
        )
    repo.salvar_looks(novos)
    aviso = ""
    if prompt.status != "aprovado":
        aviso = "\n⚠ Este prompt ainda é rascunho: não é o padrão aprovado da coleção."
    blocos = []
    for i, look in enumerate(novos, start=1):  # enumerate: numera os itens a partir de 1
        nome = f"{look.peca} ({look.cor_e_tecido})" if look.cor_e_tecido else look.peca
        blocos.append(f"── Look {i} · {nome}\n{look.texto_gerado}")
    return f'{len(novos)} look(s) gerado(s) a partir de "{prompt.titulo}":{aviso}\n\n' + (
        "\n\n".join(blocos)
    )


# Fatia 4 · H04: aprovar o prompt padrão (papel do editor-chefe)
@servidor.tool()
def aprovar_prompt(id: IdDePrompt, aprovado_por: Apelido) -> str:
    """Papel do editor-chefe: aprova o prompt padrão da coleção. O anterior volta a rascunho."""
    resultado = repo.aprovar(id.strip(), aprovado_por.strip())
    if resultado is None:
        raise ToolError(f'Não encontrei um prompt com id "{id}".')
    aprovado, anterior = resultado  # "desempacota" a dupla (aprovado, anterior)
    troca = f' O antigo padrão, "{anterior.titulo}", voltou a rascunho.' if anterior else ""
    return (
        f'"{aprovado.titulo}" agora é o prompt aprovado da coleção {aprovado.colecao}, '
        f"por {aprovado_por.strip()}.{troca}"
    )


# Fatia 4: o prompt completo no formato .prompt
@servidor.tool()
def obter_prompt(id: IdDePrompt) -> str:
    """Devolve um prompt completo pelo id, no formato Dotprompt (.prompt) do Firebase Genkit."""
    prompt = repo.obter(id.strip())
    if prompt is None:
        raise ToolError(f'Não encontrei um prompt com id "{id}".')
    return f"Arquivo sugerido: {nome_do_arquivo(prompt)}\n\n{para_dotprompt(prompt)}"


def resumo(p: Prompt) -> str:
    """Uma linha por prompt: id, título, coleção, autor, selo e um trecho do texto."""
    trecho = p.texto if len(p.texto) <= 160 else p.texto[:160] + "…"
    selo = " ★ aprovado" if p.status == "aprovado" else ""
    trecho = " ".join(trecho.split())  # junta as quebras de linha num texto corrido
    return f"• [{p.id}] {p.titulo} (coleção {p.colecao}, por {p.autor}){selo}\n  {trecho}"


# Como o Claude chega até ela:  HTTP: streamable-http
if __name__ == "__main__":
    servidor.run(transport="streamable-http")
