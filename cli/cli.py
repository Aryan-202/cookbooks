import argparse
import csv
import sys
import os

# Add the parent directory to sys.path to allow importing from the root (like benchmark.py)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from benchmark import Benchmark

def generate_html(data_unoptimized, data_optimized):
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inference Optimization Results</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121212;
            color: #ffffff;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            color: #4CAF50;
        }}
        .summary {{
            background: #1e1e1e;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        .charts {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        .chart-container {{
            background: #1e1e1e;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #333;
        }}
        th {{
            color: #4CAF50;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Model Inference Optimization Report</h1>
        
        <div class="summary">
            <h2>Run Summary</h2>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Unoptimized Baseline</th>
                    <th>Optimized Engine</th>
                </tr>
                <tr>
                    <td>Mode</td>
                    <td>{data_unoptimized['Mode']}</td>
                    <td>{data_optimized['Mode']}</td>
                </tr>
                <tr>
                    <td>Model Used</td>
                    <td>{data_unoptimized['Model']}</td>
                    <td>{data_optimized['Model']}</td>
                </tr>
                <tr>
                    <td>Context Window</td>
                    <td>{data_unoptimized['NumCtx']}</td>
                    <td>{data_optimized['NumCtx']}</td>
                </tr>
                <tr>
                    <td>Latency (s)</td>
                    <td>{data_unoptimized['Latency(s)']}</td>
                    <td>{data_optimized['Latency(s)']}</td>
                </tr>
                <tr>
                    <td>CPU Usage (%)</td>
                    <td>{data_unoptimized['CPU(%)']}</td>
                    <td>{data_optimized['CPU(%)']}</td>
                </tr>
                <tr>
                    <td>RAM Usage (%)</td>
                    <td>{data_unoptimized['RAM(%)']}</td>
                    <td>{data_optimized['RAM(%)']}</td>
                </tr>
                <tr>
                    <td>Tokens/sec</td>
                    <td>{data_unoptimized['Tokens/sec']}</td>
                    <td>{data_optimized['Tokens/sec']}</td>
                </tr>
                <tr>
                    <td>Efficiency Score</td>
                    <td>{data_unoptimized['EfficiencyScore']}</td>
                    <td>{data_optimized['EfficiencyScore']}</td>
                </tr>
            </table>
        </div>

        <div class="charts">
            <div class="chart-container">
                <canvas id="latencyChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="efficiencyChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="resourceChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="tokensChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        // Data interpolation
        const labels = ['Unoptimized Baseline', 'Optimized Engine'];
        
        const latencyData = [{data_unoptimized['Latency(s)']}, {data_optimized['Latency(s)']}];
        const effData = [{data_unoptimized['EfficiencyScore']}, {data_optimized['EfficiencyScore']}];
        const cpuData = [{data_unoptimized['CPU(%)']}, {data_optimized['CPU(%)']}];
        const ramData = [{data_unoptimized['RAM(%)']}, {data_optimized['RAM(%)']}];
        const tokensData = [{data_unoptimized['Tokens/sec']}, {data_optimized['Tokens/sec']}];

        // Chart configuration template
        function createChart(ctxId, label, data, bgColor, borderColor) {{
            const ctx = document.getElementById(ctxId).getContext('2d');
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: labels,
                    datasets: [{{
                        label: label,
                        data: data,
                        backgroundColor: bgColor,
                        borderColor: borderColor,
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            labels: {{ color: '#fff' }}
                        }},
                        title: {{
                            display: true,
                            text: label,
                            color: '#fff'
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            ticks: {{ color: '#aaa' }},
                            grid: {{ color: '#333' }}
                        }},
                        x: {{
                            ticks: {{ color: '#aaa' }},
                            grid: {{ color: '#333' }}
                        }}
                    }}
                }}
            }});
        }}

        // Initialize Charts
        createChart('latencyChart', 'Latency (Seconds)', latencyData, ['rgba(255, 99, 132, 0.6)', 'rgba(75, 192, 192, 0.6)'], ['rgba(255, 99, 132, 1)', 'rgba(75, 192, 192, 1)']);
        createChart('efficiencyChart', 'Efficiency Score', effData, ['rgba(255, 159, 64, 0.6)', 'rgba(54, 162, 235, 0.6)'], ['rgba(255, 159, 64, 1)', 'rgba(54, 162, 235, 1)']);
        createChart('tokensChart', 'Generation Speed (Tokens/sec)', tokensData, ['rgba(153, 102, 255, 0.6)', 'rgba(255, 205, 86, 0.6)'], ['rgba(153, 102, 255, 1)', 'rgba(255, 205, 86, 1)']);
        
        // Resource Chart (Multi-bar)
        const resourceCtx = document.getElementById('resourceChart').getContext('2d');
        new Chart(resourceCtx, {{
            type: 'bar',
            data: {{
                labels: labels,
                datasets: [
                    {{
                        label: 'CPU Usage (%)',
                        data: cpuData,
                        backgroundColor: 'rgba(255, 99, 132, 0.6)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    }},
                    {{
                        label: 'RAM Usage (%)',
                        data: ramData,
                        backgroundColor: 'rgba(54, 162, 235, 0.6)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }}
                ]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ labels: {{ color: '#fff' }} }},
                    title: {{
                        display: true,
                        text: 'System Resource Usage',
                        color: '#fff'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{ color: '#aaa' }},
                        grid: {{ color: '#333' }}
                    }},
                    x: {{
                        ticks: {{ color: '#aaa' }},
                        grid: {{ color: '#333' }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""
    return html_template

def main():
    parser = argparse.ArgumentParser(description="CLI to check GPU/System optimization via prompt inference")
    parser.add_argument("prompt", type=str, help="Prompt to run inference on")
    parser.add_argument("--baseline-model", type=str, default="llama3.2:latest", help="Model to use for baseline inference")
    
    args = parser.parse_args()
    prompt = args.prompt
    
    print(f"Starting analysis for prompt: '{prompt}'")
    benchmark = Benchmark()
    
    print("\n--- Running Unoptimized Baseline ---")
    benchmark.run_inference(prompt, use_optimizer=False, static_model=args.baseline_model)
    
    print("\n--- Running Optimized Edge Engine ---")
    benchmark.run_inference(prompt, use_optimizer=True)
    
    results = []
    if os.path.exists(benchmark.results_path):
        with open(benchmark.results_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            results = list(reader)
            
    if len(results) >= 2:
        data_unoptimized = results[-2]
        data_optimized = results[-1]
        
        html_content = generate_html(data_unoptimized, data_optimized)
        
        output_file = "index.html"
        with open(output_file, "w", encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"\n✅ Optimization analysis complete. Open {os.path.abspath(output_file)} in your browser to view the generated graphs.")
    else:
        print("\n❌ Error: Could not read enough data from results log to generate graphs. Execution might have failed.")

if __name__ == "__main__":
    main()
