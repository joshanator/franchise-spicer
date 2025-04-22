#!/usr/bin/env python3
"""
Launcher for Madden 25 Franchise Event Generator
"""

import os
import sys
import traceback
import importlib.util

# Set the directory to the root of the project
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    # Check if PySide6 is installed
    if importlib.util.find_spec("PySide6") is None:
        print("PySide6 is not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PySide6"])
        print("PySide6 successfully installed.")
    
    # Import and run the application
    from madden_franchise_qt.main import main
    main()
    
except Exception as e:
    print(f"Error starting application: {e}")
    print(f"Traceback: {traceback.format_exc()}")
    input("Press Enter to exit...")
    sys.exit(1) 