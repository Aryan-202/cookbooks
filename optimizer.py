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
        if len(prompt) > 600:
            prompt = prompt[:590] + "... [Trimmed]"
            
        prompt_lower = prompt.lower()
        length = len(prompt)
        
        # Classification criteria
        complex_keywords = ["write", "script", "code", "algorithm", "analyze", "compare", "function", "class", "architect", "python"]
        
        if any(kw in prompt_lower for kw in complex_keywords) or length > 300:
            return 3, "Complex", prompt
        elif length >= 100:
            return 2, "Medium", prompt
        else:
            return 1, "Simple", prompt

class OptimizationEngine:
    # DEFINITION: Complexity Threshold (theta)
    # If complexity < THETA: Preferred Phi-3 (Speed/Power)
    # If complexity >= THETA: Required Llama-3.2 (Accuracy/Depth)
    COMPLEXITY_THETA = 2

    def __init__(self, config_path="configs/model_config.json"):
        with open(config_path, "r") as f:
            self.config = json.load(f)
            
    def _get_feedback_metrics(self):
        """Fetches the last recorded latency and throughput from results.csv."""
        results_path = "logs/results.csv"
        try:
            if os.path.exists(results_path) and os.path.getsize(results_path) > 0:
                with open(results_path, 'r') as f:
                    lines = [l for l in f.readlines() if l.strip()]
                    if len(lines) > 1:
                        last_line = lines[-1].strip().split(',')
                        # Index 8 is Tokens/sec (after repair)
                        # We must be careful with indexing if repair script shifted things
                        # Model(0), NumCtx(1), NumPredict(2), Latency(3), CPU(4), RAM(5), GPU(6), GPUMem(7), Tokens(8), Eff(9), Mode(10)
                        return {
                            "latency": float(last_line[3]),
                            "throughput": float(last_line[8]) if last_line[8] != 'N/A' else 0.0,
                            "last_model": last_line[0]
                        }
        except Exception:
            pass
        return {"latency": 0.0, "throughput": 100.0, "last_model": None}
            
    def optimize_parameters(self, prompt):
        """
        Calculates optimal model and parameters using a Dynamic Decision Boundary.
        Incorporates HW utilization and historical throughput feedback.
        """
        metrics = ResourceMonitor.get_all_metrics()
        cpu_usage   = metrics["cpu"]
        ram_usage   = metrics["ram"]
        gpu_usage   = metrics["gpu_usage"]
        gpu_memory  = metrics["gpu_memory"]

        complexity_score, complexity_label, trimmed_prompt = PromptAnalyzer.classify_complexity(prompt)
        feedback = self._get_feedback_metrics()
        
        # ------------------------------------------------------------------
        # 1. BASE MODEL SELECTION (The Complexity Boundary)
        # ------------------------------------------------------------------
        if complexity_score < self.COMPLEXITY_THETA:
            model = "phi3:mini"
        else:
            model = "llama3.2:latest"

        # ------------------------------------------------------------------
        # 2. FAIL-OPEN LOGIC (Model Throughput Inversion Protection)
        # If Phi-3 was used last and was too slow (< 20 T/s), fail open to Llama.
        # ------------------------------------------------------------------
        if model == "phi3:mini" and feedback["last_model"] == "phi3:mini":
            if feedback["throughput"] < 20.0:
                 model = "llama3.2:latest"
                 print(f"[Optimizer] Throughput Inversion Detected ({feedback['throughput']} T/s) → Failing open to Llama.")

        # ------------------------------------------------------------------
        # 3. HW OVERRIDE (High Pressure)
        # ------------------------------------------------------------------
        hw_trigger = None
        if ram_usage > 95.0 or (gpu_usage is not None and gpu_usage > 90.0):
            hw_trigger = "Critical HW Pressure → Forcing Lightweight Model & Context."
            model = "phi3:mini"
            num_ctx = 256
            num_predict = 128
        elif ram_usage > 75.0:
            hw_trigger = "High RAM Usage → Reducing Context."
            num_ctx = 512
            num_predict = 256
        else:
            # Scale context based on complexity
            num_ctx = 2048 if complexity_score >= self.COMPLEXITY_THETA else 1024
            num_predict = 512

        # ------------------------------------------------------------------
        # 4. FINAL PARAMETER TWEAKS
        # ------------------------------------------------------------------
        temperature = 0.4 if complexity_score >= self.COMPLEXITY_THETA else 0.2
        
        # Console logging
        gpu_usage_str  = f"{gpu_usage}%"  if gpu_usage  is not None else "N/A"
        gpu_memory_str = f"{gpu_memory}%" if gpu_memory is not None else "N/A"

        print("\n--- Optimizer Decision ---")
        if hw_trigger: print(f"[System] {hw_trigger}")
        print(f"HW Profile   : CPU {cpu_usage}% | RAM {ram_usage}% | GPU {gpu_usage_str}")
        print(f"Prophet      : Complexity {complexity_label} ({complexity_score})")
        print(f"Decision     : Selected {model} | Boundary $\\theta$={self.COMPLEXITY_THETA}")
        print(f"Parameters   : Ctx {num_ctx} | Max Tokens {num_predict}")
        print("--------------------------\n")
        
        return {
            "model": model,
            "prompt": trimmed_prompt,
            "num_ctx": num_ctx,
            "num_predict": num_predict,
            "temperature": temperature,
            "top_k": 40,
            "top_p": 0.9,
            "num_thread": None,
            "num_batch": 128,
            "ram_usage_at_time": ram_usage,
            "cpu_usage_at_time": cpu_usage,
            "gpu_usage_at_time": gpu_usage,
            "gpu_memory_at_time": gpu_memory
        }
