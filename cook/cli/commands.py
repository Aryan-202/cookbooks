#!/usr/bin/env python3
"""
Main CLI interface for Cook Optimizer
"""
import argparse
import sys
import os
from pathlib import Path
from datetime import datetime

from cook.core.benchmark import Benchmark
from cook.reporters.html_reporter import HTMLReporter
from cook.utils.file_utils import ensure_dir, read_prompts_from_file

def main():
    parser = argparse.ArgumentParser(
        description="🍳 Cook - LLM Optimization Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cook "Explain quantum computing"
  cook "Write Python code" --baseline llama3.2:latest --output report.html
  cook batch prompts.txt --output batch_results
  cook watch --interval 5
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Single prompt command
    single_parser = subparsers.add_parser("single", help="Run optimization on a single prompt")
    single_parser.add_argument("prompt", type=str, help="Prompt to analyze")
    single_parser.add_argument("--baseline", "-b", type=str, default="llama3.2:latest", 
                              help="Baseline model to use (default: llama3.2:latest)")
    single_parser.add_argument("--output", "-o", type=str, default=None,
                              help="Output HTML file path (default: cook_report_TIMESTAMP.html)")
    single_parser.add_argument("--no-open", action="store_true",
                              help="Don't automatically open the report in browser")
    
    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Run optimization on multiple prompts from a file")
    batch_parser.add_argument("file", type=str, help="File containing prompts (one per line)")
    batch_parser.add_argument("--baseline", "-b", type=str, default="llama3.2:latest",
                             help="Baseline model to use")
    batch_parser.add_argument("--output", "-o", type=str, default="cook_batch_report.html",
                             help="Output HTML file path")
    
    # Watch command (continuous monitoring)
    watch_parser = subparsers.add_parser("watch", help="Watch mode - continuous optimization")
    watch_parser.add_argument("--interval", "-i", type=int, default=5,
                             help="Interval between checks in seconds (default: 5)")
    watch_parser.add_argument("--threshold", "-t", type=float, default=70.0,
                             help="Resource threshold percentage (default: 70)")
    
    # Version command
    subparsers.add_parser("version", help="Show version information")
    
    # For backward compatibility, if no command is specified, treat as single prompt
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    if args.command == "version":
        from cook import __version__
        print(f"🍳 Cook Optimizer version {__version__}")
        sys.exit(0)
    
    elif args.command == "single":
        run_single_prompt(args)
    
    elif args.command == "batch":
        run_batch_prompts(args)
    
    elif args.command == "watch":
        run_watch_mode(args)
    
    else:
        # Try to interpret as direct prompt for backward compatibility
        if hasattr(args, 'prompt') and args.prompt:
            run_single_prompt(args)
        else:
            parser.print_help()

def run_single_prompt(args):
    """Run optimization on a single prompt"""
    print(f"\n🍳 Cook Optimizer - Analyzing prompt: '{args.prompt}'\n")
    
    # Create output filename if not provided
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"cook_report_{timestamp}.html"
    
    # Initialize benchmark
    benchmark = Benchmark()
    
    # Run unoptimized baseline
    print("📊 Running unoptimized baseline...")
    unoptimized_result = benchmark.run_inference(
        args.prompt, 
        use_optimizer=False, 
        static_model=args.baseline
    )
    
    # Run optimized version
    print("⚡ Running optimized inference...")
    optimized_result = benchmark.run_inference(
        args.prompt, 
        use_optimizer=True
    )
    
    # Generate HTML report
    print(f"\n📈 Generating report: {args.output}")
    reporter = HTMLReporter()
    html_content = reporter.generate_report(
        unoptimized_result, 
        optimized_result,
        prompt=args.prompt
    )
    
    # Save report
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    abs_path = os.path.abspath(args.output)
    print(f"\n✅ Report saved to: {abs_path}")
    
    # Open in browser
    if not args.no_open:
        import webbrowser
        webbrowser.open(f"file://{abs_path}")
        print("🌐 Report opened in your browser")

def run_batch_prompts(args):
    """Run optimization on multiple prompts"""
    prompts = read_prompts_from_file(args.file)
    
    if not prompts:
        print(f"❌ No prompts found in {args.file}")
        return
    
    print(f"\n🍳 Cook Optimizer - Processing {len(prompts)} prompts from {args.file}\n")
    
    benchmark = Benchmark()
    results = []
    
    for i, prompt in enumerate(prompts, 1):
        print(f"[{i}/{len(prompts)}] Processing: {prompt[:50]}...")
        
        # Run both modes
        unopt = benchmark.run_inference(prompt, use_optimizer=False, static_model=args.baseline)
        opt = benchmark.run_inference(prompt, use_optimizer=True)
        
        results.append({
            'prompt': prompt,
            'unoptimized': unopt,
            'optimized': opt
        })
    
    # Generate report
    print(f"\n📈 Generating batch report...")
    reporter = HTMLReporter()
    html_content = reporter.generate_batch_report(results)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ Batch report saved to: {os.path.abspath(args.output)}")

def run_watch_mode(args):
    """Watch mode - continuously monitor and optimize"""
    import time
    from cook.core.monitor import ResourceMonitor
    
    print(f"\n🍳 Cook Optimizer - Watch Mode")
    print(f"Monitoring every {args.interval} seconds (threshold: {args.threshold}%)\n")
    print("Press Ctrl+C to stop\n")
    
    monitor = ResourceMonitor()
    
    try:
        while True:
            cpu = monitor.get_cpu_usage()
            ram = monitor.get_ram_usage()
            
            status = "✅ NORMAL" if cpu < args.threshold and ram < args.threshold else "⚠️ HIGH"
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {status} - CPU: {cpu:5.1f}% | RAM: {ram:5.1f}%")
            
            if cpu >= args.threshold or ram >= args.threshold:
                print("   🔧 Optimization recommended! Run: cook single \"your prompt\"")
            
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n\n👋 Watch mode stopped")

if __name__ == "__main__":
    main()