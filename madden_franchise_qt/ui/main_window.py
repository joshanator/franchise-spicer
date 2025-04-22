from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QMessageBox, QInputDialog,
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton,
    QSpinBox, QLineEdit, QComboBox, QStatusBar
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont, QAction

import os
import sys

from ..utils.data_manager import DataManager
from ..utils.event_manager import EventManager
from .franchise_tab import FranchiseTab
from .event_tab import EventTab
from .roster_tab import RosterTab
from .history_tab import HistoryTab


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("Madden 25 Franchise Event Generator")
        self.setMinimumSize(QSize(900, 700))
        
        # Initialize data managers
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_manager = DataManager(app_dir)
        self.event_manager = EventManager(self.data_manager)
        
        # Set up UI
        self._init_ui()
        self._create_menu()
        self._create_status_bar()
        
        # Set default tab
        self.tab_widget.setCurrentIndex(0)
    
    def _init_ui(self):
        """Initialize the main UI components"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create header
        header_label = QLabel("MADDEN 25 FRANCHISE EVENT GENERATOR")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.franchise_tab = FranchiseTab(self.event_manager)
        self.event_tab = EventTab(self.event_manager)
        self.roster_tab = RosterTab(self.event_manager)
        self.history_tab = HistoryTab(self.event_manager)
        
        # Add tabs to widget
        self.tab_widget.addTab(self.franchise_tab, "Franchise")
        self.tab_widget.addTab(self.event_tab, "Events")
        self.tab_widget.addTab(self.roster_tab, "Roster")
        self.tab_widget.addTab(self.history_tab, "History")
        
        # Connect signals
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
    
    def _create_menu(self):
        """Create the application menu"""
        # Create menu bar
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        # New franchise action
        new_action = QAction("&New Franchise", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_franchise)
        file_menu.addAction(new_action)
        
        # Load franchise action
        load_action = QAction("&Load Franchise", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load_franchise)
        file_menu.addAction(load_action)
        
        # Save franchise action
        save_action = QAction("&Save Franchise", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_franchise)
        file_menu.addAction(save_action)
        
        # Exit action
        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Settings menu
        settings_menu = menu_bar.addMenu("&Settings")
        
        # Difficulty action
        difficulty_action = QAction("Set &Difficulty", self)
        difficulty_action.triggered.connect(self.set_difficulty)
        settings_menu.addAction(difficulty_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        # About action
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Help action
        help_action = QAction("&Help", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
    
    def _create_status_bar(self):
        """Create the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.status_message = QLabel("Ready")
        self.status_bar.addWidget(self.status_message)
        
        # Add current week/year to status bar
        week, year = self.event_manager.get_current_week_year()
        self.week_year_label = QLabel(f"Week: {week} | Year: {year}")
        self.status_bar.addPermanentWidget(self.week_year_label)
    
    def update_status(self, message):
        """Update the status bar message
        
        Args:
            message: The message to display
        """
        self.status_message.setText(message)
    
    def update_week_year_display(self):
        """Update the week/year display in the status bar"""
        week, year = self.event_manager.get_current_week_year()
        self.week_year_label.setText(f"Week: {week} | Year: {year}")
    
    def new_franchise(self):
        """Create a new franchise"""
        team_name, ok = QInputDialog.getText(
            self, "New Franchise", "Enter Team Name:"
        )
        
        if ok and team_name:
            success, message, config, event_history = self.data_manager.create_new_franchise(team_name)
            
            if success:
                QMessageBox.information(self, "Success", message)
                
                # Update the event manager with the new config
                self.event_manager.reload_config()
                self.event_manager.clear_event_history()  # Clear any previous history
                
                # Refresh all tabs
                self.refresh_all_tabs()
            else:
                QMessageBox.critical(self, "Error", message)
    
    def load_franchise(self):
        """Load a franchise from a save file"""
        save_files = self.data_manager.list_save_files()
        
        if not save_files:
            QMessageBox.information(self, "No Saves", "No save files found.")
            return
        
        selected_file, ok = QInputDialog.getItem(
            self, "Load Franchise", "Select save file:", save_files, 0, False
        )
        
        if ok and selected_file:
            success, message, config, event_history = self.data_manager.load_franchise(selected_file)
            
            if success:
                QMessageBox.information(self, "Success", message)
                
                # Update the event manager with the new config and history
                self.event_manager.reload_config()
                self.event_manager.set_event_history(event_history)
                
                # Refresh all tabs
                self.refresh_all_tabs()
            else:
                QMessageBox.critical(self, "Error", message)
    
    def save_franchise(self):
        """Save the current franchise"""
        custom_name, ok = QInputDialog.getText(
            self, "Save Franchise", "Enter save name (leave blank for automatic naming):"
        )
        
        if ok:
            # Get the config with event history included
            config_with_history = self.event_manager.get_config_with_history()
            
            success, message = self.data_manager.save_franchise(
                config_with_history, custom_name if custom_name else None
            )
            
            if success:
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.critical(self, "Error", message)
    
    def set_difficulty(self):
        """Set the difficulty level"""
        difficulties = ["easy", "medium", "hard"]
        current = self.event_manager.get_difficulty()
        
        difficulty, ok = QInputDialog.getItem(
            self, "Set Difficulty", "Select difficulty level:", 
            difficulties, difficulties.index(current), False
        )
        
        if ok and difficulty:
            if self.event_manager.set_difficulty(difficulty):
                QMessageBox.information(
                    self, "Success", f"Difficulty set to {difficulty}"
                )
    
    def show_about(self):
        """Show the about dialog"""
        about_text = """
        <h3>Madden 25 Franchise Event Generator</h3>
        <p>Version 1.0</p>
        <p>This tool generates random events for your Madden 25 franchise mode to 
        make the experience more dynamic and unpredictable. Events can affect 
        players, coaches, and team circumstances.</p>
        """
        
        QMessageBox.about(self, "About", about_text)
    
    def show_help(self):
        """Show the help dialog"""
        help_text = """
        <h3>How to use this tool:</h3>
        <ol>
            <li>Create or load a franchise</li>
            <li>Set your current week and year</li>
            <li>Go to the Events tab and click "Roll for Event" to generate random events</li>
            <li>View event history in the History tab</li>
            <li>Update your roster in the Roster tab</li>
        </ol>
        <p><b>Event difficulty affects how challenging the events will be for your franchise.</b></p>
        <ul>
            <li>Easy: More positive events, less negative</li>
            <li>Medium: Balanced mix of events</li>
            <li>Hard: More challenges and negative events</li>
        </ul>
        """
        
        QMessageBox.information(self, "Help", help_text)
    
    def refresh_all_tabs(self):
        """Refresh all tabs"""
        self.franchise_tab.refresh()
        self.event_tab.refresh()
        self.roster_tab.refresh()
        self.history_tab.refresh()
        self.update_week_year_display()
    
    def _on_tab_changed(self, index):
        """Handle tab changed event
        
        Args:
            index: The index of the newly selected tab
        """
        # Reload the config when changing tabs
        self.event_manager.reload_config()
        
        # Get the current tab and refresh it
        current_tab = self.tab_widget.widget(index)
        if hasattr(current_tab, 'refresh'):
            current_tab.refresh() 