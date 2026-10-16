"""GCP-signed JWT client-assertion minter.

The runtime service account (``RUNTIME_SA_EMAIL``) never holds an IdP-trusted
secret. Instead it authenticates to the IdP's token endpoint with an RFC 7523
§2.2 client assertion:

  - ``mint_client_assertion()`` — ``sub`` = ``client_id`` (the IdP application).
                                  This is a fixed constant the IdP matches
                                  exactly, so it only proves *which app* — it
                                  cannot be used to impersonate a user.

The *user* assertion is NOT minted here — under principal propagation the end
user's forwarded token is used verbatim as the jwt-bearer ``assertion`` (see
``agent.py``). Only the *client* assertion is SA-signed, which keeps the process
from being able to choose an arbitrary ``sub`` for a user.

``signJwt`` requires ``roles/iam.serviceAccountTokenCreator`` on the SA itself;
the IdP trusts the SA's per-SA JWKS URL for client authentication.
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Any

logger = logging.getLogger(__name__)

_ASSERTION_TTL_SECONDS = 300


def _build_default_iam_client() -> Any:
    """Return a googleapiclient IAM Credentials resource (lazy import)."""
    import google.auth
    import google.auth.transport.requests
    from googleapiclient import discovery

    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    credentials.refresh(google.auth.transport.requests.Request())
    return discovery.build("iamcredentials", "v1", credentials=credentials, cache_discovery=False)


class JwtBearerAssertionMinter:
    """Mints JWT assertions signed by Google's signJwt API.

    Args:
        client_id:    IdP application client_id. Used as ``sub`` on the client
                      assertion.
        audience:     ``aud`` claim on the assertion — the IdP issuer / token
                      host URL.
        sa_email:     GCP service account email whose RSA key signs the assertion.
        issuer_url:   Optional override for the ``iss`` claim. When None the
                      per-SA JWKS URL is derived from ``sa_email`` — this must
                      match the Issuer configured in the IdP's JWT trust entry.
        iam_client:   Optional pre-built googleapiclient resource for testing.
    """

    def __init__(
        self,
        client_id: str,
        audience: str,
        sa_email: str,
        issuer_url: str | None = None,
        iam_client: Any | None = None,
    ) -> None:
        self._client_id = client_id
        self._audience = audience
        self._sa_email = sa_email
        self._issuer = issuer_url or self._derive_issuer(sa_email)
        self._iam_client = iam_client  # injected in tests; built lazily in prod

    @staticmethod
    def _derive_issuer(sa_email: str) -> str:
        # IdP trust is configured with the SA's JWKS URL as the issuer.
        return f"https://www.googleapis.com/service_accounts/v1/jwk/{sa_email}"

    def _get_iam_client(self) -> Any:
        if self._iam_client is None:
            self._iam_client = _build_default_iam_client()
        return self._iam_client

    # ── Public API ──────────────────────────────────────────────────────────

    def mint_client_assertion(self) -> str:
        """Mint an RFC 7523 §2.2 client assertion (sub == client_id)."""
        now = int(time.time())
        payload: dict[str, Any] = {
            "iss": self._issuer,
            "sub": self._client_id,
            "aud": self._audience,
            "jti": str(uuid.uuid4()),
            "iat": now,
            "nbf": now,
            "exp": now + _ASSERTION_TTL_SECONDS,
        }
        return self._sign(payload, event="client_assertion")

    # ── Internal ────────────────────────────────────────────────────────────

    def _sign(self, payload: dict[str, Any], *, event: str) -> str:
        logger.debug(
            "jwt_bearer.mint.%s.start",
            event,
            extra={"event": f"jwt_bearer.mint.{event}.start", "aud": self._audience},
        )

        resource_name = f"projects/-/serviceAccounts/{self._sa_email}"
        body = {"payload": json.dumps(payload, separators=(",", ":"))}

        # signJwt over httplib2 can hit a stale/closed socket (Broken pipe) when
        # the connection has been idle. Retry once with a freshly-built IAM client.
        last_err: Exception | None = None
        for attempt in range(2):
            try:
                iam = self._get_iam_client()
                response = (
                    iam.projects()
                    .serviceAccounts()
                    .signJwt(name=resource_name, body=body)
                    .execute()
                )
                break
            except Exception as e:
                last_err = e
                logger.warning(
                    "signJwt attempt %d failed: %s — rebuilding IAM client",
                    attempt + 1,
                    e,
                )
                self._iam_client = None  # force rebuild on next _get_iam_client()
        else:
            raise RuntimeError(f"signJwt failed for {self._sa_email}: {last_err}") from last_err

        signed_jwt: str = response.get("signedJwt") or response.get("signed_jwt", "")
        if not signed_jwt:
            raise RuntimeError(f"signJwt response missing signedJwt field: {response}")

        logger.debug(
            "jwt_bearer.mint.%s.ok",
            event,
            extra={"event": f"jwt_bearer.mint.{event}.ok"},
        )
        return signed_jwt
