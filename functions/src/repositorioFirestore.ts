import { getFirestore, Timestamp, type Firestore } from "firebase-admin/firestore";
import type { Categoria, FiltroBusca, NovoPrompt, Prompt } from "./modelo.js";
import { LIMITES } from "./modelo.js";
import { combina, contarCategorias, type RepositorioDePrompts } from "./repositorio.js";

const COLECAO = "prompts";
/** Quantos documentos recentes a busca examina. Suficiente para uma turma. */
const JANELA_DE_BUSCA = 500;

/**
 * Implementação com Firestore. O mural lê a mesma coleção em tempo real.
 * Firestore não faz busca por trecho de texto, então a busca filtra os
 * documentos mais recentes em memória: simples e adequado ao tamanho de uma
 * turma (um bom tema de discussão sobre requisitos de escala).
 */
export class RepositorioFirestore implements RepositorioDePrompts {
  constructor(private db: Firestore = getFirestore()) {}

  private paraPrompt(id: string, d: FirebaseFirestore.DocumentData): Prompt {
    return {
      id,
      titulo: d.titulo,
      texto: d.texto,
      categoria: d.categoria,
      autor: d.autor,
      modelo: d.modelo ?? undefined,
      temperatura: d.temperatura ?? undefined,
      criadoEm: (d.criadoEm as Timestamp)?.toDate?.() ?? new Date(0),
      oculto: Boolean(d.oculto),
    };
  }

  async salvar(novo: NovoPrompt): Promise<Prompt> {
    const dados = {
      titulo: novo.titulo,
      texto: novo.texto,
      categoria: novo.categoria,
      autor: novo.autor,
      modelo: novo.modelo ?? null,
      temperatura: novo.temperatura ?? null,
      criadoEm: Timestamp.now(),
      oculto: false,
    };
    const ref = await this.db.collection(COLECAO).add(dados);
    return this.paraPrompt(ref.id, dados);
  }

  private async recentes(): Promise<Prompt[]> {
    const snap = await this.db.collection(COLECAO).orderBy("criadoEm", "desc").limit(JANELA_DE_BUSCA).get();
    return snap.docs.map((doc) => this.paraPrompt(doc.id, doc.data()));
  }

  async buscar(filtro: FiltroBusca): Promise<Prompt[]> {
    const limite = Math.min(filtro.limite ?? 10, LIMITES.resultadosBusca);
    return (await this.recentes()).filter((p) => combina(p, filtro)).slice(0, limite);
  }

  async obter(id: string): Promise<Prompt | null> {
    const doc = await this.db.collection(COLECAO).doc(id).get();
    if (!doc.exists) return null;
    const p = this.paraPrompt(doc.id, doc.data()!);
    return p.oculto ? null : p;
  }

  async categorias(): Promise<Categoria[]> {
    return contarCategorias(await this.recentes());
  }
}
