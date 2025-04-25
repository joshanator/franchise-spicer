#!/usr/bin/env python3
"""
Simple script to output just the event and scenario counts
for use with GitHub Actions. This avoids complex parsing issues.
"""
import json
import sys
from pathlib import Path
from calculate_scenarios import calculate_total_scenarios

def main():
    try:
        # Get the counts
        counts = calculate_total_scenarios()
        
        # Print just the raw numbers (one per line)
        print(counts['total_events'])
        print(counts['total_scenarios'])
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        # Output default values in case of error
        print("76")  # default event count
        print("5033")  # default scenario count
        return 1

if __name__ == "__main__":
    sys.exit(main()) 