import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { paraDotprompt, nomeDoArquivo } from "./dotprompt.js";
import { LIMITES, normalizarCategoria, type Prompt } from "./modelo.js";
import type { RepositorioDePrompts } from "./repositorio.js";

const INSTRUCOES = `Gerenciador de Prompts da turma de Análise de Sistemas.
Use salvar_prompt quando a pessoa pedir para salvar, guardar ou registrar um prompt.
Se ela não disser a categoria, chame listar_categorias e sugira uma existente antes de criar outra.
Se ela não disser um título, proponha um curto (até 8 palavras) a partir do texto.
Tudo o que é salvo aparece num mural público projetado em sala: nunca salve dados pessoais
(nome completo, telefone, e-mail, documentos). Se o texto contiver algo assim, avise e peça para remover.`;

function texto(t: string) {
  return { content: [{ type: "text" as const, text: t }] };
}

function erro(t: string) {
  return { content: [{ type: "text" as const, text: t }], isError: true };
}

function resumo(p: Prompt): string {
  const trecho = p.texto.length > 160 ? `${p.texto.slice(0, 160)}…` : p.texto;
  return `• [${p.id}] ${p.titulo} (${p.categoria}, por ${p.autor})\n  ${trecho.replace(/\s+/g, " ")}`;
}

/** Cria o servidor MCP com as quatro ferramentas dos casos de uso (docs/02-casos-de-uso.md). */
export function criarServidorMcp(repo: RepositorioDePrompts): McpServer {
  const servidor = new McpServer(
    { name: "gerenciador-de-prompts", version: "1.0.0" },
    { instructions: INSTRUCOES },
  );

  // RF01: salvar prompt
  servidor.registerTool(
    "salvar_prompt",
    {
      title: "Salvar prompt",
      description:
        "Salva um prompt no gerenciador da turma, numa categoria. O prompt aparece no mural ao vivo. Não salve dados pessoais.",
      inputSchema: {
        titulo: z.string().min(1).max(LIMITES.titulo).describe("Título curto que descreve o prompt"),
        texto: z.string().min(1).max(LIMITES.texto).describe("O texto completo do prompt, exatamente como deve ser usado"),
        categoria: z.string().min(1).max(LIMITES.categoria).describe("Categoria, por exemplo: estudo, codigo, marketing, criatividade"),
        autor: z.string().max(LIMITES.autor).optional().describe("Apelido de quem salvou (opcional; nunca o nome completo)"),
        modelo: z.string().max(80).optional().describe("Modelo para o qual o prompt foi pensado (opcional)"),
        temperatura: z.number().min(0).max(2).optional().describe("Temperatura sugerida, de 0 a 2 (opcional)"),
      },
      annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false, openWorldHint: false },
    },
    async ({ titulo, texto: corpo, categoria, autor, modelo, temperatura }) => {
      const p = await repo.salvar({
        titulo: titulo.trim(),
        texto: corpo,
        categoria: normalizarCategoria(categoria),
        autor: autor?.trim() || "anônimo",
        modelo: modelo?.trim() || undefined,
        temperatura,
      });
      return texto(`Prompt salvo com id ${p.id} na categoria "${p.categoria}". Ele já aparece no mural da turma.`);
    },
  );

  // RF02: listar categorias
  servidor.registerTool(
    "listar_categorias",
    {
      title: "Listar categorias",
      description: "Lista as categorias existentes e quantos prompts há em cada uma.",
      inputSchema: {},
      annotations: { readOnlyHint: true, openWorldHint: false },
    },
    async () => {
      const cats = await repo.categorias();
      if (cats.length === 0) return texto("Ainda não há categorias. O primeiro prompt salvo cria a primeira.");
      return texto(cats.map((c) => `• ${c.nome}: ${c.total}`).join("\n"));
    },
  );

  // RF03: buscar prompts
  servidor.registerTool(
    "buscar_prompts",
    {
      title: "Buscar prompts",
      description: "Busca prompts por palavra-chave e/ou categoria. Devolve id, título, categoria e um trecho.",
      inputSchema: {
        termo: z.string().max(100).optional().describe("Palavra ou trecho a procurar no título e no texto"),
        categoria: z.string().max(LIMITES.categoria).optional().describe("Filtrar por uma categoria"),
        limite: z.number().int().min(1).max(LIMITES.resultadosBusca).optional().describe("Quantos resultados, até 20"),
      },
      annotations: { readOnlyHint: true, openWorldHint: false },
    },
    async ({ termo, categoria, limite }) => {
      const achados = await repo.buscar({
        termo: termo?.trim() || undefined,
        categoria: categoria ? normalizarCategoria(categoria) : undefined,
        limite,
      });
      if (achados.length === 0) return texto("Nenhum prompt encontrado com esses critérios.");
      return texto(`${achados.length} prompt(s):\n${achados.map(resumo).join("\n")}`);
    },
  );

  // RF04: obter prompt no formato Dotprompt
  servidor.registerTool(
    "obter_prompt",
    {
      title: "Obter prompt",
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

  return servidor;
}
