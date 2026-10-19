# Getting Started - Explore Landscapes

In this exercise, you take the role of a **landscape explorer**. Before touching any configuration, you familiarize yourself with the two landscapes used throughout this session — the SAP-managed environment (BAIP) and Google Cloud — and the story that connects them. Understanding these environments is the foundation for all subsequent exercises.

## Overview

After completing these steps you will have:
- An overview of the SAP-managed landscape and its key components (SAP's Agent Gateway, SAP Cloud Identity Services, and the already-deployed custom Joule agent)
- An overview of the Google Cloud landscape (Gemini Enterprise, Agent Platform)
- Understood the end-to-end architecture: how a Gemini agent will eventually call through SAP's Agent Gateway to a custom Joule agent

## Step 1 - Explore the Architecture

Before diving into the hands-on steps, familiarize yourself with the reference architectures that describe what you will work with today.

1. Open the **SAP Architecture Center** at [architecture.learning.sap.com](https://architecture.learning.sap.com).

2. Search for and explore the following two reference architectures:
   - **AI Agents & Business AI Platform** — the foundational architecture for SAP's agent ecosystem
   - **Integrating AI Agents into the Google Ecosystem** — describes how external agents (like Gemini) connect to SAP agents through the Agent Gateway

3. As you read, look for the components you will encounter in the exercises ahead: SAP's Agent Gateway and SAP Cloud Identity Services.

<details>
<summary>Solution — reference architecture links</summary>

- [AI Agents & Business AI Platform](https://architecture.learning.sap.com/docs/ref-arch/98efa0)
- [Integrating AI Agents into the Google Ecosystem](https://architecture.learning.sap.com/docs/ref-arch/fe0d1d)

</details>

## Summary

You now have a clear picture of the end-to-end architecture and the key components you will work with.

Continue to - [Exercise 2 - Call the Custom Agent via SAP's Agent Gateway](../ex2/README.md)
