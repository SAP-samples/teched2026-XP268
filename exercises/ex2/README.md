# Exercise 2 - Create a 3rd Party Client via SAP for Me

In this exercise, you will register a third-party client application through SAP for Me and then extend its configuration so that calls originating from Google are correctly identified and trusted by SAP's Agent Gateway.

## Exercise 2.1 - Set Up the Client in SAP for Me

After completing these steps you will have created an OIDC application in SAP for Me and configured user access for it.

1. Open SAP for Me and navigate to **Cloud Identity Services** > **Applications**.
<br>![](/exercises/ex2/images/02_01_0010.png)

2. Create a new OIDC application for your 3rd party client. Set the following:
   - **Application type**: OIDC
   - **Grant types**: Client Credentials (for machine-to-machine A2A calls)

3. Under **User Access**, assign the appropriate users or groups that are allowed to use this client.

4. Note the **Client ID** and **Client Secret** — you will need them in the next exercise.

## Exercise 2.2 - Configure the Client for External (Google) Use

After completing these steps you will have configured the client so that calls coming from Google are recognizable as such — meaning Google-issued tokens are accepted and the caller's Google identity is correctly surfaced to the Agent Gateway.

The key idea: SAP's Agent Gateway needs to know *who* is calling and *from where*. A call from a Gemini agent carries a Google-issued token, not an SAP IAS token. You need to configure a trust relationship so IAS can exchange that Google token for an SAP token, preserving the Google origin in the claims.

1. In the Cloud Identity Service administration console, navigate to **Identity Providers** and open the pre-configured **Google** corporate IdP entry.
<br>![](/exercises/ex2/images/02_02_0010.png)

2. Review the trust configuration: note the issuer URL, the JWKS endpoint, and how user attributes are mapped from Google's token to IAS user attributes.

3. In the **Applications** view, open the OIDC application you created in Exercise 2.1. Navigate to its **Token Exchange** settings and enable token exchange for Google-issued tokens:
   - Set the accepted incoming token type to Google ID token
   - Map the `sub` (subject) claim so the Google identity is preserved in the outgoing SAP token

4. Save the configuration. The client is now configured to accept calls that originate from Google: a Gemini agent presenting a Google ID token can exchange it for an SAP access token, which the Agent Gateway will accept.

5. Open Bruno and import the provided collection from `exercises/ex2/bruno/`. Configure the environment variables:
   - `client_id` and `client_secret` — from Exercise 2.1
   - `token_url` — your IAS tenant token endpoint
   - `agw_endpoint` — your Agent Gateway endpoint from Exercise 1.2

6. Run the **Get Token** request, then **Call Agent via AGW**. Inspect the response and verify your custom agent replied correctly. In the AGW console, confirm that the token claims correctly reflect the Google-originated identity.

## Summary

You've now registered a 3rd party OIDC client in SAP for Me and configured it to accept and correctly identify calls coming from Google via token exchange.

Continue to - [Exercise 3 - Create an Agent on Gemini Enterprise](../ex3/README.md)
