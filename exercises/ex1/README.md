# Exercise 1 - Create a Simple Agent in Joule Studio

In this exercise, you will create a custom agent using Joule Studio's Intent-Based Development (IBD) flow. The agent queries cost center data from SAP S/4HANA and will serve as the backend target that subsequent exercises route calls to via SAP's Agent Gateway.

## Overview

After completing these steps you will have:
- Created a Finance Controller agent using Joule Studio's IBD flow (clarifying questions → intent → PRD → SPEC → code generation)
- Tested the agent in the Joule Studio sandbox
- Deployed the agent to the development environment
- Monitored the agent via Solution Overview

---

## Step 1 - Open Joule Studio and Start the Agent

1. In the left navigation of Joule Work, select **Develop** to open Joule Studio.

2. Select the **Agent** artifact type and make sure **"Quick Create"** is **unselected** and the mode is set to **"Ideate and plan"**.

   ![Joule Studio Pop Up](./images/01_Joule_Studio_pop-up.png)
   ![Joule Studio Pop Up2](./images/01b_Joule_Studio_pop-up2.png)
   ![Ideate and Plan Mode](./images/01c_Switch_to_Plan_Mode.png)

3. Enter the following prompt in the intent statement box:

   ```
   Create an agent for Finance Controllers that enables natural language querying
   of cost center data in SAP S/4HANA Controlling — delivering instant answers
   on total count of cost centers and top 5 cost centers, so that controllers can answer
   department questions without running manual SAP transactions.
   ```

---

## Step 2 - Answer the Clarifying Questions

Joule Studio asks clarifying questions to understand your requirements. Tick the boxes as appropriate.

> **Note:** With "Quick Create" selected, Joule Studio skips most clarifying questions — but it will always ask for basic Business Metrics to correctly prioritize the implementation. Make sure "Quick Create" is **off** for the full IBD experience.

![Clarifying Questions](./images/02_Joule_Studio_clarifying_questions.png)

---

## Step 3 - Review the Intent Analysis

Your planned solution appears on the Idea Board. Joule Studio identifies the intent and creates an `intent.md` file.

Continue to the next step by replying **"yes"**, **"continue"**, or **"Build requirement for this project"** in the Joule chat on the right.

![Intent Analysis](./images/03_Joule_Studio_intent.png)

---

## Step 4 - Review the PRD

Joule Studio generates a detailed **Product Requirements Document (PRD)** covering purpose, value proposition, user personas, functional/non-functional requirements, solution architecture, and risks.

Continue by typing **"Build specification for this project"** or **"continue"**.

![PRD](./images/04_Joule_Studio_PRD.png)

---

## Step 5 - Review the SPEC

Joule Studio translates the PRD into a **technical specification** — the blueprint for the implementation (Python agent structure, data models, testing setup).

Continue by typing **"continue"** or **"build solution"**.

![SPEC](./images/05_Joule_Studio_SPEC.png)
![SPEC](./images/05b_Joule_Studio_SPEC.png)
![SPEC](./images/05c_Joule_Studio_SPEC.png)

---

## Step 6 - Code Generation

Joule Studio generates working code from the SPEC: SAP API connections, business logic, and a complete deployable package following SAP best practices for security, error handling, and observability.

You can adapt the generated code directly in **Code View**, or use **Design View** for low-code changes (MCP, prompt, and LLM settings). Test cases are generated and executed in this step.

![Code Generation](./images/06_Joule_Studio_code.png)
![Adapt](./images/06b_Joule_Studio_Adapt.png)
![Adapt](./images/06c_Joule_Studio_Adapt.png)

---

## Step 7 - Preview and Test

Preview the agent in the sandbox, send test queries, and observe traces. Review the executed test cases in the **Testing** tab.

Type **"deploy"** in the chat to proceed to deployment.

![Preview](./images/07_Joule_Studio_test.png)
![Preview](./images/07b_Joule_Studio_test.png)
![Preview](./images/07c_Joule_Studio_test.png)
![Test Results](./images/07b_Joule_Studio_testing.png)

---

## Step 8 - Deploy to Development

The agent is deployed to the Joule Studio development runtime. After deployment:

- The agent is technically deployed and registered for use by Joule Conversations or system triggers
- The agent is connected to the hard-wired S/4HANA system via formations, UCL, and SPII
- The agent is connected to the Agent Gateway as the single communication hub to external systems
- Deployment logs are visible during the process
- You can download the solution files as a ZIP at any time

![Deploy Button](./images/08_Joule_Studio_deploy.png)
![Deploying](./images/08b_Joule_Studio_deploying.png)
![Deploy Done](./images/08c_Joule_Studio_deploy_ZIP.png)

---

## Step 9 - Grant User Access via SAP Cloud Identity

Grant user access to the deployed agent via **SAP Cloud Identity (SCI)**.

> See your instructor or the Admin Setup guide for details on assigning the required user roles.

---

## Step 10 - Test on Development

Trigger and test the deployed agent directly in Joule, or from the solution overview screen in Joule Studio.

![Runtime Execution](./images/10_Joule_Studio_Run_Agent.png)
![Runtime Execution](./images/10b_Joule_Studio_run.png)

---

## Step 11 - Monitor the Agent

After deployment, monitor the agent via **Solution Overview**. Open the solution list, select your agent, and explore:

- **Tracing** tab: request count, error rate, latency per trace
- **Monitoring** tab: tokens per trace, error rate, extensions used/time

![Solution Overview](./images/09_Joule_Studio_solution_monitoring.png)
![Solution Overview](./images/09b_Joule_Studio_solution_monitoring.png)
![Monitoring Detail](./images/09c_Joule_Studio_solution_monitoring_detail.png)
![Tracing](./images/09b_Joule_Studio_solution_tracing.png)

---

## Summary

You've created and deployed a Finance Controller agent in Joule Studio using the full IBD flow — from clarifying questions through code generation to deployment and monitoring.

Continue to [Exercise 2 - Connect via SAP's Agent Gateway](../ex2/README.md)
