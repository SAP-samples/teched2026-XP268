# gcp-agent-bridge

A minimal, reusable **Gemini Enterprise → A2A proxy agent** for Google Cloud.

It is a transparent proxy: Gemini Enterprise runs the end user's OAuth consent,
forwards the resulting user token to this agent, and the agent exchanges that
token (RFC 7523 **jwt-bearer** principal propagation) for one scoped to a
**downstream A2A agent**, which it then calls on the user's behalf. Client
authentication to the IdP uses an **RFC 7523 §2.2 client assertion signed by a
GCP service account** — no client secret ever lives in the runtime.

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
                     (3) mint SA-signed client assertion (jwt_bearer.py)
                                                                      │
                     (4) POST <OAUTH_TOKEN_HOST>/oauth2/token         │
                         grant_type=jwt-bearer                        ▼
                         assertion=<forwarded user token>          IdP  ──► downstream-scoped token
                         client_assertion=<SA-signed JWT>             │
                                                                      ▼
                     (5) POST <DOWNSTREAM_AGENT_URL>  (A2A message/send, Bearer token)
                                                                      │
                                                                      ▼
                                                              downstream agent reply
```

The SA signs **only** the client assertion (proves *which app* is calling). The
*user* identity is the forwarded token, used verbatim — the process can never
choose an arbitrary `sub` for a user.

---

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/) and the Google Agents CLI:
  `uv tool install google-agents-cli`
- `gcloud` CLI, authenticated: `gcloud auth login` and
  `gcloud auth application-default login`
- A GCP project with the Vertex AI / Agent Engine APIs enabled
- A **GCP service account** that will sign client assertions
- An **IdP application** (the downstream's identity provider) where you can add
  a JWT trust configuration and obtain a `client_id`
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
| `OAUTH_CLIENT_ID` | **yes** | `client_id` of your IdP application. Used as the `sub` of the client assertion and as `client_id` in the exchange. |
| `OAUTH_TOKEN_HOST` | **yes** | IdP base URL. Token endpoint is `<host>/oauth2/token`; also the `aud` of the client assertion. |
| `TOKEN_EXCHANGE_RESOURCE` | **yes** | Resource / audience the exchanged token should be scoped to (identifies the downstream to the IdP). |
| `RUNTIME_SA_EMAIL` | **yes** | Email of the GCP service account whose key signs the client assertion. |
| `GE_AUTH_ID` | no | Gemini Enterprise authorization id keying the forwarded token in session state. Only needed when more than one authorization is registered. |

> If your IdP's token endpoint path is not `/oauth2/token`, change `_TOKEN_PATH`
> in [`app/agent.py`](app/agent.py).

---

## GCP IAM setup — `signJwt`

The runtime signs client assertions with Google's `signJwt` API, which requires
`roles/iam.serviceAccountTokenCreator` **on the signing SA itself**.

**For local testing** — grant it to *your* user account (the ADC identity):

```bash
gcloud iam service-accounts add-iam-policy-binding \
  <YOUR_SA>@<YOUR_PROJECT>.iam.gserviceaccount.com \
  --member="user:<you>@example.com" \
  --role="roles/iam.serviceAccountTokenCreator" \
  --project=<YOUR_PROJECT>
```

**For deployment** — the agent runs *as* the SA, so the SA needs the role on
itself:

```bash
gcloud iam service-accounts add-iam-policy-binding \
  <YOUR_SA>@<YOUR_PROJECT>.iam.gserviceaccount.com \
  --member="serviceAccount:<YOUR_SA>@<YOUR_PROJECT>.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountTokenCreator" \
  --project=<YOUR_PROJECT>
```

Both bindings are additive — add both so the agent works locally and deployed.

---

## IdP JWT trust registration

The IdP must trust assertions signed by your SA. In your IdP's application,
add a **JSON Web Token / JWT trust** entry with:

| Field | Value |
|---|---|
| **Issuer** | `https://www.googleapis.com/service_accounts/v1/jwk/<YOUR_SA_EMAIL>` |
| **JSON Web Key Set (JWKS) URI** | `https://www.googleapis.com/service_accounts/v1/jwk/<YOUR_SA_EMAIL>` |
| **Subject** | your `OAUTH_CLIENT_ID` |
| **Audience** | your `OAUTH_TOKEN_HOST` |

**Issuer must equal the JWKS URI** because the minter sets the assertion's `iss`
to the SA's per-SA JWKS URL (see `_derive_issuer` in
[`app/jwt_bearer.py`](app/jwt_bearer.py)), and the IdP matches `iss` literally.
To use a different `iss`, pass `issuer_url=` when constructing
`JwtBearerAssertionMinter`.

> On **SAP IAS/SCI** the path is: Applications & Resources → Applications →
> *your app* → Trust → **JSON Web Tokens** → Add. Use *Manual Configuration* and
> set Issuer, JWKS URI, Subject and Audience as above.

---

## Local development

Install dependencies (this also generates `uv.lock`, which the Docker build
needs):

```bash
uv sync
```

Smoke-test that assertion signing works end to end (after the local IAM binding
above):

```bash
uv run python - <<'PY'
from app.jwt_bearer import JwtBearerAssertionMinter
m = JwtBearerAssertionMinter(
    client_id="<OAUTH_CLIENT_ID>",
    audience="<OAUTH_TOKEN_HOST>",
    sa_email="<RUNTIME_SA_EMAIL>",
)
print(m.mint_client_assertion())  # prints a signed JWT
PY
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
`agents-cli deploy` configuration. **Do not** set a client secret — this agent
authenticates with the SA-signed client assertion only.

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
│   ├── jwt_bearer.py            # SA-signed RFC 7523 client assertion minter
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
