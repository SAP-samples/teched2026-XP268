# Exercise 3 - Configure Connection from Gemini Enterprise Agent

In this exercise, you will deploy an agent on Google's Agent Platform, configure its connection to SAP's Agent Gateway, connect it to Gemini Enterprise, and then validate the complete cross-cloud A2A call chain end-to-end.

## Exercise 3.1 - Deploy Agent on Google's Agent Platform and Configure Connection to SAP's Agent Gateway

After completing these steps you will have a deployed agent on Google's Agent Platform that is configured to route calls through SAP's Agent Gateway using Google identity for authentication.

1. Open the Google Cloud Console and navigate to **Agent Platform** in your assigned project.
<br>![](/exercises/ex3/images/03_01_0010.png)

2. Open the agent's tool configuration and add a new HTTP tool. Point it to your AGW endpoint from Exercise 1.2.
<br>![](/exercises/ex3/images/03_01_0020.png)

3. Configure authentication for the HTTP tool to use the agent's Google service account token. This is the token that will be exchanged via IAS as configured in Exercise 2.2 — the AGW will receive an SAP access token that carries the Google origin in its claims.

4. Update the agent's instructions so it knows when and how to invoke the SAP backend tool.

5. Deploy the agent on Google's Agent Platform.

## Exercise 3.2 - Connect Agent to Gemini Enterprise

After completing these steps you will have made your deployed agent available in Gemini Enterprise so that users can interact with it.

1. In the Google Cloud Console, navigate to **Gemini Enterprise** settings.
<br>![](/exercises/ex3/images/03_02_0010.png)

2. Register your deployed Agent Platform agent as an available agent in Gemini Enterprise.

3. Verify the agent appears and is selectable in the Gemini Enterprise chat interface.

## Exercise 3.3 - Test End-to-End: Gemini Agent to AGW to Custom Agent

After completing these steps you will have validated the full cross-cloud A2A call chain: a Gemini Enterprise agent calling through SAP's Agent Gateway to your custom Joule agent using token exchange.

1. Open the Gemini Enterprise chat interface and select your agent.
<br>![](/exercises/ex3/images/03_03_0010.png)

2. Send a prompt that requires the agent to invoke the SAP backend (e.g., ask it something only your custom Joule agent can answer).

3. Observe the agent's reasoning and verify it calls the AGW tool. Confirm you receive a valid response from your custom Joule agent.

4. In the AGW console, inspect the incoming call:
   - Verify the token was correctly exchanged from a Google-issued token to an SAP IAS token
   - Confirm the Google identity (service account) is correctly reflected in the token claims

5. Trace the full flow across both landscapes:
   ```
   Gemini Enterprise (Google Cloud)
        → HTTP tool call with Google service account token
        → IAS Token Exchange → SAP access token
        → SAP Agent Gateway (validates token, routes call)
        → Custom Joule Agent (processes request, returns response)
        → Response flows back to Gemini agent
        → Gemini agent presents answer to user
   ```

## Summary

You've now deployed an agent on Google's Agent Platform, connected it to Gemini Enterprise, and validated the fully governed cross-cloud A2A call chain.

This completes the XP268 session. You've built and tested a secure agent-to-agent architecture spanning Google Cloud and SAP's managed landscape, governed end-to-end by SAP's Agent Gateway and Cloud Identity Service.
