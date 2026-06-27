# agents/negotiator.py

import httpx

class Negotiator:
    def __init__(self, country: str, positions: dict, ollama_url: str):
        self.country = country
        self.positions = positions
        self.ollama_url = ollama_url
        self.model = "llama3"
        pass
    async def generate_response(self, prompt: str):
        async with httpx.AsyncClient() as client:
            response=await client.post(
                f"{self.ollama_url}/api/generate",
                json ={
                    "model":self.model,
                    "prompt":prompt,
                    "stream":False,   # To get the fully reply at once, not word by word
                },
                timeout=60.0,
            )
            response.raise_for_status() # raise an error is Ollama responded with a failure
            return response.json()["response"]
        pass

    async def make_proposal(self, issue: str, history: list):

        prompt = f""" You are a negotiator for {self.country}.
        your key is priorities are :{', '.join(self.positions['priorities'])}.
        The negotiation is about: {issue}.
        Negotiation history so far: {history}
        Based on this, make a concise, actionable proposal.
        Respond with a single sentence only.
        """
        return await self.generate_response(prompt)
