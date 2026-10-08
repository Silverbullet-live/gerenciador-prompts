import { randomUUID } from "node:crypto";
import type {
  Colecao,
  DadosDaColecao,
  Entrega,
  FiltroBusca,
  Look,
  NovaEntrega,
  NovoLook,
  NovoPrompt,
  Prompt,
  ResumoDaColecao,
} from "./modelo.js";
import { idDaColecao, LIMITES } from "./modelo.js";

/**
 * Onde a Fashion Co. guarda coleções, prompts, looks e entregas. O servidor MCP
 * depende só desta interface, então dá para trocar o Firestore por outro banco
 * (ou pela memória, nos testes) sem mexer nas ferramentas.
 */
export interface Repositorio {
  /** Devolve a coleção, criando-a se ainda não existir. */
  garantirColecao(dados: DadosDaColecao): Promise<Colecao>;
  colecoes(): Promise<ResumoDaColecao[]>;
  salvarPrompt(novo: NovoPrompt): Promise<Prompt>;
  buscar(filtro: FiltroBusca): Promise<Prompt[]>;
  obter(id: string): Promise<Prompt | null>;
  /** Aprova o prompt como padrão da coleção. O padrão anterior, se houver, volta a rascunho. */
  aprovar(id: string, aprovadoPor: string): Promise<{ aprovado: Prompt; anterior?: Prompt } | null>;
  salvarLooks(looks: NovoLook[]): Promise<Look[]>;
  looksDoPrompt(promptId: string): Promise<Look[]>;
  registrarEntrega(nova: NovaEntrega): Promise<Entrega>;
}

const novoId = () => randomUUID().slice(0, 8);

/** Filtro comum às duas implementações. */
export function combina(p: Prompt, filtro: FiltroBusca): boolean {
  if (p.oculto) return false;
  if (filtro.colecao && p.colecao !== filtro.colecao) return false;
  if (filtro.somenteAprovados && p.status !== "aprovado") return false;
  if (filtro.termo) {
    const t = filtro.termo.toLowerCase();
    if (!`${p.titulo} ${p.texto} ${p.colecao}`.toLowerCase().includes(t)) return false;
  }
  return true;
}

export function resumir(colecoes: Colecao[], prompts: Prompt[]): ResumoDaColecao[] {
  return colecoes
    .map((c) => {
      const daColecao = prompts.filter((p) => p.colecao === c.id && !p.oculto);
      return {
        ...c,
        totalDePrompts: daColecao.length,
        aprovado: daColecao.find((p) => p.status === "aprovado")?.titulo,
      };
    })
    .sort((a, b) => b.criadaEm.getTime() - a.criadaEm.getTime());
}

/** Implementação em memória: usada no desenvolvimento local e nos testes. */
export class RepositorioEmMemoria implements Repositorio {
  private listaDeColecoes: Colecao[] = [];
  private prompts: Prompt[] = [];
  private looks: Look[] = [];
  private entregas: Entrega[] = [];

  async garantirColecao(dados: DadosDaColecao): Promise<Colecao> {
    const id = idDaColecao(dados.nome);
    let c = this.listaDeColecoes.find((x) => x.id === id);
    if (!c) {
      c = { id, nome: dados.nome.trim(), criadaEm: new Date() };
      this.listaDeColecoes.push(c);
    }
    // Completa o que faltava (temporada, ano, editor), sem apagar o que já havia.
    c.temporada ??= dados.temporada;
    c.ano ??= dados.ano;
    c.editorResponsavel ??= dados.editorResponsavel;
    return c;
  }

  async colecoes(): Promise<ResumoDaColecao[]> {
    return resumir(this.listaDeColecoes, this.prompts);
  }

  async salvarPrompt(novo: NovoPrompt): Promise<Prompt> {
    const p: Prompt = { ...novo, id: novoId(), versao: 1, status: "rascunho", criadoEm: new Date(), oculto: false };
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

  async aprovar(id: string, aprovadoPor: string) {
    const p = await this.obter(id);
    if (!p) return null;
    const anterior = this.prompts.find((x) => x.colecao === p.colecao && x.status === "aprovado" && x.id !== id);
    if (anterior) {
      anterior.status = "rascunho";
      anterior.aprovadoPor = undefined;
      anterior.aprovadoEm = undefined;
    }
    p.status = "aprovado";
    p.aprovadoPor = aprovadoPor;
    p.aprovadoEm = new Date();
    return { aprovado: p, anterior };
  }

  async salvarLooks(novos: NovoLook[]): Promise<Look[]> {
    const criados = novos.map((n) => ({ ...n, id: novoId(), criadoEm: new Date() }));
    this.looks.push(...criados);
    return criados;
  }

  async looksDoPrompt(promptId: string): Promise<Look[]> {
    return this.looks.filter((l) => l.promptId === promptId);
  }

  async registrarEntrega(nova: NovaEntrega): Promise<Entrega> {
    const e: Entrega = { ...nova, id: novoId(), data: new Date() };
    this.entregas.push(e);
    for (const l of this.looks) if (nova.looks.includes(l.id)) l.entregaId = e.id;
    return e;
  }
}
