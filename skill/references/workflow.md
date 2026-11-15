# Universal Negotiation Workflow

## 1. Overview

The Universal Negotiation Skill supports structured negotiations between two parties across business, trade, purchasing, employment, and other negotiation scenarios.

A negotiation consists of:

1. Request preparation
2. Party profile validation
3. Constraint identification
4. Proposal generation
5. Proposal evaluation
6. Counteroffer handling
7. Agreement verification
8. Result reporting

The negotiation is a simulation. It does not create a legally binding agreement between real-world parties.

## 2. Request Preparation

Collect the following information before starting:

- Party A profile
- Party B profile
- Negotiation topic
- Issues to negotiate
- Maximum negotiation rounds

The `NegotiationRequest` model is the authoritative API input schema.

Provider and model configuration are managed separately through environment variables. They are not fields in `NegotiationRequest`.

Do not invent missing priorities, constraints, or acceptable terms.

Ask the user for missing essential information or clearly identify assumptions when proceeding without non-essential details.

## 3. Party Profile Validation

Each party has an independent `PartyProfile`.

A profile contains:

| Field | Purpose |
|---|---|
| `name` | Identifies the negotiating party |
| `role` | Defines the party's role |
| `priorities` | Assigns importance to negotiation issues |
| `constraints` | Human-readable requirements |
| `constraint_rules` | Machine-readable conditions |
| `background` | Additional party context |

Party names must be different.

Keep each party's priorities and background separate in the negotiation workflow.

Do not intentionally disclose one party's private profile information in the other party's proposal or response.

**Confidentiality limitation:** Separate prompts and negotiation contexts are application-level safeguards, not a cryptographic security boundary. They do not guarantee confidentiality against model behavior, provider logging, infrastructure access, or application vulnerabilities. Do not use this simulation to process highly sensitive secrets without appropriate security controls.

## 4. Constraint Validation

`ConstraintRule` supports four operators:

| Operator | Meaning | Example |
|---|---|---|
| `eq` | Must equal a value | `warranty_months = 12` |
| `le` | Must be less than or equal to a value | `price_inr <= 90000` |
| `ge` | Must be greater than or equal to a value | `delivery_days >= 21` |
| `in` | Must belong to an allowed list | `currency in ["INR", "USD"]` |

Each structured constraint has a `hard` flag.

### Hard constraints

A hard constraint is non-negotiable.

A proposal that violates an applicable hard constraint must not be accepted as a verified agreement.

### Soft constraints

A soft constraint represents a preference rather than a mandatory condition.

It may influence proposal evaluation and negotiation decisions, but it must not be represented as a mandatory condition.

Do not claim that a soft constraint has been automatically satisfied or scored unless the implemented evaluation logic provides that evidence.

### Human-readable constraints

The `constraints` field contains free-text requirements.

These can provide useful context to the negotiating agents. However, a free-text statement is not automatically equivalent to a machine-verifiable `constraint_rule`.

Do not claim that a free-text constraint has been formally verified unless an appropriate validation mechanism exists.

## 5. Negotiation Round Lifecycle

Each negotiation round follows the configured engine workflow.

### Step 1: Party A proposes

Party A generates a proposal containing:

- Negotiation terms
- Proposed values for relevant issues
- Explanation of the proposal

### Step 2: Party B evaluates

Party B evaluates the proposal using its own:

- Priorities
- Hard constraints
- Soft constraints
- Background information
- Previous negotiation history

Party B can accept, reject, or provide a counterproposal.

### Step 3: Party A evaluates the response

If Party B provides a counterproposal, Party A evaluates the proposed terms against its own requirements.

Party A may accept or reject the counterproposal.

### Step 4: Confirm the final terms

If Party A accepts a counterproposal, Party B must explicitly confirm the same final terms.

Do not treat a counterproposal as an agreement merely because one party accepts it.

Continue negotiating while the configured round limit permits.

## 6. Agreement Verification

An agreement must never be inferred from conversational wording.

Before reporting an agreement, verify:

1. Both parties explicitly accepted the final terms.
2. Both parties accepted the same complete set of recorded terms.
3. All applicable hard constraints are satisfied.
4. No unresolved mandatory issue remains.

A proposal containing words such as "accepted", "approved", or "agreed" is not sufficient proof.

If these conditions are not satisfied, report that no verified agreement was reached.

The exact accepted terms must be recorded in:

- `party_a_accepted_terms`
- `party_b_accepted_terms`

These fields provide evidence for comparing the terms accepted by both parties.

## 7. Maximum Round Handling

The maximum number of rounds is controlled by `max_rounds`.

The valid range is 1 to 50. The default is 5.

When the round limit is reached without a verified agreement:

- Stop the negotiation.
- Preserve the recorded rounds.
- Report unresolved issues.
- Explain that no verified agreement was reached.

Do not fabricate additional negotiation rounds.

## 8. Result Structure

The negotiation result follows the `NegotiationResult` model.

### NegotiationResult

| Field | Description |
|---|---|
| `topic` | Negotiation subject |
| `party_a_name` | First party |
| `party_b_name` | Second party |
| `rounds` | Recorded negotiation rounds |
| `outcome` | Final negotiation outcome |

### RoundRecord

| Field | Description |
|---|---|
| `round_number` | Round identifier |
| `party_a_proposal` | Party A proposal |
| `party_b_response` | Party B response |
| `party_a_accepted` | Party A acceptance status |
| `party_b_accepted` | Party B acceptance status |
| `party_a_accepted_terms` | Exact terms accepted by Party A |
| `party_b_accepted_terms` | Exact terms accepted by Party B |
| `notes` | Round-specific observations |

### NegotiationOutcome

| Field | Description |
|---|---|
| `agreement_reached` | Whether a verified agreement exists |
| `final_terms` | Final agreed terms |
| `unresolved_issues` | Issues that remain unresolved |
| `evaluation_summary` | Summary of the outcome |

Only report final terms as agreed terms when `agreement_reached` is true and the engine's verification requirements are satisfied.

## 9. Provider Configuration

The current Python local execution implementation supports Ollama.

Default configuration in the provider factory:

- Provider: `ollama`
- Model: `llama3:latest` when no model override is configured
- Default endpoint: `http://127.0.0.1:11434`
- Default timeout: `180` seconds

The repository's `.env.example` provides an example configuration. Its configured values can override the provider factory defaults.

For Docker Compose, the Ollama endpoint normally uses the service hostname:

`http://ollama:11434`

For execution directly on the host machine, use the host-accessible Ollama endpoint.

The provider must be configured and available before execution.

If provider execution fails:

- Report the failure.
- Do not invent proposals or results.
- Do not claim that the negotiation completed.

OpenAI-compatible and Python host-agent provider adapters are not implemented in the current provider factory. Do not advertise them as supported Python providers until their integrations are implemented.

An Agensi-connected host agent following this skill is a separate execution mode and should not be confused with a Python provider adapter.

## 10. Reliability and Security Rules

- Never intentionally reveal one party's private information to the other party.
- Never ignore applicable hard constraints.
- Never invent acceptance or rejection.
- Never fabricate negotiation results.
- Never report an unverified agreement.
- Preserve the original negotiation history.
- Respect the configured maximum number of rounds.
- Clearly distinguish proposals from final agreed terms.
- Clearly identify the output as a simulated negotiation.
- Do not claim confidentiality guarantees that the application and provider infrastructure cannot establish.
- Report provider and validation failures honestly.