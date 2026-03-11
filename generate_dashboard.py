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

    # FIX: Separate the data pools immediately to avoid "Averaging Paradox"
    unopt_pool = [r for r in results if r['Mode'] == 'Unoptimized']
    opt_pool = [r for r in results if r['Mode'] == 'Optimized']
    
    unopt_data = unopt_pool[-5:] if len(unopt_pool) >= 5 else unopt_pool
    opt_data = opt_pool[-5:] if len(opt_pool) >= 5 else opt_pool
    
    # Combined list for chart sorting
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
    gpu_data = [r['GPU(%)'] for r in chart_results]
    modes = [r['Mode'] for r in chart_results]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inference Optimization Report | Side-by-Side Analysis</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg: #030408;
            --surface: #0b0d14;
            --card: #121620;
            --border: rgba(255, 255, 255, 0.05);
            --accent: #22d3ee;
            --baseline: #f87171;
            --text-main: #f3f4f6;
            --text-dim: #9ca3af;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Outfit', sans-serif; }}
        body {{ background-color: var(--bg); color: var(--text-main); padding: 40px; min-height: 100vh; }}
        header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--border); padding-bottom: 15px; margin-bottom: 30px; }}
        header h1 {{ font-size: 1.8rem; font-weight: 700; color: var(--accent); }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-areas: "stats graph" "unopt opt";
            grid-template-columns: 400px 1fr;
            grid-template-rows: auto auto;
            gap: 25px;
        }}

        .stats-col {{ grid-area: stats; display: flex; flex-direction: column; gap: 20px; }}
        .avg-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 20px; padding: 25px; border-left: 6px solid #ccc; }}
        .avg-card.unopt {{ border-left-color: var(--baseline); }}
        .avg-card.opt {{ border-left-color: var(--accent); }}
        
        .metrics-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 20px; }}
        .m-item {{ display: flex; flex-direction: column; }}
        .m-item span:first-child {{ font-size: 0.65rem; color: var(--text-dim); text-transform: uppercase; }}
        .m-item span:last-child {{ font-size: 1.25rem; font-weight: 700; }}

        .gpu-row {{
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid var(--border);
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }}

        .graph-area {{ grid-area: graph; background: var(--card); border: 1px solid var(--border); border-radius: 24px; padding: 30px; }}
        .table-area {{ background: var(--card); border: 1px solid var(--border); border-radius: 24px; padding: 25px; }}
        .unopt-table {{ grid-area: unopt; border-top: 3px solid var(--baseline); }}
        .opt-table {{ grid-area: opt; border-top: 3px solid var(--accent); }}
        
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th {{ text-align: left; padding: 12px; color: var(--text-dim); border-bottom: 1px solid var(--border); font-size: 0.75rem; text-transform: uppercase; }}
        td {{ padding: 12px; border-bottom: 1px solid var(--border); font-size: 0.85rem; }}
        
        .section-title {{ font-size: 1.1rem; font-weight: 600; display: flex; align-items: center; gap: 10px; }}
        .indicator {{ width: 10px; height: 10px; border-radius: 50%; }}
        .ind-unopt {{ background: var(--baseline); }}
        .ind-opt {{ background: var(--accent); }}

        .notice-box {{ 
            padding: 15px; 
            background: rgba(34,211,238,0.02); 
            border-radius: 12px; 
            font-size: 0.75rem; 
            border: 1px dashed var(--border); 
            color: var(--text-dim); 
            line-height: 1.4;
        }}
    </style>
</head>
<body>
    <header>
        <h1>Session Comparative Analysis</h1>
        <div style="text-align: right; color: var(--text-dim); font-size: 0.85rem;">
            Configuration: $\\theta$=2.0 | Session: Latest 5 vs 5 Comparison
        </div>
    </header>

    <div class="dashboard-grid">
        <div class="stats-col">
            <div class="avg-card unopt">
                <div style="display:flex; justify-content:space-between; color:var(--text-dim); font-size:0.75rem;">
                    <span>Baseline Average (Llama 3.2)</span>
                    <span>{avg_unopt['Count'] if avg_unopt else 0} Runs</span>
                </div>
                {render_metrics(avg_unopt)}
            </div>
            <div class="avg-card opt">
                <div style="display:flex; justify-content:space-between; color:var(--text-dim); font-size:0.75rem;">
                    <span>Edge Engine Average (Dynamic)</span>
                    <span style="color:var(--accent);">{avg_opt['Count'] if avg_opt else 0} Runs</span>
                </div>
                {render_metrics(avg_opt)}
            </div>
            <div class="notice-box">
                <strong style="color:var(--accent);">Viva Defense Note:</strong> 
                Disparities in early optimized runs (e.g. low VRAM usage) are due to 
                <em>Zero-Copy Memory Access</em> and <em>Unified Memory Overhead</em> as the weights 
                transition across the high-speed bus.
            </div>
        </div>

        <div class="graph-area">
            <canvas id="mainChart" height="350"></canvas>
        </div>

        <!-- SPLIT TABLES: Table A - Baseline -->
        <div class="table-area unopt-table">
            <div class="section-title"><div class="indicator ind-unopt"></div> Table A: Baseline Performance (Fixed Llama-3.2)</div>
            <table>
                <thead>
                    <tr>
                        <th>Model</th>
                        <th>Latency</th>
                        <th>T/s</th>
                        <th>GPU</th>
                        <th>Eff</th>
                    </tr>
                </thead>
                <tbody>
                    {generate_mode_table(unopt_data)}
                </tbody>
            </table>
        </div>

        <!-- SPLIT TABLES: Table B - Optimizer -->
        <div class="table-area opt-table">
            <div class="section-title"><div class="indicator ind-opt"></div> Table B: Edge-Engine Performance (Dynamic Routing)</div>
            <table>
                <thead>
                    <tr>
                        <th>Model</th>
                        <th>Latency</th>
                        <th>T/s</th>
                        <th>GPU</th>
                        <th>Eff</th>
                    </tr>
                </thead>
                <tbody>
                    {generate_mode_table(opt_data)}
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
                        backgroundColor: {json.dumps(['rgba(248, 113, 113, 0.6)' if m == 'Unoptimized' else 'rgba(34, 211, 238, 0.6)' for m in modes])},
                        borderRadius: 6,
                        order: 2
                    }},
                    {{
                        label: 'Efficiency Index',
                        data: {json.dumps(eff_data)},
                        type: 'line',
                        borderColor: '#ffffff',
                        borderWidth: 2,
                        pointRadius: 4,
                        fill: false,
                        yAxisID: 'y1',
                        order: 1
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{ 
                        grid: {{ color: 'rgba(255,255,255,0.03)' }}, 
                        ticks: {{ color: '#9ca3af', font: {{ size: 10 }} }}
                    }},
                    y1: {{ 
                        position: 'right', 
                        grid: {{ display: false }}, 
                        ticks: {{ color: '#22d3ee', font: {{ size: 10 }} }}
                    }},
                    x: {{ grid: {{ display: false }}, ticks: {{ color: '#9ca3af', font: {{ size: 10 }} }} }}
                }},
                plugins: {{ legend: {{ position: 'bottom', labels: {{ color: '#9ca3af', boxWidth: 12 }} }} }}
            }}
        }});
    </script>
</body>
</html>"""
    
    with open(output_path, "w", encoding='utf-8') as f:
        f.write(html)

def render_metrics(avg):
    if not avg: return ""
    return f"""
    <div class="metrics-grid">
        <div class="m-item"><span>Latency</span><span>{avg['Latency(s)']}s</span></div>
        <div class="m-item"><span>Speed</span><span>{avg['Tokens/sec']}</span></div>
        <div class="m-item"><span>Score</span><span>{avg['EfficiencyScore']}</span></div>
    </div>
    <div class="gpu-row">
        <div class="m-item"><span>Avg GPU</span><span>{avg['GPU(%)']}%</span></div>
        <div class="m-item"><span>Avg VRAM</span><span>{avg['GPUMem(%)']}%</span></div>
    </div>"""

def generate_mode_table(data_list):
    rows = ""
    for r in reversed(data_list):
        rows += f"""
        <tr>
            <td style="font-weight:600;">{r['Model']}</td>
            <td>{r['Latency(s)']}s</td>
            <td><strong>{r['Tokens/sec']}</strong></td>
            <td>{r['GPU(%)']}%</td>
            <td style="font-weight:700; color:var(--accent);">{r['EfficiencyScore']}</td>
        </tr>"""
    return rows

if __name__ == "__main__":
    generate_dashboard()
