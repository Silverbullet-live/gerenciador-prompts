import { randomUUID } from "node:crypto";
import type { Categoria, FiltroBusca, NovoPrompt, Prompt } from "./modelo.js";
import { LIMITES } from "./modelo.js";

/**
 * Onde os prompts são guardados. O servidor MCP depende só desta interface,
 * então dá para trocar o Firestore por outro banco (ou pela memória, nos testes)
 * sem mexer nas ferramentas.
 */
export interface RepositorioDePrompts {
  salvar(novo: NovoPrompt): Promise<Prompt>;
  buscar(filtro: FiltroBusca): Promise<Prompt[]>;
  obter(id: string): Promise<Prompt | null>;
  categorias(): Promise<Categoria[]>;
}

/** Filtro comum às duas implementações. */
export function combina(p: Prompt, filtro: FiltroBusca): boolean {
  if (p.oculto) return false;
  if (filtro.categoria && p.categoria !== filtro.categoria) return false;
  if (filtro.termo) {
    const t = filtro.termo.toLowerCase();
    const alvo = `${p.titulo} ${p.texto} ${p.categoria}`.toLowerCase();
    if (!alvo.includes(t)) return false;
  }
  return true;
}

export function contarCategorias(prompts: Prompt[]): Categoria[] {
  const contagem = new Map<string, number>();
  for (const p of prompts) {
    if (p.oculto) continue;
    contagem.set(p.categoria, (contagem.get(p.categoria) ?? 0) + 1);
  }
  return [...contagem.entries()]
    .map(([nome, total]) => ({ nome, total }))
    .sort((a, b) => b.total - a.total || a.nome.localeCompare(b.nome));
}

/** Implementação em memória: usada no desenvolvimento local e nos testes. */
export class RepositorioEmMemoria implements RepositorioDePrompts {
  private prompts: Prompt[] = [];

  async salvar(novo: NovoPrompt): Promise<Prompt> {
    const p: Prompt = { ...novo, id: randomUUID().slice(0, 8), criadoEm: new Date(), oculto: false };
    this.prompts.unshift(p);
    return p;
  }

  async buscar(filtro: FiltroBusca): Promise<Prompt[]> {
    const limite = Math.min(filtro.limite ?? 10, LIMITES.resultadosBusca);
    return this.prompts.filter((p) => combina(p, filtro)).slice(0, limite);
  }

  async obter(id: string): Promise<Prompt | null> {
    return this.prompts.find((p) => p.id === id && !p.oculto) ?? null;
  }

  async categorias(): Promise<Categoria[]> {
    return contarCategorias(this.prompts);
  }
}
