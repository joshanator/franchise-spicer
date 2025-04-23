#!/usr/bin/env python3
"""
Madden Franchise Event Generator
----------------------------------
A tool to create random events for Madden franchise mode.
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication
from madden_franchise_qt.ui.main_window import MainWindow
from madden_franchise_qt.utils.data_manager import DataManager


def set_application_metadata():
    """Set application metadata"""
    QCoreApplication.setApplicationName("Madden Franchise Event Generator")
    QCoreApplication.setOrganizationName("Madden Tools")
    QCoreApplication.setApplicationVersion("1.0")


def setup_environment():
    """Set up the application environment"""
    # Ensure we're in the project directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)
    
    # Create necessary directories
    for directory in ['data', 'saves']:
        os.makedirs(os.path.join(app_dir, directory), exist_ok=True)


def main():
    """Main application entry point"""
    # Set up environment
    setup_environment()
    
    # Create application
    app = QApplication(sys.argv)
    
    # Reset config.json to defaults at startup
    app_dir = os.path.dirname(os.path.abspath(__file__))
    data_manager = DataManager(app_dir)
    data_manager._create_default_config()  # Force reset config to defaults
    
    # Set application metadata
    set_application_metadata()
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 