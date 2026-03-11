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
                results.append(row)
            except (ValueError, KeyError): continue

    if not results: return

    # FILTER: ONLY take the last 5 Unoptimized and last 5 Optimized runs as requested
    unopt_data = [r for r in results if r['Mode'] == 'Unoptimized'][-5:]
    opt_data = [r for r in results if r['Mode'] == 'Optimized'][-5:]
    
    # Combined list for the journal (sorted by time/index)
    display_results = sorted(unopt_data + opt_data, key=lambda x: results.index(x))

    def get_avg(data_list):
        if not data_list: return None
        count = len(data_list)
        return {
            'Latency(s)': round(sum(r['Latency(s)'] for r in data_list) / count, 2),
            'EfficiencyScore': round(sum(r['EfficiencyScore'] for r in data_list) / count, 2),
            'Tokens/sec': round(sum(r['Tokens/sec'] for r in data_list) / count, 2),
            'CPU(%)': round(sum(r['CPU(%)'] for r in data_list) / count, 1),
            'RAM(%)': round(sum(r['RAM(%)'] for r in data_list) / count, 1),
            'Model': data_list[-1]['Model'], # Latest model used
            'Count': count
        }

    avg_unopt = get_avg(unopt_data)
    avg_opt = get_avg(opt_data)

    # Chart data
    labels = [f"Run {i+1}" for i in range(len(display_results))]
    tokens_data = [r['Tokens/sec'] for r in display_results]
    eff_data = [r['EfficiencyScore'] for r in display_results]
    modes = [r['Mode'] for r in display_results]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inference Insights | Focused Analytics</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg: #05060a;
            --surface: #0f121a;
            --card: #161a25;
            --border: rgba(255, 255, 255, 0.08);
            --accent: #22d3ee;
            --baseline: #f87171;
            --text-main: #f3f4f6;
            --text-dim: #9ca3af;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Outfit', sans-serif; }}
        body {{ background-color: var(--bg); color: var(--text-main); padding: 40px; min-height: 100vh; }}
        header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--border); padding-bottom: 15px; margin-bottom: 30px; }}
        header h1 {{ font-size: 2.2rem; font-weight: 700; color: var(--accent); }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-areas: "stats graph" "table table";
            grid-template-columns: 420px 1fr;
            gap: 25px;
        }}

        .stats-col {{ grid-area: stats; display: flex; flex-direction: column; gap: 20px; }}
        .avg-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 20px; padding: 25px; border-left: 6px solid #ccc; }}
        .avg-card.unopt {{ border-left-color: var(--baseline); }}
        .avg-card.opt {{ border-left-color: var(--accent); }}
        
        .metrics-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 15px; }}
        .m-item {{ display: flex; flex-direction: column; }}
        .m-item span:first-child {{ font-size: 0.7rem; color: var(--text-dim); text-transform: uppercase; }}
        .m-item span:last-child {{ font-size: 1.3rem; font-weight: 700; }}

        .graph-area {{ grid-area: graph; background: var(--card); border: 1px solid var(--border); border-radius: 24px; padding: 30px; }}
        .table-area {{ grid-area: table; background: var(--card); border: 1px solid var(--border); border-radius: 24px; padding: 30px; margin-top: 10px; }}
        
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th {{ text-align: left; padding: 15px; color: var(--text-dim); border-bottom: 2px solid var(--border); font-size: 0.85rem; }}
        td {{ padding: 15px; border-bottom: 1px solid var(--border); font-size: 0.95rem; }}
        .badge {{ padding: 4px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; }}
        .badge-opt {{ background: rgba(34, 211, 238, 0.1); color: var(--accent); }}
        .badge-unopt {{ background: rgba(248, 113, 113, 0.1); color: var(--baseline); }}
    </style>
</head>
<body>
    <header>
        <h1>Session Audit Pro</h1>
        <div style="text-align: right; color: var(--text-dim);">
            Focus Group: Latest 5 Runs per Mode | Total Snapshots: {len(display_results)}
        </div>
    </header>

    <div class="dashboard-grid">
        <div class="stats-col">
            <div class="avg-card unopt">
                <div style="display:flex; justify-content:space-between; color:var(--text-dim); font-size:0.8rem;">
                    <span>Baseline (Last 5)</span>
                    <span>{avg_unopt['Model'] if avg_unopt else 'N/A'}</span>
                </div>
                {render_metrics(avg_unopt)}
            </div>
            <div class="avg-card opt">
                <div style="display:flex; justify-content:space-between; color:var(--text-dim); font-size:0.8rem;">
                    <span>Elite (Last 5)</span>
                    <span style="color:var(--accent);">{avg_opt['Model'] if avg_opt else 'N/A'}</span>
                </div>
                {render_metrics(avg_opt)}
            </div>
            <div style="padding: 15px; background: rgba(34,211,238,0.03); border-radius: 12px; font-size: 0.8rem; border: 1px dashed var(--border);">
                Notice: The system switches models based on real-time RAM usage and complexity score.
            </div>
        </div>

        <div class="graph-area">
            <canvas id="mainChart" height="350"></canvas>
        </div>

        <div class="table-area">
            <h3>Consolidated Inference Logs (Focus Group)</h3>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Mode</th>
                        <th>Model</th>
                        <th>Latency</th>
                        <th>Tokens/s</th>
                        <th>CPU/RAM %</th>
                        <th>Efficiency</th>
                    </tr>
                </thead>
                <tbody>
                    {generate_table_body(display_results)}
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
                        label: 'Throughput (T/s)',
                        data: {json.dumps(tokens_data)},
                        backgroundColor: {json.dumps(['rgba(248, 113, 113, 0.7)' if m == 'Unoptimized' else 'rgba(34, 211, 238, 0.7)' for m in modes])},
                        borderRadius: 6
                    }},
                    {{
                        label: 'Efficiency Index',
                        data: {json.dumps(eff_data)},
                        type: 'line',
                        borderColor: '#ffffff',
                        borderWidth: 2,
                        pointRadius: 4,
                        fill: false,
                        yAxisID: 'y1'
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#9ca3af' }} }},
                    y1: {{ position: 'right', grid: {{ display: false }}, ticks: {{ color: '#22d3ee' }} }},
                    x: {{ grid: {{ display: false }}, ticks: {{ color: '#9ca3af' }} }}
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
    </div>"""

def generate_table_body(results):
    rows = ""
    for i, r in enumerate(reversed(results)):
        badge = "badge-opt" if r['Mode'] == 'Optimized' else "badge-unopt"
        rows += f"""
        <tr>
            <td>#{len(results)-i}</td>
            <td><span class="badge {badge}">{r['Mode']}</span></td>
            <td style="font-weight:600;">{r['Model']}</td>
            <td>{r['Latency(s)']}s</td>
            <td><strong>{r['Tokens/sec']}</strong></td>
            <td>{r['CPU(%)']}% / {r['RAM(%)']}%</td>
            <td style="font-weight:700; color:var(--accent);">{r['EfficiencyScore']}</td>
        </tr>"""
    return rows

if __name__ == "__main__":
    generate_dashboard()
