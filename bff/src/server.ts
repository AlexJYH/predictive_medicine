import Fastify from "fastify";

import { getCoreBootstrap } from "./core-client.js";

const app = Fastify({ logger: true, requestIdHeader: "x-request-id" });
const coreApiUrl = process.env.CORE_API_URL ?? "http://api:8000";

app.get("/health", async () => ({ status: "ok", service: "bff" }));

/**
 * UI-facing DTO. Future page routes aggregate Core resources here; Core stays
 * the authority for authorization, classifications, retrieval, and model policy.
 */
app.get("/bff/v1/bootstrap", async (request, reply) => {
  try {
    const core = await getCoreBootstrap(coreApiUrl, request.id);
    return {
      application: { name: "RAG Parse", service: core.service },
      environment: core.environment,
      features: core.capabilities.map((capability) => ({ capability, enabled: false })),
    };
  } catch (error) {
    request.log.warn({ error }, "core_bootstrap_unavailable");
    return reply.code(503).send({ code: "core_unavailable" });
  }
});

const port = Number(process.env.PORT ?? "3000");
await app.listen({ host: "0.0.0.0", port });
