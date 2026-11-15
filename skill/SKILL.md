---
name: universal-negotiation
description: Run configurable two-party negotiations between countries, companies, buyers, suppliers, or other parties. Supports multi-round negotiations, independent party priorities, structured constraints, proposal evaluation, verified agreements, and local Ollama-powered execution.
summary: Simulate structured negotiations between two parties, evaluate proposals, and identify mutually acceptable agreements.
version: "1.0.0"
tags:
  - negotiation
  - multi-agent
  - trade
  - business
  - decision-making
keywords:
  - bilateral negotiation
  - multi-agent negotiation
  - trade negotiation
  - negotiation strategy
  - counteroffers
  - agreement evaluation
use_cases:
  - Country-to-country trade negotiations
  - Buyer and supplier negotiations
  - Company partnership negotiations
  - Business contract negotiations
  - Strategic decision simulations
---

# Universal Multi-Agent Negotiation Skill

## Purpose

This skill helps users simulate structured negotiations between two parties.

It supports different negotiation scenarios, including:

- Country-to-country negotiations
- Company-to-company negotiations
- Buyer-to-supplier negotiations
- Employer-to-employee negotiations
- Business partnerships
- Other two-party negotiation scenarios

The original USA-China trade negotiation remains an example, not a restriction.

The skill supports two execution modes:

1. **Host-agent execution:** The connected AI agent performs the negotiation workflow using its available reasoning capabilities.
2. **Local engine execution:** The existing Python negotiation engine can be used with a configured local LLM provider such as Ollama.

These are separate execution paths.

Do not claim that the local Python engine was executed when only the host agent performed the simulation.

Do not claim that two separate LLM processes were launched during host-agent execution.

## 1. Understand the user's request

Before starting a negotiation, identify:

- Party A
- Party B
- Negotiation topic
- Issues to negotiate
- Priorities of each party
- Constraints of each party
- Maximum number of negotiation rounds

Ask the user for missing essential information.

Do not assume that all negotiations are international trade negotiations.

If the user provides incomplete information, ask focused questions or clearly identify reasonable assumptions before proceeding.

## 2. Configure the parties

Create a separate profile for each party.

Each profile should contain:

- Party name
- Role
- Negotiation priorities
- Acceptable conditions
- Preferred outcomes
- Non-negotiable constraints
- Negotiation flexibility

Keep party-specific priorities and constraints separate within the negotiation workflow.

Do not intentionally disclose one party's private profile information in the other party's proposals or responses.

Do not invent private priorities or constraints. Treat unknown information as unspecified.

**Confidentiality limitation:** Separate party contexts and prompts are application-level safeguards, not a cryptographic security boundary. They do not guarantee confidentiality against model behavior, provider logging, infrastructure access, or application vulnerabilities. Do not use this simulation to process highly sensitive secrets without appropriate security controls.

## 3. Prepare the negotiation

Before running the negotiation:

1. Validate the supplied party profiles.
2. Identify the shared negotiation issues.
3. Identify constraints that must not be violated.
4. Set the maximum number of rounds.
5. Identify missing information and assumptions.
6. Select the available execution mode.

### Execution mode selection

**Host-agent execution**

- Use the connected host AI agent's reasoning capabilities.
- Simulate the two negotiating party roles independently.
- Follow the negotiation and agreement-verification rules in this skill.
- Do not require Docker, Ollama, or a separate local server.
- Do not pretend that two separate LLM processes were launched.
- Clearly identify the result as a host-agent simulation.

**Local engine execution**

- Use the existing Python negotiation engine when the user explicitly requests it and it is available.
- Preserve the configured LLM provider.
- Use Ollama when the local Ollama provider is selected.
- Respect the configured model, endpoint, and timeout.
- Never claim successful execution if the local engine or provider fails.

Provider and model configuration for the Python engine comes from environment variables, not from the `NegotiationRequest` API body.

## 4. Run negotiation rounds

For each round:

1. Party A generates a proposal based on its own priorities and constraints.
2. Party B evaluates the proposal against its own priorities and constraints.
3. Party B responds with acceptance, rejection, or a counterproposal.
4. Party A evaluates Party B's response.
5. If Party A accepts a counterproposal, Party B must explicitly confirm the same final terms.
6. Continue until a verified agreement is reached or the round limit is reached.

### Response types

- **ACCEPT:** Explicit acceptance of the complete proposal.
- **COUNTEROFFER:** A proposal containing revised terms.
- **REJECT:** Rejection without accepting the proposed terms.

Do not claim an agreement merely because a proposal contains words such as "agree", "accept", or "compromise".

An agreement requires explicit acceptance of the same complete final terms by both parties and satisfaction of applicable hard constraints.

Do not skip negotiation rounds or fabricate responses.

## 5. Evaluate the outcome

Evaluate:

- Whether both parties accepted the final terms.
- Whether hard constraints were respected.
- How well the outcome addresses each party's stated priorities.
- Whether concessions were made.
- Whether unresolved issues remain.
- Whether the negotiation ended because of rejection or the maximum-round limit.

Do not invent acceptance, utility values, economic impacts, or negotiation outcomes.

Only provide numerical scores when the required inputs and a defined evaluation method are available.

### Agreement verification

A verified agreement requires:

1. Explicit acceptance by Party A.
2. Explicit acceptance by Party B.
3. Identical complete final terms accepted by both parties.
4. Complete and unambiguous values for all required issues.
5. No violation of applicable hard constraints.
6. No unresolved mandatory issue.

If any condition is missing, report that no verified agreement was reached.

The local engine records exact accepted terms separately for both parties. Use this evidence when evaluating a local-engine result.

## 6. Return the result

Present:

- Party names
- Negotiation topic
- Execution mode
- Number of rounds
- Proposals and responses
- Negotiation transcript
- Whether an agreement was reached
- Final agreed terms, if any
- Unresolved issues
- Constraint validation results
- Evaluation summary

Clearly label the result as a simulation, not a real-world agreement.

Distinguish between:

- Verified facts
- User-provided information
- Retrieved information
- Assumptions
- Simulated proposals

Do not describe a proposed term as an agreed term unless the agreement-verification requirements have been met.

## 7. Provider behavior

The current Python provider implementation supports local Ollama execution.

Default provider factory configuration:

- Provider: `ollama`
- Default model: `llama3:latest`
- Default endpoint: `http://127.0.0.1:11434`
- Default timeout: `180` seconds

The repository's `.env.example` provides an example configuration and can override these defaults.

For Docker Compose, the Ollama endpoint normally uses:

`http://ollama:11434`

For execution directly on the host machine, use the host-accessible Ollama endpoint.

Only use another Python provider when its integration is implemented, configured, and available.

The current Python provider factory does not implement:

- OpenAI-compatible provider integration
- Python host-agent provider adapter

Do not advertise these as supported Python providers until their integrations are implemented.

### Host-agent provider behavior

When operating through an Agensi-connected host agent:

- Use the host agent's available reasoning capabilities.
- Do not require the user to configure an additional LLM API solely for the skill's host-agent execution.
- Do not claim to have used Ollama unless the local Ollama engine was actually invoked.
- Do not claim that a Python provider adapter was used when the host agent executed the workflow directly.

### Local provider behavior

When using the existing Python engine:

- Respect the configured provider.
- Respect the configured model.
- Preserve the existing provider abstraction.
- Report connection and generation failures honestly.

Never claim that a negotiation was executed if the provider call failed.

## 8. Important rules

- Support different party names and negotiation topics.
- Do not hardcode USA and China into the negotiation workflow.
- Keep party-specific information separate.
- Respect applicable hard constraints.
- Do not fabricate agreement or evaluation results.
- Explain when no agreement is reached.
- Treat all negotiation outputs as simulated proposals.
- Preserve the existing local Ollama implementation.
- Do not require Docker or a local model for host-agent execution.
- Do not create duplicate negotiation engines.
- Do not claim guaranteed confidentiality from prompt separation alone.
- Do not expose private party information in shared reports.

## 9. Optional market-data integration

When a negotiation requires current external information, identify the relevant data.

Examples:

- Commodity prices
- Stock market information
- Cryptocurrency prices
- Industry benchmarks
- Relevant economic indicators

If an appropriate Agensi tool is available:

1. Identify the relevant tool.
2. Explain why the data is needed.
3. Check the applicable tool price.
4. Obtain user approval before making a paid tool call.
5. Retrieve the information through the authorized tool.
6. Record the source and timestamp when available.
7. Use the retrieved information as evidence during negotiation evaluation.

Never invent market prices or claim that external information was retrieved when a tool call did not succeed.

If no suitable tool is available, ask the user to provide the information or continue without it while clearly identifying the limitation.

Market-data integration is optional. Ordinary negotiations must work without external market-data tools.

## 10. Final reliability requirements

The skill must:

- Work with different negotiation topics and party configurations.
- Maintain independent party profiles.
- Support multiple negotiation rounds.
- Evaluate proposals against party-specific constraints.
- Verify explicit acceptance before reporting an agreement.
- Explain unresolved issues.
- Support host-agent execution without mandatory local infrastructure.
- Preserve the existing Python and Ollama execution option.
- Report execution failures honestly.
- Produce structured and understandable negotiation reports.