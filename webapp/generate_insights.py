#!/usr/bin/env python3
"""
Batch script to generate strategic insights for all applications.
This is a one-time process that calls OpenAI API to analyze all data.

Usage:
    python generate_insights.py

Estimated cost: ~$5-10 depending on number of applications and transcript length.
Uses GPT-4o for highest quality insights.
"""

import sys
import os

# Ensure webapp modules can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from insight_generator import run_full_insight_generation

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         AVANGRID APM STRATEGIC INSIGHT GENERATOR             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

This script will:
1. Analyze all applications using GPT-4o
2. Generate deep strategic insights per application
3. Identify portfolio-level patterns and opportunities
4. Store all insights in the database

Estimated cost: $5-10 (one-time)
Estimated time: 2-5 minutes

    """)

    response = input("Continue? (y/n): ")

    if response.lower() == 'y':
        run_full_insight_generation()
    else:
        print("\n❌ Cancelled by user")
