# Authenticate Inbound Connections from GCP Agents Using Three-Legged OAuth with Google Auth Manager

This cookbook explains how to integrate agents hosted on the GCP Agent Platform or Gemini Enterprise with an SAP landscape through SAP Agent Gateway.

## Overview

Connecting an agent deployed on Google's Agent Platform and integrated with Gemini Enterprise to an agent hosted on SAP Business AI Platform requires an additional component. Gemini Enterprise cannot currently connect directly to an SAP agent through SAP Agent Gateway because it does not support cross-provider A2A authentication with an in-product sign-in prompt.

To enable the three-legged OAuth flow, deploy a proxy agent to Google's Agent Runtime. The proxy initiates the authentication flow, allowing Gemini Enterprise to display a sign-in prompt in its chat UI and authenticate the user with SAP IAS.

The result is GCP-Agent-Generic, a transparent proxy agent that sits between Gemini Enterprise and a downstream A2A agent. It runs on Google Agent Runtime (Vertex AI Agent Engine), is deployed with `agents-cli`, and performs one task: it exchanges the end-user token forwarded by Gemini Enterprise at SAP IAS for a downstream-scoped token, then relays the call to the downstream agent over A2A. The resulting architecture is shown below.

![](./images/gcp-agw-flow.png)

## Prerequisites

Before you begin, assign the Agent Gateway consumer system to formations. Follow the guidance in the following SAP Help Portal document:

https://help.sap.com/docs/CROSS_DOMAIN_AGENTS/85abb1b3c5734138826f02d079b04975/a0465991ba964736a781c275ddd852db.html?state=DRAFT&ai=true#loioc1e0e4ef9ce145eea314bbb9e9f61514

- SAP BTP Subaccount
  - SAP for Me
  - SAP Business AI Platform
  - SAP Cloud Identity Services
- GCP Project
  - [Google Cloud CLI](https://docs.cloud.google.com/sdk/docs/install-sdk)
  - APIs enabled
  - Gemini Enterprise license
  - A user with the following roles:
    - Agent Identity Admin
    - Agent Identity Editor
    - Agent Identity User
    - Vertex AI User / Agent Platform User
    - Service Usage Consumer

## Recipe

All commands are given for Windows PowerShell.

### 1. Create a Google Cloud Service Account

Confirm that you have completed all prerequisites before continuing.

Sign in using the Google Cloud CLI.

```
gcloud auth login
```

```
gcloud auth application-default login
```

Enable the IAM Service Account Credentials API. For reference, see the [IAM Credentials API documentation](https://docs.cloud.google.com/iam/docs/reference/credentials/rest).

```
gcloud services enable iamcredentials.googleapis.com --project <your-project-id>
```

Create a Google Cloud service account. You can change the `sap-ias-signer` account ID and display name as needed.
```
gcloud iam service-accounts create sap-ias-signer --project <your-project-id> `
  --display-name "SAP IAS client-assertion signer"
```

Verify that the service account creation was successful.

```
gcloud iam service-accounts create sap-ias-signer --project <your-project-id> `
  --display-name "SAP IAS client-assertion signer"

# Expected Output:
# DISPLAY NAME                                         EMAIL                                                               DISABLED
# SAP IAS client-assertion signer                      sap-ias-signer@<your-project-id>.iam.gserviceaccount.com             False
```

This command creates only the identity. It does not yet grant roles, create or download keys, or configure the account to sign IAS client assertions.

The resulting principal is `sap-ias-signer@<your-project-id>.iam.gserviceaccount.com`. Use it later to configure the GCP-Agent-Generic `RUNTIME_SA_EMAIL`.

### 2. Configure the SAP IAS Application

Add the following redirect URIs under `Applications & Resources` &rarr; `<your-application>` &rarr; `OpenID Connect Configuration` &rarr; `Redirect` &rarr; `Add`:

- `https://vertexaisearch.cloud.google.com/oauth-redirect`
- `https://vertexaisearch.cloud.google.com/static/oauth/oauth.html`

Create credentials under `Applications & Resources` &rarr; `<your-application>` &rarr; `Client Authentication` &rarr; `Secrets` &rarr; `Add`.

Add a description and select `Application` and `OpenID` and click `Save`.

**Note down the shown credentials!**

Add the previously configured service account under `Applications & Resources` &rarr; `<your-application>` &rarr; `Client Authentication` &rarr; `JSON Web Tokens` &rarr; `Configure Trust by Issuer` &rarr; `Add`.

Complete the fields as follows:

| Variable | Value |
|-|-|
| `Description` | Enter a description. |
| `Issuer Configuration` | Manual Configuration |
| `Issuer` | `https://www.googleapis.com/service_accounts/v1/jwk/<RUNTIME_SA_URI>` |
| `JSON Web Key Set URI` | `https://www.googleapis.com/service_accounts/v1/jwk/<RUNTIME_SA_URI>` |
| `Refresh Interval` | 24 hours |
| `Corporate Identity Provider - Name` | **Leave blank!** |
| `Subject` | Client ID from the credentials created previously. |
| `Audience` | The SAP IAS tenant base URL, e.g. `https://<tenant>.accounts400.ondemand.com` |
| `API Permission Groups` | **Leave blank!**

Save the configuration.

### 3. Configure and Deploy GCP-Agent-Generic

Copy the `.env` template:
```PowerShell
cp env.example .env
```

Set the following variables:


| Variable | Required | Value |
|---|---|---|
| `MODEL` | No | For example, `gemini-3.8-flash`. |
| `AGENT_NAME` | Yes | For example, `gcp_agent_generic`, you also need to adjust this in the `agents-cli-manifest.yaml`! |
| `DOWNSTREAM_AGENT_URL` | Yes | The downstream A2A JSON-RPC endpoint or the Agent Gateway A2A URL. |
| `OAUTH_CLIENT_ID` | Yes | The `client_id` of the **SAP IAS application** created in step 2. |
| `OAUTH_TOKEN_HOST` | Yes | The SAP IAS tenant base URL, for example `https://<tenant>.accounts400.ondemand.com`. |
| `TOKEN_EXCHANGE_RESOURCE` | Yes | The resource or audience that identifies the downstream service to IAS, for example `urn:sap:identity:application:provider:name:agent-gateway`. |
| `RUNTIME_SA_EMAIL` | Yes | The email of the GCP service account created in step 1 that signs the client assertion, for example `<sa>@<project>.iam.gserviceaccount.com`. |
| `GE_AUTH_ID` | No | Set this only when more than one Gemini Enterprise authorization is registered on the agent; it selects the forwarded token to read. |

Open the GCP-Agent-Generic
```
cd ./<path-on-your-machine>/gcp-agent-generic/
```

Install `uv`:
```
pip install uv
```

Install the Google Agents CLI:
```
uv tool install google-agents-cli
```

Deploy the agent:
```
uv sync                          # generates uv.lock (Docker build needs it)
agents-cli deploy                # pass .env to the runtime; do NOT set a client secret
```

### 4. Add Policy Binding to Google Cloud Platform Service Account

Open the deployed agent in the Agent Registry and look out for the identity service account. Copy the service account mail, it should look like the following.

`<service-account>@gcp-sa-aiplatform-re.iam.gserviceaccount.com`

Grant the service account permission to create credentials.

```
gcloud iam service-accounts add-iam-policy-binding `
  sap-ias-signer@<your-project-id>.iam.gserviceaccount.com `
  --member "<service-account>@gcp-sa-aiplatform-re.iam.gserviceaccount.com" `
  --role roles/iam.serviceAccountTokenCreator `
  --project <your-project-id>
```

Verify the policy binding.

```
gcloud iam service-accounts get-iam-policy `
  sap-ias-signer@<your-project-id>.iam.gserviceaccount.com `
  --project <your-project-id> `
  --format="table(bindings.role, bindings.members)"

# Expected Output
# ROLE                                      MEMBERS
# ['roles/iam.serviceAccountTokenCreator']  [['serviceAccount:sap-ias-signer@<your-project-id>.iam.gserviceaccount.com']]
```

*Optional: Add yourself as a member for local testing.*

```
gcloud iam service-accounts add-iam-policy-binding `
  sap-ias-signer@<your-project-id>.iam.gserviceaccount.com `
  --member "user:<your-email>" `
  --role roles/iam.serviceAccountTokenCreator `
  --project <your-project-id>
```

### 5. Integrate GCP-Agent-Generic with Gemini Enterprise

Open the Agent Registry in Google Cloud Console, find the deployed GCP-Agent-Generic, and open it. Under **Protocols**, note the relevant portion of the URI in the following format:

`projects/<project-number>/locations/<region>/reasoningEngines/<engine-number>`

Open Gemini Enterprise in Google Cloud Console and create an app. Once it has been created, open the app.

Add the deployed agent to Gemini Enterprise.

Select `Agents` &rarr; `Add agent` &rarr; `Custom agent via Agent Runtime` &rarr; `Add`.

Select `Add authorization` and enter the following values:

| Variable | Value |
|-|-|
| `Authorization name` | Enter a name of your choice. |
| `Client ID` | The `client_id` of the **SAP IAS application** created in step 2. |
| `Client secret` | The `client_secret` of the **SAP IAS application** created in step 2. |
| `Token URI` | `https://<tenant>.accounts400.ondemand.com/oauth2/token` |
| `Authorization URI` | `https://<tenant>.accounts400.ondemand.com/oauth2/authorize?response_type=code&scope=openid`
| `PKCE verification enabled` | unchecked |
| `Use HTTP Basic authentication` | unchecked |

Select `Next` and enter the following values:

| Variable | Value |
|-|-|
| `Agent name` | Enter a name of your choice. |
| `Agent description` | Enter a description, for example: "Proxy agent that forwards requests to an SAP agent through SAP Agent Gateway." |
| `Agent Runtime reasoning engine` | Paste the URI noted at the beginning of this step, for example `projects/<project-number>/locations/<region>/reasoningEngines/<engine-number>`. |

Select `Create`.

### 6. Validate the Integration
