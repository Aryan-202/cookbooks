{
  "models": {
    "phi3:mini": {
      "type": "small",
      "default_ctx": 4096,
      "description": "Short prompts, low compute"
    },
    "llama3.2:latest": {
      "type": "large",
      "default_ctx": 4096,
      "description": "Heavy compute, long reasoning"
    }
  },
  "optimization_thresholds": {
    "high_cpu_usage": 80,
    "high_ram_usage": 70
  }
}