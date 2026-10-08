/**
 * Roda o servidor no seu computador, guardando os prompts na memória.
 * Útil para testar sem Firebase:  npm run dev
 */
import { criarApp } from "./app.js";
import { RepositorioEmMemoria } from "./repositorio.js";

const porta = Number(process.env.PORT ?? 8787);
criarApp(new RepositorioEmMemoria()).listen(porta, () => {
  console.log(`Servidor MCP local em http://localhost:${porta}/mcp`);
});
