/**
 * Teste de ponta a ponta: sobe o servidor com o repositório em memória e conversa com
 * ele como o Claude faria, usando o cliente MCP oficial. Percorre a troca de coleção
 * da Fashion Co. na ordem do Event Storming (docs/03-classes.md):
 * salvar → buscar → reusar trocando os looks → aprovar → entregar.
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
  const chamar = async (name: string, args: Record<string, unknown> = {}) =>
    (await cliente.callTool({ name, arguments: args })) as Resultado;

  const { tools } = await cliente.listTools();
  assert.deepEqual(tools.map((t) => t.name).sort(), [
    "aprovar_prompt",
    "buscar_prompts",
    "entregar_colecao",
    "listar_colecoes",
    "obter_prompt",
    "reusar_prompt",
    "salvar_prompt",
  ]);
  console.log("✓ sete ferramentas publicadas");

  assert.match(textoDe(await chamar("listar_colecoes")), /Ainda não há coleções/);
  console.log("✓ nenhuma coleção no início");

  // H01 · salvar prompt da coleção
  const salvo = textoDe(
    await chamar("salvar_prompt", {
      titulo: "Editorial de praia",
      texto:
        "Foto editorial de moda, luz natural de fim de tarde numa praia. A modelo veste {{look}}. Enquadramento de corpo inteiro, fundo desfocado.",
      colecao: "Verão 2027",
      temporada: "verão",
      ano: 2027,
      autor: "rafa",
      modelo: "imagen-4",
      temperatura: 0.4,
    }),
  );
  const id = salvo.match(/id (\S+)/)?.[1];
  assert.ok(id, "deveria devolver um id");
  assert.match(salvo, /coleção "Verão 2027", como rascunho/);
  console.log("✓ salva na coleção, como rascunho (H01)");

  const semLook = textoDe(
    await chamar("salvar_prompt", {
      titulo: "Fundo de estúdio",
      texto: "Foto de estúdio com fundo cinza e luz difusa, vestido vermelho de seda.",
      colecao: "Verão 2027",
      autor: "lu",
    }),
  );
  const idSemLook = semLook.match(/id (\S+)/)?.[1]!;
  assert.match(semLook, /não tem \{\{look\}\}/);
  console.log("✓ avisa quando o prompt não tem {{look}}");

  await chamar("salvar_prompt", { titulo: "Lookbook de inverno", texto: "Lookbook na neve com {{look}}.", colecao: "Inverno 2027" });

  assert.match(textoDe(await chamar("listar_colecoes")), /Verão 2027 \(verão 2027\): 2 prompt\(s\) · sem prompt aprovado/);
  console.log("✓ lista coleções com contagem");

  // H02 · buscar por coleção
  const busca = textoDe(await chamar("buscar_prompts", { colecao: "verão 2027" }));
  assert.match(busca, /Editorial de praia/);
  assert.match(busca, /Fundo de estúdio/);
  assert.doesNotMatch(busca, /Lookbook de inverno/);
  console.log("✓ busca por coleção (H02)");

  // H03 · reusar trocando os looks
  const reuso = await chamar("reusar_prompt", {
    id,
    looks: [
      { peca: "vestido midi", corETecido: "verde-oliva, linho" },
      { peca: "conjunto de alfaiataria", corETecido: "areia, crepe" },
    ],
  });
  assert.equal(reuso.isError, undefined);
  assert.match(textoDe(reuso), /A modelo veste vestido midi, verde-oliva, linho\./);
  assert.match(textoDe(reuso), /A modelo veste conjunto de alfaiataria, areia, crepe\./);
  assert.match(textoDe(reuso), /ainda é rascunho/);
  console.log("✓ reusa trocando os looks (H03)");

  const reusoSemLook = await chamar("reusar_prompt", { id: idSemLook, looks: [{ peca: "saia" }] });
  assert.equal(reusoSemLook.isError, true);
  console.log("✓ recusa reusar prompt sem {{look}}");

  // H05 antes de H04: sem aprovado, não há entrega
  const cedo = await chamar("entregar_colecao", { colecao: "Verão 2027", recebidoPor: "eng.joao" });
  assert.equal(cedo.isError, true);
  assert.match(textoDe(cedo), /ainda não tem prompt aprovado/);
  console.log("✓ não entrega coleção sem prompt aprovado");

  // H04 · aprovar prompt padrão (um só por coleção)
  assert.match(textoDe(await chamar("aprovar_prompt", { id: idSemLook, aprovadoPor: "chefe.ana" })), /agora é o prompt aprovado/);
  const troca = textoDe(await chamar("aprovar_prompt", { id, aprovadoPor: "chefe.ana" }));
  assert.match(troca, /"Fundo de estúdio", voltou a rascunho/);
  const aprovados = textoDe(await chamar("buscar_prompts", { colecao: "Verão 2027", somenteAprovados: true }));
  assert.match(aprovados, /^1 prompt\(s\):/);
  assert.match(aprovados, /Editorial de praia .* ★ aprovado/);
  console.log("✓ aprova o padrão e só existe um por coleção (H04)");

  // Publicar a partir de .prompt
  const doc = textoDe(await chamar("obter_prompt", { id }));
  assert.match(doc, /Arquivo sugerido: verao-2027\/editorial_de_praia\.prompt/);
  assert.match(doc, /^---\nmodel: imagen-4\nconfig:\n  temperature: 0\.4\ninput:\n  schema:\n    look: string, a peça com cor e tecido\n/m);
  assert.match(doc, /status: aprovado/);
  assert.match(doc, /\{\{look\}\}/);
  console.log("✓ exporta em Dotprompt, com {{look}} como entrada declarada");

  // H05 · entregar à engenharia
  const entrega = textoDe(await chamar("entregar_colecao", { colecao: "Verão 2027", recebidoPor: "eng.joao" }));
  assert.match(entrega, /Entrega \S+ registrada para eng\.joao/);
  assert.match(entrega, /Looks enviados \(2\):\n• vestido midi \(verde-oliva, linho\)\n• conjunto de alfaiataria \(areia, crepe\)/);
  console.log("✓ entrega o .prompt aprovado e os looks à engenharia (H05)");

  // Erros e limites
  assert.equal((await chamar("obter_prompt", { id: "nao-existe" })).isError, true);
  assert.equal((await chamar("salvar_prompt", { titulo: "x", texto: "a".repeat(5000), colecao: "teste" })).isError, true);
  console.log("✓ erro claro para id inexistente e texto acima de 4.000 caracteres");

  await cliente.close();

  // Modo sem estado: uma conexão nova enxerga os mesmos dados.
  const outro = await conectar();
  const r = (await outro.callTool({ name: "buscar_prompts", arguments: { colecao: "Inverno 2027" } })) as Resultado;
  assert.match(textoDe(r), /Lookbook de inverno/);
  await outro.close();
  console.log("✓ nova conexão vê os dados (servidor sem estado)");

  console.log("\nTodos os testes passaram.");
} finally {
  http.close();
}
