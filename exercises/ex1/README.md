# Exercise 1 - Create a Custom Agent in Joule Studio

In this exercise, you will create a custom agent using Joule Studio. This agent will serve as the backend target that all subsequent exercises route calls to via SAP's Agent Gateway.

## Exercise 1.1 - Set Up the Agent in Joule Studio

After completing these steps you will have created a new custom agent in Joule Studio with a basic configuration.

1. Open Joule Studio from the Joule Work launchpad.

2. Create a new agent and give it a descriptive name (e.g., `xp268-agent-XX` where `XX` is your participant number).

3. Configure the agent's system prompt and define at least one tool or skill that demonstrates a meaningful capability.

4. Save and activate the agent.

## Exercise 1.2 - Expose the Agent via SAP's Agent Gateway

After completing these steps you will have registered your custom agent with SAP's Agent Gateway (AGW), making it reachable by external clients.

1. Navigate to SAP's Agent Gateway configuration within Joule Work.

2. Register your Joule Studio agent as a backend target in the Agent Gateway. Note the AGW endpoint URL assigned to your agent — you will need it in later exercises.

3. Verify the registration by sending a test request from the AGW console.

## Summary

You've now created a custom agent in Joule Studio and exposed it through SAP's Agent Gateway.

Continue to - [Exercise 2 - Create a 3rd Party Client via SAP for Me](../ex2/README.md)
