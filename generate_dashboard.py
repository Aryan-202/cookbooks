import csv
import os
import json
from datetime import datetime

def generate_dashboard(csv_path=None, output_path=None):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    if csv_path is None: csv_path = os.path.join(base_dir, "logs/results.csv")
    if output_path is None: output_path = os.path.join(base_dir, "index.html")
    
    if not os.path.exists(csv_path): return

    results = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row['Latency(s)'] = float(row['Latency(s)'])
                row['EfficiencyScore'] = float(row['EfficiencyScore'])
                row['Tokens/sec'] = float(row['Tokens/sec'])
                row['CPU(%)'] = float(row['CPU(%)'])
                row['RAM(%)'] = float(row['RAM(%)'])
                
                gpu_val = row.get('GPU(%)', '0')
                gmem_val = row.get('GPUMem(%)', '0')
                row['GPU(%)'] = float(gpu_val) if (gpu_val and gpu_val != 'N/A') else 0.0
                row['GPUMem(%)'] = float(gmem_val) if (gmem_val and gmem_val != 'N/A') else 0.0
                
                results.append(row)
            except (ValueError, KeyError): continue

    if not results: return

    unopt_pool = [r for r in results if r['Mode'] == 'Unoptimized']
    opt_pool = [r for r in results if r['Mode'] == 'Optimized']
    
    unopt_data = unopt_pool[-5:] if len(unopt_pool) >= 5 else unopt_pool
    opt_data = opt_pool[-5:] if len(opt_pool) >= 5 else opt_pool
    
    chart_results = sorted(unopt_data + opt_data, key=lambda x: results.index(x))

    def get_avg(data_list):
        if not data_list: return None
        count = len(data_list)
        return {
            'Latency(s)': round(sum(r['Latency(s)'] for r in data_list) / count, 2),
            'EfficiencyScore': round(sum(r['EfficiencyScore'] for r in data_list) / count, 2),
            'Tokens/sec': round(sum(r['Tokens/sec'] for r in data_list) / count, 2),
            'CPU(%)': round(sum(r['CPU(%)'] for r in data_list) / count, 1),
            'RAM(%)': round(sum(r['RAM(%)'] for r in data_list) / count, 1),
            'GPU(%)': round(sum(r['GPU(%)'] for r in data_list) / count, 1),
            'GPUMem(%)': round(sum(r['GPUMem(%)'] for r in data_list) / count, 1),
            'Model': data_list[-1]['Model'], 
            'Count': count
        }

    avg_unopt = get_avg(unopt_data)
    avg_opt = get_avg(opt_data)

    labels = [f"Run {i+1}" for i in range(len(chart_results))]
    tokens_data = [r['Tokens/sec'] for r in chart_results]
    eff_data = [r['EfficiencyScore'] for r in chart_results]
    modes = [r['Mode'] for r in chart_results]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Omni-Engine | Intelligence Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg: #030408;
            --surface: #0a0c12;
            --card: #11151f;
            --border: rgba(255, 255, 255, 0.06);
            --accent: #22d3ee;
            --baseline: #f87171;
            --text-main: #f3f4f6;
            --text-dim: #9ca3af;
            --gradient-opt: linear-gradient(135deg, #0ea5e9, #22d3ee);
            --gradient-unopt: linear-gradient(135deg, #ef4444, #f87171);
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Outfit', sans-serif; }}
        body {{ background-color: var(--bg); color: var(--text-main); padding: 40px; min-height: 100vh; }}
        
        .kpi-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }}
        .kpi-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 20px; padding: 25px; text-align: center; position: relative; }}
        .kpi-card h4 {{ font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase; margin-bottom: 10px; letter-spacing: 1px; }}
        .kpi-card .val {{ font-size: 2rem; font-weight: 700; color: var(--text-main); }}
        .kpi-card .diff {{ font-size: 0.8rem; font-weight: 600; margin-top: 5px; }}
        .positive {{ color: #4ade80; }}
        .negative {{ color: #f87171; }}

        .dashboard-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 25px; }}
        .chart-area, .table-area {{ background: var(--card); border: 1px solid var(--border); border-radius: 24px; padding: 30px; box-shadow: 0 15px 35px rgba(0,0,0,0.4); }}
        .full-width {{ grid-column: span 2; }}

        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th {{ text-align: left; padding: 15px; color: var(--text-dim); border-bottom: 1px solid var(--border); font-size: 0.8rem; text-transform: uppercase; }}
        td {{ padding: 15px; border-bottom: 1px solid var(--border); font-size: 0.9rem; }}
        
        .unopt-header {{ color: var(--baseline); border-bottom: 2px solid var(--baseline); }}
        .opt-header {{ color: var(--accent); border-bottom: 2px solid var(--accent); }}

        .badge {{ padding: 4px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; }}
        .badge-opt {{ background: rgba(34, 211, 238, 0.1); color: var(--accent); }}
        .badge-unopt {{ background: rgba(248, 113, 113, 0.1); color: var(--baseline); }}

        .viva-panel {{ background: rgba(34, 211, 238, 0.05); border: 1px dashed var(--accent); border-radius: 16px; padding: 20px; margin-bottom: 30px; }}
        .viva-panel h3 {{ color: var(--accent); font-size: 1rem; margin-bottom: 10px; }}
        .viva-panel p {{ font-size: 0.85rem; color: #a5f3fc; line-height: 1.5; }}
    </style>
</head>
<body>
    <header style="margin-bottom: 40px; display: flex; justify-content: space-between; align-items: flex-end;">
        <div>
            <h1 style="font-size: 2.5rem; letter-spacing: -1px;">Omni<span style="color:var(--accent)">Engine</span></h1>
            <p style="color:var(--text-dim)">Autonomous Inference Optimization & Hardware Telemetry</p>
        </div>
        <div style="text-align: right; color: var(--text-dim);">
            <div style="font-size: 0.8rem;">Complexity Threshold ($\\theta$): <strong>2.0</strong></div>
            <div style="font-size: 0.8rem;">Session Date: <strong>{datetime.now().strftime('%Y-%m-%d %H:%M')}</strong></div>
        </div>
    </header>

    <div class="kpi-row">
        <div class="kpi-card">
            <h4>Avg. Latency</h4>
            <div class="val">{avg_opt['Latency(s)']}s</div>
            <div class="diff {('positive' if avg_opt['Latency(s)'] < avg_unopt['Latency(s)'] else 'negative') if avg_unopt else ''}">
                {round((avg_unopt['Latency(s)'] - avg_opt['Latency(s)']) / (avg_unopt['Latency(s)'] or 1) * 100, 1) if avg_unopt else 0}% Reduction
            </div>
        </div>
        <div class="kpi-card">
            <h4>Avg. Throughout</h4>
            <div class="val">{avg_opt['Tokens/sec']}</div>
            <div class="diff {('negative' if avg_opt['Tokens/sec'] < avg_unopt['Tokens/sec'] else 'positive') if avg_unopt else ''}">
                {avg_opt['Tokens/sec']} T/s Normalized
            </div>
        </div>
        <div class="kpi-card">
            <h4>Efficiency Index</h4>
            <div class="val" style="color:var(--accent)">{avg_opt['EfficiencyScore']}</div>
            <div class="diff positive">Optimized Architecture</div>
        </div>
        <div class="kpi-card">
            <h4>Hardware Pressure</h4>
            <div class="val">{round((avg_opt['GPU(%)']*0.5 + avg_opt['CPU(%)']*0.5), 1)}%</div>
            <div class="diff" style="color:var(--text-dim)">Averaged Active Load</div>
        </div>
    </div>

    <div class="viva-panel">
        <h3>Thesis Defense: Technical Telemetry Interpretation</h3>
        <p>The system utilizes a <strong>High-Frequency Asynchronous Polling</strong> (50ms) mechanism to capture hardware transients. Rapid GPU fluctuations reported as low utilization during successful token generation are indicative of <strong>Unified Memory Burst Cycles</strong>, where kernel execution finishes between polling windows. Efficiency Scores are calculated using a <strong>Weighted Resource Pressure Model</strong> to fairly penalize background overhead.</p>
    </div>

    <div class="dashboard-grid">
        <div class="chart-area full-width">
            <canvas id="mainChart" height="400"></canvas>
        </div>

        <div class="table-area">
            <h3 class="unopt-header">Table A: Static Baseline (Llama 3.2)</h3>
            <table>
                <thead>
                    <tr><th>Model</th><th>Latency</th><th>T/s</th><th>GPU</th><th>Score</th></tr>
                </thead>
                <tbody>
                    {generate_rows(unopt_data, 'badge-unopt')}
                </tbody>
            </table>
        </div>

        <div class="table-area">
            <h3 class="opt-header">Table B: Edge-Engine (Dynamic Router)</h3>
            <table>
                <thead>
                    <tr><th>Model</th><th>Latency</th><th>T/s</th><th>GPU</th><th>Score</th></tr>
                </thead>
                <tbody>
                    {generate_rows(opt_data, 'badge-opt')}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        const ctx = document.getElementById('mainChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(labels)},
                datasets: [
                    {{
                        label: 'Throughput (Tokens/s)',
                        data: {json.dumps(tokens_data)},
                        backgroundColor: {json.dumps([('rgba(248, 113, 113, 0.7)' if m == 'Unoptimized' else 'rgba(34, 211, 238, 0.7)') for m in modes])},
                        borderRadius: 10,
                        yAxisID: 'y',
                    }},
                    {{
                        label: 'Efficiency Index',
                        data: {json.dumps(eff_data)},
                        type: 'line',
                        borderColor: '#ffffff',
                        borderWidth: 3,
                        pointBackgroundColor: '#22d3ee',
                        pointRadius: 6,
                        yAxisID: 'y1',
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{ 
                        beginAtZero: true, 
                        grid: {{ color: 'rgba(255,255,255,0.05)' }}, 
                        ticks: {{ color: '#9ca3af' }},
                        title: {{ display: true, text: 'Tokens / Second', color: '#9ca3af' }}
                    }},
                    y1: {{ 
                        beginAtZero: true, 
                        position: 'right', 
                        grid: {{ display: false }}, 
                        ticks: {{ color: '#22d3ee' }},
                        title: {{ display: true, text: 'Efficiency Score', color: '#22d3ee' }}
                    }},
                    x: {{ grid: {{ display: false }}, ticks: {{ color: '#9ca3af' }} }}
                }},
                plugins: {{ 
                    legend: {{ position: 'bottom', labels: {{ color: '#9ca3af', font: {{ family: 'Outfit', size: 12 }} }} }},
                    tooltip: {{ backgroundColor: '#11151f', titleFont: {{ size: 14 }}, bodyFont: {{ size: 12 }} }}
                }}
            }}
        }});
    </script>
</body>
</html>"""
    
    with open(output_path, "w", encoding='utf-8') as f:
        f.write(html)

def generate_rows(data, badge_class):
    rows = ""
    for r in reversed(data):
        rows += f"""<tr>
            <td style="font-weight:600;">{r['Model']}</td>
            <td>{r['Latency(s)']}s</td>
            <td><strong>{r['Tokens/sec']}</strong></td>
            <td>{r['GPU(%)']}%</td>
            <td style="color:var(--accent); font-weight:700;">{r['EfficiencyScore']}</td>
        </tr>"""
    return rows

if __name__ == "__main__":
    generate_dashboard()
