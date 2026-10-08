/**
 * Modelo de dados: a classe Prompt do diagrama em docs/03-classes.md.
 */
export interface Prompt {
  id: string;
  titulo: string;
  texto: string;
  categoria: string;
  autor: string;
  modelo?: string;
  temperatura?: number;
  criadoEm: Date;
  oculto: boolean;
}

export type NovoPrompt = Omit<Prompt, "id" | "criadoEm" | "oculto">;

export interface Categoria {
  nome: string;
  total: number;
}

export interface FiltroBusca {
  termo?: string;
  categoria?: string;
  limite?: number;
}

/** Limites que implementam o RNF04 (segurança). */
export const LIMITES = {
  titulo: 120,
  texto: 4000,
  categoria: 40,
  autor: 40,
  resultadosBusca: 20,
} as const;

/** Normaliza o nome da categoria: "Marketing Digital" vira "marketing-digital". */
export function normalizarCategoria(nome: string): string {
  return nome
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, LIMITES.categoria) || "geral";
}
