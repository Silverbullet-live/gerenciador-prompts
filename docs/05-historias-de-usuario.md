# 5. Histórias de usuário e Kanban

Formato: **Como** [quem], **quero** [o quê], **para** [por quê].

## Backlog

| ID | História | Critério de aceite | Ferramenta |
|---|---|---|---|
| H01 | Como editor de moda, quero salvar o prompt de uma coleção pedindo ao Claude, para não perdê-lo no histórico. | Ao pedir, o Claude confirma e o prompt aparece no mural como rascunho. | `salvar_prompt` |
| H02 | Como editor de moda, quero buscar prompts por coleção, para reaproveitar o que já funcionou. | A busca devolve título, coleção, autor e trecho; dá para pedir só o aprovado. | `buscar_prompts` |
| H03 | Como editor de moda, quero reusar um prompt trocando só os looks, para não reescrever tudo a cada coleção. | Para cada look informado, o sistema devolve o prompt com o `{{look}}` preenchido. | `reusar_prompt` |
| H04 | Como editor-chefe, quero aprovar o prompt padrão de cada coleção, para manter a qualidade das imagens. | O prompt ganha o selo "aprovado" no mural; só há um aprovado por coleção. | `aprovar_prompt` |
| H05 | Como engenheiro, quero receber os prompts aprovados em arquivo `.prompt`, para não depender de mensagens no WhatsApp. | A entrega traz o `.prompt` aprovado e a lista de looks, e fica registrada. | `entregar_colecao` |
| H06 | Como editor de moda, quero criar uma nova versão de um prompt sem apagar a anterior, para comparar as coleções. | Desafio v3 (ver `03-classes.md`). | — |

## O quadro da aula

Assim o quadro estava no meio da sprint, como aparece na apresentação:

| A fazer | Fazendo | Revisão | Feito |
|---|---|---|---|
| H05, H06 | H04 | H03 | H01, H02 |

Neste repositório, **H01 a H05 já estão entregues** (rode `npm test` para ver cada uma funcionando). H06 fica para vocês.

## Desafios para depois da aula

| Versão | Desafio | Por onde começar |
|---|---|---|
| **v2** | **Login por pessoa.** Hoje qualquer um usa qualquer apelido e pode se dizer editor-chefe. Cada pessoa entra com a própria conta, e só o editor-chefe aprova. | O Claude aceita conectores com OAuth. Comece pelo requisito: quem pode fazer o quê? |
| **v3** | **Versões de cada prompt (H06).** | O diagrama de classes v3 em `03-classes.md`. |
| **v4** | **Plugin para o Claude Code.** O mesmo gerenciador como comando `/salvar-prompt`, gravando os `.prompt` direto no repositório. | O formato `.prompt` já está pronto em `functions/src/dotprompt.ts`. |

**Escolham um, façam a análise antes, e me mostrem.**

Uma sprint de uma semana pode ter uma história por pessoa do grupo. Montem o quadro no GitHub Projects.
