# Universal Trade Negotiation Agents

A configurable, multi-agent negotiation system that enables two independent AI agents to negotiate business agreements, trade deals, partnerships, procurement contracts, and other structured negotiations.

Unlike fixed country-specific simulations, this system allows you to define any two negotiating parties, their roles, priorities, constraints, and negotiation issues.

Powered by **Python, FastAPI, Ollama, and Llama 3**, the system supports multi-round negotiations, structured proposals, constraint validation, and evidence-based agreement evaluation.

The project is designed to run locally using Ollama and Docker, without requiring a paid OpenAI API key.

---

## Key Features

- **Universal Negotiation:** Configure any two parties, including buyers and suppliers, companies, countries, or business partners.
- **Multi-Round Negotiation:** Parties exchange proposals and counterproposals over configurable rounds.
- **Independent Party Profiles:** Each party has its own role, priorities, constraints, and background.
- **Structured Proposals:** Negotiation terms are represented as structured JSON.
- **Constraint Validation:** Supports machine-readable rules for validating negotiation terms.
- **Agreement Verification:** An agreement requires both parties to explicitly accept identical terms and applicable constraints to pass.
- **Provider Architecture:** LLM provider configuration is separated from negotiation logic.
- **Local LLM Execution:** Uses Ollama to run models locally.
- **Evaluation CLI:** Independently validates negotiation results against their original requests.
- **Docker Support:** Run the API, Ollama, and automated tests through Docker Compose.

---

## How It Works

The negotiation engine follows a structured workflow:

1. **Define the parties:** Configure two parties with their roles, priorities, constraints, and backgrounds.
2. **Define the negotiation:** Specify the topic and the issues that need agreement.
3. **Initialize agents:** The engine creates independent negotiators for both parties.
4. **Generate proposals:** The first party generates a structured proposal using the configured LLM.
5. **Evaluate and respond:** The other party reviews the proposal and generates an acceptance or counterproposal.
6. **Continue negotiation:** The process continues until an agreement is reached or the maximum number of rounds is exhausted.
7. **Validate agreement:** The evaluator checks explicit acceptance, matching accepted terms, and applicable constraints.
8. **Return results:** The API returns the complete negotiation transcript and verified outcome.

### Agreement Verification

The system does not consider a negotiation successful simply because the agents use cooperative language.

An agreement is considered valid only when:

- Both parties explicitly accept the agreement.
- Both parties accept the same recorded terms.
- Applicable constraints are successfully verified.

If these conditions are not satisfied, the system does not report a verified agreement.

---

## Architecture

```text
                 Client / API Request
                         |
                         v
                  FastAPI Application
                         |
                         v
                 Negotiation Engine
                         |
                +--------+--------+
                |                 |
                v                 v
          Party A Agent      Party B Agent
                |                 |
                +--------+--------+
                         |
                         v
                   Provider Factory
                         |
                         v
                   Ollama Provider
                         |
                         v
                    Ollama LLM
                         |
                         v
                Structured Proposals
                         |
                         v
                Constraint Validation
                         |
                         v
                Agreement Evaluator
                         |
                         v
                 Negotiation Result
                         |
                         v
                    JSON Response
```

### Architectural Components

| Component | Responsibility |
|---|---|
| FastAPI | Exposes the negotiation API |
| Negotiation Engine | Controls the negotiation workflow |
| Negotiator | Generates proposals and responses |
| Provider Factory | Creates the configured LLM provider |
| Ollama Provider | Communicates with the local Ollama service |
| Constraint Validator | Checks structured negotiation constraints |
| Agreement Evaluator | Verifies whether an agreement is valid |
| Pydantic Models | Validates requests, proposals, and results |

---

## Project Structure

```text
trade-negotiation-agents/
│
├── agents/
│   ├── negotiator.py
│   └── strategies.py
│
├── core/
│   ├── models.py
│   ├── engine.py
│   ├── evaluator.py
│   ├── constraint_validator.py
│   └── issue_validator.py
│
├── providers/
│   ├── base.py
│   ├── factory.py
│   └── ollama.py
│
├── data/
│   └── example_profiles/
│
├── skill/
│   ├── SKILL.md
│   ├── references/
│   │   └── workflow.md
│   ├── scripts/
│   │   └── evaluate_negotiation.py
│   └── examples/
│       ├── sample_negotiation.json
│       ├── valid_result.json
│       └── invalid_result.json
│
├── tests/
│   ├── test_negotiation.py
│   ├── test_engine.py
│   ├── test_engine_provider_integration.py
│   ├── test_constraint_negotiation_flow.py
│   ├── test_evaluator.py
│   ├── test_provider_factory.py
│   ├── test_providers.py
│   └── test_real_ollama_negotiation.py
│
├── .dockerignore
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── main.py
├── requirements.txt
└── README.md
```

---

## Requirements

- Python 3.11 or later
- Docker Desktop with Docker Compose
- Sufficient system resources to run the selected Ollama model

You do not need a paid OpenAI API key for the default local Ollama configuration.

---

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/vikram0678/trade-negotiation-agents.git

cd trade-negotiation-agents
```

### 2. Configure environment variables

Create your local environment file:

```bash
cp .env.example .env
```

The `.env` file contains provider configuration.

Example configuration:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3:latest
OLLAMA_TIMEOUT=180
```

Adjust the model and timeout according to your environment.

**Important:** The `.env` file contains local configuration and should not be committed to Git.

### 3. Build and start Docker services

```bash
docker compose up --build
```

Docker Compose builds the API image, starts the required services, and initializes the configured Ollama model through the model initialization service.

The first startup can take longer because the model needs to be downloaded.

### 4. Access the API

Open:

http://localhost:8000/docs

You can interact with the API using Swagger UI.

---

## API Reference

### POST `/negotiate`

Starts a negotiation between two configured parties.

#### Request body

```json
{
  "party_a": {
    "name": "Buyer Corporation",
    "role": "Equipment Buyer",
    "priorities": {
      "price": 0.9,
      "delivery_days": 0.8
    },
    "constraints": [
      "Maximum budget is 95000"
    ],
    "constraint_rules": [
      {
        "issue": "price",
        "operator": "le",
        "value": 95000,
        "hard": true
      },
      {
        "issue": "delivery_days",
        "operator": "le",
        "value": 30,
        "hard": true
      }
    ],
    "background": "A company purchasing industrial equipment."
  },
  "party_b": {
    "name": "Supplier Corporation",
    "role": "Equipment Supplier",
    "priorities": {
      "price": 0.9,
      "delivery_days": 0.7
    },
    "constraints": [
      "Minimum acceptable price is 80000"
    ],
    "constraint_rules": [
      {
        "issue": "price",
        "operator": "ge",
        "value": 80000,
        "hard": true
      }
    ],
    "background": "A supplier providing industrial equipment."
  },
  "topic": "Business Equipment Purchase Agreement",
  "issues": [
    {
      "name": "price",
      "description": "Final equipment purchase price",
      "unit": "USD"
    },
    {
      "name": "delivery_days",
      "description": "Number of days required for delivery",
      "unit": "days"
    }
  ],
  "max_rounds": 5
}
```

#### Request fields

| Field | Type | Required | Description |
|---|---|---|---|
| `party_a` | Object | Yes | First negotiating party |
| `party_b` | Object | Yes | Second negotiating party |
| `topic` | String | Yes | Negotiation subject |
| `issues` | Array | Yes | Negotiation issues |
| `max_rounds` | Integer | No | Maximum rounds, default 5; range 1–50 |

#### Party profile fields

| Field | Type | Description |
|---|---|---|
| `name` | String | Party name |
| `role` | String | Negotiation role |
| `priorities` | Object | Issue priorities represented by numeric weights |
| `constraints` | Array | Human-readable constraints |
| `constraint_rules` | Array | Structured machine-readable constraints |
| `background` | String | Additional party context |

#### Constraint operators

| Operator | Meaning | Example |
|---|---|---|
| `eq` | Equal to | Price must equal 90000 |
| `le` | Less than or equal to | Price must be at most 95000 |
| `ge` | Greater than or equal to | Price must be at least 80000 |
| `in` | Value must belong to a list | Delivery method must be one of the permitted options |

The `hard` field identifies whether a structured rule is a hard constraint.

### Example response

The following illustrates the response structure; actual proposals and terms depend on the negotiation.

```json
{
  "topic": "Business Equipment Purchase Agreement",
  "party_a_name": "Buyer Corporation",
  "party_b_name": "Supplier Corporation",
  "rounds": [
    {
      "round_number": 1,
      "party_a_proposal": {
        "party_name": "Buyer Corporation",
        "terms": {
          "price": 85000,
          "delivery_days": 28
        },
        "explanation": "Initial proposal."
      },
      "party_b_response": {
        "party_name": "Supplier Corporation",
        "terms": {
          "price": 90000,
          "delivery_days": 25
        },
        "explanation": "Counterproposal."
      },
      "party_a_accepted": true,
      "party_b_accepted": true,
      "party_a_accepted_terms": {
        "price": 90000,
        "delivery_days": 25
      },
      "party_b_accepted_terms": {
        "price": 90000,
        "delivery_days": 25
      },
      "notes": []
    }
  ],
  "outcome": {
    "agreement_reached": true,
    "final_terms": {
      "price": 90000,
      "delivery_days": 25
    },
    "unresolved_issues": [],
    "evaluation_summary": "Both parties explicitly accepted the same recorded terms and applicable hard constraints were verified."
  }
}
```

This is an illustrative response, not a guaranteed negotiation result.

---

## Testing the API

### Option 1: Swagger UI

Open:

http://localhost:8000/docs

1. Find `POST /negotiate`.
2. Select **Try it out**.
3. Paste a valid negotiation request.
4. Select **Execute**.
5. Inspect the negotiation transcript and outcome.

### Option 2: Automated local tests

Activate your Python virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python -m pytest -q
```

### Option 3: Docker test suite

Build the test image if needed:

```bash
docker compose build test
```

Run the Docker test profile:

```bash
docker compose --profile testing run --rm test
```

The test profile verifies the project using its configured test services, including the real Ollama integration test.

The real LLM integration test can take considerably longer than ordinary unit tests because model inference depends on available hardware and model performance.

---

## Independent Negotiation Result Evaluation

The project includes a standalone evaluation script.

It checks whether a negotiation result is consistent with the original request and whether a reported agreement is supported by the recorded acceptance evidence.

Run the evaluator against the valid example:

```bash
python skill/scripts/evaluate_negotiation.py \
  --request skill/examples/sample_negotiation.json \
  --result skill/examples/valid_result.json
```

Test the invalid example:

```bash
python skill/scripts/evaluate_negotiation.py \
  --request skill/examples/sample_negotiation.json \
  --result skill/examples/invalid_result.json
```

The invalid example is intentionally designed to demonstrate that a reported agreement can be rejected when the parties' accepted terms differ.

---

## Environment Variables

Provider configuration is managed through environment variables rather than API request fields.

| Variable | Description | Default |
|---|---|---|
| `LLM_PROVIDER` | Configured LLM provider | `ollama` |
| `OLLAMA_BASE_URL` | Ollama service endpoint | `http://127.0.0.1:11434` |
| `OLLAMA_MODEL` | Model used for negotiation | `llama3:latest` |
| `OLLAMA_TIMEOUT` | Provider request timeout in seconds | `180` |

**Docker note:** When the API runs inside Docker Compose, the Ollama service hostname is typically `ollama`, so the example configuration uses `http://ollama:11434`.

When running the API directly on your host machine, use the host-accessible Ollama endpoint instead.

---

## LLM Provider Architecture

The project uses a provider abstraction to separate negotiation logic from model-specific communication.

Current implementation:

| Provider | Status |
|---|---|
| Ollama | Implemented |
| OpenAI-compatible | Not implemented |
| Host-agent provider adapter | Not implemented |

The provider factory currently supports Ollama and validates provider configuration.

The Agensi skill's host-agent execution instructions are a separate execution path; they do not mean that a Python `host_agent` provider adapter is already implemented.

---

## Agensi Skill

The repository includes a reusable negotiation skill:

```text
skill/
├── SKILL.md
├── references/
│   └── workflow.md
├── scripts/
│   └── evaluate_negotiation.py
└── examples/
    ├── sample_negotiation.json
    ├── valid_result.json
    └── invalid_result.json
```

Skill name:

`universal-negotiation`

It is designed for configurable bilateral negotiations, including:

- Country-to-country trade negotiations
- Buyer and supplier agreements
- Business partnerships
- Commercial contract negotiations
- Strategic decision simulations

The skill provides negotiation instructions, workflow references, examples, and an independent result evaluation script.

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core implementation |
| FastAPI | REST API |
| Pydantic | Data validation and schemas |
| Ollama | Local LLM runtime |
| Llama 3 | Negotiation language model |
| httpx | Asynchronous HTTP communication |
| Docker | Application containerization |
| Docker Compose | Multi-service orchestration |
| pytest | Automated testing |

---

## Design Principles

- **Configurable parties:** No hardcoded country-specific negotiation logic.
- **Separation of concerns:** Agents, providers, engine, validation, and evaluation are separate components.
- **Structured outputs:** Negotiation terms are represented as machine-readable data.
- **Conservative agreement verification:** Cooperation in generated text is not sufficient evidence of agreement.
- **Independent evaluation:** Results can be checked separately from the negotiation execution.
- **Local-first execution:** The default model runtime can operate locally through Ollama.

---

## Current Limitations

- The implemented LLM provider is currently Ollama.
- The negotiation engine currently handles two parties per negotiation.
- LLM-generated proposals may require validation and retries.
- Human-readable constraints without a corresponding structured validation mechanism cannot automatically be treated as fully verified.
- Local inference performance depends on the selected model and available hardware.
- The system is a negotiation simulation and decision-support tool, not a replacement for legal, financial, or commercial review.

---

## Future Improvements

- Additional LLM provider adapters.
- Multi-party negotiation support.
- Improved negotiation strategy selection.
- Stronger proposal consistency and validation.
- Negotiation performance analytics.
- Persistent negotiation history and reporting.
- More extensive adversarial and reliability testing.

---

## License

Add your chosen open-source license here before publishing the repository.