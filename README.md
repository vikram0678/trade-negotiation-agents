# Trade Negotiation Agents

Two AI agents — one for the USA, one for China — negotiate a trade deal over several rounds. Built this to learn how multi-agent LLM systems work in practice.

Each agent knows its country's priorities, reads the conversation history, and generates proposals round by round. At the end, a scoring function measures how much both sides compromised. The whole thing is containerized using Docker, so it runs the same on any machine — no OpenAI key, no cloud, nothing external.

---

## How It Works

1. You send a POST request with a trade issue and number of rounds
2. USA agent makes a proposal using Llama 3 via Ollama
3. China agent responds, seeing everything said so far
4. This repeats for each round
5. A score is calculated based on compromise language in the conversation
6. The full transcript and outcome is returned as JSON

---

## Project Structure

```
trade-negotiation-agents/
├── agents/
│   └── negotiator.py         # AI agent class — talks to Ollama, builds prompts
├── data/
│   └── trade_positions.json  # Each country's goals and flexibility scores
├── tests/
│   └── test_negotiation.py   # Pytest tests for the API
├── .env.example              # Environment variable template
├── docker-compose.yml        # Runs Ollama + API containers together
├── Dockerfile                # Builds the API container
├── main.py                   # FastAPI app — the /negotiate endpoint
├── requirements.txt          # Python dependencies
└── README.md
└── scoring.py                # Scores how much agents compromised (0.0 to 1.0)

```

---

## Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Ollama](https://ollama.com/) — to run Llama 3 locally
- [Python 3.11+](https://www.python.org/downloads/) — only needed if running outside Docker
---

## Setup and Run

### 1. Clone the repo

```bash
git clone https://github.com/vikram0678/trade-negotiation-agents.git
cd trade-negotiation-agents
```

### 2. Start the containers

```bash
docker-compose up --build
```

Wait until you see this line in the logs:

```
api  | INFO:     Application startup complete.
```

### 4. Pull the Llama 3 model

Open a new terminal and run:

```bash
docker exec -it ollama ollama pull llama3
```

> This is a one-time download of around 4.7 GB. Once it's done it's cached — you won't need to pull again.

Wait until you see:

```
success
```

### 5. You're ready

Open the interactive API docs in your browser:

```
http://localhost:8000/docs
```

---

## Testing the API

### Option 1 — Swagger UI (Easiest)

Open your browser and go to:

```
http://localhost:8000/docs
```

1. Click **POST /negotiate**
2. Click **Try it out**
3. Paste this into the request body:

```json
{
  "issue": "Technology Tariffs",
  "rounds": 3
}
```

4. Click **Execute**
5. Scroll down to see the full negotiation transcript and outcome

---

### Option 2 — curl

```bash
curl -X POST http://localhost:8000/negotiate \
  -H "Content-Type: application/json" \
  -d '{"issue": "Technology Tariffs", "rounds": 3}'
```

---

### Option 3 — Pytest (Automated)

```bash
docker-compose exec api python -m pytest tests/ -v
```

Expected output:

```
tests/test_negotiation.py::test_negotiation_endpoint_success       PASSED
tests/test_negotiation.py::test_agents_reference_their_priorities  PASSED

2 passed
```

> Note: Each test calls Llama 3 locally so the full run takes around 4 to 8 minutes. Just let it run.

---

## API Reference

### POST `/negotiate`

**Request body:**

```json
{
  "issue": "Technology Tariffs",
  "rounds": 3
}
```

| Field | Type | Required | Default |
|-------|------|----------|---------|
| issue | string | Yes | — |
| rounds | integer | No | 3 |

**Response:**

```json
{
  "rounds": [
    {
      "round": 1,
      "usa_proposal": "We propose reducing tariffs by 10% in exchange for IP protection...",
      "china_response": "We accept IP discussions if agricultural access is guaranteed..."
    },
    {
      "round": 2,
      "usa_proposal": "We agree to the joint committee proposal...",
      "china_response": "We accept the revised terms and commit to IP enforcement..."
    }
  ],
  "outcome": {
    "agreement_reached": true,
    "final_terms": "USA: ... | China: ...",
    "compromise_score": 0.8
  }
}
```

**Outcome fields:**

| Field | Type | Description |
|-------|------|-------------|
| agreement_reached | boolean | True when compromise score is 0.6 or above |
| final_terms | string | Summary of the last round from both agents |
| compromise_score | float | 0.0 to 1.0 — how much both sides compromised |

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| OLLAMA_BASE_URL | URL where Ollama is running | http://ollama:11434 |
| API_PORT | Port the FastAPI app runs on | 8000 |

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| FastAPI | API framework |
| Ollama + Llama 3 | Local LLM — runs entirely on your machine |
| Docker + Compose | Containerization |
| httpx | Async HTTP calls to Ollama |
| pytest | Automated testing |

---

## Notes

- All AI runs locally — no OpenAI key, no costs, no data leaving your machine
- Negotiation logs are saved to `negotiation_log.json` after each run
- Compromise score is keyword-based — more concession language means a higher score
- `agreement_reached` flips to true when score is 0.6 or above
- Response times depend on your machine — CPU only will take 2 to 4 minutes per request


















## Setup and Run

**Start the containers**

```bash
# Modern Docker (V2) — recommended
docker compose up --build

# Older Docker (V1)
docker-compose up --build
```

## Setup and Run

**1. Clone the repo**
```bash
git clone https://github.com/yourusername/trade-negotiation-agents.git
cd trade-negotiation-agents
```

**2. Start the containers**
```bash
# Modern Docker (V2)
docker compose up --build

# Older Docker (V1)
docker-compose up --build
```
> Wait until you see:
> ```
> api | INFO:     Application startup complete.
> ```

**3. Pull the Llama 3 model — open a new terminal**
```bash
docker exec -it ollama ollama pull llama3
```
> ⚠️ Only after startup complete. One-time download (~4.7 GB)

**4. Open the API**
```
http://localhost:8000/docs
```