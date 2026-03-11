import os

def reset_logs():
    csv_path = "logs/results.csv"
    os.makedirs("logs", exist_ok=True)
    header = "Model,NumCtx,NumPredict,Latency(s),CPU(%),RAM(%),Tokens/sec,EfficiencyScore,Mode\n"
    
    # Force rewrite with standard UTF-8 (no BOM)
    with open(csv_path, "w", encoding='utf-8') as f:
        f.write(header)
    print(f"Successfully reset {csv_path} with standard UTF-8 encoding.")

if __name__ == "__main__":
    reset_logs()
