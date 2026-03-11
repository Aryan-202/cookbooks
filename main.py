from benchmark import Benchmark

def main():
    print("Optimizing LLM Inference")
    benchmark = Benchmark()
    
    prompts = [
        "Explain quantum computing in 5 sentences.",
        "Write a python script to reverse a linked list.",
        "Summarize the plot of the Matrix."
    ]
    
    print("\n--- Running Unoptimized Baseline ---")
    for prompt in prompts:
        # We explicitly show unoptimized behaviour on a typical model
        benchmark.run_inference(prompt, use_optimizer=False, static_model="llama3.2:latest")
        
    print("\n--- Running Optimized Edge Engine ---")
    for prompt in prompts:
        benchmark.run_inference(prompt, use_optimizer=True)
        
    from generate_dashboard import generate_dashboard
    import os

    print("\nScaling the results and updating the Intelligence Dashboard...")
    generate_dashboard()
    
    output_file = "index.html"
    abs_path = os.path.abspath(output_file).replace('\\', '/')
    print(f"\n✅ Experiments completed. View your results at: file:///{abs_path}")

if __name__ == "__main__":
    main()
