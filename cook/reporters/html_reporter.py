"""
HTML Report Generator for Cook Optimizer
"""
import json
from datetime import datetime
from cook.reporters.chart_generator import ChartGenerator

class HTMLReporter:
    def __init__(self):
        self.chart_gen = ChartGenerator()
    
    def generate_report(self, unoptimized_result, optimized_result, prompt=""):
        """Generate HTML report comparing unoptimized vs optimized results"""
        
        # Prepare data for charts
        chart_data = {
            'unoptimized': unoptimized_result,
            'optimized': optimized_result,
            'prompt': prompt
        }
        
        # Generate chart configurations
        latency_chart = self.chart_gen.create_latency_chart(unoptimized_result, optimized_result)
        efficiency_chart = self.chart_gen.create_efficiency_chart(unoptimized_result, optimized_result)
        resource_chart = self.chart_gen.create_resource_chart(unoptimized_result, optimized_result)
        tokens_chart = self.chart_gen.create_tokens_chart(unoptimized_result, optimized_result)
        
        # Calculate improvements
        if unoptimized_result['success'] and optimized_result['success']:
            latency_improvement = ((unoptimized_result['latency'] - optimized_result['latency']) 
                                  / unoptimized_result['latency'] * 100)
            speed_improvement = ((optimized_result['tokens_per_sec'] - unoptimized_result['tokens_per_sec']) 
                               / unoptimized_result['tokens_per_sec'] * 100)
            efficiency_improvement = ((optimized_result['efficiency'] - unoptimized_result['efficiency']) 
                                    / unoptimized_result['efficiency'] * 100)
        else:
            latency_improvement = speed_improvement = efficiency_improvement = 0
        
        # Generate HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🍳 Cook Optimizer - Inference Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        :root {{
            --bg-primary: #0a0c10;
            --bg-secondary: #1a1e24;
            --accent-green: #4ade80;
            --accent-red: #f87171;
            --accent-blue: #60a5fa;
            --accent-orange: #fb923c;
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --border-color: #2d3748;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 3rem;
        }}
        
        .header h1 {{
            font-size: 3rem;
            background: linear-gradient(135deg, #4ade80, #60a5fa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }}
        
        .prompt-box {{
            background: var(--bg-secondary);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            margin-bottom: 2rem;
        }}
        
        .prompt-box h3 {{
            color: var(--accent-blue);
            margin-bottom: 0.5rem;
        }}
        
        .prompt-box p {{
            color: var(--text-primary);
            font-size: 1.1rem;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .stat-card {{
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid var(--border-color);
        }}
        
        .stat-card h3 {{
            color: var(--text-secondary);
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 1rem;
        }}
        
        .stat-value {{
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }}
        
        .stat-label {{
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}
        
        .improvement {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
            margin-left: 1rem;
        }}
        
        .improvement.positive {{
            background: rgba(74, 222, 128, 0.1);
            color: var(--accent-green);
        }}
        
        .improvement.negative {{
            background: rgba(248, 113, 113, 0.1);
            color: var(--accent-red);
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .chart-container {{
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid var(--border-color);
        }}
        
        .chart-container h3 {{
            margin-bottom: 1rem;
            color: var(--text-secondary);
        }}
        
        .chart-wrapper {{
            height: 300px;
            position: relative;
        }}
        
        .comparison-table {{
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid var(--border-color);
            overflow-x: auto;
        }}
        
        .comparison-table table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .comparison-table th {{
            text-align: left;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-secondary);
            font-weight: 500;
        }}
        
        .comparison-table td {{
            padding: 1rem;
            border-bottom: 1px solid var(--border-color);
        }}
        
        .comparison-table tr:last-child td {{
            border-bottom: none;
        }}
        
        .model-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            background: rgba(96, 165, 250, 0.1);
            color: var(--accent-blue);
            border-radius: 20px;
            font-size: 0.9rem;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 3rem;
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}
        
        .error {{
            background: rgba(248, 113, 113, 0.1);
            color: var(--accent-red);
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid var(--accent-red);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🍳 Cook Optimizer</h1>
            <p>LLM Inference Optimization Report</p>
            <p style="color: var(--text-secondary); margin-top: 0.5rem;">{datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="prompt-box">
            <h3>📝 Prompt Analyzed</h3>
            <p>"{prompt}"</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Latency</h3>
                <div class="stat-value">{optimized_result.get('latency', 0):.2f}s</div>
                <div class="stat-label">
                    vs {unoptimized_result.get('latency', 0):.2f}s baseline
                    <span class="improvement {'positive' if latency_improvement > 0 else 'negative'}">
                        {latency_improvement:+.1f}%
                    </span>
                </div>
            </div>
            
            <div class="stat-card">
                <h3>Speed</h3>
                <div class="stat-value">{optimized_result.get('tokens_per_sec', 0):.1f} tok/s</div>
                <div class="stat-label">
                    vs {unoptimized_result.get('tokens_per_sec', 0):.1f} tok/s baseline
                    <span class="improvement {'positive' if speed_improvement > 0 else 'negative'}">
                        {speed_improvement:+.1f}%
                    </span>
                </div>
            </div>
            
            <div class="stat-card">
                <h3>Efficiency Score</h3>
                <div class="stat-value">{optimized_result.get('efficiency', 0):.1f}</div>
                <div class="stat-label">
                    vs {unoptimized_result.get('efficiency', 0):.1f} baseline
                    <span class="improvement {'positive' if efficiency_improvement > 0 else 'negative'}">
                        {efficiency_improvement:+.1f}%
                    </span>
                </div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-container">
                <h3>⏱️ Latency Comparison</h3>
                <div class="chart-wrapper">
                    <canvas id="latencyChart"></canvas>
                </div>
            </div>
            
            <div class="chart-container">
                <h3>⚡ Generation Speed</h3>
                <div class="chart-wrapper">
                    <canvas id="tokensChart"></canvas>
                </div>
            </div>
            
            <div class="chart-container">
                <h3>📊 Efficiency Score</h3>
                <div class="chart-wrapper">
                    <canvas id="efficiencyChart"></canvas>
                </div>
            </div>
            
            <div class="chart-container">
                <h3>💻 Resource Usage</h3>
                <div class="chart-wrapper">
                    <canvas id="resourceChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="comparison-table">
            <h3 style="margin-bottom: 1rem;">📋 Detailed Comparison</h3>
            <table>
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>Unoptimized Baseline</th>
                        <th>Optimized Engine</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Model</td>
                        <td><span class="model-badge">{unoptimized_result.get('model', 'N/A')}</span></td>
                        <td><span class="model-badge">{optimized_result.get('model', 'N/A')}</span></td>
                    </tr>
                    <tr>
                        <td>Context Window</td>
                        <td>{unoptimized_result.get('num_ctx', 'N/A')}</td>
                        <td>{optimized_result.get('num_ctx', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td>Max Tokens</td>
                        <td>{unoptimized_result.get('num_predict', 'N/A')}</td>
                        <td>{optimized_result.get('num_predict', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td>Temperature</td>
                        <td>{unoptimized_result.get('temperature', 'N/A')}</td>
                        <td>{optimized_result.get('temperature', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td>Latency (s)</td>
                        <td>{unoptimized_result.get('latency', 'N/A')}</td>
                        <td>{optimized_result.get('latency', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td>CPU Usage (%)</td>
                        <td>{unoptimized_result.get('cpu_usage', 'N/A')}</td>
                        <td>{optimized_result.get('cpu_usage', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td>RAM Usage (%)</td>
                        <td>{unoptimized_result.get('ram_usage', 'N/A')}</td>
                        <td>{optimized_result.get('ram_usage', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td>Tokens/sec</td>
                        <td>{unoptimized_result.get('tokens_per_sec', 'N/A')}</td>
                        <td>{optimized_result.get('tokens_per_sec', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td>Efficiency Score</td>
                        <td>{unoptimized_result.get('efficiency', 'N/A')}</td>
                        <td>{optimized_result.get('efficiency', 'N/A')}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>⚡ Generated by Cook Optimizer v1.0.0</p>
        </div>
    </div>
    
    <script>
        {latency_chart}
        {efficiency_chart}
        {resource_chart}
        {tokens_chart}
    </script>
</body>
</html>"""
        
        return html
    
    def generate_batch_report(self, results):
        """Generate HTML report for batch processing"""
        # Simplified batch report (you can expand this)
        html = "<html><body><h1>Batch Processing Results</h1></body></html>"
        return html