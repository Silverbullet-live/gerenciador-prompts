"""Exportação para o formato Dotprompt (.prompt), do Firebase Genkit (RNF03).

É o arquivo que a equipe de engenharia recebe: um cabeçalho YAML entre "---" e o texto
do prompt. As variáveis {{look}} viram a entrada declarada (input.schema), para quem
usa o arquivo saber o que precisa passar.
"""

import re
import unicodedata

import yaml

from gerenciador_prompts.modelo import Prompt, variaveis_do_texto


def data_iso(momento) -> str:
    """2026-11-03T15:42:10.000Z: o mesmo formato de data da versão anterior."""
    return momento.strftime("%Y-%m-%dT%H:%M:%S.") + f"{momento.microsecond // 1000:03d}Z"


def para_dotprompt(p: Prompt) -> str:
    """O prompt inteiro em .prompt: cabeçalho YAML + texto."""
    cabecalho = {}
    if p.modelo:
        cabecalho["model"] = p.modelo
    if p.temperatura is not None:
        cabecalho["config"] = {"temperature": p.temperatura}
    variaveis = variaveis_do_texto(p.texto)
    if variaveis:
        cabecalho["input"] = {
            "schema": {
                v: "string, a peça com cor e tecido" if v == "look" else "string" for v in variaveis
            }
        }
    metadata = {
        "titulo": p.titulo,
        "colecao": p.colecao,
        "versao": p.versao,
        "status": p.status,
    }
    if p.aprovado_por:
        metadata["aprovadoPor"] = p.aprovado_por
    metadata["autor"] = p.autor
    metadata["criadoEm"] = data_iso(p.criado_em)
    cabecalho["metadata"] = metadata
    yaml_texto = yaml.safe_dump(cabecalho, sort_keys=False, allow_unicode=True).rstrip()
    return f"---\n{yaml_texto}\n---\n\n{p.texto.strip()}\n"


def nome_do_arquivo(p: Prompt) -> str:
    """Nome sugerido: colecao/titulo.prompt, ex.: verao-2027/editorial_de_praia.prompt."""
    base = unicodedata.normalize("NFD", p.titulo)
    base = "".join(letra for letra in base if not unicodedata.combining(letra)).lower()
    base = re.sub(r"[^a-z0-9]+", "_", base).strip("_")[:60] or p.id
    return f"{p.colecao}/{base}.prompt"
