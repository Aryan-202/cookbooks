import json
import os
from monitor import ResourceMonitor

class PromptAnalyzer:
    """Analyzes prompts to ascertain complexity score before invoking models."""
    
    @staticmethod
    def classify_complexity(prompt):
        """
        Classifies complexity into 'Simple', 'Medium', 'Complex' 
        and returns a numerical score (1 to 3) + trimmed prompt.
        """
        # 1. Prompt Trimming 
        # If prompt length > 1000 characters, aggressively trim.
        if len(prompt) > 1000:
            prompt = prompt[:990] + "... [Trimmed]"
            
        prompt_lower = prompt.lower()
        length = len(prompt)
        
        # 2. Classification logic
        complex_keywords = ["write", "script", "code", "algorithm", "analyze", "compare", "function", "class", "architect", "python"]
        
        if any(kw in prompt_lower for kw in complex_keywords) or length > 300:
            return 3, "Complex", prompt
        elif length >= 100:
            return 2, "Medium", prompt
        else:
            return 1, "Simple", prompt

class OptimizationEngine:
    def __init__(self, config_path="configs/model_config.json"):
        with open(config_path, "r") as f:
            self.config = json.load(f)
            
    def _get_last_latency(self):
        """Fetches the last recorded latency from results.csv for feedback loops."""
        results_path = "logs/results.csv"
        try:
            if os.path.exists(results_path) and os.path.getsize(results_path) > 0:
                with open(results_path, 'r') as f:
                    lines = f.readlines()
                    if len(lines) > 1:
                        last_line = lines[-1].strip().split(',')
                        return float(last_line[3]) # Index 3 is Latency(s)
        except Exception:
            pass
        return 0.0
            
    def optimize_parameters(self, prompt):
        """
        Calculates a dynamic scoring threshold and returns optimal payload.
        """
        cpu_usage = ResourceMonitor.get_cpu_usage()
        ram_usage = ResourceMonitor.get_ram_usage()
        
        complexity_score, complexity_label, trimmed_prompt = PromptAnalyzer.classify_complexity(prompt)
        last_latency = self._get_last_latency()
        
        # Calculate dynamic stress score 
        normalized_complexity = (complexity_score / 3.0) * 100 
        stress_score = (cpu_usage * 0.4) + (ram_usage * 0.3) + (normalized_complexity * 0.3)
        
        # Latency Feedback Adjustment
        if last_latency > 20.0:
            # Heavily penalize score to force lightweight parameters
            stress_score += 25.0
        elif last_latency > 0 and last_latency < 10.0:
            # Reward score to allow for heavier constraints
            stress_score -= 10.0
            
        # Decision Matrix
        if stress_score < 45.0:
            model = "llama3.2:latest" if complexity_score > 1 else "phi3:latest"
            num_ctx = 2048 if complexity_score == 3 else (512 if model == "phi3:latest" else 1024)
            num_predict = 512
            temperature = 0.6 if complexity_score > 1 else 0.3
            top_p = 0.9
            top_k = 40
            num_batch = 512
            
        elif stress_score < 75.0:
            # Medium Load: Route model based heavily on prompt logic
            model = "llama3.2:latest" if complexity_score > 1 else "phi3:latest"
            num_ctx = 1024 if complexity_score == 3 else 512
            num_predict = 256
            temperature = 0.4
            top_p = 0.7
            top_k = 20
            num_batch = 256
            
        else:
            model = "phi3:latest"
            num_ctx = 256
            num_predict = 128
            temperature = 0.1
            top_p = 0.3
            top_k = 10
            num_batch = 64
            
            if stress_score > 90.0:
                num_ctx = 128
                num_predict = 50
                
        # Console Logging output       
        print("\n--- Optimizer Decision ---")
        print(f"CPU Usage: {cpu_usage}%")
        print(f"RAM Usage: {ram_usage}%")
        print(f"Prompt Complexity: {complexity_label} (Score: {complexity_score})")
        print(f"Latency Modifier: {last_latency}s (Stress Metric: {stress_score:.1f})")
        print(f"Selected Model: {model}")
        print(f"Context Size: {num_ctx}")
        print(f"Max Tokens: {num_predict}")
        print("--------------------------\n")
        
        return {
            "model": model,
            "prompt": trimmed_prompt,
            "num_ctx": num_ctx,
            "num_predict": num_predict,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "num_thread": None, 
            "num_batch": num_batch,
            "cpu_usage_at_time": cpu_usage,
            "ram_usage_at_time": ram_usage,
            "system_stress_score": stress_score
        }
