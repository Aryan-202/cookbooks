"""
Ollama API client for LLM inference
"""
import requests
import time

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        self.timeout = 300  # 5 minute timeout
    
    def generate(self, model, prompt, num_ctx, num_predict, temperature, 
                 top_k=40, top_p=0.9, num_thread=None, num_batch=128):
        """Sends a generation request to the local Ollama instance."""
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "5m",
            "options": {
                "num_ctx": num_ctx,
                "num_predict": num_predict,
                "temperature": temperature,
                "top_k": top_k,
                "top_p": top_p,
                "num_batch": num_batch
            }
        }
        if num_thread is not None:
            payload["options"]["num_thread"] = num_thread
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/api/generate", 
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            end_time = time.time()
            
            return {
                "response": data.get("response", ""),
                "eval_count": data.get("eval_count", 0),
                "eval_duration": data.get("eval_duration", 0),
                "latency": end_time - start_time,
                "success": True
            }
        except requests.exceptions.ConnectionError:
            return {
                "error": "Cannot connect to Ollama. Is it running?",
                "success": False
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }
    
    def list_models(self):
        """List available models in Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            return response.json().get("models", [])
        except Exception:
            return []