"""
Optimization Engine - Dynamically adjusts parameters based on system resources
"""
import json
import os
from pathlib import Path

from cook.core.monitor import ResourceMonitor
from cook.analyzers.prompt_analyzer import PromptAnalyzer

class OptimizationEngine:
    def __init__(self, config_path=None):
        if config_path is None:
            # Look for config in multiple locations
            possible_paths = [
                config_path,
                os.path.join(Path.home(), ".cook", "configs", "model_config.json"),
                os.path.join(os.path.dirname(__file__), "..", "..", "configs", "model_config.json"),
                os.path.join(os.getcwd(), "configs", "model_config.json")
            ]
            
            for path in possible_paths:
                if path and os.path.exists(path):
                    config_path = path
                    break
            
            if config_path is None:
                # Use default config
                config_path = os.path.join(os.path.dirname(__file__), "..", "..", "configs", "model_config.json")
        
        with open(config_path, "r") as f:
            self.config = json.load(f)
    
    def _get_last_latency(self):
        """Fetches the last recorded latency from logs"""
        results_path = os.path.join(Path.home(), ".cook", "logs")
        try:
            if os.path.exists(results_path):
                files = [f for f in os.listdir(results_path) if f.startswith("results_")]
                if files:
                    latest = max(files)
                    with open(os.path.join(results_path, latest), 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if len(lines) > 1:
                            last_line = lines[-1].strip().split(',')
                            return float(last_line[4])  # Index 4 is Latency(s)
        except Exception:
            pass
        return 0.0
    
    def optimize_parameters(self, prompt):
        """
        Calculates optimal parameters based on system resources and prompt complexity
        """
        cpu_usage = ResourceMonitor.get_cpu_usage()
        ram_usage = ResourceMonitor.get_ram_usage()
        
        complexity_score, complexity_label, trimmed_prompt = PromptAnalyzer.classify_complexity(prompt)
        last_latency = self._get_last_latency()
        
        # Determine Base Context Capacity dynamically scaled on RAM
        max_ctx = 4096 if complexity_score > 1 else 2048
        scaled_ctx = int(max_ctx * (1 - (ram_usage / 100.0)))
        dynamic_ctx = max(128, min(scaled_ctx, 2048))
        
        ram_trigger = None
        
        # RAM-aware optimization rules
        if ram_usage > 80.0:
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
            
        else:  # RAM usage < 65%
            # Normal logic uses CPU + complexity stress
            model = "llama3.2:latest" if complexity_score > 1 else "phi3:mini"
            num_ctx = dynamic_ctx
            num_predict = 512
            temperature = 0.6 if complexity_score > 1 else 0.3
            top_p = 0.9
            top_k = 40
            num_batch = 256
        
        # Console Logging output (quiet mode for CLI)
        # print(f"  ⚙️  Optimizer: {complexity_label} prompt, {model}, ctx={num_ctx}")
        
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
            "system_stress_score": 0.0
        }