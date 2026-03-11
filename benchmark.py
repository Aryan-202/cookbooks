import csv
import os
import gc
from ollama_client import OllamaClient
from optimizer import OptimizationEngine
from monitor import ResourceMonitor

class Benchmark:
    def __init__(self):
        self.client = OllamaClient()
        self.optimizer = OptimizationEngine()
        self.results_path = "logs/results.csv"
        
        # Ensure log dir exists
        os.makedirs("logs", exist_ok=True)
        file_exists = os.path.exists(self.results_path) and os.path.getsize(self.results_path) > 0
        if not file_exists:
            with open(self.results_path, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Model", "NumCtx", "NumPredict", "Latency(s)", "CPU(%)", "RAM(%)", "Tokens/sec", "EfficiencyScore", "Mode"])

    def run_inference(self, prompt, use_optimizer=True, static_model="phi3:mini"):
        """Runs the LLM inference and records performance metrics."""
        
        try:
            if use_optimizer:
                params = self.optimizer.optimize_parameters(prompt)
                model = params["model"]
                prompt = params["prompt"]
                num_ctx = params["num_ctx"]
                num_predict = params["num_predict"]
                temperature = params["temperature"]
                top_k = params["top_k"]
                top_p = params["top_p"]
                num_thread = params["num_thread"]
                num_batch = params["num_batch"]
                cpu_usage = params["cpu_usage_at_time"]
                ram_usage = params["ram_usage_at_time"]
                mode = "Optimized"
            else:
                # Traditional greedy approach (Unoptimized)
                model = static_model
                num_ctx = 4096
                num_predict = 1000 
                temperature = 0.8
                top_k = 40
                top_p = 0.9
                num_thread = None
                num_batch = 128
                # Measure resources anyway
                cpu_usage = ResourceMonitor.get_cpu_usage()
                ram_usage = ResourceMonitor.get_ram_usage()
                mode = "Unoptimized"
                
            print(f"Running query... Mode: {mode}, Model: {model}, Ctx: {num_ctx}")
            result = self.client.generate(
                model=model,
                prompt=prompt,
                num_ctx=num_ctx,
                num_predict=num_predict,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                num_thread=num_thread,
                num_batch=num_batch
            )
            
            if result["success"]:
                latency = result["latency"]
                tokens = result["eval_count"]
                
                # Metric calculation
                tokens_per_sec = tokens / latency if latency > 0 else 0
                # Compute Economy Score = (Speed / Resource Overhead) * Context Savings
                context_savings = 4096 / num_ctx if num_ctx > 0 else 1
                efficiency = round((tokens_per_sec / (cpu_usage + 1)) * context_savings, 2)
                
                print(f"Result: {latency:.2f}s | {cpu_usage}% CPU | {tokens_per_sec:.2f} tok/s | Eff: {efficiency:.2f}\n")
                
                # Log results
                with open(self.results_path, "a", newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        model, 
                        num_ctx, 
                        num_predict, 
                        round(latency, 2), 
                        cpu_usage, 
                        ram_usage, 
                        round(tokens_per_sec, 2), 
                        round(efficiency, 2), 
                        mode
                    ])
            else:
                print(f"Error during inference: {result.get('error')}")
        finally:
            # Add garbage collection after inference.
            # Explicitly release memory to reduce accumulation across runs.
            gc.collect()
