#!/usr/bin/env python3
"""
Tools copy of test_setup.py (original remains at project root).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from db import initialize_database

if __name__ == '__main__':
    initialize_database()
    print('Initialized DB (tools copy)')
