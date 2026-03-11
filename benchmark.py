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
        
        os.makedirs("logs", exist_ok=True)
        file_exists = os.path.exists(self.results_path) and os.path.getsize(self.results_path) > 0
        if not file_exists:
            with open(self.results_path, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Model", "NumCtx", "NumPredict",
                    "Latency(s)", "CPU(%)", "RAM(%)", "GPU(%)", "GPUMem(%)",
                    "Tokens/sec", "EfficiencyScore", "Mode"
                ])

    def run_inference(self, prompt, use_optimizer=True, static_model="phi3:mini", is_warmup=False):
        """Runs the LLM inference and records performance metrics."""
        try:
            if use_optimizer:
                params = self.optimizer.optimize_parameters(prompt)
                model        = params["model"]
                p_text       = params["prompt"]
                num_ctx      = params["num_ctx"]
                num_predict  = params["num_predict"]
                temperature  = params["temperature"]
                top_k        = params["top_k"]
                top_p        = params["top_p"]
                num_thread   = params["num_thread"]
                num_batch    = params["num_batch"]
                ram_usage    = params["ram_usage_at_time"]
                mode         = "Optimized"
            else:
                model       = static_model
                p_text      = prompt
                num_ctx     = 4096
                num_predict = 1000
                temperature = 0.8
                top_k       = 40
                top_p       = 0.9
                num_thread  = None
                num_batch   = 128
                ram_usage   = ResourceMonitor.get_ram_usage()
                mode        = "Unoptimized"
                
            if is_warmup:
                print(f"--- Warm-up: Priming {model} into VRAM ---")
            else:
                print(f"Running query... Mode: {mode}, Model: {model}, Ctx: {num_ctx}")
            
            # Start background telemetry monitor
            from monitor import TelemetryMonitor
            t_monitor = TelemetryMonitor()
            t_monitor.start()
            
            result = self.client.generate(
                model=model,
                prompt=p_text,
                num_ctx=num_ctx,
                num_predict=num_predict,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                num_thread=num_thread,
                num_batch=num_batch
            )
            
            # Stop monitor and get session metrics (Peaks for hardware usage)
            metrics = t_monitor.stop()
            cpu_usage  = metrics["avg_cpu"]
            gpu_usage  = metrics["avg_gpu"]
            gpu_memory = metrics["avg_gmem"]

            if result["success"]:
                latency = result["latency"]
                tokens  = result["eval_count"]
                
                tokens_per_sec = tokens / latency if latency > 0 else 0
                
                # REFINED EFFICIENCY FORMULA
                # - Stability: Added +20.0 base cost to prevent 100x spikes.
                # - Fairness: Balanced weighting to value Context Savings vs Speed.
                hw_pressure = (cpu_usage * 0.2) + (gpu_usage * 0.4) + (ram_usage * 0.4) + 20.0
                context_multiplier = 4096 / num_ctx if num_ctx > 0 else 1
                efficiency = round((tokens_per_sec * context_multiplier) / (hw_pressure / 10.0), 2)
                
                if not is_warmup:
                    gpu_str    = f"GPU {gpu_usage}%"   if gpu_usage > 0 else "GPU N/A"
                    gmem_str   = f"GMem {gpu_memory}%" if gpu_memory > 0 else "GMem N/A"

                    print(
                        f"Result: {latency:.1f}s | CPU {cpu_usage}% | {gpu_str} | {gmem_str} | "
                        f"tok/s {tokens_per_sec:.1f} | Eff {efficiency:.2f}\n"
                    )
                    
                    with open(self.results_path, "a", newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            model, num_ctx, num_predict, round(latency, 2),
                            cpu_usage, ram_usage, gpu_usage, gpu_memory,
                            round(tokens_per_sec, 2), round(efficiency, 2), mode
                        ])
                else:
                    print(f"Warm-up complete for {model}.\n")
            else:
                if not is_warmup:
                    print(f"Error during inference: {result.get('error')}")
        finally:
            gc.collect()
