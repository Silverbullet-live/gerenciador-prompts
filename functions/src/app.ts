import express, { type Request, type Response } from "express";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { criarServidorMcp } from "./servidorMcp.js";
import type { Repositorio } from "./repositorio.js";

/**
 * Aplicação HTTP do conector. Usa o transporte Streamable HTTP do MCP em modo
 * "sem estado": cada requisição cria um servidor novo. Isso combina com
 * funções serverless, que não guardam memória entre chamadas (RNF05).
 */
export function criarApp(repo: Repositorio) {
  const app = express();
  app.use(express.json({ limit: "64kb" }));

  const atenderMcp = async (req: Request, res: Response) => {
    const servidor = criarServidorMcp(repo);
    const transporte = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });
    res.on("close", () => {
      transporte.close();
      servidor.close();
    });
    try {
      await servidor.connect(transporte);
      await transporte.handleRequest(req, res, req.body);
    } catch (e) {
      console.error("Erro no MCP:", e);
      if (!res.headersSent) {
        res.status(500).json({ jsonrpc: "2.0", error: { code: -32603, message: "Erro interno" }, id: null });
      }
    }
  };

  const naoPermitido = (_req: Request, res: Response) => {
    res.status(405).json({ jsonrpc: "2.0", error: { code: -32000, message: "Método não permitido" }, id: null });
  };

  // "/" atende a URL direta da função; "/mcp" atende a URL do Hosting (rewrite).
  for (const rota of ["/", "/mcp"]) {
    app.post(rota, atenderMcp);
    app.get(rota, naoPermitido);
    app.delete(rota, naoPermitido);
  }

  return app;
}
