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
from PySide6.QtGui import QPalette, QColor
from madden_franchise_qt.ui.main_window import MainWindow
from madden_franchise_qt.utils.data_manager import DataManager

# Get version from version.py or version.txt
def get_version():
    """Get version from version.py (created during builds) or version.txt file"""
    try:
        # First try to import version.py if it exists (created by build script)
        try:
            from madden_franchise_qt.version import VERSION
            return VERSION
        except ImportError:
            pass
        
        # Then try reading from version.txt
        version_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'version.txt')
        with open(version_path, 'r') as f:
            version = f.read().strip()
        return version
    except:
        return "0.1"  # Default fallback version


def set_application_metadata():
    """Set application metadata"""
    version = get_version()
    QCoreApplication.setApplicationName("Madden Franchise Event Generator")
    QCoreApplication.setOrganizationName("Madden Tools")
    QCoreApplication.setApplicationVersion(version)


def setup_environment():
    """Set up the application environment"""
    # Ensure we're in the project directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)
    
    # Create necessary directories
    for directory in ['data', 'saves']:
        os.makedirs(os.path.join(app_dir, directory), exist_ok=True)


def apply_football_theme(app):
    """Apply an NFL-inspired color scheme to the application"""
    # Define colors - NFL inspired but not team specific
    dark_navy = QColor("#0B1C2C")     # Dark navy/charcoal
    medium_navy = QColor("#173753")   # Medium navy
    light_navy = QColor("#234B6E")    # Lighter navy
    silver = QColor("#9EA2A2")        # NFL silver
    silver_light = QColor("#C0C2C4")  # Lighter silver
    maroon = QColor("#862633")        # Muted maroon instead of bright red
    maroon_light = QColor("#9E3542")  # Lighter maroon for hover states
    white = QColor("#FFFFFF")         # White
    light_text = QColor("#F0F0F0")    # Almost white text
    dark_text = QColor("#232323")     # Dark text
    disabled = QColor("#777777")      # Disabled gray
    
    # Create and set the palette
    palette = QPalette()
    
    # Set window/widget background colors
    palette.setColor(QPalette.Window, dark_navy)
    palette.setColor(QPalette.WindowText, light_text)
    palette.setColor(QPalette.Base, medium_navy)
    palette.setColor(QPalette.AlternateBase, light_navy)
    
    # Set text colors
    palette.setColor(QPalette.Text, light_text)
    palette.setColor(QPalette.BrightText, white)
    
    # Set button colors
    palette.setColor(QPalette.Button, silver)
    palette.setColor(QPalette.ButtonText, dark_text)
    
    # Set highlight/selection colors
    palette.setColor(QPalette.Highlight, maroon)
    palette.setColor(QPalette.HighlightedText, white)
    
    # Set disabled colors
    palette.setColor(QPalette.Disabled, QPalette.WindowText, disabled)
    palette.setColor(QPalette.Disabled, QPalette.Text, disabled)
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, disabled)
    
    # Set tooltip colors
    palette.setColor(QPalette.ToolTipBase, dark_navy)
    palette.setColor(QPalette.ToolTipText, light_text)
    
    # Apply the palette
    app.setPalette(palette)
    
    # Create a stylesheet to further customize the appearance
    stylesheet = """
    /* Global styles */
    QWidget {
        font-size: 10pt;
    }
    
    /* Header styles */
    QLabel[objectName="headerLabel"] {
        font-size: 16pt;
        font-weight: bold;
        color: #862633;  /* Muted maroon */
    }
    
    /* Tab widget styles */
    QTabWidget::pane {
        border: 1px solid #9EA2A2;
        border-radius: 4px;
        background-color: #0B1C2C;
    }
    
    QTabBar::tab {
        background-color: #173753;
        color: #F0F0F0;
        min-width: 100px;
        padding: 8px 12px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    
    QTabBar::tab:selected {
        background-color: #9EA2A2;
        color: #0B1C2C;
        font-weight: bold;
    }
    
    QTabBar::tab:hover:!selected {
        background-color: #234B6E;
    }
    
    /* Button styles */
    QPushButton {
        background-color: #9EA2A2;
        color: #0B1C2C;
        border-radius: 4px;
        padding: 6px 12px;
        font-weight: bold;
    }
    
    QPushButton:hover {
        background-color: #C0C2C4;
    }
    
    QPushButton:pressed {
        background-color: #7A7C7C;
    }
    
    QPushButton:disabled {
        background-color: #2A3F53;
        color: #777777;
    }
    
    QPushButton#roll_button {
        background-color: #862633;
        color: #FFFFFF;
        font-size: 12pt;
        padding: 10px;
        border: 1px solid #F0F0F0;
    }
    
    QPushButton#roll_button:hover {
        background-color: #9E3542;
    }
    
    QPushButton#roll_button:pressed {
        background-color: #6E1F2A;
    }
    
    /* Group box styles */
    QGroupBox {
        font-weight: bold;
        background-color: #0B1C2C;
        border: 1px solid #9EA2A2;
        border-radius: 4px;
        margin-top: 16px;
        padding-top: 16px;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 5px 10px;
        background-color: #9EA2A2;
        color: #0B1C2C;
        border-radius: 3px;
    }
    
    /* Input field styles */
    QLineEdit, QTextEdit, QComboBox, QSpinBox {
        background-color: #173753;
        color: #F0F0F0;
        border: 1px solid #9EA2A2;
        border-radius: 4px;
        padding: 4px;
    }
    
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {
        border: 1px solid #862633;
    }
    
    /* List and tree views */
    QTreeView, QListView, QTableView {
        alternate-background-color: #173753;
        background-color: #0B1C2C;
        color: #F0F0F0;
        border: 1px solid #9EA2A2;
        border-radius: 4px;
    }
    
    QTreeView::item:selected, QListView::item:selected, QTableView::item:selected {
        background-color: #862633;
        color: #FFFFFF;
    }
    
    /* Scroll bars */
    QScrollBar:vertical {
        background-color: #0B1C2C;
        width: 12px;
        margin: 0px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #9EA2A2;
        min-height: 20px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #C0C2C4;
    }
    
    QScrollBar:horizontal {
        background-color: #0B1C2C;
        height: 12px;
        margin: 0px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #9EA2A2;
        min-width: 20px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #C0C2C4;
    }
    
    /* Status bar */
    QStatusBar {
        background-color: #0B1C2C;
        color: #F0F0F0;
        border-top: 1px solid #9EA2A2;
    }
    
    /* Menu bar */
    QMenuBar {
        background-color: #0B1C2C;
        color: #F0F0F0;
    }
    
    QMenuBar::item:selected {
        background-color: #9EA2A2;
        color: #0B1C2C;
    }
    
    QMenu {
        background-color: #0B1C2C;
        color: #F0F0F0;
        border: 1px solid #9EA2A2;
    }
    
    QMenu::item:selected {
        background-color: #9EA2A2;
        color: #0B1C2C;
    }
    
    /* Status message styling */
    QLabel[styleSheet*="background-color: #BDE5F8"] {
        background-color: #173753 !important;
        color: #F0F0F0 !important;
        border: 1px solid #9EA2A2;
    }
    
    QLabel[styleSheet*="background-color: #FFBABA"] {
        background-color: #422436 !important;
        color: #FFCCCC !important;
        border: 1px solid #862633;
    }
    """
    
    # Apply the stylesheet
    app.setStyleSheet(stylesheet)


def main(app=None):
    """Main application entry point"""
    # Set up environment
    setup_environment()
    
    # Create application if not provided
    if app is None:
        app = QApplication(sys.argv)
    
    # Reset config.json to defaults at startup
    app_dir = os.path.dirname(os.path.abspath(__file__))
    data_manager = DataManager(app_dir)
    data_manager._create_default_config()  # Force reset config to defaults
    
    # Set application metadata
    set_application_metadata()
    
    # Set application style
    app.setStyle('Fusion')
    
    # Apply football-themed color scheme
    apply_football_theme(app)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 