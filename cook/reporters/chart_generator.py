"""
Chart generation utilities for HTML reports
"""
import json

class ChartGenerator:
    def create_latency_chart(self, unopt, opt):
        """Generate latency comparison chart"""
        return f"""
        new Chart(document.getElementById('latencyChart'), {{
            type: 'bar',
            data: {{
                labels: ['Unoptimized', 'Optimized'],
                datasets: [{{
                    label: 'Latency (seconds)',
                    data: [{unopt.get('latency', 0)}, {opt.get('latency', 0)}],
                    backgroundColor: ['#f87171', '#4ade80'],
                    borderRadius: 8
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        grid: {{ color: '#2d3748' }},
                        ticks: {{ color: '#9ca3af' }}
                    }},
                    x: {{
                        grid: {{ display: false }},
                        ticks: {{ color: '#9ca3af' }}
                    }}
                }}
            }}
        }});
        """
    
    def create_efficiency_chart(self, unopt, opt):
        """Generate efficiency score chart"""
        return f"""
        new Chart(document.getElementById('efficiencyChart'), {{
            type: 'bar',
            data: {{
                labels: ['Unoptimized', 'Optimized'],
                datasets: [{{
                    label: 'Efficiency Score',
                    data: [{unopt.get('efficiency', 0)}, {opt.get('efficiency', 0)}],
                    backgroundColor: ['#fb923c', '#60a5fa'],
                    borderRadius: 8
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        grid: {{ color: '#2d3748' }},
                        ticks: {{ color: '#9ca3af' }}
                    }},
                    x: {{
                        grid: {{ display: false }},
                        ticks: {{ color: '#9ca3af' }}
                    }}
                }}
            }}
        }});
        """
    
    def create_resource_chart(self, unopt, opt):
        """Generate resource usage chart"""
        return f"""
        new Chart(document.getElementById('resourceChart'), {{
            type: 'bar',
            data: {{
                labels: ['Unoptimized', 'Optimized'],
                datasets: [
                    {{
                        label: 'CPU Usage (%)',
                        data: [{unopt.get('cpu_usage', 0)}, {opt.get('cpu_usage', 0)}],
                        backgroundColor: '#60a5fa',
                        borderRadius: 8
                    }},
                    {{
                        label: 'RAM Usage (%)',
                        data: [{unopt.get('ram_usage', 0)}, {opt.get('ram_usage', 0)}],
                        backgroundColor: '#f87171',
                        borderRadius: 8
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ labels: {{ color: '#9ca3af' }} }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        grid: {{ color: '#2d3748' }},
                        ticks: {{ color: '#9ca3af' }}
                    }},
                    x: {{
                        grid: {{ display: false }},
                        ticks: {{ color: '#9ca3af' }}
                    }}
                }}
            }}
        }});
        """
    
    def create_tokens_chart(self, unopt, opt):
        """Generate tokens per second chart"""
        return f"""
        new Chart(document.getElementById('tokensChart'), {{
            type: 'bar',
            data: {{
                labels: ['Unoptimized', 'Optimized'],
                datasets: [{{
                    label: 'Tokens/Second',
                    data: [{unopt.get('tokens_per_sec', 0)}, {opt.get('tokens_per_sec', 0)}],
                    backgroundColor: ['#c084fc', '#f472b6'],
                    borderRadius: 8
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        grid: {{ color: '#2d3748' }},
                        ticks: {{ color: '#9ca3af' }}
                    }},
                    x: {{
                        grid: {{ display: false }},
                        ticks: {{ color: '#9ca3af' }}
                    }}
                }}
            }}
        }});
        """