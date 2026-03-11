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
        # 1. Prompt Trimming (RAM awareness)
        # If a prompt is very long (e.g., >600 characters), shorten it before inference to reduce memory usage.
        if len(prompt) > 600:
            prompt = prompt[:590] + "... [Trimmed]"
            
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
        Calculates a dynamic scoring threshold and returns optimal payload based heavily on RAM usage.
        """
        cpu_usage = ResourceMonitor.get_cpu_usage()
        ram_usage = ResourceMonitor.get_ram_usage()
        
        complexity_score, complexity_label, trimmed_prompt = PromptAnalyzer.classify_complexity(prompt)
        last_latency = self._get_last_latency()
        
        # Determine Base Context Capacity dynamically scaled on RAM
        # Formula: context_size = max_ctx * (1 - ram_usage / 100)
        max_ctx = 4096 if complexity_score > 1 else 2048
        scaled_ctx = int(max_ctx * (1 - (ram_usage / 100.0)))
        # Clamp context_size between: 128 <= context_size <= 2048
        dynamic_ctx = max(128, min(scaled_ctx, 2048))
        
        ram_trigger = None
        
        # RAM-aware optimization rules (DEMO: Threshold raised to 95% to show model switching)
        if ram_usage > 95.0:
            ram_trigger = "High RAM usage detected → reducing context and switching to lightweight model."
            model = "phi3:mini"
            num_ctx = min(dynamic_ctx, 256)
            num_predict = 128
            temperature = 0.2
            top_p = 0.5
            top_k = 20
            num_batch = 64
            
        elif ram_usage >= 65.0:
            ram_trigger = "Medium RAM pressure → capping context size and limiting token span."
            model = "llama3.2:latest" if complexity_score > 1 else "phi3:mini"
            num_ctx = min(dynamic_ctx, 1024)
            num_predict = 256
            temperature = 0.4
            top_p = 0.7
            top_k = 30
            num_batch = 128
            
        else: # RAM usage < 65%
            # Normal logic uses CPU + complexity stress
            model = "llama3.2:latest" if complexity_score > 1 else "phi3:mini"
            # Allow higher context scaling unhindered 
            num_ctx = dynamic_ctx
            num_predict = 512
            temperature = 0.6 if complexity_score > 1 else 0.3
            top_p = 0.9
            top_k = 40
            num_batch = 256
                
        # Console Logging output       
        print("\n--- Optimizer Decision ---")
        if ram_trigger:
            print(f"[{ram_trigger}]")
        print(f"CPU Usage: {cpu_usage}%")
        print(f"RAM Usage: {ram_usage}%")
        print(f"Prompt Complexity: {complexity_label} (Score: {complexity_score})")
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
            "system_stress_score": 0.0 # kept for compatibility
        }

