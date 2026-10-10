import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { nomeDoArquivo, paraDotprompt } from "./dotprompt.js";
import { idDaColecao, LIMITES, preencherLook, variaveisDoTexto, type Prompt } from "./modelo.js";
import type { Repositorio } from "./repositorio.js";

const INSTRUCOES = `Gerenciador de Prompts da Fashion Co. (marca fictícia, projeto de aula de Análise de Sistemas).
Os editores de moda guardam aqui os prompts que geram as imagens de cada coleção, para não perdê-los,
não reescrevê-los a cada troca de coleção e manter um padrão de qualidade.

- Salvar: use salvar_prompt quando a pessoa pedir para salvar, guardar ou registrar um prompt. Se ela falar
  em "categoria", trate como coleção. Se não disser a coleção, chame listar_colecoes e sugira uma existente.
  Se não disser um título, proponha um curto (até 8 palavras).
- {{look}}: quando o prompt descreve uma peça específica, sugira trocar a peça por {{look}} antes de salvar.
  Assim o prompt pode ser reusado em toda a coleção (reusar_prompt).
- Aprovar: aprovar_prompt é papel do editor-chefe. Cada coleção tem um único prompt aprovado, o padrão.
- Entregar: entregar_colecao gera o pacote da equipe de engenharia (o .prompt aprovado e os looks).
- Tudo aparece num mural público projetado em sala: nunca salve dados pessoais (nome completo, telefone,
  e-mail, documentos). Se o texto contiver algo assim, avise e peça para remover.`;

function texto(t: string) {
  return { content: [{ type: "text" as const, text: t }] };
}

function erro(t: string) {
  return { content: [{ type: "text" as const, text: t }], isError: true };
}

function resumo(p: Prompt): string {
  const trecho = p.texto.length > 160 ? `${p.texto.slice(0, 160)}…` : p.texto;
  const selo = p.status === "aprovado" ? " ★ aprovado" : "";
  return `• [${p.id}] ${p.titulo} (coleção ${p.colecao}, por ${p.autor})${selo}\n  ${trecho.replace(/\s+/g, " ")}`;
}

const apelido = z.string().min(1).max(LIMITES.apelido);
const nomeDeColecao = z.string().min(1).max(LIMITES.colecao);

/** Cria o servidor MCP com as ferramentas dos casos de uso (docs/02-casos-de-uso.md). */
export function criarServidorMcp(repo: Repositorio): McpServer {
  const servidor = new McpServer(
    { name: "gerenciador-de-prompts-fashion-co", version: "1.0.0" },
    { instructions: INSTRUCOES },
  );

  // H01 · Salvar prompt da coleção
  servidor.registerTool(
    "salvar_prompt",
    {
      title: "Salvar prompt da coleção",
      description:
        "Salva um prompt numa coleção da Fashion Co. O prompt entra como rascunho e aparece no mural. Use {{look}} onde a peça muda. Não salve dados pessoais.",
      inputSchema: {
        titulo: z.string().min(1).max(LIMITES.titulo).describe("Título curto que descreve o prompt"),
        texto: z.string().min(1).max(LIMITES.texto).describe("O texto completo do prompt; use {{look}} no lugar da peça"),
        colecao: nomeDeColecao.describe('Nome da coleção, por exemplo "Verão 2027" (se a pessoa disser categoria, use-a aqui)'),
        autor: apelido.optional().describe("Apelido de quem salvou (opcional; nunca o nome completo)"),
        temporada: z.string().max(40).optional().describe("Temporada da coleção, se for nova (ex.: verão)"),
        ano: z.number().int().min(2000).max(2100).optional().describe("Ano da coleção, se for nova"),
        modelo: z.string().max(80).optional().describe("Modelo de IA para o qual o prompt foi pensado (opcional)"),
        temperatura: z.number().min(0).max(2).optional().describe("Temperatura sugerida, de 0 a 2 (opcional)"),
      },
      annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false, openWorldHint: false },
    },
    async ({ titulo, texto: corpo, colecao, autor, temporada, ano, modelo, temperatura }) => {
      const c = await repo.garantirColecao({ nome: colecao, temporada, ano, editorResponsavel: autor?.trim() });
      const p = await repo.salvarPrompt({
        colecao: c.id,
        titulo: titulo.trim(),
        texto: corpo,
        autor: autor?.trim() || "anônimo",
        modelo: modelo?.trim() || undefined,
        temperatura,
      });
      const dica = variaveisDoTexto(corpo).includes("look")
        ? ""
        : " Dica: ele não tem {{look}}, então ainda não pode ser reusado trocando a peça.";
      return texto(`Prompt salvo com id ${p.id} na coleção "${c.nome}", como rascunho. Já aparece no mural.${dica}`);
    },
  );

  // apoio a H02 · Listar coleções
  servidor.registerTool(
    "listar_colecoes",
    {
      title: "Listar coleções",
      description: "Lista as coleções, quantos prompts cada uma tem e qual é o prompt aprovado (o padrão).",
      inputSchema: {},
      annotations: { readOnlyHint: true, openWorldHint: false },
    },
    async () => {
      const lista = await repo.colecoes();
      if (lista.length === 0) return texto("Ainda não há coleções. O primeiro prompt salvo cria a primeira.");
      return texto(
        lista
          .map((c) => {
            const quando = [c.temporada, c.ano].filter(Boolean).join(" ");
            const padrao = c.aprovado ? ` · aprovado: "${c.aprovado}"` : " · sem prompt aprovado";
            return `• ${c.nome}${quando ? ` (${quando})` : ""}: ${c.totalDePrompts} prompt(s)${padrao}`;
          })
          .join("\n"),
      );
    },
  );

  // H02 · Buscar por coleção
  servidor.registerTool(
    "buscar_prompts",
    {
      title: "Buscar prompts",
      description: "Busca prompts por coleção e/ou palavra-chave. Pode trazer só os aprovados.",
      inputSchema: {
        colecao: nomeDeColecao.optional().describe("Filtrar por uma coleção"),
        termo: z.string().max(100).optional().describe("Palavra ou trecho a procurar no título e no texto"),
        somenteAprovados: z.boolean().optional().describe("true para trazer só o prompt aprovado (o padrão)"),
        limite: z.number().int().min(1).max(LIMITES.resultadosBusca).optional().describe("Quantos resultados, até 20"),
      },
      annotations: { readOnlyHint: true, openWorldHint: false },
    },
    async ({ colecao, termo, somenteAprovados, limite }) => {
      const achados = await repo.buscar({
        colecao: colecao ? idDaColecao(colecao) : undefined,
        termo: termo?.trim() || undefined,
        somenteAprovados,
        limite,
      });
      if (achados.length === 0) return texto("Nenhum prompt encontrado com esses critérios.");
      return texto(`${achados.length} prompt(s):\n${achados.map(resumo).join("\n")}`);
    },
  );

  // H03 · Reusar trocando os looks
  servidor.registerTool(
    "reusar_prompt",
    {
      title: "Reusar trocando os looks",
      description:
        "Gera um prompt por look, trocando o {{look}} do prompt pela peça. Registra os looks da coleção e devolve os textos prontos para a IA de imagem.",
      inputSchema: {
        id: z.string().min(1).max(64).describe("Id do prompt a reusar"),
        looks: z
          .array(
            z.object({
              peca: z.string().min(1).max(LIMITES.peca).describe('A peça, ex.: "vestido midi"'),
              corETecido: z.string().max(LIMITES.peca).optional().describe('Cor e tecido, ex.: "verde-oliva, linho"'),
            }),
          )
          .min(1)
          .max(LIMITES.looksPorPedido)
          .describe("Os looks da coleção, até 12 por pedido"),
      },
      annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false, openWorldHint: false },
    },
    async ({ id, looks }) => {
      const p = await repo.obter(id.trim());
      if (!p) return erro(`Não encontrei um prompt com id "${id}".`);
      if (!variaveisDoTexto(p.texto).includes("look")) {
        return erro(
          `O prompt "${p.titulo}" não tem {{look}}: não há onde trocar a peça. Salve uma versão com {{look}} no lugar da peça.`,
        );
      }
      const criados = await repo.salvarLooks(
        looks.map((l) => ({
          promptId: p.id,
          colecao: p.colecao,
          peca: l.peca.trim(),
          corETecido: l.corETecido?.trim() || undefined,
          textoGerado: preencherLook(p.texto, l.peca.trim(), l.corETecido?.trim()),
        })),
      );
      const aviso = p.status === "aprovado" ? "" : "\n⚠ Este prompt ainda é rascunho: não é o padrão aprovado da coleção.";
      return texto(
        `${criados.length} look(s) gerado(s) a partir de "${p.titulo}":${aviso}\n\n` +
          criados.map((l, i) => `── Look ${i + 1} · ${l.peca}${l.corETecido ? ` (${l.corETecido})` : ""}\n${l.textoGerado}`).join("\n\n"),
      );
    },
  );

  // H04 · Aprovar prompt padrão
  servidor.registerTool(
    "aprovar_prompt",
    {
      title: "Aprovar prompt padrão",
      description:
        "Papel do editor-chefe: aprova o prompt como padrão da coleção. Cada coleção tem um só aprovado; o anterior volta a rascunho.",
      inputSchema: {
        id: z.string().min(1).max(64).describe("Id do prompt a aprovar"),
        aprovadoPor: apelido.describe("Apelido de quem aprova (o editor-chefe)"),
      },
      annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: true, openWorldHint: false },
    },
    async ({ id, aprovadoPor }) => {
      const r = await repo.aprovar(id.trim(), aprovadoPor.trim());
      if (!r) return erro(`Não encontrei um prompt com id "${id}".`);
      const troca = r.anterior ? ` O antigo padrão, "${r.anterior.titulo}", voltou a rascunho.` : "";
      return texto(`"${r.aprovado.titulo}" agora é o prompt aprovado da coleção ${r.aprovado.colecao}, por ${aprovadoPor}.${troca}`);
    },
  );

  // Caso de uso "Publicar a partir de .prompt"
  servidor.registerTool(
    "obter_prompt",
    {
      title: "Obter prompt em .prompt",
      description: "Devolve um prompt completo pelo id, no formato Dotprompt (.prompt) do Firebase Genkit.",
      inputSchema: { id: z.string().min(1).max(64).describe("O id devolvido por salvar_prompt ou buscar_prompts") },
      annotations: { readOnlyHint: true, openWorldHint: false },
    },
    async ({ id }) => {
      const p = await repo.obter(id.trim());
      if (!p) return erro(`Não encontrei um prompt com id "${id}".`);
      return texto(`Arquivo sugerido: ${nomeDoArquivo(p)}\n\n${paraDotprompt(p)}`);
    },
  );

  // H05 · Entregar à engenharia
  servidor.registerTool(
    "entregar_colecao",
    {
      title: "Entregar coleção à engenharia",
      description:
        "Monta a entrega da coleção para a equipe de engenharia: o prompt aprovado em .prompt e ao menos um look gerado a partir dele. Exige um prompt aprovado e looks gerados antes de registrar a entrega.",
      inputSchema: {
        colecao: nomeDeColecao.describe("A coleção a entregar"),
        recebidoPor: apelido.describe("Quem recebe na engenharia"),
      },
      annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false, openWorldHint: false },
    },
    async ({ colecao, recebidoPor }) => {
      const id = idDaColecao(colecao);
      const [aprovado] = await repo.buscar({ colecao: id, somenteAprovados: true, limite: 1 });
      if (!aprovado) {
        return erro(`A coleção "${colecao}" ainda não tem prompt aprovado. O editor-chefe precisa aprovar um antes da entrega.`);
      }
      const looks = await repo.looksDoPrompt(aprovado.id);
      // A entrega representa um pacote efetivamente enviado, então exige ao menos um look.
      if (looks.length === 0) {
        return erro(`A coleção "${colecao}" ainda não tem looks gerados. Use reusar_prompt antes de entregar à engenharia.`);
      }
      const entrega = await repo.registrarEntrega({
        colecao: id,
        promptId: aprovado.id,
        looks: looks.map((l) => l.id),
        recebidoPor: recebidoPor.trim(),
      });
      const listaDeLooks = looks.map((l) => `• ${l.peca}${l.corETecido ? ` (${l.corETecido})` : ""}`).join("\n");
      return texto(
        `Entrega ${entrega.id} registrada para ${entrega.recebidoPor}.\n\n` +
          `Arquivo: ${nomeDoArquivo(aprovado)}\n\n${paraDotprompt(aprovado)}\n` +
          `Looks enviados (${looks.length}):\n${listaDeLooks}`,
      );
    },
  );

  return servidor;
}
