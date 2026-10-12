"""Fatia 6: o mesmo repositório, agora gravando no Firestore.

Tem exatamente os mesmos métodos do RepositorioEmMemoria. Por isso o servidor não muda:
ele só recebe outro repositório (a decisão "o servidor não sabe qual banco usa", slide 25).

Os nomes dos campos no banco (titulo, criadoEm, aprovadoPor...) são os mesmos da versão
anterior do sistema: o mural lê o Firestore e continua funcionando sem mudar nada.
"""

from google.cloud import firestore

from gerenciador_prompts.modelo import (
    LIMITES,
    Colecao,
    Entrega,
    Look,
    Prompt,
    ResumoDaColecao,
    agora,
    id_da_colecao,
)
from gerenciador_prompts.repositorio import combina

# Quantos prompts recentes a busca examina. O Firestore não busca por trecho de texto,
# então a busca filtra em memória os mais recentes: suficiente para uma turma.
JANELA_DE_BUSCA = 500


# ── Conversões: objeto Python ↔ documento do Firestore ─────────────────────


def colecao_para_doc(c: Colecao) -> dict:
    return {
        "nome": c.nome,
        "temporada": c.temporada,
        "ano": c.ano,
        "editorResponsavel": c.editor_responsavel,
        "criadaEm": c.criada_em,
    }


def doc_para_colecao(id: str, d: dict) -> Colecao:
    return Colecao(
        id=id,
        nome=d["nome"],
        temporada=d.get("temporada"),
        ano=d.get("ano"),
        editor_responsavel=d.get("editorResponsavel"),
        criada_em=d.get("criadaEm") or agora(),
    )


def prompt_para_doc(p: Prompt) -> dict:
    return {
        "colecao": p.colecao,
        "titulo": p.titulo,
        "texto": p.texto,
        "versao": p.versao,
        "status": p.status,
        "aprovadoPor": p.aprovado_por,
        "aprovadoEm": p.aprovado_em,
        "autor": p.autor,
        "modelo": p.modelo,
        "temperatura": p.temperatura,
        "criadoEm": p.criado_em,
        "oculto": p.oculto,
    }


def doc_para_prompt(id: str, d: dict) -> Prompt:
    return Prompt(
        id=id,
        titulo=d["titulo"],
        texto=d["texto"],
        colecao=d["colecao"],
        autor=d.get("autor") or "anônimo",
        status="aprovado" if d.get("status") == "aprovado" else "rascunho",
        versao=d.get("versao") or 1,
        aprovado_por=d.get("aprovadoPor"),
        aprovado_em=d.get("aprovadoEm"),
        modelo=d.get("modelo"),
        temperatura=d.get("temperatura"),
        criado_em=d.get("criadoEm") or agora(),
        oculto=bool(d.get("oculto")),
    )


def look_para_doc(look: Look) -> dict:
    return {
        "promptId": look.prompt_id,
        "colecao": look.colecao,
        "peca": look.peca,
        "corETecido": look.cor_e_tecido,
        "textoGerado": look.texto_gerado,
        "imagemGerada": look.imagem_gerada,
        "entregaId": look.entrega_id,
        "criadoEm": look.criado_em,
    }


def doc_para_look(id: str, d: dict) -> Look:
    return Look(
        id=id,
        prompt_id=d["promptId"],
        colecao=d["colecao"],
        peca=d["peca"],
        cor_e_tecido=d.get("corETecido"),
        texto_gerado=d["textoGerado"],
        imagem_gerada=d.get("imagemGerada"),
        entrega_id=d.get("entregaId"),
        criado_em=d.get("criadoEm") or agora(),
    )


class RepositorioFirestore:
    """Coleções do banco: colecoes, prompts, looks, entregas. O mural lê "prompts" ao vivo."""

    def __init__(self, cliente: firestore.Client | None = None):
        # Sem cliente informado, usa o projeto e a credencial do ambiente (no Firebase, automático).
        self.db = cliente or firestore.Client()

    def salvar_prompt(self, prompt: Prompt) -> Prompt:
        self.db.collection("prompts").document(prompt.id).set(prompt_para_doc(prompt))
        return prompt

    def garantir_colecao(
        self,
        nome: str,
        temporada: str | None = None,
        ano: int | None = None,
        editor_responsavel: str | None = None,
    ) -> Colecao:
        ref = self.db.collection("colecoes").document(id_da_colecao(nome))

        # Transação: se dois editores salvarem ao mesmo tempo, a coleção não é criada duas vezes.
        @firestore.transactional
        def garantir(transacao):
            doc = ref.get(transaction=transacao)
            if doc.exists:
                colecao = doc_para_colecao(ref.id, doc.to_dict())
            else:
                colecao = Colecao(id=ref.id, nome=nome.strip())
            colecao.temporada = colecao.temporada or temporada
            colecao.ano = colecao.ano or ano
            colecao.editor_responsavel = colecao.editor_responsavel or editor_responsavel
            transacao.set(ref, colecao_para_doc(colecao))
            return colecao

        return garantir(self.db.transaction())

    def recentes(self) -> list[Prompt]:
        consulta = (
            self.db.collection("prompts")
            .order_by("criadoEm", direction=firestore.Query.DESCENDING)
            .limit(JANELA_DE_BUSCA)
        )
        return [doc_para_prompt(doc.id, doc.to_dict()) for doc in consulta.stream()]

    def resumo_das_colecoes(self) -> list[ResumoDaColecao]:
        prompts = self.recentes()
        resumos = []
        for doc in self.db.collection("colecoes").stream():
            colecao = doc_para_colecao(doc.id, doc.to_dict())
            da_colecao = [p for p in prompts if p.colecao == colecao.id and not p.oculto]
            aprovado = next((p.titulo for p in da_colecao if p.status == "aprovado"), None)
            resumos.append(ResumoDaColecao(colecao, len(da_colecao), aprovado))
        return sorted(resumos, key=lambda r: r.colecao.criada_em, reverse=True)

    def buscar(
        self,
        termo: str | None = None,
        colecao: str | None = None,
        somente_aprovados: bool = False,
        limite: int = 10,
    ) -> list[Prompt]:
        limite = min(limite, LIMITES["resultados_busca"])
        achados = [p for p in self.recentes() if combina(p, termo, colecao, somente_aprovados)]
        return achados[:limite]

    def obter(self, id: str) -> Prompt | None:
        doc = self.db.collection("prompts").document(id).get()
        if not doc.exists:
            return None
        prompt = doc_para_prompt(doc.id, doc.to_dict())
        return None if prompt.oculto else prompt

    def salvar_looks(self, looks: list[Look]) -> list[Look]:
        lote = self.db.batch()  # lote: grava todos de uma vez, ou nenhum
        for look in looks:
            lote.set(self.db.collection("looks").document(look.id), look_para_doc(look))
        lote.commit()
        return looks

    def looks_do_prompt(self, prompt_id: str) -> list[Look]:
        consulta = self.db.collection("looks").where(
            filter=firestore.FieldFilter("promptId", "==", prompt_id)
        )
        looks = [doc_para_look(doc.id, doc.to_dict()) for doc in consulta.stream()]
        return sorted(looks, key=lambda look: look.criado_em)

    def aprovar(self, id: str, aprovado_por: str) -> tuple[Prompt, Prompt | None] | None:
        prompts = self.db.collection("prompts")

        @firestore.transactional
        def aprovar_na_transacao(transacao):
            doc = prompts.document(id).get(transaction=transacao)
            if not doc.exists or doc.to_dict().get("oculto"):
                return None
            prompt = doc_para_prompt(doc.id, doc.to_dict())
            outros = prompts.where(
                filter=firestore.FieldFilter("colecao", "==", prompt.colecao)
            ).where(filter=firestore.FieldFilter("status", "==", "aprovado"))
            anterior = None
            for outro in outros.stream(transaction=transacao):
                if outro.id == id:
                    continue
                anterior = doc_para_prompt(outro.id, outro.to_dict())
                transacao.update(
                    outro.reference, {"status": "rascunho", "aprovadoPor": None, "aprovadoEm": None}
                )
            momento = agora()
            transacao.update(
                doc.reference,
                {"status": "aprovado", "aprovadoPor": aprovado_por, "aprovadoEm": momento},
            )
            prompt.status, prompt.aprovado_por, prompt.aprovado_em = (
                "aprovado",
                aprovado_por,
                momento,
            )
            return prompt, anterior

        return aprovar_na_transacao(self.db.transaction())

    def registrar_entrega(self, entrega: Entrega) -> Entrega:
        lote = self.db.batch()
        lote.set(
            self.db.collection("entregas").document(entrega.id),
            {
                "colecao": entrega.colecao,
                "promptId": entrega.prompt_id,
                "looks": entrega.looks,
                "recebidoPor": entrega.recebido_por,
                "data": entrega.data,
            },
        )
        for look_id in entrega.looks:
            lote.update(self.db.collection("looks").document(look_id), {"entregaId": entrega.id})
        lote.update(
            self.db.collection("prompts").document(entrega.prompt_id),
            {"entregas": firestore.Increment(1)},
        )
        lote.commit()
        return entrega
