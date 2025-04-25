from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QMessageBox, QInputDialog,
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton,
    QSpinBox, QLineEdit, QComboBox, QStatusBar, QDialog
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QIcon, QFont, QAction

import os
import sys

from ..utils.data_manager import DataManager
from ..utils.event_manager import EventManager
from .franchise_tab import FranchiseTab
from .event_tab import EventTab
from .roster_tab import RosterTab
from .history_tab import HistoryTab
from .effects_tab import EffectsTab

# Get version
def get_version():
    """Get version from version.py (created during builds) or version.txt file"""
    try:
        # First try to import version.py if it exists (created by build script)
        try:
            from ..version import VERSION
            return VERSION
        except ImportError:
            pass
        
        # Then try reading from version.txt
        version_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'version.txt')
        with open(version_path, 'r') as f:
            version = f.read().strip()
        return version
    except:
        return "0.1"  # Default fallback version


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Get version
        self.version = get_version()
        
        # Set window properties
        self.setWindowTitle(f"Madden Franchise Event Generator v{self.version}")
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
        
        # Show startup dialog requiring franchise creation/loading
        QTimer.singleShot(200, self.show_startup_dialog)
    
    def _init_ui(self):
        """Initialize the main UI components"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create header
        header_label = QLabel("MADDEN FRANCHISE EVENT GENERATOR")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setObjectName("headerLabel")
        main_layout.addWidget(header_label)
        
        # Version label
        version_label = QLabel(f"Version {self.version}")
        version_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(version_label)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.franchise_tab = FranchiseTab(self.event_manager)
        self.event_tab = EventTab(self.event_manager)
        self.roster_tab = RosterTab(self.event_manager)
        self.history_tab = HistoryTab(self.event_manager)
        self.effects_tab = EffectsTab(self.event_manager)
        
        # Add tabs to widget
        self.tab_widget.addTab(self.franchise_tab, "Franchise")
        self.tab_widget.addTab(self.event_tab, "Events")
        self.tab_widget.addTab(self.roster_tab, "Roster")
        self.tab_widget.addTab(self.history_tab, "History")
        self.tab_widget.addTab(self.effects_tab, "Effects")
        
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
        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_franchise)
        file_menu.addAction(save_action)
        
        # Save As franchise action
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_franchise_as)
        file_menu.addAction(save_as_action)
        
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
    
    def show_startup_dialog(self):
        """Show startup dialog requiring user to create or load a franchise"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Welcome to Madden Franchise Event Generator")
        dialog.setModal(True)
        dialog.setMinimumWidth(400)
        
        # Prevent closing the dialog with X button
        dialog.setWindowFlag(Qt.WindowCloseButtonHint, False)
        
        layout = QVBoxLayout(dialog)
        
        # Add logo or title
        title = QLabel("Welcome to Madden Franchise Event Generator")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Add instruction
        instruction = QLabel("To begin, you must create a new franchise or load an existing one.")
        instruction.setWordWrap(True)
        instruction.setAlignment(Qt.AlignCenter)
        layout.addWidget(instruction)
        
        # Add spacer
        layout.addSpacing(20)
        
        # Add buttons
        btn_layout = QHBoxLayout()
        
        new_btn = QPushButton("Create New Franchise")
        new_btn.setMinimumHeight(40)
        new_btn.clicked.connect(lambda: self.handle_startup_selection(dialog, "new"))
        btn_layout.addWidget(new_btn)
        
        load_btn = QPushButton("Load Existing Franchise")
        load_btn.setMinimumHeight(40)
        
        # Check if there are any save files to load
        save_files = self.data_manager.list_save_files()
        if not save_files:
            load_btn.setEnabled(False)
            load_btn.setToolTip("No save files found")
        
        load_btn.clicked.connect(lambda: self.handle_startup_selection(dialog, "load"))
        btn_layout.addWidget(load_btn)
        
        layout.addLayout(btn_layout)
        
        # Add exit button
        exit_btn = QPushButton("Exit")
        exit_btn.clicked.connect(self.close)
        layout.addWidget(exit_btn)
        
        dialog.show()
    
    def handle_startup_selection(self, dialog, action):
        """Handle the startup dialog selection
        
        Args:
            dialog: The dialog to close if successful
            action: Either 'new' or 'load'
        """
        if action == "new":
            success = self.new_franchise()
            if success:
                dialog.accept()
        elif action == "load":
            success = self.load_franchise()
            if success:
                dialog.accept()
    
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
                return True
            else:
                QMessageBox.critical(self, "Error", message)
        
        return False
    
    def load_franchise(self):
        """Load a franchise from a save file"""
        save_files = self.data_manager.list_save_files()
        
        if not save_files:
            QMessageBox.information(self, "No Saves", "No save files found.")
            return False
        
        # Create a mapping of display names (without .json) to actual filenames
        display_names = []
        name_to_file_map = {}
        
        for save_file in save_files:
            display_name = save_file
            if display_name.lower().endswith('.json'):
                display_name = display_name[:-5]
            display_names.append(display_name)
            name_to_file_map[display_name] = save_file
        
        selected_display, ok = QInputDialog.getItem(
            self, "Load Franchise", "Select save file:", display_names, 0, False
        )
        
        if ok and selected_display:
            # Map the selected display name back to the actual filename
            selected_file = name_to_file_map[selected_display]
            
            success, message, config, event_history = self.data_manager.load_franchise(selected_file)
            
            if success:
                QMessageBox.information(self, "Success", message)
                
                # Update the event manager with the new config and history
                self.event_manager.reload_config()
                self.event_manager.set_event_history(event_history)
                
                # Refresh all tabs
                self.refresh_all_tabs()
                return True
            else:
                QMessageBox.critical(self, "Error", message)
        
        return False
    
    def save_franchise(self):
        """Save the current franchise to the current file"""
        # Get the current save file
        current_save_file = self.event_manager.config.get('franchise_info', {}).get('save_file', '')
        
        if not current_save_file:
            # If no current save file, do a save as
            return self.save_franchise_as()
        
        # Get the config with event history included
        config_with_history = self.event_manager.get_config_with_history()
        
        success, message = self.data_manager.save_franchise(
            config_with_history, current_save_file
        )
        
        if success:
            # Hide .json extension in status message
            display_name = current_save_file
            if display_name.lower().endswith('.json'):
                display_name = display_name[:-5]
            self.status_message.setText(f"Saved to {display_name}")
            return True
        else:
            QMessageBox.critical(self, "Error", f"Failed to save: {message}")
            return False
    
    def save_franchise_as(self):
        """Save the current franchise to a new file"""
        custom_name, ok = QInputDialog.getText(
            self, "Save Franchise As", "Enter save name (leave blank for automatic naming):"
        )
        
        if ok:
            # Get the config with event history included
            config_with_history = self.event_manager.get_config_with_history()
            
            success, message = self.data_manager.save_franchise(
                config_with_history, custom_name if custom_name else None
            )
            
            if success:
                QMessageBox.information(self, "Success", message)
                return True
            else:
                QMessageBox.critical(self, "Error", message)
                return False
        
        return False
    
    def set_difficulty(self):
        """Set the difficulty level"""
        difficulties = ["cupcake", "rookie", "pro", "all-madden", "diabolical"]
        current = self.event_manager.get_difficulty()
        
        difficulty, ok = QInputDialog.getItem(
            self, "Set Difficulty", "Select difficulty level:", 
            difficulties, difficulties.index(current) if current in difficulties else 2, False
        )
        
        if ok and difficulty:
            if self.event_manager.set_difficulty(difficulty):
                QMessageBox.information(
                    self, "Success", f"Difficulty set to {difficulty}"
                )
    
    def show_about(self):
        """Show the about dialog"""
        about_text = f"""
        <h3>Madden Franchise Event Generator</h3>
        <p>Version {self.version}</p>
        <p>This tool generates random events for your Madden franchise mode to 
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
            <li>Check active effects in the Effects tab</li>
            <li>Update your roster in the Roster tab</li>
        </ol>
        <p><b>Event difficulty affects how challenging the events will be for your franchise.</b></p>
        <ul>
            <li>Cupcake: Very few negative events, more positive outcomes</li>
            <li>Rookie: Fewer challenges, suitable for casual play</li>
            <li>Pro: Balanced mix of events (default)</li>
            <li>All-Madden: More challenges and negative events</li>
            <li>Diabolical: Extreme challenges, for the masochistic player</li>
        </ul>
        """
        
        QMessageBox.information(self, "Help", help_text)
    
    def refresh_all_tabs(self):
        """Refresh all tabs"""
        self.franchise_tab.refresh()
        self.event_tab.refresh()
        self.roster_tab.refresh()
        self.history_tab.refresh()
        self.effects_tab.refresh()
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