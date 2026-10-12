"""Fatia 6: o servidor como aplicação web, para publicar na internet.

Localmente, `servidor.py` sobe o servidor com `servidor.run(...)`. Para publicar, a
hospedagem precisa de um objeto "aplicação" que ela mesma liga, recebendo as requisições.
Este arquivo cria esse objeto:

    uv run uvicorn gerenciador_prompts.app:app --port 8000

Duas escolhas, ambas pela mesma razão da versão anterior (RNF05, sem servidor fixo):
- stateless_http: cada requisição é independente, sem guardar sessão na memória da
  instância. Combina com hospedagens que ligam e desligam instâncias sozinhas.
- json_response: responde em JSON simples, em vez de um fluxo de eventos.
"""

import os

from mcp.server.transport_security import TransportSecuritySettings

from gerenciador_prompts.servidor import servidor


def hosts_permitidos() -> TransportSecuritySettings:
    """Quem pode chamar. Fora do computador local, o endereço público precisa ser aceito.

    HOSTS_PERMITIDOS="meu-app.web.app,meu-servico-xyz.run.app" (separados por vírgula).
    Sem a variável, a proteção fica desligada, o que só é aceitável para testes.
    """
    hosts = [h.strip() for h in os.environ.get("HOSTS_PERMITIDOS", "").split(",") if h.strip()]
    if not hosts:
        return TransportSecuritySettings(enable_dns_rebinding_protection=False)
    return TransportSecuritySettings(allowed_hosts=hosts)


app = servidor.streamable_http_app(
    stateless_http=True,
    json_response=True,
    transport_security=hosts_permitidos(),
)
