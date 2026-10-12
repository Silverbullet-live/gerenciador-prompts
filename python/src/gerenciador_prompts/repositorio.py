"""Onde os prompts ficam guardados. Por enquanto, na memória."""

from gerenciador_prompts.modelo import (
    LIMITES,
    Colecao,
    Look,
    Prompt,
    ResumoDaColecao,
    agora,
    id_da_colecao,
)


class RepositorioEmMemoria:
    """Guarda os prompts numa lista: some quando o servidor reinicia."""

    def __init__(self):
        self.prompts = []  # a "gaveta" deste repositório: começa vazia
        self.colecoes = {}  # Fatia 2: as coleções, pelo id ("verao-2027" → Colecao)
        self.looks = []  # Fatia 3: os looks gerados a partir dos prompts

    def salvar_prompt(self, prompt: Prompt) -> Prompt:
        """Guarda o prompt e o devolve."""
        self.prompts.append(prompt)
        return prompt

    # ── Fatia 2 · H02: coleções, busca e consulta ──────────────────────────

    def garantir_colecao(
        self,
        nome: str,
        temporada: str | None = None,
        ano: int | None = None,
        editor_responsavel: str | None = None,
    ) -> Colecao:
        """Devolve a coleção, criando-a se ainda não existir.

        Se ela já existe, só completa o que faltava (temporada, ano, editor):
        nunca apaga o que já havia.
        """
        id = id_da_colecao(nome)
        colecao = self.colecoes.get(id)
        if colecao is None:
            colecao = Colecao(id=id, nome=nome.strip())
            self.colecoes[id] = colecao
        if colecao.temporada is None:
            colecao.temporada = temporada
        if colecao.ano is None:
            colecao.ano = ano
        if colecao.editor_responsavel is None:
            colecao.editor_responsavel = editor_responsavel
        return colecao

    def resumo_das_colecoes(self) -> list[ResumoDaColecao]:
        """Cada coleção com o total de prompts e o título do aprovado (mais nova primeiro)."""
        resumos = []
        for colecao in self.colecoes.values():
            da_colecao = [p for p in self.prompts if p.colecao == colecao.id and not p.oculto]
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
        """Os prompts que combinam com o filtro, do mais novo para o mais antigo."""
        limite = min(limite, LIMITES["resultados_busca"])
        achados = []
        for prompt in reversed(self.prompts):  # reversed: o último salvo vem primeiro
            if combina(prompt, termo, colecao, somente_aprovados):
                achados.append(prompt)
        return achados[:limite]

    def obter(self, id: str) -> Prompt | None:
        """O prompt com esse id, ou None se não existir (ou estiver oculto)."""
        for prompt in self.prompts:
            if prompt.id == id and not prompt.oculto:
                return prompt
        return None

    # ── Fatia 3 · H03: looks ───────────────────────────────────────────────

    def salvar_looks(self, looks: list[Look]) -> list[Look]:
        """Guarda os looks gerados de uma vez e os devolve."""
        self.looks.extend(looks)  # extend: acrescenta todos os itens de uma lista
        return looks

    def looks_do_prompt(self, prompt_id: str) -> list[Look]:
        """Os looks que nasceram de um prompt."""
        return [look for look in self.looks if look.prompt_id == prompt_id]

    # ── Fatia 4 · H04: aprovar o padrão ─────────────────────────────────────

    def aprovar(self, id: str, aprovado_por: str) -> tuple[Prompt, Prompt | None] | None:
        """Aprova o prompt como padrão da coleção.

        Regra de negócio: cada coleção tem um só aprovado. O padrão anterior, se houver,
        volta a rascunho. Devolve (aprovado, anterior), ou None se o id não existir.
        """
        prompt = self.obter(id)
        if prompt is None:
            return None
        anterior = None
        for outro in self.prompts:
            if (
                outro.colecao == prompt.colecao
                and outro.status == "aprovado"
                and outro is not prompt
            ):
                outro.status = "rascunho"
                outro.aprovado_por = None
                outro.aprovado_em = None
                anterior = outro
        prompt.status = "aprovado"
        prompt.aprovado_por = aprovado_por
        prompt.aprovado_em = agora()
        return prompt, anterior


def combina(
    prompt: Prompt,
    termo: str | None,
    colecao: str | None,
    somente_aprovados: bool,
) -> bool:
    """A regra do filtro, separada do repositório para valer também no Firestore (fatia 6)."""
    if prompt.oculto:
        return False
    if colecao and prompt.colecao != colecao:
        return False
    if somente_aprovados and prompt.status != "aprovado":
        return False
    if termo:
        onde_procurar = f"{prompt.titulo} {prompt.texto} {prompt.colecao}".lower()
        if termo.lower() not in onde_procurar:
            return False
    return True
