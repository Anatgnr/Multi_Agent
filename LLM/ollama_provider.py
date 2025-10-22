import requests
import json

import requests, json

class OllamaLLM:
    """
    Provider compatible CrewAI / creAI pour Ollama.
    Permet de passer un modèle global ou un modèle spécifique par appel.
    Renvoie toujours un dict {"output": str}.
    """

    def __init__(self, default_model="llama3.2", base_url="http://127.0.0.1:11434"):
        self.default_model = default_model
        self.base_url = base_url

    def call(self, messages, model=None, **kwargs):
        """
        Appelle Ollama pour générer un texte.
        - messages: str ou list de dicts [{"role":..., "content":...}]
        - model: nom du modèle à utiliser pour cet appel (optionnel)
        Retourne {"output": str}
        """
        # Concatène le prompt si messages est une liste
        if isinstance(messages, list):
            prompt = "\n".join([m.get("content", str(m)) if isinstance(m, dict) else str(m) for m in messages])
        else:
            prompt = str(messages)

        model_to_use = model or self.default_model

        payload = {
            "model": model_to_use,
            "prompt": prompt
        }

        response = requests.post(f"{self.base_url}/api/generate", json=payload, stream=False)

        if not response.ok:
            raise Exception(f"Ollama error: {response.text}")

        # Lit la réponse et concatène
        output = ""
        try:
            for line in response.text.splitlines():
                if not line.strip():
                    continue
                data = json.loads(line)
                output += data.get("response", "")
                if data.get("done"):
                    break
        except Exception as e:
            raise Exception(f"Erreur parsing Ollama response: {e}\n{response.text}")

        return {"output": output}


# Wrapper pour un agent spécifique avec modèle dédié
class OllamaAgentLLM:
    """
    Permet de passer un modèle spécifique à chaque agent.
    """
    def __init__(self, provider: OllamaLLM, model_name=None):
        self.provider = provider
        self.model_name = model_name

    def call(self, messages, **kwargs):
        return self.provider.call(messages, model=self.model_name, **kwargs)
