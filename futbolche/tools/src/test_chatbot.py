#!/usr/bin/env python3
"""Tools copy of src/test_chatbot.py (original remains in src/)"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import chatbot

if __name__ == '__main__':
    print('Tools test runner')
    intent, params = chatbot.parse_input('помощ')
    print(intent, params)
