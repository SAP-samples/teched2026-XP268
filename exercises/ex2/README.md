# Exercise 2 - Call the Custom Agent via SAP's Agent Gateway

In this exercise you call the already-deployed Joule agent through SAP's Agent Gateway. The setup in SAP for Me and SAP Cloud Identity Services was **completed in advance on your behalf** — you cannot perform it live in the workshop, but you will **read through** what was configured so you understand the trust chain. You then switch to a **developer persona**: you discover the callable agent via Agent Resource Discovery (ARD) and invoke it with the Bruno API client.

The sub-steps:
- **2.1 & 2.2** — *read-through* (admin persona): understand the Agent Gateway Consumer and the SAP Cloud Identity Services OIDC application that were created for you.
- **2.3** — *discover* (developer persona): use ARD to find which agents are callable and read the identifiers you need.
- **2.4** — *call* (developer persona): invoke the agent end-to-end in Bruno.

## Exercise 2.1 - SAP for Me: Creating an Agent Gateway Consumer System

> **Read-through only.** The steps below were already performed in advance for your workshop tenant — you are not expected (and will not have the access) to do them live. Read them to understand how the external agent's identity was established. The full procedure is documented in the official SAP Help tutorial: [Creating an Agent Gateway Consumer System](https://help.sap.com/docs/CROSS_DOMAIN_AGENTS/85abb1b3c5734138826f02d079b04975/f6f218644e704192b3a9b7af0f5794b4.html?ai=true).

An agent gateway consumer system in SAP for Me represents the external agent that is integrated with SAP agents through the agent gateway. It establishes the agent's identity record and is referenced by all subsequent formation assignments.

### Creating the System

1. Log in to **SAP for Me** with your cloud administrator credentials.

2. Navigate to **Portfolio & Products** > **My Product Packages** > **Joule** > **Customer Landscape** > **Systems**.

![](./images//sap4me-1.jpg)

3. Create a new system of type **Agent Gateway Consumer** with the following settings:

   | Field | Value |
   |---|---|
   | **System Type** | Agent Gateway Consumer |
   | **Resource URL** | leave blank |
   | **JWKS Endpoint URL** | leave blank |
   | **Name** | `XP268-{YOUR-NUMBER}-AGW-Consumer` |
   | **Application Identifier** | e.g. `xp268-{your-number}` |

![](./images//sap4me-2.jpg)
![](./images//sap4me-3.jpg)

4. Confirm that the system is created successfully. The system name identifies the third-party agent in all subsequent formations.

![](./images//sap4me-4.jpg)

### Assigning the System to Formations

Three formations must be assigned in order. Each formation produces a configuration that the next depends on — do not create Formation 2 before Formation 1 reaches `READY` state, and do not create Formation 3 before Formation 2 reaches `READY` state.

**Formation 1: Integration with SAP Cloud Identity Services**

![](./images//sap4me-7.jpg)

1. Navigate to the **Formations** tab.
2. Find the formation of type **Integration with SAP Cloud Identity Services** (e.g. `sap-sci<your-formation-id>`). Click **Include Systems**.
3. Select your `XP268-{YOUR-NUMBER}-AGW-Consumer` system and click **Next Step**.
4. Review the selected system and click **Include**.

> **Result:** A single-tenant OIDC application representing your system is created in SAP Cloud Identity Services, establishing the agent's identity.

![](./images//sap4me-8.jpg)
![](./images//sap4me-9.jpg)
![](./images//sap4me-10.jpg)

**Formation 2: Integration with Agent Gateway**

> ⚠️ **Known issue:** Adding the Agent Gateway Consumer system to this formation is currently not working in the workshop environment. You can skip this step — the workaround in Exercise 2.2 compensates for the missing formation dependency.

1. Find the formation of type **Integration with Agent Gateway** (e.g. `sap-agw<your-formation-id>`). Click **Include Systems**.
2. Select your `XP268-{YOUR-NUMBER}-AGW-Consumer` system and click **Next Step**.
3. Review and click **Include**.

> **Result:** The dependency between the agent's identity and the agent gateway is established, enabling your system to call SAP agents through the agent gateway.

![](./images//sap4me-5.jpg)
![](./images//sap4me-6.jpg)
![](./images//sap4me-7.jpg)

**Formation 3: Integration with Agent Gateway Consumer** *(must be created, it does not exist yet)*

1. Click **Create Formation**.
2. Enter a **Formation Name** (e.g. `XP268-{YOUR-NUMBER}-Agent-Integration`), set **Formation Type** to **Integration with Agent Gateway Consumer**, and click **Next Step**.
3. Select the **Agent Gateway** system and click **Next Step**.
4. Select your `XP268-{YOUR-NUMBER}-AGW-Consumer` system (System Type: Agent Gateway Consumer) and click **Next Step**.
5. Select the SAP agents and/or assistants you want your system to be able to invoke. Click **Next Step**.

> **Result:** Formation 3 is created with all three systems included, establishing the allow list of SAP agents your consumer is permitted to invoke.

![](./images//sap4me-11.jpg)
![](./images//sap4me-12.jpg)
![](./images//sap4me-13.jpg)
![](./images//sap4me-14.jpg)

## Exercise 2.2 - SAP Cloud Identity Services: Configure the Agent Gateway Consumer

> **Read-through only.** As with 2.1, this configuration was done in advance. The resulting **Client ID** and **Client Secret** are **provided to you** for the workshop — you will not generate them live. Read through to understand where these credentials come from and how the agent gateway trusts your consumer. Reference documentation: [Configuring Client Credentials-Based Access for Third-Party Agents](https://help.sap.com/docs/CROSS_DOMAIN_AGENTS/4d8be6737cf24797bf753cbcc6e2288f/72cdc81ab3c648268dda8a16ad547453.html?ai=true).

When the Agent Gateway Consumer system was included in the **Integration with SAP Cloud Identity Services** formation, a single-tenant OIDC application named `XP268-{YOUR-NUMBER}-AGW-Consumer` was created in SAP Cloud Identity Services. That application carries the client credentials used to obtain tokens.

1. In SAP Cloud Identity Services, the Agent Gateway Consumer application named `XP268-{YOUR-NUMBER}-AGW-Consumer` is selected. Under **Client Authentication** → **Secrets**, a secret is added.
![](./images//sci-1.png)

2. The secret is added with the API access settings **Application** and **OpenID**.
![](./images//sci-2.png)

3. The **Client ID** and **Client Secret** are captured here. In the workshop these values are **handed to you** — the secret is only shown once at creation time and cannot be retrieved again afterwards.
![](./images//sci-3.png)

4. **Additional step (workaround).** Because the Agent Gateway Consumer system could not be included in the SAP for Me formation **Integration with Agent Gateway** in this environment, a dependency was added directly on the application, outside the official documentation:
   - On the application's **Dependencies**.
   - A new dependency with:
     - Application: **Agent Gateway…**
     - API name: **external**

![](./images//sci-4.png)
![](./images//sci-5.png)

## Exercise 2.3 - Discover the Agent via ARD

You now switch to a **developer persona**. Before you can call an agent, you need to know **which** agents are reachable through the Agent Gateway and **which of them are callable**. SAP's Agent Gateway exposes an **Agent Resource Discovery (ARD)** document for exactly this: a catalogue of the agents behind the gateway, each with its identifier, agent-card URL, and metadata.

You run discovery with the same Bruno collection and the same token you obtained for the test call.

1. Open Bruno and import the provided collection from [`exercises/ex2/bruno/`](./bruno/) (if not already imported). Configure the environment variables:
   - `ias_host` — your SAP Cloud Identity Services tenant URL
   - `client_id` and `client_secret` — the credentials handed to you in Exercise 2.2
   - `username` and `password` — your SAP Cloud Identity Services user credentials
   - `agent_gateway_host` — your Agent Gateway endpoint

2. Run **Fetch User Token**, then **Exchange User Token** (see Exercise 2.4 for what each does). The exchanged token is stored as `agent_gateway_token` and reused by the discovery request.

3. Run the **Fetch ARD Document** request. It sends a GET to `{{agent_gateway_host}}/v1/.well-known/ard.json` with the exchanged token as a Bearer Token and returns the discovery document.

4. Inspect the response. It has the shape:

   ```json
   {
     "specVersion": "1.0",
     "entries": [
       {
         "identifier": "urn:air:sap.com:sap.joule:joule:v1",
         "displayName": "SAP Joule",
         "type": "application/a2a-agent-card+json",
         "url": "https://eu12.access.sapdas.cloud.sap/v1/a2a/sap.joule:agent:joule:v1/ba8c48c3-c204-4786-a193-e5fffc2abb9a/.well-known/agent-card.json",
         "version": "1.0.0",
         "metadata": {
           "ordId": "sap.joule:agent:joule:v1",
           "callable": false
         }
       },
       {
         "identifier": "urn:air:sap.com:sap.agtblgpostg:billing-posting-agent:v1",
         "displayName": "Billing Posting Agent",
         "type": "application/a2a-agent-card+json",
         "url": "https://eu12.access.sapdas.cloud.sap/v1/a2a/<agent-ord>/<agent-tenant>/.well-known/agent-card.json",
         "metadata": {
           "ordId": "...",
           "callable": true
         }
       }
     ]
   }
   ```

5. Find the entry whose `metadata.callable` is `true` — that is the agent you are allowed to invoke. Note that some entries are **not** callable: `SAP Joule` itself has `"callable": false`, while the **Billing Posting Agent** is callable.

6. From the callable entry, read the two identifiers the next sub-step needs and set them in your Bruno environment:
   - `agent_ord` ← the entry's `metadata.ordId`
   - `agent_tenant` ← the tenant segment of the entry's agent-card `url` (the path segment **after** the ORD id in `.../v1/a2a/<agent_ord>/<agent_tenant>/.well-known/...`)

## Exercise 2.4 - Test the Call Chain with Bruno

With `agent_ord` and `agent_tenant` filled in from discovery, you now call the agent end-to-end. After completing these steps you will have successfully called the Joule agent through SAP's Agent Gateway using the Agent Gateway Consumer.

1. Make sure the environment variables from Exercise 2.3 are configured, including `agent_ord` and `agent_tenant` discovered via ARD.

2. Run the **Fetch User Token** request. It sends a `password` grant to `{{ias_host}}/oauth2/token` and returns a JWT access token.
<br>![](./images//bruno-1.png)

3. Run the **Exchange User Token** request. It performs a JWT bearer grant (`urn:ietf:params:oauth:grant-type:jwt-bearer`) using the token from the previous step as the `assertion`, scoped to the Agent Gateway resource, and returns a new JWT token bound to the Agent Gateway.
<br>![](./images//bruno-2.png)

4. Run the **Fetch Agent Card** request. It sends a GET to `{{agent_gateway_host}}/v1/a2a/{{agent_ord}}/{{agent_tenant}}/.well-known/agent-card.json` with the exchanged token as a Bearer Token, and returns the agent's capability descriptor.
<br>![](./images//bruno-3.png)

5. Run the **Invoke Agent** request. It sends an A2A (Agent-to-Agent Protocol) call as a JSON-RPC 2.0 `message/send` to `{{agent_gateway_host}}/v1/a2a/{{agent_ord}}/{{agent_tenant}}/jsonrpc` with a user message — feel free to change the `text` field to something of your own. Inspect the response and verify the agent replied correctly.
<br>![](./images//bruno-4.png)

## Summary

You've now read through the Agent Gateway Consumer setup in SAP for Me and SAP Cloud Identity Services, discovered the callable agent via ARD, and successfully called the Joule agent through SAP's Agent Gateway.

Continue to - [Exercise 3 - Configure Connection from Gemini Enterprise Agent](../ex3/README.md)
