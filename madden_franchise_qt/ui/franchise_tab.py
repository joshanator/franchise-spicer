from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSpinBox, QLineEdit, QGroupBox,
    QRadioButton, QMessageBox, QButtonGroup, QComboBox,
    QCheckBox
)
from PySide6.QtCore import Qt, Signal, QTimer
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
        
        # Status message for feedback
        self.status_message = QLabel("")
        self.status_message.setStyleSheet("QLabel { color: #00529B; background-color: #BDE5F8; padding: 8px; border-radius: 4px; }")
        self.status_message.setWordWrap(True)
        self.status_message.setVisible(False)
        main_layout.addWidget(self.status_message)
        
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
        
        # Season stage dropdown
        season_stage_layout = QHBoxLayout()
        season_stage_layout.addWidget(QLabel("Current Season Stage:"))
        self.season_stage_combo = QComboBox()
        self.season_stage_combo.addItems([
            "Pre-Season",
            "Regular Season (Weeks 1-8)",
            "Trade Deadline (Week 8)",
            "Regular Season (Weeks 9-18)",
            "Playoffs",
            "Free Agency"
        ])
        season_stage_layout.addWidget(self.season_stage_combo)
        
        # Season stage update button
        self.update_season_stage_button = QPushButton("Update Season Stage")
        self.update_season_stage_button.clicked.connect(self._update_season_stage)
        season_stage_layout.addWidget(self.update_season_stage_button)
        
        info_layout.addLayout(season_stage_layout)
        
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
        
        self.save_franchise_button = QPushButton("Save")
        self.save_franchise_button.clicked.connect(self._save_franchise)
        buttons_layout.addWidget(self.save_franchise_button)
        
        self.save_as_franchise_button = QPushButton("Save As...")
        self.save_as_franchise_button.clicked.connect(self._save_franchise_as)
        buttons_layout.addWidget(self.save_as_franchise_button)
        
        self.load_franchise_button = QPushButton("Load Franchise")
        self.load_franchise_button.clicked.connect(self._load_franchise)
        buttons_layout.addWidget(self.load_franchise_button)
        
        save_layout.addLayout(buttons_layout)
        
        # Auto-save checkbox
        self.auto_save_checkbox = QCheckBox("Auto-save when changes are made")
        self.auto_save_checkbox.setToolTip("Automatically save the franchise file when making any changes")
        self.auto_save_checkbox.stateChanged.connect(self._toggle_auto_save)
        save_layout.addWidget(self.auto_save_checkbox)
        
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
        
        # Update auto-save checkbox
        auto_save = self.event_manager.config.get('auto_save', False)
        print(f"Refresh: auto_save={auto_save}")
        self.auto_save_checkbox.setChecked(auto_save)
        
        # Update season stage
        season_stage = franchise_info.get('season_stage', 'Pre-Season')
        index = self.season_stage_combo.findText(season_stage)
        if index >= 0:
            self.season_stage_combo.setCurrentIndex(index)
        
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
            if auto_save:
                self.save_file_label.setText(f"Current save file: {save_file} (Auto-save ON)")
            else:
                self.save_file_label.setText(f"Current save file: {save_file}")
        else:
            self.save_file_label.setText("No save file loaded")
    
    def _update_team_name(self):
        """Update the team name"""
        team_name = self.team_name_edit.text().strip()
        if team_name:
            self.event_manager.update_franchise_info(team_name=team_name)
            self._show_status_message(f"Team name updated to {team_name}")
        else:
            self._show_status_message("Team name cannot be empty", error=True)
    
    def _update_week_year(self):
        """Update the week and year"""
        week = self.week_spinner.value()
        year = self.year_spinner.value()
        
        if week < 1 or week > 17:
            self._show_status_message("Week must be between 1 and 17", error=True)
            return
        
        if year < 1:
            self._show_status_message("Year must be positive", error=True)
            return
        
        self.event_manager.update_franchise_info(week=week, year=year)
        self._show_status_message(f"Updated to Week {week}, Year {year}")
        
        # Emit signal for main window to update status bar
        self.week_year_changed.emit(week, year)
        
        # Check if main window has update method
        main_window = self.window()
        if hasattr(main_window, 'update_week_year_display'):
            main_window.update_week_year_display()
    
    def _update_season_stage(self):
        """Update the current season stage"""
        season_stage = self.season_stage_combo.currentText()
        
        # Update the franchise info with season stage
        if 'franchise_info' not in self.event_manager.config:
            self.event_manager.config['franchise_info'] = {}
        
        self.event_manager.config['franchise_info']['season_stage'] = season_stage
        self.event_manager.data_manager.save_config(self.event_manager.config)
        
        self._show_status_message(f"Season stage updated to {season_stage}")
    
    def _advance_week(self):
        """Advance to the next week"""
        week, year = self.event_manager.get_current_week_year()
        
        # Advance to next week
        if week < 17:
            week += 1
            
            # Auto-update season stage
            current_stage = self.season_stage_combo.currentText()
            new_stage = current_stage
            
            if week == 8:
                new_stage = "Trade Deadline (Week 8)"
            elif week > 8 and week <= 18 and current_stage in ["Pre-Season", "Regular Season (Weeks 1-8)", "Trade Deadline (Week 8)"]:
                new_stage = "Regular Season (Weeks 9-18)"
            
            if new_stage != current_stage:
                index = self.season_stage_combo.findText(new_stage)
                if index >= 0:
                    self.season_stage_combo.setCurrentIndex(index)
                    self.event_manager.config['franchise_info']['season_stage'] = new_stage
                    self.event_manager.data_manager.save_config(self.event_manager.config)
        else:
            week = 1
            year += 1
            
            # Reset to pre-season for new year
            new_stage = "Pre-Season"
            index = self.season_stage_combo.findText(new_stage)
            if index >= 0:
                self.season_stage_combo.setCurrentIndex(index)
                self.event_manager.config['franchise_info']['season_stage'] = new_stage
                self.event_manager.data_manager.save_config(self.event_manager.config)
        
        self.event_manager.update_franchise_info(week=week, year=year)
        self.week_spinner.setValue(week)
        self.year_spinner.setValue(year)
        
        self._show_status_message(f"Advanced to Week {week}, Year {year}")
        
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
        self._show_status_message(f"Difficulty set to {difficulty}")
    
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
    
    def _save_franchise_as(self):
        """Save the current franchise as a new file"""
        # Access main window method
        main_window = self.window()
        if hasattr(main_window, 'save_franchise_as'):
            main_window.save_franchise_as()
    
    def _load_franchise(self):
        """Load a franchise"""
        # Access main window method
        main_window = self.window()
        if hasattr(main_window, 'load_franchise'):
            main_window.load_franchise()
    
    def _toggle_auto_save(self, state):
        """Toggle auto-save feature
        
        Args:
            state: The checkbox state
        """
        is_checked = state == Qt.Checked
        
        # Debug print
        print(f"Auto-save checkbox toggled to: {is_checked}")
        
        # Update the config
        self.event_manager.config['auto_save'] = is_checked
        self.event_manager.data_manager.save_config(self.event_manager.config)
        
        # More debug info
        print(f"Config auto_save value after toggle: {self.event_manager.config.get('auto_save')}")
        
        if is_checked:
            # Trigger an immediate auto-save to verify it's working
            success, message = self.event_manager._try_auto_save()
            
            if success:
                self._show_auto_save_status(True)
                
                # Update save file label to indicate auto-save is on
                save_file = self.event_manager.config.get('franchise_info', {}).get('save_file', '')
                if save_file:
                    self.save_file_label.setText(f"Current save file: {save_file} (Auto-save ON)")
            else:
                self._show_status_message(
                    f"Auto-save is enabled but couldn't perform initial save: {message}. "
                    "Please save your franchise manually first.",
                    error=True
                )
        else:
            self._show_auto_save_status(False)
            
            # Update save file label to indicate auto-save is off
            save_file = self.event_manager.config.get('franchise_info', {}).get('save_file', '')
            if save_file:
                self.save_file_label.setText(f"Current save file: {save_file}")
    
    def _show_auto_save_status(self, enabled):
        """Show in-UI auto-save status message
        
        Args:
            enabled: Whether auto-save is enabled
        """
        if enabled:
            self._show_status_message("Auto-save is now enabled. Your franchise will be saved automatically when changes are made.")
        else:
            self._show_status_message("Auto-save is now disabled. Remember to save your franchise manually.")
    
    def _show_status_message(self, message, error=False):
        """Show a status message
        
        Args:
            message: The message to display
            error: Whether this is an error message
        """
        if error:
            self.status_message.setStyleSheet("QLabel { color: #D8000C; background-color: #FFBABA; padding: 8px; border-radius: 4px; }")
        else:
            self.status_message.setStyleSheet("QLabel { color: #00529B; background-color: #BDE5F8; padding: 8px; border-radius: 4px; }")
        
        self.status_message.setText(message)
        self.status_message.setVisible(True)
        
        # Hide the message after 5 seconds
        QTimer.singleShot(5000, lambda: self.status_message.setVisible(False)) 