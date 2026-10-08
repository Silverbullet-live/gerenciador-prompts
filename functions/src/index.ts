import { initializeApp } from "firebase-admin/app";
import { onRequest } from "firebase-functions/v2/https";
import { criarApp } from "./app.js";
import { RepositorioFirestore } from "./repositorioFirestore.js";

initializeApp();

/**
 * Função publicada no Firebase. Pelo Hosting, fica em:
 *   https://<seu-projeto>.web.app/mcp
 * É essa URL que se cola em "Adicionar conector personalizado" no claude.ai.
 */
export const mcp = onRequest(
  {
    region: "southamerica-east1",
    cors: false,
    maxInstances: 5,
    concurrency: 40,
    memory: "256MiB",
    timeoutSeconds: 30,
  },
  criarApp(new RepositorioFirestore()),
);
