# 1. Requisitos

## O problema

Você é editor de moda da **Fashion Co.** e precisa organizar as trocas de coleção do ano. Elas acontecem **4 vezes por ano**, e a cada troca você escreve **prompts complexos** para gerar as imagens com as roupas da coleção, aprova as que atendem ao padrão e envia **as imagens aprovadas** dos novos looks para a **equipe de engenharia**, que as publica.

Três dores aparecem:

| Dor | O que acontece hoje |
|---|---|
| **Prompts soltos** | Ficam no histórico do chat, no bloco de notas, numa mensagem de WhatsApp. |
| **Muita refação** | Cada editor reescreve o mesmo prompt, trocando só os looks. |
| **Falta de padrão** | Há coleções com produções boas e ruins: a qualidade não se mantém. |

**A solução:** um gerenciador de prompts. Hoje, na "esteira da fábrica", estão os trabalhadores que produzem com IA, e todos precisam organizar e **versionar prompts**, assim como se versiona código no GitHub.

> A Fashion Co. é uma marca fictícia. O case é real; o foco é estudantil.
> Inspiração: Chip Huyen, *Engenharia de IA*, cap. 5, sobre organizar e versionar prompts.

### Por que este projeto

**Um prompt é um requisito entregue a uma máquina.** Quando o prompt é vago, a IA entende errado. Quando o requisito é vago, a equipe constrói errado. É o mesmo problema, e quem aprende a resolver um aprende a resolver o outro. Por isso este projeto ensina análise duas vezes.

## Partes interessadas

| Quem | O que espera |
|---|---|
| Editor de moda | Salvar, encontrar e reusar os prompts de cada coleção sem sair da conversa com o Claude |
| Editor-chefe | Garantir a qualidade: aprovar o prompt padrão de cada coleção |
| Equipe de engenharia | Receber a imagem aprovada de cada look e o prompt aprovado num formato de mercado (`.prompt`), e não por WhatsApp |
| Claude (ator-sistema) | Ferramentas com nomes e parâmetros claros, para saber quando usar cada uma |

## Requisitos funcionais (o que o sistema faz)

| ID | Requisito | Ferramenta |
|---|---|---|
| RF01 | Salvar um prompt com título, texto e coleção, pedindo ao Claude. (Na aula, a coleção faz o papel de categoria.) | `salvar_prompt` |
| RF02 | Buscar prompts por palavra ou por coleção. | `buscar_prompts`, `listar_colecoes` |
| RF03 | Mostrar no mural os prompts salvos, do mais novo para o mais antigo. | mural |
| RF04 | Reusar um prompt trocando só os looks (o `{{look}}` do texto). | `reusar_prompt` |
| RF05 | O editor-chefe aprova o prompt padrão de cada coleção (um só por coleção). | `aprovar_prompt` |
| RF06 | Entregar à engenharia a imagem aprovada pelo editor de cada look (ao menos um), com o prompt aprovado em `.prompt`. A engenharia publica essas imagens: não gera outras. | `entregar_colecao` (parcial na v1: ver abaixo) |

**RF06 na v1:** a entrega leva o `.prompt` aprovado e a lista de looks, mas **ainda não as imagens aprovadas**: a imagem é gerada no Claude, pela IA de imagem, e o sistema não recebe o arquivo. Sem a imagem, a engenharia teria de gerar outra a partir do prompt, e a qualidade aprovada pelo editor se perde. Registrado na issue #5.

## Requisitos não funcionais (como o sistema se comporta)

| ID | Categoria | Requisito |
|---|---|---|
| RNF01 | Desempenho | Um prompt salvo aparece no mural em menos de 2 segundos. |
| RNF02 | Usabilidade | Funciona no app do Claude no celular, sem instalar nada além do conector. |
| RNF03 | Interoperabilidade | Os prompts seguem um formato padrão de mercado: **Dotprompt** (cabeçalho YAML + texto), do Firebase Genkit. |
| RNF04 | Segurança | O mural só lê dados; só o servidor grava. Textos até 4.000 caracteres; até 12 looks por pedido. |
| RNF05 | Disponibilidade | Hospedagem gerenciada (Firebase), sem servidor para manter ligado. |
| RNF06 | Privacidade | Nesta versão não há login: o autor é só um apelido. **Ninguém deve salvar dados pessoais.** |

## Ninguém entrega os requisitos prontos: elicitação de requisitos

| Técnica | Na aula |
|---|---|
| **Entrevista** | Perguntar ao cliente. Hoje o professor é o cliente: o que vocês perguntariam antes de construir? |
| **Observação** | Ver como se faz hoje. Como cada um de vocês guarda os prompts que funcionam? |
| **Protótipo** | Mostrar antes de construir. Um rabisco da tela revela o que a conversa esqueceu (ver `06-wireframe.md`). |

## Um requisito escondido

A primeira versão **não tem login**: qualquer um salva com qualquer apelido, e qualquer um pode se dizer editor-chefe e aprovar um prompt. Vamos descobrir, na prática, por que isso é um problema.

**E se alguém salvar um prompt usando o apelido de outra pessoa? Que requisito faltou?** Esse é o ponto de partida do desafio v2 (ver `05-historias-de-usuario.md`).
