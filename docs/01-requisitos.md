# 1. Requisitos

## O problema

Quem usa IA no dia a dia acumula prompts espalhados: no histórico do chat, em notas, em mensagens para si mesmo. Quando precisa de novo daquele prompt que funcionou, não encontra. Em equipe é pior: cada pessoa reinventa o mesmo prompt, e ninguém sabe qual versão está em uso.

> Inspiração: Chip Huyen, *Engenharia de IA*, cap. 5 (Engenharia de prompts), seção sobre organizar e versionar prompts.

## Partes interessadas

| Quem | O que espera |
|---|---|
| Estudante (autor do prompt) | Salvar um prompt sem sair da conversa com o Claude |
| Turma | Ver e reaproveitar os prompts dos colegas |
| Professor | Projetar o mural em sala e moderar o que aparece |
| Claude (sistema) | Ferramentas com nomes e parâmetros claros para saber quando usá-las |

## Requisitos funcionais (o que o sistema faz)

| ID | Requisito |
|---|---|
| RF01 | O usuário salva um prompt informando título, texto e categoria, a partir de uma frase em linguagem natural no app do Claude. |
| RF02 | O sistema lista as categorias existentes e quantos prompts cada uma tem. |
| RF03 | O usuário busca prompts por palavra-chave e/ou categoria. |
| RF04 | O usuário obtém um prompt completo no formato Dotprompt (`.prompt`). |
| RF05 | O mural exibe os prompts salvos em tempo real, do mais recente para o mais antigo. |
| RF06 | O mural filtra por categoria. |
| RF07 | O professor oculta um prompt do mural (moderação). |

## Requisitos não funcionais (como o sistema se comporta)

| ID | Categoria | Requisito |
|---|---|---|
| RNF01 | Desempenho | Um prompt salvo aparece no mural em menos de 2 segundos. |
| RNF02 | Interoperabilidade | Os prompts seguem o formato Dotprompt (cabeçalho YAML + texto), usado pelo Firebase Genkit. |
| RNF03 | Usabilidade | Funciona no app do Claude no celular, sem instalar nada além do conector. |
| RNF04 | Segurança | O mural só lê dados; só o servidor grava. Textos limitados a 4.000 caracteres. |
| RNF05 | Disponibilidade | Hospedagem gerenciada (Firebase), sem servidor para manter ligado. |
| RNF06 | Privacidade | Nesta versão não há login: o autor é só um apelido. **Ninguém deve salvar dados pessoais.** |

## Técnicas de elicitação usadas na aula

1. **Entrevista**: o professor faz o papel do cliente; a turma pergunta.
2. **Observação**: como cada um guarda prompts hoje?
3. **Prototipagem**: o wireframe do mural é validado antes de existir código (ver `06-wireframe.md`).

## Requisito descoberto em aula (de propósito)

A versão 1 não tem login. Isso permite que qualquer um grave com qualquer apelido. **Qual requisito falta?** Esse é o ponto de partida do desafio para casa (ver `05-historias-de-usuario.md`).
