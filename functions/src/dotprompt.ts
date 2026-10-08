import { stringify } from "yaml";
import type { Prompt } from "./modelo.js";

/**
 * Converte um Prompt para o formato Dotprompt (.prompt), usado pelo
 * Firebase Genkit: cabeçalho YAML entre "---" seguido do texto do prompt.
 * Implementa o RNF02 (interoperabilidade).
 */
export function paraDotprompt(p: Prompt): string {
  const cabecalho: Record<string, unknown> = {};
  if (p.modelo) cabecalho.model = p.modelo;
  if (p.temperatura !== undefined) cabecalho.config = { temperature: p.temperatura };
  cabecalho.metadata = {
    titulo: p.titulo,
    categoria: p.categoria,
    autor: p.autor,
    criadoEm: p.criadoEm.toISOString(),
  };
  return `---\n${stringify(cabecalho).trimEnd()}\n---\n\n${p.texto.trim()}\n`;
}

/** Nome de arquivo sugerido: categoria/titulo.prompt */
export function nomeDoArquivo(p: Prompt): string {
  const base = p.titulo
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "")
    .slice(0, 60) || p.id;
  return `${p.categoria}/${base}.prompt`;
}
