import { FieldValue, getFirestore, Timestamp, type DocumentData, type Firestore } from "firebase-admin/firestore";
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
import { combina, resumir, type Repositorio } from "./repositorio.js";

/** Quantos prompts recentes a busca examina. Suficiente para uma turma. */
const JANELA_DE_BUSCA = 500;

const data = (v: unknown) => (v instanceof Timestamp ? v.toDate() : undefined);
const semNulos = <T extends object>(o: T) =>
  Object.fromEntries(Object.entries(o).filter(([, v]) => v !== undefined)) as T;

/**
 * Implementação com Firestore. Coleções do banco: colecoes, prompts, looks, entregas.
 * O mural lê "prompts" em tempo real.
 *
 * Firestore não faz busca por trecho de texto, então a busca filtra os prompts mais
 * recentes em memória: simples e adequado ao tamanho de uma turma (um bom tema de
 * discussão sobre requisitos de escala).
 */
export class RepositorioFirestore implements Repositorio {
  constructor(private db: Firestore = getFirestore()) {}

  private paraColecao(id: string, d: DocumentData): Colecao {
    return semNulos({
      id,
      nome: d.nome,
      temporada: d.temporada ?? undefined,
      ano: d.ano ?? undefined,
      editorResponsavel: d.editorResponsavel ?? undefined,
      criadaEm: data(d.criadaEm) ?? new Date(0),
    });
  }

  private paraPrompt(id: string, d: DocumentData): Prompt {
    return semNulos({
      id,
      colecao: d.colecao,
      titulo: d.titulo,
      texto: d.texto,
      versao: d.versao ?? 1,
      status: d.status === "aprovado" ? "aprovado" : "rascunho",
      aprovadoPor: d.aprovadoPor ?? undefined,
      aprovadoEm: data(d.aprovadoEm),
      autor: d.autor,
      modelo: d.modelo ?? undefined,
      temperatura: d.temperatura ?? undefined,
      criadoEm: data(d.criadoEm) ?? new Date(0),
      oculto: Boolean(d.oculto),
    });
  }

  private paraLook(id: string, d: DocumentData): Look {
    return semNulos({
      id,
      promptId: d.promptId,
      colecao: d.colecao,
      peca: d.peca,
      corETecido: d.corETecido ?? undefined,
      textoGerado: d.textoGerado,
      imagemGerada: d.imagemGerada ?? undefined,
      entregaId: d.entregaId ?? undefined,
      criadoEm: data(d.criadoEm) ?? new Date(0),
    });
  }

  async garantirColecao(dados: DadosDaColecao): Promise<Colecao> {
    const ref = this.db.collection("colecoes").doc(idDaColecao(dados.nome));
    return this.db.runTransaction(async (tx) => {
      const doc = await tx.get(ref);
      const atual = doc.exists ? doc.data()! : { nome: dados.nome.trim(), criadaEm: Timestamp.now() };
      const completo = {
        ...atual,
        temporada: atual.temporada ?? dados.temporada ?? null,
        ano: atual.ano ?? dados.ano ?? null,
        editorResponsavel: atual.editorResponsavel ?? dados.editorResponsavel ?? null,
      };
      tx.set(ref, completo);
      return this.paraColecao(ref.id, completo);
    });
  }

  private async recentes(): Promise<Prompt[]> {
    const snap = await this.db.collection("prompts").orderBy("criadoEm", "desc").limit(JANELA_DE_BUSCA).get();
    return snap.docs.map((doc) => this.paraPrompt(doc.id, doc.data()));
  }

  async colecoes(): Promise<ResumoDaColecao[]> {
    const snap = await this.db.collection("colecoes").get();
    return resumir(
      snap.docs.map((d) => this.paraColecao(d.id, d.data())),
      await this.recentes(),
    );
  }

  async salvarPrompt(novo: NovoPrompt): Promise<Prompt> {
    const dados = {
      ...novo,
      modelo: novo.modelo ?? null,
      temperatura: novo.temperatura ?? null,
      versao: 1,
      status: "rascunho",
      aprovadoPor: null,
      aprovadoEm: null,
      criadoEm: Timestamp.now(),
      oculto: false,
    };
    const ref = await this.db.collection("prompts").add(dados);
    return this.paraPrompt(ref.id, dados);
  }

  async buscar(filtro: FiltroBusca): Promise<Prompt[]> {
    const limite = Math.min(filtro.limite ?? 10, LIMITES.resultadosBusca);
    return (await this.recentes()).filter((p) => combina(p, filtro)).slice(0, limite);
  }

  async obter(id: string): Promise<Prompt | null> {
    const doc = await this.db.collection("prompts").doc(id).get();
    if (!doc.exists) return null;
    const p = this.paraPrompt(doc.id, doc.data()!);
    return p.oculto ? null : p;
  }

  async aprovar(id: string, aprovadoPor: string) {
    const prompts = this.db.collection("prompts");
    return this.db.runTransaction(async (tx) => {
      const doc = await tx.get(prompts.doc(id));
      if (!doc.exists || doc.data()!.oculto) return null;
      const p = this.paraPrompt(doc.id, doc.data()!);
      const outros = await tx.get(prompts.where("colecao", "==", p.colecao).where("status", "==", "aprovado"));
      let anterior: Prompt | undefined;
      for (const o of outros.docs) {
        if (o.id === id) continue;
        anterior = this.paraPrompt(o.id, o.data());
        tx.update(o.ref, { status: "rascunho", aprovadoPor: null, aprovadoEm: null });
      }
      const agora = Timestamp.now();
      tx.update(doc.ref, { status: "aprovado", aprovadoPor, aprovadoEm: agora });
      return { aprovado: { ...p, status: "aprovado" as const, aprovadoPor, aprovadoEm: agora.toDate() }, anterior };
    });
  }

  async salvarLooks(novos: NovoLook[]): Promise<Look[]> {
    const lote = this.db.batch();
    const criados = novos.map((n) => {
      const ref = this.db.collection("looks").doc();
      const dados = { ...n, corETecido: n.corETecido ?? null, criadoEm: Timestamp.now() };
      lote.set(ref, dados);
      return this.paraLook(ref.id, dados);
    });
    await lote.commit();
    return criados;
  }

  async looksDoPrompt(promptId: string): Promise<Look[]> {
    const snap = await this.db.collection("looks").where("promptId", "==", promptId).get();
    return snap.docs.map((d) => this.paraLook(d.id, d.data()));
  }

  async registrarEntrega(nova: NovaEntrega): Promise<Entrega> {
    const ref = this.db.collection("entregas").doc();
    const agora = Timestamp.now();
    const lote = this.db.batch();
    lote.set(ref, { ...nova, data: agora });
    for (const id of nova.looks) lote.update(this.db.collection("looks").doc(id), { entregaId: ref.id });
    lote.update(this.db.collection("prompts").doc(nova.promptId), { entregas: FieldValue.increment(1) });
    await lote.commit();
    return { ...nova, id: ref.id, data: agora.toDate() };
  }
}
