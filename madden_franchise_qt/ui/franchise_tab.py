from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSpinBox, QLineEdit, QGroupBox,
    QRadioButton, QMessageBox, QButtonGroup
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class FranchiseTab(QWidget):
    """Tab for managing franchise information"""
    
    # Signals
    week_year_changed = Signal(int, int)
    
    def __init__(self, event_manager):
        super().__init__()
        
        self.event_manager = event_manager
        
        # Set up UI
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI components"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Create franchise info section
        info_group = QGroupBox("Franchise Information")
        info_layout = QVBoxLayout(info_group)
        
        # Team name
        team_layout = QHBoxLayout()
        team_layout.addWidget(QLabel("Team Name:"))
        self.team_name_edit = QLineEdit()
        team_layout.addWidget(self.team_name_edit)
        self.update_team_button = QPushButton("Update")
        self.update_team_button.clicked.connect(self._update_team_name)
        team_layout.addWidget(self.update_team_button)
        info_layout.addLayout(team_layout)
        
        # Week and year
        week_year_layout = QHBoxLayout()
        
        # Week
        week_layout = QHBoxLayout()
        week_layout.addWidget(QLabel("Current Week:"))
        self.week_spinner = QSpinBox()
        self.week_spinner.setRange(1, 17)
        self.week_spinner.setValue(1)
        week_layout.addWidget(self.week_spinner)
        week_year_layout.addLayout(week_layout)
        
        # Year
        year_layout = QHBoxLayout()
        year_layout.addWidget(QLabel("Current Year:"))
        self.year_spinner = QSpinBox()
        self.year_spinner.setRange(1, 30)
        self.year_spinner.setValue(1)
        year_layout.addWidget(self.year_spinner)
        week_year_layout.addLayout(year_layout)
        
        # Update button
        self.update_week_year_button = QPushButton("Update Week/Year")
        self.update_week_year_button.clicked.connect(self._update_week_year)
        week_year_layout.addWidget(self.update_week_year_button)
        
        info_layout.addLayout(week_year_layout)
        
        # Advance week button
        self.advance_button = QPushButton("Advance to Next Week")
        self.advance_button.clicked.connect(self._advance_week)
        info_layout.addWidget(self.advance_button)
        
        main_layout.addWidget(info_group)
        
        # Difficulty section
        difficulty_group = QGroupBox("Event Difficulty")
        difficulty_layout = QVBoxLayout(difficulty_group)
        
        # Create radio buttons for difficulty
        self.difficulty_buttons = QButtonGroup(self)
        
        self.easy_radio = QRadioButton("Easy - More positive events")
        self.medium_radio = QRadioButton("Medium - Balanced events")
        self.hard_radio = QRadioButton("Hard - More challenging events")
        
        self.difficulty_buttons.addButton(self.easy_radio, 0)
        self.difficulty_buttons.addButton(self.medium_radio, 1)
        self.difficulty_buttons.addButton(self.hard_radio, 2)
        
        difficulty_layout.addWidget(self.easy_radio)
        difficulty_layout.addWidget(self.medium_radio)
        difficulty_layout.addWidget(self.hard_radio)
        
        # Set default
        self.medium_radio.setChecked(True)
        
        # Update button
        self.update_difficulty_button = QPushButton("Update Difficulty")
        self.update_difficulty_button.clicked.connect(self._update_difficulty)
        difficulty_layout.addWidget(self.update_difficulty_button)
        
        main_layout.addWidget(difficulty_group)
        
        # Save management section
        save_group = QGroupBox("Save Management")
        save_layout = QVBoxLayout(save_group)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        self.new_franchise_button = QPushButton("New Franchise")
        self.new_franchise_button.clicked.connect(self._new_franchise)
        buttons_layout.addWidget(self.new_franchise_button)
        
        self.save_franchise_button = QPushButton("Save Franchise")
        self.save_franchise_button.clicked.connect(self._save_franchise)
        buttons_layout.addWidget(self.save_franchise_button)
        
        self.load_franchise_button = QPushButton("Load Franchise")
        self.load_franchise_button.clicked.connect(self._load_franchise)
        buttons_layout.addWidget(self.load_franchise_button)
        
        save_layout.addLayout(buttons_layout)
        
        # Current save file
        self.save_file_label = QLabel("No save file loaded")
        save_layout.addWidget(self.save_file_label)
        
        main_layout.addWidget(save_group)
        
        # Instructions
        instructions_group = QGroupBox("Instructions")
        instructions_layout = QVBoxLayout(instructions_group)
        
        instructions_text = """
        1. Create a new franchise or load an existing one
        2. Set your current week and year to match your Madden franchise
        3. Go to the Events tab to roll for random events
        4. Update your roster in the Roster tab
        5. View your event history in the History tab
        
        After each week in your Madden franchise, come back and advance to the next week!
        """
        
        instructions = QLabel(instructions_text)
        instructions.setWordWrap(True)
        instructions_layout.addWidget(instructions)
        
        main_layout.addWidget(instructions_group)
        
        # Stretch to fill space
        main_layout.addStretch()
        
        # Load current data
        self.refresh()
    
    def refresh(self):
        """Refresh tab with current data"""
        # Update franchise info
        franchise_info = self.event_manager.config.get('franchise_info', {})
        self.team_name_edit.setText(franchise_info.get('team_name', ''))
        self.week_spinner.setValue(franchise_info.get('current_week', 1))
        self.year_spinner.setValue(franchise_info.get('current_year', 1))
        
        # Update difficulty
        difficulty = self.event_manager.get_difficulty()
        if difficulty == 'easy':
            self.easy_radio.setChecked(True)
        elif difficulty == 'medium':
            self.medium_radio.setChecked(True)
        elif difficulty == 'hard':
            self.hard_radio.setChecked(True)
        
        # Update save file info
        save_file = franchise_info.get('save_file', '')
        if save_file:
            self.save_file_label.setText(f"Current save file: {save_file}")
        else:
            self.save_file_label.setText("No save file loaded")
    
    def _update_team_name(self):
        """Update the team name"""
        team_name = self.team_name_edit.text().strip()
        if team_name:
            self.event_manager.update_franchise_info(team_name=team_name)
            QMessageBox.information(self, "Success", f"Team name updated to {team_name}")
        else:
            QMessageBox.warning(self, "Error", "Team name cannot be empty")
    
    def _update_week_year(self):
        """Update the week and year"""
        week = self.week_spinner.value()
        year = self.year_spinner.value()
        
        if week < 1 or week > 17:
            QMessageBox.warning(self, "Error", "Week must be between 1 and 17")
            return
        
        if year < 1:
            QMessageBox.warning(self, "Error", "Year must be positive")
            return
        
        self.event_manager.update_franchise_info(week=week, year=year)
        QMessageBox.information(self, "Success", f"Updated to Week {week}, Year {year}")
        
        # Emit signal for main window to update status bar
        self.week_year_changed.emit(week, year)
        
        # Check if main window has update method
        main_window = self.window()
        if hasattr(main_window, 'update_week_year_display'):
            main_window.update_week_year_display()
    
    def _advance_week(self):
        """Advance to the next week"""
        week, year = self.event_manager.get_current_week_year()
        
        # Advance to next week
        if week < 17:
            week += 1
        else:
            week = 1
            year += 1
        
        self.event_manager.update_franchise_info(week=week, year=year)
        self.week_spinner.setValue(week)
        self.year_spinner.setValue(year)
        
        QMessageBox.information(self, "Success", f"Advanced to Week {week}, Year {year}")
        
        # Emit signal for main window to update status bar
        self.week_year_changed.emit(week, year)
        
        # Check if main window has update method
        main_window = self.window()
        if hasattr(main_window, 'update_week_year_display'):
            main_window.update_week_year_display()
    
    def _update_difficulty(self):
        """Update the difficulty level"""
        difficulty = 'medium'
        if self.easy_radio.isChecked():
            difficulty = 'easy'
        elif self.medium_radio.isChecked():
            difficulty = 'medium'
        elif self.hard_radio.isChecked():
            difficulty = 'hard'
        
        self.event_manager.set_difficulty(difficulty)
        QMessageBox.information(self, "Success", f"Difficulty set to {difficulty}")
    
    def _new_franchise(self):
        """Create a new franchise"""
        # Access main window method
        main_window = self.window()
        if hasattr(main_window, 'new_franchise'):
            main_window.new_franchise()
    
    def _save_franchise(self):
        """Save the current franchise"""
        # Access main window method
        main_window = self.window()
        if hasattr(main_window, 'save_franchise'):
            main_window.save_franchise()
    
    def _load_franchise(self):
        """Load a franchise"""
        # Access main window method
        main_window = self.window()
        if hasattr(main_window, 'load_franchise'):
            main_window.load_franchise() 