# 9. Depois do release: monitorar e evoluir

A análise não termina quando a versão 1 vai para o ar. O produto em uso gera **evidências**, e elas alimentam as próximas ondas de correção e evolução.

```mermaid
flowchart LR
    M["Monitorar<br/>observar o produto em uso"] --> R["Registrar<br/>evidências e impacto"]
    R --> A["Analisar<br/>classificar, priorizar,<br/>atualizar requisitos"]
    A --> Me["Melhorar<br/>corrigir, implementar, testar"]
    Me --> P["Publicar<br/>uma nova versão do produto"]
    P --> M
```

## Monitorar: de onde vêm as evidências

Neste projeto, sem nenhuma ferramenta extra:

| Fonte | O que mostra |
|---|---|
| A conversa com o Claude | O que o editor pediu, que ferramenta o Claude escolheu e o que ele respondeu quando o sistema não tinha como atender. |
| O mural | O que de fato foi salvo, aprovado e repetido. |
| O Firestore (`entregas`, `looks`) | O que chegou à engenharia. |
| Os logs da função (console do Firebase) | Erros do servidor (`Erro no MCP`). |
| Os editores e a engenharia | Suporte e feedback: "não achei", "veio errado", "faltou". |

## Registrar: o que toda evidência precisa ter

Um registro por problema (por exemplo, uma *issue* no GitHub do seu fork):

```markdown
**Resumo:** uma frase.
**Tipo:** defeito | gap ou nova necessidade
**Requisito relacionado:** RF/RNF/H (ou "nenhum": isso já é uma pista de gap)
**Passos para reproduzir:** 1. … 2. … 3. …
**Esperado:** o que o requisito diz.
**Observado:** o que aconteceu.
**Contexto e impacto:** quem é afetado, com que frequência, o que se perde.
**Versão do produto:** ex.: v1.0.0
```

## Analisar: defeito ou gap?

A pergunta que separa os dois: **existe um requisito que cobre isso?**

| | Defeito | Gap ou nova necessidade |
|---|---|---|
| Requisito | Existe, e o sistema não cumpre. | Não existe, ou a necessidade mudou. |
| O que se registra | Passos, esperado e observado. | Contexto, impacto e quem é afetado. |
| O que muda na análise | Nada: o requisito estava certo. Falta um teste que o garanta. | Os requisitos e o backlog: nasce uma história nova (ou muda uma antiga). |
| Onde entra a correção | Uma versão de correção (ex.: v1.0.1). | Uma versão de evolução (ex.: v2). |

Nem toda mudança é bug, e nem toda evolução é uma versão de prompt.

Depois de classificar, **priorize** pelo impacto e pela urgência e leve ao Kanban (`05-historias-de-usuario.md`).

## Exemplos reais deste projeto

**Defeito.** `entregar_colecao` registrava uma entrega mesmo sem nenhum look gerado.
- Requisito: RF06, entregar à engenharia a imagem aprovada **de cada look**, com o prompt aprovado.
- Passos: aprovar um prompt que nunca foi reusado e pedir a entrega da coleção.
- Esperado: recusar, porque não há o que entregar. Observado: entrega registrada, vazia.
- Correção: a ferramenta passou a recusar, e um teste em `functions/src/teste.ts` garante a regra.

**Gaps.** O ensaio da aula (09/10/2026) revelou dois requisitos que não existiam:
- **Login.** Bastou dizer "sou o editor-chefe" para aprovar. Hoje o papel é uma declaração, não uma credencial. Vai para o desafio **v2**.
- **Versões de prompt.** Não há como editar um prompt: a correção virou um segundo cartão no mural, e o rascunho velho ficou lá. Vai para o desafio **v3** (H06).

Nos dois casos, o sistema fez exatamente o que os requisitos mandavam. O que faltava era o requisito.

## Publicar: versão do produto não é versão do prompt

São duas coisas diferentes, que por acaso usam a mesma palavra:

| | Versão do produto (release) | Versão do prompt |
|---|---|---|
| O que versiona | O sistema inteiro: código, regras, ferramentas. | Um prompt da coleção. |
| Onde fica | Tag no Git (ex.: `v1.0.0`) e o `version` em `functions/package.json`. | O campo `versao` de `Prompt` (`functions/src/modelo.ts`). |
| Quem muda | A equipe que desenvolve, a cada publicação. | O editor, ao melhorar um prompt. |
| Na v1 | Existe. | Existe no modelo, mas é sempre 1. |

O desafio **v3** é uma versão do produto que traz, como novidade, **versões de prompt**. Cada release precisa ser rastreável: saber qual versão estava no ar quando a evidência foi registrada é o que permite reproduzir o problema.

## Perguntas para a turma

1. "O mural não mostra a imagem do look." É defeito ou gap? Que requisito você procuraria primeiro?
2. Um editor digitou "pôr do sol" na busca e não achou o prompt de "fim de tarde". É defeito ou gap? Escreva o registro completo.
3. A correção do defeito acima vira v1.0.1 ou v2? E o login?
