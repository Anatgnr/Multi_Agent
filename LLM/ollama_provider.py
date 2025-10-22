import requests

class OllamaLLM:
    def __init__(self, model_name):
        self.model_name = model_name
        self.api_url = "http://localhost:11434/api/generate"
        
    def __call__(self, input_text, **kwds):
        # Transform user input in prompt text
        if isinstance(input_text, list):
            prompt = "\n".join(
                [m["content"] if isinstance(m, dict) and "content" in m else str(m)
                 for m in input_text]
            )
        else:
            prompt = str(input_text)
            
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(self.api_url, json=payload)
        if response.status_code != 200:
            raise RuntimeError(f"OLLAMA API ERROR {response.status_code}: {response.text}")
        
        data = response.json()
        return {"output" : data.get("response", "")}