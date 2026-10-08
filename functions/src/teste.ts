/**
 * Teste de ponta a ponta: sobe o servidor com o repositório em memória e
 * conversa com ele como o Claude faria, usando o cliente MCP oficial.
 *   npm test
 */
import assert from "node:assert/strict";
import type { AddressInfo } from "node:net";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import { criarApp } from "./app.js";
import { RepositorioEmMemoria } from "./repositorio.js";

type Resultado = { content: { type: string; text: string }[]; isError?: boolean };
const textoDe = (r: unknown) => (r as Resultado).content.map((c) => c.text).join("\n");

const http = criarApp(new RepositorioEmMemoria()).listen(0);
await new Promise((ok) => http.once("listening", ok));
const { port } = http.address() as AddressInfo;

async function conectar() {
  const cliente = new Client({ name: "teste", version: "1.0.0" });
  await cliente.connect(new StreamableHTTPClientTransport(new URL(`http://localhost:${port}/mcp`)));
  return cliente;
}

try {
  const cliente = await conectar();

  const { tools } = await cliente.listTools();
  assert.deepEqual(tools.map((t) => t.name).sort(), ["buscar_prompts", "listar_categorias", "obter_prompt", "salvar_prompt"]);
  console.log("✓ quatro ferramentas publicadas");

  assert.match(textoDe(await cliente.callTool({ name: "listar_categorias", arguments: {} })), /Ainda não há categorias/);
  console.log("✓ lista vazia no início");

  const salvo = textoDe(
    await cliente.callTool({
      name: "salvar_prompt",
      arguments: {
        titulo: "Resumo para revisão",
        texto: "Resuma o texto abaixo em 5 tópicos para eu revisar antes da prova:\n{{texto}}",
        categoria: "Estudo",
        autor: "rafa",
        modelo: "claude-sonnet",
        temperatura: 0.3,
      },
    }),
  );
  const id = salvo.match(/id (\S+)/)?.[1];
  assert.ok(id, "deveria devolver um id");
  assert.match(salvo, /categoria "estudo"/);
  console.log("✓ salva e normaliza a categoria");

  await cliente.callTool({
    name: "salvar_prompt",
    arguments: { titulo: "Revisor de código", texto: "Revise este código Python e aponte bugs.", categoria: "Código" },
  });

  assert.match(textoDe(await cliente.callTool({ name: "listar_categorias", arguments: {} })), /codigo: 1[\s\S]*estudo: 1/);
  console.log("✓ conta por categoria");

  const busca = textoDe(await cliente.callTool({ name: "buscar_prompts", arguments: { termo: "prova" } }));
  assert.match(busca, /Resumo para revisão/);
  assert.doesNotMatch(busca, /Revisor de código/);
  console.log("✓ busca por termo");

  const doc = textoDe(await cliente.callTool({ name: "obter_prompt", arguments: { id } }));
  assert.match(doc, /Arquivo sugerido: estudo\/resumo_para_revisao\.prompt/);
  assert.match(doc, /^---\nmodel: claude-sonnet\nconfig:\n  temperature: 0\.3\n/m);
  assert.match(doc, /\{\{texto\}\}/);
  console.log("✓ exporta em Dotprompt");

  const inexistente = (await cliente.callTool({ name: "obter_prompt", arguments: { id: "nao-existe" } })) as Resultado;
  assert.equal(inexistente.isError, true);
  console.log("✓ erro claro para id inexistente");

  const grande = (await cliente.callTool({
    name: "salvar_prompt",
    arguments: { titulo: "x", texto: "a".repeat(5000), categoria: "teste" },
  })) as Resultado;
  assert.equal(grande.isError, true);
  console.log("✓ recusa texto acima de 4.000 caracteres (RNF04)");

  await cliente.close();

  // Modo sem estado: uma conexão nova enxerga os mesmos dados.
  const outro = await conectar();
  assert.match(textoDe(await outro.callTool({ name: "buscar_prompts", arguments: { categoria: "codigo" } })), /Revisor de código/);
  await outro.close();
  console.log("✓ nova conexão vê os dados (servidor sem estado)");

  console.log("\nTodos os testes passaram.");
} finally {
  http.close();
}
