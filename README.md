# Gerenciador de Prompts · Fashion Co.

Um conector para o app do Claude que salva, organiza, reusa e aprova os prompts de uma equipe de moda, com um **mural ao vivo** para projetar em sala.

Projeto-base da aula de **Análise de Sistemas**: a análise primeiro, o código depois. Comece pela pasta [`docs/`](docs/).

Quer colaborar? Leia o [guia de colaboração](CONTRIBUTING.md): do fork ao pull request, com os erros mais comuns.

> **A Fashion Co. é uma marca fictícia.** O case é real; o foco é estudantil.

## O case

Você é editor de moda da Fashion Co. e precisa organizar as **quatro trocas de coleção do ano**. A cada troca, escreve prompts complexos para gerar as imagens das roupas, aprova as que atendem ao padrão e envia as imagens aprovadas dos novos looks para a equipe de engenharia. Hoje os prompts ficam soltos (no chat, em notas, no WhatsApp), cada editor reescreve o mesmo prompt trocando só os looks, e a qualidade varia de coleção para coleção.

A solução é um gerenciador de prompts: o mesmo cuidado que se tem com código (organizar, versionar, aprovar), agora com prompts.

> Inspirado em Chip Huyen, *Engenharia de IA*, cap. 5. Os prompts são exportados no formato **Dotprompt**, do Firebase Genkit.

## Como funciona

Você conversa com o Claude normalmente. Quando um prompt fica bom, diz:

> "salva esse prompt na coleção Verão 2027, meu apelido é rafa"

O Claude chama a ferramenta certa do conector, o prompt vai para o Firestore e aparece no mural em segundos. Escreva **`{{look}}`** onde a peça muda: assim o mesmo prompt serve para a coleção inteira.

| Ferramenta | O que faz | História |
|---|---|---|
| `salvar_prompt` | Salva título, texto e coleção (cria a coleção se for nova) | H01 |
| `listar_colecoes` | Lista as coleções, quantos prompts há em cada uma e qual é o aprovado | H02 |
| `buscar_prompts` | Busca por coleção e/ou palavra; pode trazer só o aprovado | H02 |
| `reusar_prompt` | Gera um prompt por look, trocando o `{{look}}` pela peça | H03 |
| `aprovar_prompt` | O editor-chefe aprova o prompt padrão da coleção (um só por coleção) | H04 |
| `obter_prompt` | Devolve um prompt no formato `.prompt` | publicar |
| `entregar_colecao` | Entrega à engenharia o `.prompt` aprovado e os looks gerados (as imagens aprovadas ainda não: issue #5) | H05 |

Exemplo de um `.prompt` exportado:

```yaml
---
model: imagen-4
config:
  temperature: 0.4
input:
  schema:
    look: string, a peça com cor e tecido
metadata:
  titulo: Editorial de praia
  colecao: verao-2027
  versao: 1
  status: aprovado
  aprovadoPor: chefe.ana
  autor: rafa
  criadoEm: 2026-11-03T15:42:10.000Z
---

Foto editorial de moda, luz natural de fim de tarde numa praia. A modelo veste {{look}}. Enquadramento de corpo inteiro, fundo desfocado.
```

## Estrutura

```
docs/            ← a análise: comece por aqui
  01-requisitos.md            o problema, requisitos funcionais e não funcionais
  02-casos-de-uso.md          casos de uso, com o Claude como ator-sistema
  03-classes.md               Event Storming, modelo de domínio e o desafio das versões
  04-sequencia.md             o caminho de uma frase, da conversa ao mural
  05-historias-de-usuario.md  histórias de usuário, Kanban e desafios
  06-wireframe.md             do wireframe à tela real
  07-projeto.md               projeto: arquitetura (mapa das peças) e decisões técnicas
  09-evolucao-pos-release.md  depois do release: monitorar, registrar, classificar e evoluir
functions/       ← o servidor que conversa com o Claude (TypeScript, Firebase Cloud Functions)
  src/modelo.ts               Coleção, Prompt, Look, Entrega
  src/servidorMcp.ts          as sete ferramentas
  src/repositorio*.ts         onde os dados ficam (memória ou Firestore)
  src/dotprompt.ts            exportação para .prompt
  src/teste.ts                teste de ponta a ponta: salvar → buscar → reusar → aprovar → entregar
mural/           ← o mural e a página de conexão (Firebase Hosting)
  index.html                  mural ao vivo (para o projetor)
  conectar.html               passo a passo para conectar o Claude (é para onde o QR code aponta)
```

## Rodar no seu computador (sem Firebase)

Precisa de Node 20 ou mais novo (no Firebase, a função roda em Node 22).

```bash
cd functions
npm install
npm test        # sobe o servidor e percorre a troca de coleção inteira
npm run dev     # servidor local em http://localhost:8787/mcp (dados na memória)
```

Para mexer no servidor local com uma interface, use o MCP Inspector:

```bash
npx @modelcontextprotocol/inspector
# Transport: Streamable HTTP · URL: http://localhost:8787/mcp
```

Abrindo `mural/index.html` direto no navegador, o mural entra em **modo de demonstração**, com exemplos da Fashion Co.

## Publicar no Firebase (no seu projeto)

O repositório não aponta para nenhum projeto: o `.firebaserc` fica fora do Git e o mural lê a configuração do próprio Hosting. Cada fork publica no **seu** projeto Firebase.

1. **Projeto.** Crie um projeto no [console do Firebase](https://console.firebase.google.com).
2. **Plano Blaze.** Cloud Functions exige o plano Blaze (pago por uso), que pede um cartão de crédito cadastrado. Para uma turma, o uso fica dentro da cota gratuita. Sem cartão, fique no "Rodar no seu computador": dá para fazer todos os desafios.
3. **Firestore.** No console do Firebase, crie o banco Firestore (região sugerida: `southamerica-east1`).
4. **CLI e projeto:**
   ```bash
   npm install -g firebase-tools
   firebase login
   cp .firebaserc.exemplo .firebaserc   # troque as 3 ocorrências de SEU-PROJETO-FIREBASE pelo id do projeto
   cd functions && npm install && cd ..
   firebase deploy
   ```
   Se a CLI disser que a credencial expirou, rode `firebase login --reauth`. Para publicar só uma parte: `firebase deploy --only functions` ou `--only hosting:mural`.
5. **Endereços** depois do deploy:
   - Mural: `https://SEU-PROJETO.web.app`
   - Conector (MCP): `https://SEU-PROJETO.web.app/mcp`
   - Instruções para a turma: `https://SEU-PROJETO.web.app/conectar.html`

## Conectar o Claude

1. Abra **claude.ai no navegador** (o app de celular não deixa adicionar conectores; depois de adicionado, ele aparece no app).
2. **Configurações → Conectores → Adicionar conector personalizado.**
3. Nome: `Prompts Fashion Co.`. URL: `https://SEU-PROJETO.web.app/mcp`. A página `conectar.html` do seu deploy já mostra essa URL pronta para copiar.
4. No app, peça para salvar um prompt.

## Limites desta versão (de propósito)

Esta é a versão 1, pensada para uma aula. Ela **não tem login**: qualquer pessoa com a URL pode salvar, o autor é só um apelido, e qualquer um pode se dizer editor-chefe e aprovar. Esse é o **requisito escondido** discutido em `docs/01-requisitos.md`, e o ponto de partida do desafio v2. Como uma lacuna dessas é observada, registrada e vira a próxima versão está em `docs/09-evolucao-pos-release.md`.

- O mural é público e projetado: **ninguém deve salvar dados pessoais**.
- Textos têm até 4.000 caracteres; até 12 looks por pedido; a função tem no máximo 5 instâncias, o que limita abuso e custo.
- "Ocultar" no mural esconde o cartão daquela tela (moderação da projeção); o dado continua no banco.
- Se você publicou, apague as coleções do Firestore no console ou desative a função quando não precisar mais dela.

## Desafios: o projeto é de vocês

Faça um **fork** deste repositório e escolha um desafio. **Façam a análise antes, e me mostrem.**

| Versão | Desafio |
|---|---|
| **v2** | **Login por pessoa.** Cada um com a própria conta, e só o editor-chefe aprova. O Claude aceita conectores com OAuth. |
| **v3** | **Versões de cada prompt (H06).** Criar uma versão nova sem apagar a anterior, para comparar as coleções (diagrama em `docs/03-classes.md`). |
| **v4** | **Plugin para o Claude Code.** O mesmo gerenciador como comando `/salvar-prompt`, gravando os `.prompt` direto no repositório. |

## Licença

MIT. O mural inclui `qrcode-generator` 1.4.4 (MIT, Kazuhiko Arase).
