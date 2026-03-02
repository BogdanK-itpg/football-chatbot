import re
import json
import os

# Tools copy of chatbot.py for offline inspection; original remains in src/
INTENTS_FILE = os.path.join(os.path.dirname(__file__), 'intents.json')

def load_intents():
    try:
        with open(INTENTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('intents', [])
    except Exception:
        return []

if __name__ == '__main__':
    print('Tools chatbot copy - intents:', len(load_intents()))
