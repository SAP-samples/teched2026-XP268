<p align="center">
  <img src="_assets/aioli-logo.jpg" alt="AIOLI Logo" width="150">
</p>

# AIOLI - Agent InterOperability Lab Initiative

## Mission

Connect agents and let them collaborate -- then test that it actually works.

SAP is heading into a future where AI Agents become a significant part of the enterprise application landscape. The ecosystem around SAP is moving in the same direction: agents from different vendors (Microsoft, Google, AWS, IBM, and others) deployed to different platforms will need to collaborate to jointly solve tasks across domains. Standards like the [A2A protocol](https://github.com/google/A2A) (Agent-to-Agent, now a Linux Foundation (AAIF) project) and [MCP](https://modelcontextprotocol.io) (Model Context Protocol, part of [The Agentic AI Foundation](www.aaif.io)) provide pieces of the puzzle, but they do not define the complete picture.
**Agent interoperability** refers to the capacity of autonomous systems to understand and collaborate with one another,
regardless of their internal designs or origins.

The relevance of multi agent orchestration, collaboration and integrations is expressed also in several publications, like [chapter 4 "Process Layer: Applications and Agents" of the SAP AI-Native North Star Architecture](https://pages.github.tools.sap/OCTO/ai-native-northstar-arch/#process) and the [Agent Interoperability Whitepaper](https://sap.sharepoint.com/sites/209131/Shared%20Documents/Forms/AllItems.aspx?id=%2Fsites%2F209131%2FShared%20Documents%2FWG%20AI%2FWG%5FAI%5FWhitepaper%5FAgent%5FInteroperability%2Epdf&parent=%2Fsites%2F209131%2FShared%20Documents%2FWG%20AI) from the CPA Working Group Artificial Intelligence – Agent Architecture.

Furthermore, with SAPs [Data Access Strategy](https://sap.sharepoint.com/sites/210727/SitePages/Update-on-our-API-Policy.aspx) including the [SAP API Policy](https://help.sap.com/doc/sap-api-policy/latest/en-US/API_Policy_latest.pdf), Agent-to-Agent Integration through A2A is the endorsed AI and Data Access Patterns for the AI layer.

> *"... we orchestrate our agentic layer across of course, think of end to end processes much more so than of functional siloed agentic use cases.
> Now when it comes to the collaboration with third party agents, what we have said at Sapphire very publicly is that we are fully supporting A2A actually without an additional charge.
> So agent to agent communication, so our agents can communicate and interact with third party agents.
> So if you have a process, an end to end process, take order to cash that stands across two or three vendors.
> ... actually our agents can collaborate with other agents and that's something that I think is important for the future so that that you can actually traverse a process and trend and get the maximum."* 
[Sebastian Steinhaeuser, Chief Operating Officer at SAP on Bloomberg Intelligence - Tech Disruptors podcast](https://open.spotify.com/episode/0wzkU39MmlNiP7cPgm3P7V?si=7NstP3aMSrKC7SUJkzZs5w)


**AIOLI provides guidance (external facing on SAP Architecture Center), as well as the infrastructure for testing interoperability between AI agents across SAP and partner/customer ecosystems.** We run concrete interoperability scenarios, surface gaps, and feed findings back to product teams and standards bodies.

## Why This Matters

- **Enterprise is the first real environment for agents** -- consumer-grade patterns don't apply. Authentication, authorization, multi-tenancy, compliance, and auditability are the primary complexity drivers.
- **The protocol is not enough** -- A2A defines how agents talk, but identity federation, trust establishment, capability discovery across catalogues, orchestration, and evaluation are equally critical.
- **Heterogeneous reality** -- customers run SAP alongside agents on Azure, GCP, AWS, and IBM. Interop must be tested across this landscape, not just within SAP.

## Caveat

This goal has a decent level of complexity, needs to cover many different aspects and stakeholders, and has dependencies within and outside of SAP. We try to sketch the full picture -- which might stay incomplete. At the same time, we proceed pragmatically, even with tiny steps, to approach the goal.

Let's go.

## Scope

| In Scope | Out of Scope (for now) |
|---|---|
| Interop test infrastructure | Production-grade agent orchestration |
| A2A protocol compliance validation and feedback to A2A standard body | Defining the A2A standard itself |
| Identity & trust federation testing | Replacing existing SAP agent eval frameworks |
| Cross-Vendor + platform agent connectivity | Building customer-facing products |
| Recommendations & feedback to product teams | |

## Key Technical Pillars

- **Protocol Layer** -- A2A v0.3.0 (REST default + JSON-RPC 2.0; SAP Agent Gateway pinned to 0.3.0, upstream moving toward 1.0) for agent-to-agent communication; MCP for agent-internal tool access (also handled by SAP Agent Gateway as a transparent proxy with SSE streaming)
- **Identity & Trust** -- IAS / SCI configuration, identity provider federation, **agent-as-application IAM model (CPA HYB-004)** with Agent Application + Agent User in SCI, two-stage authorization at Agent Gateway, AMS policy enforcement. See [`docs/research/agent-identity/`](docs/research/agent-identity/) for the deep dive.
- **Orchestration** -- Joule as orchestrator (or dedicated Orchestrator Agent), intelligent skill/agent routing, multi-catalogue discovery
- **Routing** -- SAP Agent Gateway as the endorsed routing component for agent interoperability
- **Evaluation & Testing** -- Repeatable interop test scenarios, agent evaluation (building on [SAP AI Golden Path](https://pages.github.tools.sap/SAP-Business-AI-Architecture/ai-golden-path/build/agents/evaluate/)), regression testing

## Scenarios under investigation

Agent communication scenarios / patterns between SAP and non-SAP agents; e.g. an agent build and deployed on Microsoft Foundry (MS Azure) 

```text
                    Our (owned) landscape

  +------------------------------+         +------------------------------+
  |        MS Environment        |         |             SAP              |
  |                              |         |                              |
  |  +------------------------+  |         |  +-----------+ +----------+  |
  |  | Scenario: MS to FI     |  |         |  | FI Agent  |-| LOB App  |  |
  |  |                        |  |         |  +-----------+ +----------+  |
  |  |                        |  |         |        ^                     |
  |  |  +----------+          |  |         |        |                     |
  |  |  | MS Agent |----------+--+---------+--------+                     |
  |  |  +----------+          |  |         |                              |
  |  +------------------------+  |         |                              |
  +------------------------------+         |                              |
                                           |                              |
  +------------------------------+         |                              |
  |       IBM Environment        |         |                              |
  |                              |         |  +-----------+ +----------+  |
  |  +------------------------+  |         |  | SF Agent  |-| LOB App  |  |
  |  | Scenario: IBM to SF    |  |         |  +-----------+ +----------+  |
  |  |                        |  |         |        ^                     |
  |  |  +-----------+         |  |         |        |                     |
  |  |  | IBM Agent |---------+--+---------+--------+                     |
  |  |  +-----------+         |  |         |                              |
  |  +------------------------+  |         |   SAP side: standard agents, |
  +------------------------------+         |   custom agents, ...         |
                |                          +------------------------------+
                |                                       |
                |                                       |
                +------------------+--------------------+
                                   |
                                   v
                          +-----------------+
                          |  Connectivity   |
                          +-----------------+
                                   |
              +--------------------+--------------------+
              |                    |                    |
              v                    v                    v
       +-------------+      +-------------+      +-------------+
       |  IAM        |      |     A2A     |      |      ?      |
       +-------------+      +-------------+      +-------------+
```

## Deliverables + Task Tracking

Details for connecting (setup and integration) agents on non-SAP platforms to SAP as well as according reference architectures and / or cookbooks alongside a sample implementation:
  - Microsoft Azure (Copilot)
  - Google Cloud Platform
  - Amazon Web Services (aws)

AILOI targets for providing:

- **Environment / System Landscape** (systems, services, integration, ... ) to understand the architectural concepts of agent interoperability, how it is envisioned and handled in the SAP ecosystem

- **Playground / Sandpit** in the AILOI environment (application with UI)- Features:
  - Overview of the running / testable scenarios
  - Onboarding to Playground; meaning partner, customer agents can be onboarded to test and validate the e2e process chain

- **Collaboration and alignment**

  - [Agenter Interop Github Org](https://github.tools.sap/Agent-Interop)
  - [Headless SAP — Gated Access to 3rd Party Agents](https://github.tools.sap/OCTO/ag-gated-access)

- **Feedback**

  - to Engineering teams on feature implementation, process
  - Standardization bodies (like A2A and AAIF)

- **Public (external facing) exposure** (education)

  - [Cookbook / Recipes for agent interoperability with (major) 3rd-party platforms](./agent-interoperability-cookbook/)
  - Reference Architectures for agent interoperability with (major) 3rd-party platforms
  - Sample Implementation for agent interoperability with (major) 3rd-party platforms
  - Educational sessions during major conferences like SAP TechED or ASUG Tech Connect

[Aioli Backlog](https://github.tools.sap/orgs/PAA-SCE-EMEA/projects/18)

Ailoi has already published and contributed to the [SAP Architecture Center](https://architecture.learning.sap.com/) with following Reference Architectures referring to agent interoperability:

- [A2A and MCP for Interoperability](https://architecture.learning.sap.com/docs/ref-arch/ca1d2a3e/1)
- [Integrating AI Agents with Joule - **OUTCOUND**](https://architecture.learning.sap.com/docs/ref-arch/ca1d2a3e/4)
- [Integrating Joule Agents into Your Ecosystem - **INBOUND**](https://architecture.learning.sap.com/docs/ref-arch/ca1d2a3e/5)

> These Reference Architectures are already also referred from [Frequently Asked Questions On SAP API Policy](https://www.sap.com/documents/2026/04/e2a0665e-4c7f-0010-bca6-c68f7e60039b.html)

## Infrastructure (Landscape, Systems, Services, ... )

see for [aioli Landscape setup and access](./system-landscape/README.md)

## Agent Interops Lab Documentation and Research

## Key Standards, References Documentation and further Resources

### Standards and Protocols

- [A2A Protocol](https://github.com/google/A2A) -- Agent-to-Agent communication (Linux Foundation)
- [MCP](https://modelcontextprotocol.io) -- Model Context Protocol (Anthropic)
- [NIST AI Agent Standards Initiative](https://www.nist.gov/caisi/ai-agent-standards-initiative) -- Enterprise agent security & interop standards
[OSPO - AI Standards at SAP  *SAP internal*](https://pages.github.tools.sap/OSPO/agent-standards/)

### **SAP Internal** Resources, Guides and Documentation
- [SAP AI Golden Path - Agent Evaluation](https://pages.github.tools.sap/SAP-Business-AI-Architecture/ai-golden-path/build/agents/evaluate/)
- [SAP Agent Gateway Documentation](https://pages.github.tools.sap/AI/agent-gateway-documentation/)
- [OCTO Eval on SAP Agent Gateway | Gated Access](https://github.tools.sap/OCTO/ag-gated-access/blob/main/execution-brief.md)
- [Headless Joule - An Endorsed Pathway for Third-Party Agentic Access to SAP | Anirban Majumdar](https://github.tools.sap/OCTO/ag-gated-access/blob/main/references/Agent_Gateway_Gated_Access_Proposal-v4.pdf)

### Enablement and Learning

- [DeepLearning.AI - A2A Protocol Course](https://learn.deeplearning.ai/courses/a2a-the-agent2agent-protocol/lesson/vtf72ap4/introduction) |
- [AI Explain Session - A2A & MCP: Agent Interoperability at SAP ](https://video.sap.com/playlist/dedicated/253682133/1_9j8ks2ig/1_bwrx9c1i) |
- [Standardising the Agentic Web: The 5 Core Protocols ](https://video.sap.com/media/t/1_raa246ke) |
- [Demystifying the MCP, A2A, and ACP Protocols to Build Custom Multi-Agent Systems ](https://www.youtube.com/live/ki-4CHTT8O8?si=fY5RNwRiN_ffcEev) |

### Further resources

 - [SIX OrchestratorX Demo](https://six-orchestrator-x.cfapps.us10.hana.ondemand.com/) -- A2A agent orchestration demo + [SIX OrchestratorX Code - Github Repo](https://github.tools.sap/SIX-AI/a2a-orchestration)