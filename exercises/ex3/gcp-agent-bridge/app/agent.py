# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Proxy agent: forwards every request to a downstream agent over A2A.

Gemini Enterprise runs the end user's OAuth consent (via the authorization
registered on this agent) and forwards the resulting access token into the
session state. This agent reads that token, exchanges it at the IdP for a token
scoped to the downstream resource (RFC 7523 jwt-bearer principal propagation),
and calls the downstream agent on the user's behalf. It runs no OAuth flow
itself.

Client authentication for the token exchange uses an RFC 7523 §2.2 client
assertion signed by a GCP service account (see jwt_bearer.py) — no client secret
is held by the runtime.

All deployment-specific values are read from the environment. See .env.example
and README.md for what each one is and how to obtain it.
"""

import os
import uuid
from typing import Any

import httpx
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import FunctionTool, ToolContext
from google.genai import types

from app.jwt_bearer import JwtBearerAssertionMinter

# ── Configuration (fill in via .env / deployment env — see README.md) ────────

# Gemini model the proxy agent runs on.
MODEL = os.environ.get("MODEL", "gemini-2.5-flash")

# Name the ADK agent reports on its A2A card and as telemetry gen_ai.agent.name.
# Must be a valid identifier (letters, digits, underscores; not starting with a
# digit). Keep agents-cli-manifest.yaml `root_agent_name:` in sync when you
# override this, or trace queries selecting by name won't find this agent.
AGENT_NAME = os.environ.get("AGENT_NAME", "proxy_agent")

# A2A endpoint of the downstream agent every request is forwarded to.
DOWNSTREAM_AGENT_URL = os.environ.get("DOWNSTREAM_AGENT_URL", "")

# IdP application client_id — used both as the `sub` of the client assertion and
# as `client_id` in the token exchange.
OAUTH_CLIENT_ID = os.environ.get("OAUTH_CLIENT_ID", "")

# IdP base URL. The token endpoint is derived as `<host>/oauth2/token`, and this
# value is also the `aud` of the signed client assertion.
OAUTH_TOKEN_HOST = os.environ.get("OAUTH_TOKEN_HOST", "")

# Resource / audience the exchanged token should be scoped to (the downstream).
TOKEN_EXCHANGE_RESOURCE = os.environ.get("TOKEN_EXCHANGE_RESOURCE", "")

# Email of the GCP service account whose key signs the client assertion.
RUNTIME_SA_EMAIL = os.environ.get("RUNTIME_SA_EMAIL", "")

# Gemini Enterprise authorization id that keys the forwarded user token in
# session state. Only needed when more than one authorization is registered.
GE_AUTH_ID = os.environ.get("GE_AUTH_ID", "")

# Token endpoint path appended to OAUTH_TOKEN_HOST. Change here if your IdP uses
# a different path.
_TOKEN_PATH = "/oauth2/token"

_minter: JwtBearerAssertionMinter | None = None


def _get_minter() -> JwtBearerAssertionMinter:
    global _minter
    if _minter is None:
        _minter = JwtBearerAssertionMinter(
            client_id=OAUTH_CLIENT_ID,
            audience=OAUTH_TOKEN_HOST,
            sa_email=RUNTIME_SA_EMAIL,
        )
    return _minter


def _forwarded_token(tool_context: ToolContext) -> str | None:
    """Return the user token Gemini Enterprise forwarded into session state.

    GE keys each forwarded token by its authorization id. We take the one named
    by GE_AUTH_ID, or — when a single authorization is registered — the only
    token present.
    """
    state = tool_context.session.state or {}
    if GE_AUTH_ID:
        return state.get(GE_AUTH_ID)
    if len(state) == 1:
        return next(iter(state.values()))
    return None


async def _exchange_token(forwarded_token: str) -> str:
    """Exchange the forwarded user token for a downstream-scoped token.

    RFC 7523 jwt-bearer principal propagation: the IdP re-mints the forwarded
    user token with the downstream resource as the audience (``resource``) while
    preserving ``sub``. Client authentication uses a service-account-signed
    client assertion (RFC 7523 §2.2) instead of a client secret; the IdP
    validates it against the SA's JWKS URL configured in the application's JWT
    trust entry.

    Raises ``httpx.HTTPError`` on transport/status failures and ``RuntimeError``
    on an IdP error body or a missing ``access_token``.
    """
    client_assertion = _get_minter().mint_client_assertion()
    payload = {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": forwarded_token,
        "resource": TOKEN_EXCHANGE_RESOURCE,
        "client_id": OAUTH_CLIENT_ID,
        "client_assertion": client_assertion,
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "token_format": "jwt",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{OAUTH_TOKEN_HOST}{_TOKEN_PATH}", data=payload, headers=headers
        )

    try:
        body = resp.json()
    except ValueError:
        body = {}
    if resp.is_error:
        detail = body.get("error_description") or body.get("error") or resp.text
        raise RuntimeError(f"IAS token endpoint returned {resp.status_code}: {detail}")
    if "error" in body:
        raise RuntimeError(body.get("error_description") or body["error"])
    token = body.get("access_token")
    if not token:
        raise RuntimeError("Token response contained no access_token")
    return token


def _extract_text(node: Any) -> str:
    """Collect the text parts from an A2A message/task result."""
    found: list[str] = []

    def walk(n: Any) -> None:
        if isinstance(n, dict):
            if isinstance(n.get("text"), str):
                found.append(n["text"])
            for v in n.values():
                walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)

    walk(node)
    return "\n".join(found)


async def call_downstream_agent(request: str, tool_context: ToolContext) -> str:
    """Forward the user's request to the downstream agent and return its reply.

    Args:
        request: The end user's request, forwarded verbatim to the downstream agent.

    Returns:
        The downstream agent's text response, or a short error description.
    """
    if not DOWNSTREAM_AGENT_URL:
        return "Proxy misconfigured: DOWNSTREAM_AGENT_URL is not set."
    if not OAUTH_TOKEN_HOST:
        return "Proxy misconfigured: OAUTH_TOKEN_HOST is not set."
    if not RUNTIME_SA_EMAIL:
        return "Proxy misconfigured: RUNTIME_SA_EMAIL is not set."

    forwarded_token = _forwarded_token(tool_context)
    if not forwarded_token:
        present = sorted((tool_context.session.state or {}).keys())
        return (
            "No credential was forwarded by Gemini Enterprise. Confirm the agent "
            "is registered with an authorization and consent completed; set "
            "GE_AUTH_ID if several authorizations exist. "
            f"Authorizations in session: {present or 'none'}."
        )
    try:
        token = await _exchange_token(forwarded_token)
    except (httpx.HTTPError, RuntimeError) as e:
        return f"Failed to exchange the forwarded token: {e}"

    payload = {
        "jsonrpc": "2.0",
        "id": uuid.uuid4().hex,
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": request}],
                "messageId": uuid.uuid4().hex,
            }
        },
    }
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(DOWNSTREAM_AGENT_URL, json=payload, headers=headers)
    except httpx.HTTPError as e:
        return f"Failed to reach the downstream agent: {e}"

    if resp.is_error:
        correlation_id = (
            resp.headers.get("x-correlationid")
            or resp.headers.get("x-vcap-request-id")
            or resp.headers.get("x-request-id")
            or "<none>"
        )
        return (
            f"Downstream agent returned {resp.status_code}: "
            f"{resp.text or '<empty body>'} (x-correlationid: {correlation_id})"
        )

    body = resp.json()
    if "error" in body:
        return f"Downstream agent returned an error: {body['error']}"
    return _extract_text(body.get("result")) or "Downstream agent returned no text."


root_agent = Agent(
    # Defaults to "proxy_agent"; override with AGENT_NAME. Keep that in sync with
    # agents-cli-manifest.yaml `root_agent_name:` — agents-cli records the name
    # there and telemetry reports it as gen_ai.agent.name, so a divergence makes
    # anything selecting traces by name stop finding this agent's.
    name=AGENT_NAME,
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are a transparent proxy to a downstream agent. For every user "
        "message, call the call_downstream_agent tool with the user's request "
        "verbatim and relay its response back to the user without adding, "
        "summarizing, or omitting content. Do not answer from your own "
        "knowledge."
    ),
    tools=[FunctionTool(func=call_downstream_agent)],
)

app = App(
    root_agent=root_agent,
    name="app",
)
