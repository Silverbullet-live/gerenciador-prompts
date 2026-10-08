/**
 * Modelo de domínio da Fashion Co. (docs/03-classes.md).
 *
 *   Coleção 1 ── N Prompt 1 ── N Look N ── 1 Entrega
 *
 * Saiu do Event Storming da troca de coleção: coleção planejada → looks definidos →
 * prompt escrito → imagens geradas → prompt aprovado → looks entregues à engenharia.
 */

export type StatusDoPrompt = "rascunho" | "aprovado";

/** Uma das quatro trocas de coleção do ano. */
export interface Colecao {
  id: string; // "verao-2027", derivado do nome
  nome: string; // "Verão 2027"
  temporada?: string;
  ano?: number;
  editorResponsavel?: string;
  criadaEm: Date;
}

/** O prompt que gera as imagens de uma coleção. O texto usa {{look}} onde a peça muda. */
export interface Prompt {
  id: string;
  colecao: string; // id da coleção
  titulo: string;
  texto: string;
  versao: number; // na v1 é sempre 1: versões são o desafio da v3 (H06)
  status: StatusDoPrompt;
  aprovadoPor?: string;
  aprovadoEm?: Date;
  autor: string; // só um apelido: a v1 não tem login (o "requisito escondido")
  modelo?: string;
  temperatura?: number;
  criadoEm: Date;
  oculto: boolean;
}

/** Uma peça da coleção, gerada a partir de um prompt trocando o {{look}}. */
export interface Look {
  id: string;
  promptId: string;
  colecao: string;
  peca: string;
  corETecido?: string;
  textoGerado: string; // o prompt com o {{look}} já preenchido, pronto para a IA de imagem
  imagemGerada?: string; // URL da imagem, quando houver (fora do escopo da v1)
  entregaId?: string;
  criadoEm: Date;
}

/** O pacote que a equipe de engenharia recebe: o prompt aprovado e os looks da coleção. */
export interface Entrega {
  id: string;
  colecao: string;
  data: Date;
  promptId: string; // o prompt aprovado (o padrão da coleção)
  looks: string[]; // ids dos looks enviados
  recebidoPor: string;
}

export interface DadosDaColecao {
  nome: string;
  temporada?: string;
  ano?: number;
  editorResponsavel?: string;
}

export type NovoPrompt = Pick<Prompt, "colecao" | "titulo" | "texto" | "autor" | "modelo" | "temperatura">;
export type NovoLook = Pick<Look, "promptId" | "colecao" | "peca" | "corETecido" | "textoGerado">;
export type NovaEntrega = Pick<Entrega, "colecao" | "promptId" | "looks" | "recebidoPor">;

export interface ResumoDaColecao extends Colecao {
  totalDePrompts: number;
  aprovado?: string; // título do prompt aprovado, se houver
}

export interface FiltroBusca {
  termo?: string;
  colecao?: string;
  somenteAprovados?: boolean;
  limite?: number;
}

/** Limites que implementam o requisito de segurança (docs/01-requisitos.md). */
export const LIMITES = {
  titulo: 120,
  texto: 4000,
  colecao: 40,
  apelido: 40,
  peca: 80,
  looksPorPedido: 12,
  resultadosBusca: 20,
} as const;

/** "Verão 2027" vira "verao-2027": o id da coleção. */
export function idDaColecao(nome: string): string {
  return (
    nome
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, "")
      .toLowerCase()
      .trim()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .slice(0, LIMITES.colecao) || "geral"
  );
}

/** As variáveis {{assim}} de um texto, na ordem em que aparecem, sem repetir. */
export function variaveisDoTexto(texto: string): string[] {
  const nomes = [...texto.matchAll(/\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}/g)].map((m) => m[1]);
  return [...new Set(nomes)];
}

/** H03: troca o {{look}} pela descrição da peça. */
export function preencherLook(texto: string, peca: string, corETecido?: string): string {
  const look = corETecido ? `${peca}, ${corETecido}` : peca;
  return texto.replace(/\{\{\s*look\s*\}\}/g, look);
}
