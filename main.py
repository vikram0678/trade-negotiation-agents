from fastapi import FastAPI, HTTPException
import json
import os 
from agents.negotiator import Negotiator
from scoring import calculate_compromise



app = FastAPI()

#load positions at startup
with open("./data/trade_positions.json") as f:
    positions = json.load(f)

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL","http://ollama:11434")

usa_agent = Negotiator("USA", positions["usa"], OLLAMA_URL)
china_agent = Negotiator("China", positions["china"], OLLAMA_URL)


@app.get("/health")
def health():
    return {
        "status":"ok"
    }

@app.post("/negotiate")
async def negotiate(request: dict):
    issue = request.get("issue")
    rounds = request.get("rounds", 3)

    if not issue:
        raise HTTPException(
            status_code=400, 
            detail="'issue'field is required"
        )
    
    history = []

    for round_number in range(1, rounds+1):
        usa_proposal = await(usa_agent.make_proposal(issue, history))
        china_response = await(china_agent.make_proposal(issue, history +[{"usa":usa_proposal}]))
        round_record = {
            "round":round_number,
            "usa_proposal" : usa_proposal,
            "china_response": china_response
        }
        history.append(round_record)

    score = calculate_compromise(history, positions)
    agreement = score >=0.6
    last_round = history[-1]
    final_terms = (
        f"USA:{last_round['usa_proposal']}"
        f"China:{last_round['china_response']}"
    )
    final_outcome = {
        "agreement_reached":agreement,
        "final_terms": final_terms,
        "compromise_score":score,
    }
    log_entry = {"issue": issue, "rounds":history, "outcome":final_outcome}
    _append_to_log(log_entry)

    return {"rounds": history, "outcome":final_outcome}

def _append_to_log(entry: dict):
    log_path = "negotiation_log.json"
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            log = json.load(f)
    else:
        log = []
    log.append(entry)
    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)