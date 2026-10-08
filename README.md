# Gerenciador de Prompts

Um conector para o app do Claude que salva, organiza e busca prompts, com um **mural ao vivo** para projetar em sala.

Projeto-base da aula de **Análise de Sistemas**: antes do código, a análise. Comece pela pasta [`docs/`](docs/).

> Inspirado em Chip Huyen, *Engenharia de IA*, cap. 5 (organizar e versionar prompts). Os prompts são exportados no formato **Dotprompt**, do Firebase Genkit.

## Como funciona

Você conversa com o Claude normalmente. Quando um prompt fica bom, diz:

> "salva esse prompt na categoria estudo, meu apelido é rafa"

O Claude chama a ferramenta `salvar_prompt` do conector, o prompt vai para o Firestore e aparece no mural em segundos.

| Ferramenta | O que faz | Requisito |
|---|---|---|
| `salvar_prompt` | Salva título, texto, categoria, apelido (e, opcionalmente, modelo e temperatura) | RF01 |
| `listar_categorias` | Lista as categorias e quantos prompts há em cada | RF02 |
| `buscar_prompts` | Busca por palavra e/ou categoria | RF03 |
| `obter_prompt` | Devolve o prompt completo em formato `.prompt` | RF04 |

## Estrutura

```
docs/            ← a análise: comece por aqui
  01-requisitos.md          requisitos funcionais e não funcionais
  02-casos-de-uso.md        diagrama de casos de uso
  03-classes.md             diagrama de classes (v1 e desafio v2)
  04-sequencia.md           do celular ao mural, passo a passo
  05-historias-de-usuario.md  backlog e Kanban
  06-wireframe.md           protótipo de baixa fidelidade do mural
functions/       ← servidor MCP (TypeScript, Firebase Cloud Functions)
  src/servidorMcp.ts        as quatro ferramentas
  src/repositorio*.ts       onde os prompts ficam (memória ou Firestore)
  src/dotprompt.ts          exportação para .prompt
  src/teste.ts              teste de ponta a ponta
mural/           ← site do Firebase Hosting
  index.html                mural ao vivo (para o projetor)
  conectar.html             passo a passo para conectar o Claude (é para onde o QR code aponta)
```

## Rodar no seu computador (sem Firebase)

Precisa de Node 22.

```bash
cd functions
npm install
npm test        # sobe o servidor e testa as quatro ferramentas
npm run dev     # servidor local em http://localhost:8787/mcp (dados na memória)
```

Para mexer no servidor local com uma interface, use o MCP Inspector:

```bash
npx @modelcontextprotocol/inspector
# Transport: Streamable HTTP · URL: http://localhost:8787/mcp
```

Abrindo `mural/index.html` direto no navegador, o mural entra em **modo de demonstração**, com exemplos.

## Publicar no Firebase

1. **Plano Blaze.** Cloud Functions exige o plano Blaze (pago por uso). Para uma turma, o uso fica dentro da cota gratuita, mas o projeto precisa estar nesse plano.
2. **Firestore.** No console do Firebase, crie o banco Firestore (região sugerida: `southamerica-east1`).
3. **CLI e projeto:**
   ```bash
   npm install -g firebase-tools
   firebase login
   cp .firebaserc.exemplo .firebaserc   # troque SEU-PROJETO-FIREBASE pelo id do projeto
   cd functions && npm install && cd ..
   firebase deploy
   ```
4. **Endereços** depois do deploy:
   - Mural: `https://SEU-PROJETO.web.app`
   - Conector (MCP): `https://SEU-PROJETO.web.app/mcp`
   - Instruções para a turma: `https://SEU-PROJETO.web.app/conectar.html`

## Conectar o Claude

1. Abra **claude.ai no navegador** (o app de celular não deixa adicionar conectores; depois de adicionado, ele aparece no app).
2. **Configurações → Conectores → Adicionar conector personalizado.**
3. Nome: `Mural de Prompts`. URL: `https://SEU-PROJETO.web.app/mcp`.
4. No app, peça para salvar um prompt.

No plano gratuito do Claude, cada pessoa pode ter um conector personalizado.

## Limites desta versão (de propósito)

Esta é a versão 1, pensada para uma aula. Ela **não tem login**: qualquer pessoa com a URL pode salvar, e o autor é só um apelido. Isso é discutido em `docs/01-requisitos.md` e é o ponto de partida do desafio.

- O mural é público e projetado: **ninguém deve salvar dados pessoais**.
- Textos têm até 4.000 caracteres; a função tem no máximo 5 instâncias, o que limita abuso e custo.
- "Ocultar" no mural esconde o cartão daquela tela (moderação da projeção); o dado continua no banco.
- Depois da aula, apague a coleção `prompts` no console ou desative a função.

## Desafios para depois da aula

1. **Login (H06):** OAuth com GitHub para cada pessoa ter os próprios prompts. O Claude suporta conectores com OAuth.
2. **Versões (H07):** implementar o diagrama de classes v2 de `docs/03-classes.md`.
3. **Exportação (H08):** gerar uma pasta de arquivos `.prompt` prontos para o Genkit.
4. **Plugin para o Claude Code:** o mesmo gerenciador como comando `/salvar-prompt`, gravando os `.prompt` direto no repositório.

## Licença

MIT. O mural inclui `qrcode-generator` 1.4.4 (MIT, Kazuhiko Arase).
