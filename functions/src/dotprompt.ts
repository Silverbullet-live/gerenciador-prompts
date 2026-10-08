import { stringify } from "yaml";
import type { Prompt } from "./modelo.js";
import { variaveisDoTexto } from "./modelo.js";

/**
 * Converte um Prompt para o formato Dotprompt (.prompt), usado pelo Firebase Genkit:
 * cabeçalho YAML entre "---" seguido do texto do prompt. É o arquivo que a equipe de
 * engenharia recebe (caso de uso "Publicar a partir de .prompt").
 *
 * As variáveis {{look}} do texto viram a entrada declarada do prompt (input.schema),
 * no formato Picoschema do Dotprompt: quem usa o arquivo sabe o que precisa passar.
 */
export function paraDotprompt(p: Prompt): string {
  const cabecalho: Record<string, unknown> = {};
  if (p.modelo) cabecalho.model = p.modelo;
  if (p.temperatura !== undefined) cabecalho.config = { temperature: p.temperatura };
  const variaveis = variaveisDoTexto(p.texto);
  if (variaveis.length > 0) {
    cabecalho.input = {
      schema: Object.fromEntries(
        variaveis.map((v) => [v, v === "look" ? "string, a peça com cor e tecido" : "string"]),
      ),
    };
  }
  cabecalho.metadata = {
    titulo: p.titulo,
    colecao: p.colecao,
    versao: p.versao,
    status: p.status,
    ...(p.aprovadoPor ? { aprovadoPor: p.aprovadoPor } : {}),
    autor: p.autor,
    criadoEm: p.criadoEm.toISOString(),
  };
  return `---\n${stringify(cabecalho).trimEnd()}\n---\n\n${p.texto.trim()}\n`;
}

/** Nome de arquivo sugerido: colecao/titulo.prompt */
export function nomeDoArquivo(p: Prompt): string {
  const base =
    p.titulo
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_+|_+$/g, "")
      .slice(0, 60) || p.id;
  return `${p.colecao}/${base}.prompt`;
}
