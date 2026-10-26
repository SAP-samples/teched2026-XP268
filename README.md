# XP268 - Govern the Agent Economy: Secure A2A using SAP's Agent Gateway

[![REUSE status](https://api.reuse.software/info/github.com/SAP-samples/teched2026-XP268)](https://api.reuse.software/info/github.com/SAP-samples/teched2026-XP268)

This repository contains the material for the SAP TechEd 2026 session called XP268 - Govern the agent economy: Secure A2A using SAP Agent Gateway.

![](/assets/images/sap-agent-gateway.png)

## Overview

As the agent economy grows, the hard problem shifts from building a single agent to letting agents from different vendors and platforms call each other securely across organizational boundaries. This hands-on session gives you direct experience with cross-provider agent-to-agent (A2A) communication governed by **SAP Agent Gateway** — the component that establishes identity, enforces trust, and controls which agents a caller is allowed to invoke.

Across the exercises you will follow a single A2A call from the outside in, working across two landscapes — Google Cloud with Gemini Enterprise and SAP Business AI Platform. You'll start by exploring the reference architecture that connects agents in the Google ecosystem to SAP agents through the Agent Gateway. As an admin, you'll see how the calling agent is registered as an Agent Gateway Consumer in SAP for Me and SAP Cloud Identity Services so the gateway trusts it. Then, as a developer, you'll discover which agents are reachable and callable through that consumer using Agent Resource Discovery (ARD), and call one end-to-end with the Bruno API client — following the OAuth token exchange into an A2A invocation. Finally, you'll integrate a Gemini Enterprise agent so it can call through SAP's Agent Gateway to a Joule agent over a three-legged OAuth flow, tracing a secure, governed A2A call all the way from Google Gemini to the SAP side.

The end-to-end flow is captured in the reference architecture on the [SAP Architecture Center](https://architecture.learning.sap.com):
![Gemini Enterprise Integration with Joule Agents](https://architecture.learning.sap.com/architecture-e7ec0d75ab0abf64.svg)


## Requirements

### SAP Business AI Platform
- [SAP for Me](https://me.sap.com/)
- Joule Work
    - SAP's Agent Gateway
- SAP Cloud Identity Services

### Google Cloud
- Gemini Enterprise
- Agent Platform

## Exercises

- [Exercise 1 - Getting Started - Explore Landscape](exercises/ex1/)
- [Exercise 2 - Call the Joule Agent via SAP's Agent Gateway](exercises/ex2/)
    - [Exercise 2.1 - SAP for Me: Creating an Agent Gateway Consumer System](exercises/ex2#exercise-21-sap-for-me-creating-an-agent-gateway-consumer-system)
    - [Exercise 2.2 - SAP Cloud Identity Services: Configure the Agent Gateway Consumer](exercises/ex2#exercise-22-sap-cloud-identity-services-configure-the-agent-gateway-consumer)
    - [Exercise 2.3 - Discover the Agent via ARD](exercises/ex2#exercise-23-discover-the-agent-via-ard)
    - [Exercise 2.4 - Invoke the SAP Agent with Bruno](exercises/ex2#exercise-24-invoke-the-sap-agent-with-bruno)
- [Exercise 3 - Configure Connection from Gemini Enterprise](exercises/ex3/)
    - [Exercise 3.1 - Deploy Agent on Google's Agent Platform and Configure Connection to SAP's Agent Gateway](exercises/ex3#exercise-31-deploy-agent-on-googles-agent-platform-and-configure-connection-to-saps-agent-gateway)
    - [Exercise 3.2 - Connect Agent to Gemini Enterprise](exercises/ex3#exercise-32-connect-agent-to-gemini-enterprise)
    - [Exercise 3.3 - Test End-to-End: Gemini Agent to AGW to Joule Agent](exercises/ex3#exercise-33-test-end-to-end-gemini-agent-to-agw-to-custom-agent)


## Learning Objectives

By completing these exercises, you will:

✅ Understand how SAP's Agent Gateway governs cross-provider agent-to-agent (A2A) communication

✅ Read how a calling agent is registered as an Agent Gateway Consumer in SAP for Me and SAP Cloud Identity Services

✅ Discover reachable and callable agents through the Agent Gateway using Agent Resource Discovery (ARD)

✅ Follow the OAuth token exchange and invoke an SAP agent end-to-end with the Bruno API client

✅ Integrate a Gemini Enterprise agent with SAP's Agent Gateway using a three-legged OAuth flow

✅ Trace a secure, governed A2A call from Google Gemini through to a Joule agent on the SAP side

## Contributing
Please read the [CONTRIBUTING.md](./CONTRIBUTING.md) to understand the contribution guidelines.

## Code of Conduct
Please read the [SAP Open Source Code of Conduct](https://github.com/SAP-samples/.github/blob/main/CODE_OF_CONDUCT.md).


## How to obtain support

Support for the content in this repository is available during the actual time of the online session for which this content has been designed. Otherwise, you may request support via the [Issues](../../issues) tab.

## License
Copyright 2026 SAP SE or an SAP affiliate company. Please see our [LICENSE](LICENSE) for copyright and license information. Detailed information including third-party components and their licensing/copyright information is available [via the REUSE tool](https://api.reuse.software/info/github.com/SAP-samples/teched2026-XP268).
