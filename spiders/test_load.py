import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'

def test_load():
    try:
        with open(DATA_DIR / 'matches.json', 'r', encoding='utf-8') as f:
            matches = json.load(f)['matches']
        print(f"Loaded {len(matches)} matches.")
        for m in matches:
            print(f"- {m['id']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_load()
