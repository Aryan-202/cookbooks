cook-optimizer/
├── setup.py
├── README.md
├── cook/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── commands.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── benchmark.py
│   │   ├── optimizer.py
│   │   ├── monitor.py
│   │   └── ollama_client.py
│   ├── analyzers/
│   │   ├── __init__.py
│   │   └── prompt_analyzer.py
│   ├── reporters/
│   │   ├── __init__.py
│   │   ├── html_reporter.py
│   │   └── chart_generator.py
│   └── utils/
│       ├── __init__.py
│       └── file_utils.py
├── configs/
│   └── model_config.json
└── requirements.txt