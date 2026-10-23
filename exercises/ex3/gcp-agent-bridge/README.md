# gcp-agent-bridge

A minimal, reusable **Gemini Enterprise → A2A proxy agent** for Google Cloud.

It is a transparent proxy: Gemini Enterprise runs the end user's OAuth consent,
forwards the resulting user token to this agent, and the agent exchanges that
token (RFC 7523 **jwt-bearer** principal propagation) for one scoped to a
**downstream A2A agent**, which it then calls on the user's behalf. Client
authentication to the IdP uses the application's **`client_id` / `client_secret`**
(OAuth 2.0 client credentials in the request body).

This is a genericized template. Every deployment-specific value is an
environment variable with a placeholder in [`env.example`](env.example); fill
them in and deploy.

---

## Request flow

```
end user
   │  (1) OAuth consent, handled by Gemini Enterprise
   ▼
Gemini Enterprise ──(2) forwards user token in session state──► this proxy agent
                                                                      │
                     (3) POST <OAUTH_TOKEN_HOST>/oauth2/token         │
                         grant_type=jwt-bearer                        ▼
                         assertion=<forwarded user token>          IdP  ──► downstream-scoped token
                         client_id / client_secret                    │
                                                                      ▼
                     (4) POST <DOWNSTREAM_AGENT_URL>  (A2A message/send, Bearer token)
                                                                      │
                                                                      ▼
                                                              downstream agent reply
```

Client authentication (`client_id` / `client_secret`) proves *which app* is
calling. The *user* identity is the forwarded token, used verbatim as the
jwt-bearer `assertion` — the process can never choose an arbitrary `sub` for a
user.

---

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/) and the Google Agents CLI:
  `uv tool install google-agents-cli`
- `gcloud` CLI, authenticated: `gcloud auth login` and
  `gcloud auth application-default login`
- A GCP project with the Vertex AI / Agent Engine APIs enabled
- An **IdP application** (the downstream's identity provider) where you can
  obtain a `client_id` and `client_secret`
- The **downstream agent's A2A endpoint** URL and its resource audience

---

## Configuration

All configuration is via environment variables. Copy the template and fill it
in:

```bash
cp env.example .env
```

| Variable | Required | What it is |
|---|---|---|
| `MODEL` | no (default `gemini-2.5-flash`) | Gemini model the proxy runs on. |
| `AGENT_NAME` | no (default `proxy_agent`) | Name on the A2A card and telemetry (`gen_ai.agent.name`). Must be a valid identifier; keep `root_agent_name:` in `agents-cli-manifest.yaml` in sync. |
| `DOWNSTREAM_AGENT_URL` | **yes** | A2A (JSON-RPC) endpoint every request is forwarded to, e.g. `https://host/a2a/my-agent`. |
| `OAUTH_CLIENT_ID` | **yes** | `client_id` of your IdP application. Used as `client_id` in the exchange. |
| `OAUTH_CLIENT_SECRET` | **yes** | `client_secret` of your IdP application. Authenticates the client leg of the exchange. |
| `OAUTH_TOKEN_HOST` | **yes** | IdP base URL. Token endpoint is `<host>/oauth2/token`. |
| `TOKEN_EXCHANGE_RESOURCE` | **yes** | Resource / audience the exchanged token should be scoped to (identifies the downstream to the IdP). |
| `GE_AUTH_ID` | no | Gemini Enterprise authorization id keying the forwarded token in session state. Only needed when more than one authorization is registered. |

> If your IdP's token endpoint path is not `/oauth2/token`, change `_TOKEN_PATH`
> in [`app/agent.py`](app/agent.py).

---

## Local development

Install dependencies (this also generates `uv.lock`, which the Docker build
needs):

```bash
uv sync
```

Run the agent interactively:

```bash
agents-cli playground
```

---

## Deploy

This template ships without Terraform. Generate the infrastructure, then
deploy:

```bash
# One-time: scaffold the single-project Terraform for your GCP project
agents-cli infra single-project

# Deploy (requires uv.lock to exist — run `uv sync` first)
agents-cli deploy
```

Pass the environment from `.env` to the deployed runtime per your
`agents-cli deploy` configuration — including `OAUTH_CLIENT_SECRET`, which the
agent uses to authenticate the client leg of the token exchange.

After deploy, register the agent's A2A card
(`<app-url>/a2a/app/.well-known/agent-card.json`) with Gemini Enterprise and
attach the authorization that produces the forwarded user token.

---

## File layout

```
gcp-agent-bridge/
├── app/
│   ├── __init__.py
│   ├── agent.py                 # proxy agent + token exchange (configure here)
│   ├── fast_api_app.py          # FastAPI app: ADK web + A2A + reasoning_engine
│   └── app_utils/
│       ├── a2a.py               # A2A card + JSON-RPC routes
│       ├── services.py          # shared session/artifact services
│       └── reasoning_engine_adapter.py
├── Dockerfile
├── pyproject.toml
├── agents-cli-manifest.yaml
├── env.example                  # copy to .env and fill in
├── .gcloudignore
├── .gitignore
└── README.md
```
