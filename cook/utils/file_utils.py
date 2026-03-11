"""
File utilities for Cook Optimizer
"""
import os
import json
from pathlib import Path

def ensure_dir(directory):
    """Ensure directory exists"""
    os.makedirs(directory, exist_ok=True)

def read_prompts_from_file(filepath):
    """Read prompts from a file (one per line)"""
    prompts = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    prompts.append(line)
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
    return prompts

def save_json(data, filepath):
    """Save data as JSON"""
    ensure_dir(os.path.dirname(filepath))
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def load_json(filepath):
    """Load JSON data"""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def get_cook_home():
    """Get Cook home directory"""
    home = Path.home() / ".cook"
    ensure_dir(home)
    return home