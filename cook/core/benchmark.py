"""
Benchmark module for running inference comparisons
"""
import csv
import os
import gc
import time
from datetime import datetime
from pathlib import Path

from cook.core.ollama_client import OllamaClient
from cook.core.optimizer import OptimizationEngine
from cook.core.monitor import ResourceMonitor

class Benchmark:
    def __init__(self, log_dir=None):
        if log_dir is None:
            log_dir = os.path.join(str(Path.home()), ".cook", "logs")
        
        self.log_dir = log_dir
        self.client = OllamaClient()
        self.optimizer = OptimizationEngine()
        
        # Create log directory
        os.makedirs(log_dir, exist_ok=True)
        
        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_path = os.path.join(log_dir, f"results_{timestamp}.csv")
        
        # Initialize CSV
        self._init_csv()

    def _init_csv(self):
        """Initialize CSV file with headers"""
        with open(self.results_path, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Timestamp", "Model", "NumCtx", "NumPredict", 
                "Latency(s)", "CPU(%)", "RAM(%)", "Tokens/sec", 
                "EfficiencyScore", "Mode", "Prompt"
            ])

    def run_inference(self, prompt, use_optimizer=True, static_model="phi3:mini"):
        """
        Runs LLM inference and records performance metrics.
        Returns a dictionary with results.
        """
        timestamp = datetime.now().isoformat()
        
        try:
            if use_optimizer:
                params = self.optimizer.optimize_parameters(prompt)
                model = params["model"]
                prompt_used = params["prompt"]
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
                # Traditional unoptimized approach
                model = static_model
                prompt_used = prompt
                num_ctx = 4096
                num_predict = 1000
                temperature = 0.8
                top_k = 40
                top_p = 0.9
                num_thread = None
                num_batch = 128
                cpu_usage = ResourceMonitor.get_cpu_usage()
                ram_usage = ResourceMonitor.get_ram_usage()
                mode = "Unoptimized"
            
            print(f"  → Running {mode} with {model}...")
            
            result = self.client.generate(
                model=model,
                prompt=prompt_used,
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
                
                # Calculate metrics
                tokens_per_sec = tokens / latency if latency > 0 else 0
                context_savings = 4096 / num_ctx if num_ctx > 0 else 1
                efficiency = round((tokens_per_sec / (cpu_usage + 1)) * context_savings, 2)
                
                # Log results
                with open(self.results_path, "a", newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        timestamp,
                        model,
                        num_ctx,
                        num_predict,
                        round(latency, 2),
                        cpu_usage,
                        ram_usage,
                        round(tokens_per_sec, 2),
                        efficiency,
                        mode,
                        prompt[:100]  # Truncate prompt for logging
                    ])
                
                # Return result dictionary
                return {
                    "success": True,
                    "mode": mode,
                    "model": model,
                    "latency": round(latency, 2),
                    "tokens": tokens,
                    "tokens_per_sec": round(tokens_per_sec, 2),
                    "cpu_usage": cpu_usage,
                    "ram_usage": ram_usage,
                    "efficiency": efficiency,
                    "num_ctx": num_ctx,
                    "num_predict": num_predict,
                    "temperature": temperature,
                    "response": result.get("response", "")[:200] + "..."
                }
            else:
                return {
                    "success": False,
                    "mode": mode,
                    "error": result.get("error")
                }
        finally:
            gc.collect()