#!/usr/bin/env python3
"""
Launcher for Madden Franchise Event Generator
"""

import os
import sys
import traceback
import importlib.util

# Fix for Qt dialogs on macOS
if sys.platform == 'darwin':
    os.environ['QT_MAC_WANTS_LAYER'] = '1'

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
    
    # Check if appdirs is installed
    if importlib.util.find_spec("appdirs") is None:
        print("appdirs is not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "appdirs"])
        print("appdirs successfully installed.")
    
    # Import and run the application
    from madden_franchise_qt.main import main
    
    # Import QApplication and QIcon to set app icon
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QIcon
    
    # Set app icon
    app = QApplication(sys.argv)
    icon_path = os.path.join(project_root, 'resources', 'logo1.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    main(app)  # Pass the app instance to main
    
except Exception as e:
    print(f"Error starting application: {e}")
    print(f"Traceback: {traceback.format_exc()}")
    input("Press Enter to exit...")
    sys.exit(1) 