from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSpinBox, QLineEdit, QGroupBox,
    QRadioButton, QMessageBox, QButtonGroup, QComboBox,
    QCheckBox, QFormLayout
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont


# Season stages
PRE_SEASON = "Pre-Season"
REGULAR_SEASON_START = "Regular Season (Weeks 1-8)"
REGULAR_SEASON_MID = "Trade Deadline (Week 8)"
REGULAR_SEASON_END = "Regular Season (Weeks 9-18)"
POST_SEASON = "Post-Season"
OFF_SEASON = "Off-Season"

# Week ranges for each season stage
# Pre-season: 1-4
# Regular season start: 5-7
# Regular season mid: 8-15
# Regular season end: 16-22
# Post-season: 23-26
# Off-season: 27+

def get_season_stage_for_week(week):
    """Map a week to its corresponding season stage"""
    if week <= 4:
        return PRE_SEASON
    elif week <= 7:
        return REGULAR_SEASON_START
    elif week <= 15:
        return REGULAR_SEASON_MID
    elif week <= 22:
        return REGULAR_SEASON_END
    elif week <= 26:
        return POST_SEASON
    else:
        return OFF_SEASON

def get_week_for_season_stage(stage):
    """Map a season stage to a default week"""
    if stage == PRE_SEASON:
        return 1
    elif stage == REGULAR_SEASON_START:
        return 5
    elif stage == REGULAR_SEASON_MID:
        return 8
    elif stage == REGULAR_SEASON_END:
        return 16
    elif stage == POST_SEASON:
        return 23
    elif stage == OFF_SEASON:
        return 27
    else:
        return 1  # default


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
        info_layout = QFormLayout()
        info_group.setLayout(info_layout)
        
        # Team name
        team_layout = QHBoxLayout()
        team_layout.addWidget(QLabel("Team Name:"))
        self.team_name_edit = QLineEdit()
        team_layout.addWidget(self.team_name_edit)
        self.update_team_button = QPushButton("Update")
        self.update_team_button.clicked.connect(self._update_team_name)
        team_layout.addWidget(self.update_team_button)
        info_layout.addRow(QLabel("Team Name:"), team_layout)
        
        # Week and year
        week_year_layout = QHBoxLayout()
        
        # Week
        week_layout = QHBoxLayout()
        week_layout.addWidget(QLabel("Current Week:"))
        self.week_spinner = QSpinBox()
        self.week_spinner.setMinimum(1)  # Start from pre-season week 1
        self.week_spinner.setMaximum(27)  # Go through offseason (27)
        self.week_spinner.valueChanged.connect(self._on_week_changed)
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
        
        info_layout.addRow(QLabel("Current Week:"), week_year_layout)
        
        # Season stage dropdown
        season_stage_layout = QHBoxLayout()
        season_stage_layout.addWidget(QLabel("Current Season Stage:"))
        self.season_stage_combo = QComboBox()
        self.season_stage_combo.addItems([PRE_SEASON, REGULAR_SEASON_START, REGULAR_SEASON_MID, REGULAR_SEASON_END, POST_SEASON, OFF_SEASON])
        self.season_stage_combo.currentTextChanged.connect(self._on_season_stage_changed)
        season_stage_layout.addWidget(self.season_stage_combo)
        
        # Season stage update button
        self.update_season_stage_button = QPushButton("Update Season Stage")
        self.update_season_stage_button.clicked.connect(self._update_season_stage)
        season_stage_layout.addWidget(self.update_season_stage_button)
        
        info_layout.addRow(QLabel("Current Season Stage:"), season_stage_layout)
        
        # Advance week button
        self.advance_button = QPushButton("Advance to Next Week")
        self.advance_button.clicked.connect(self._advance_week)
        info_layout.addWidget(self.advance_button)
        
        main_layout.addWidget(info_group)
        
        # Difficulty section
        difficulty_group = QGroupBox("Event Difficulty")
        difficulty_layout = QVBoxLayout(difficulty_group)
        difficulty_layout.setSpacing(15)
        difficulty_layout.setContentsMargins(15, 20, 15, 20)
        
        # Create horizontal layout for difficulty selection
        difficulty_selection_layout = QHBoxLayout()
        
        # Create dropdown for difficulty
        difficulty_label = QLabel("Select difficulty level:")
        difficulty_label.setFont(QFont("Arial", 10))
        difficulty_selection_layout.addWidget(difficulty_label)
        
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems([
            "Cupcake - Very few negative events",
            "Rookie - Fewer challenges",
            "Pro - Balanced events",
            "All-Madden - More challenges",
            "Diabolical - Extreme challenges"
        ])
        self.difficulty_combo.setMinimumHeight(30)
        # Set a fixed width for the combobox to prevent it from stretching
        self.difficulty_combo.setMinimumWidth(200)
        self.difficulty_combo.setMaximumWidth(300)
        difficulty_selection_layout.addWidget(self.difficulty_combo)
        
        # Add stretch to push elements toward the middle/left
        difficulty_selection_layout.addStretch(1)
        
        # Add the selection layout to the main difficulty layout
        difficulty_layout.addLayout(difficulty_selection_layout)
        
        # Update button
        self.update_difficulty_button = QPushButton("Update Difficulty")
        self.update_difficulty_button.setMinimumHeight(30)
        self.update_difficulty_button.clicked.connect(self._update_difficulty)
        difficulty_layout.addWidget(self.update_difficulty_button)
        
        main_layout.addWidget(difficulty_group)
        
        # Save management section
        save_group = QGroupBox("Save Management")
        save_layout = QVBoxLayout(save_group)
        save_layout.setSpacing(15)
        save_layout.setContentsMargins(15, 20, 15, 20)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
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
        
        # Make buttons consistent height
        self.new_franchise_button.setMinimumHeight(30)
        self.save_franchise_button.setMinimumHeight(30)
        self.save_as_franchise_button.setMinimumHeight(30)
        self.load_franchise_button.setMinimumHeight(30)
        
        save_layout.addLayout(buttons_layout)
        
        # Auto-save checkbox
        self.auto_save_checkbox = QCheckBox("Auto-save when changes are made")
        self.auto_save_checkbox.setMinimumHeight(30)
        self.auto_save_checkbox.setToolTip("Automatically save the franchise file when making any changes")
        # Make sure we set the initial state correctly
        self.auto_save_checkbox.setTristate(False)  # Make it a two-state checkbox (not tristate)
        self.auto_save_checkbox.setCheckState(Qt.Unchecked)  # Start unchecked
        # Connect to our handler
        self.auto_save_checkbox.stateChanged.connect(self._toggle_auto_save)
        save_layout.addWidget(self.auto_save_checkbox)
        
        # Current save file
        self.save_file_label = QLabel("No save file loaded")
        save_layout.addWidget(self.save_file_label)
        
        main_layout.addWidget(save_group)
        
        # Instructions
        instructions_group = QGroupBox("Instructions")
        instructions_layout = QVBoxLayout(instructions_group)
        instructions_layout.setSpacing(15)
        instructions_layout.setContentsMargins(15, 20, 15, 20)
        
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
        
        # Ensure group boxes have better visual separation
        info_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 12px; }")
        difficulty_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 12px; }")
        save_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 12px; }")
        instructions_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 12px; }")
    
    def refresh(self):
        """Refresh tab with current data"""
        # Update franchise info
        franchise_info = self.event_manager.config.get('franchise_info', {})
        self.team_name_edit.setText(franchise_info.get('team_name', ''))
        self.week_spinner.setValue(franchise_info.get('current_week', PRE_SEASON))
        self.year_spinner.setValue(franchise_info.get('current_year', 1))
        
        # Update auto-save checkbox
        auto_save = self.event_manager.config.get('auto_save', False)
        print(f"Refresh: auto_save={auto_save}")
        # Set the checkbox state explicitly using setCheckState
        if auto_save:
            self.auto_save_checkbox.setCheckState(Qt.Checked)
        else:
            self.auto_save_checkbox.setCheckState(Qt.Unchecked)
        # The line below is kept for backward compatibility
        self.auto_save_checkbox.setChecked(auto_save)
        
        # Update season stage
        season_stage = get_season_stage_for_week(franchise_info.get('current_week', PRE_SEASON))
        index = self.season_stage_combo.findText(season_stage)
        if index >= 0:
            self.season_stage_combo.setCurrentIndex(index)
        
        # Update difficulty
        difficulty = self.event_manager.get_difficulty()
        difficulty_index = 2  # Default to Pro
        if difficulty == 'cupcake':
            difficulty_index = 0
        elif difficulty == 'rookie':
            difficulty_index = 1
        elif difficulty == 'pro':
            difficulty_index = 2
        elif difficulty == 'all-madden':
            difficulty_index = 3
        elif difficulty == 'diabolical':
            difficulty_index = 4
        self.difficulty_combo.setCurrentIndex(difficulty_index)
        
        # Update save file info - hide the .json extension from display
        save_file = franchise_info.get('save_file', '')
        if save_file:
            # Remove .json extension for display purposes
            display_name = save_file
            # if display_name.lower().endswith('.json'):
            #     display_name = display_name[:-5]  # Remove the .json extension
                
            if auto_save:
                self.save_file_label.setText(f"Current save file: {display_name} (Auto-save ON)")
            else:
                self.save_file_label.setText(f"Current save file: {display_name}")
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
    
    def _on_week_changed(self, week):
        """Update season stage when week changes"""
        # Block signals temporarily to avoid recursive loop
        self.season_stage_combo.blockSignals(True)
        
        # Update the season stage dropdown
        stage = get_season_stage_for_week(week)
        index = self.season_stage_combo.findText(stage)
        if index >= 0:
            self.season_stage_combo.setCurrentIndex(index)
            
        # Re-enable signals
        self.season_stage_combo.blockSignals(False)
    
    def _on_season_stage_changed(self, stage):
        """Update week when season stage changes"""
        # Get the week corresponding to the selected season stage
        week = get_week_for_season_stage(stage)
        
        # Block signals temporarily to avoid recursive loop
        self.week_spinner.blockSignals(True)
        self.week_spinner.setValue(week)
        self.week_spinner.blockSignals(False)
        
        # Also update the franchise info if auto-save is enabled
        if self.event_manager.config.get('auto_save', False):
            if 'franchise_info' not in self.event_manager.config:
                self.event_manager.config['franchise_info'] = {}
            
            self.event_manager.config['franchise_info']['current_week'] = week
            self.event_manager.config['franchise_info']['season_stage'] = stage
            self.event_manager.data_manager.save_config(self.event_manager.config)
    
    def _update_week_year(self):
        """Update the current week and year in the configuration"""
        week = self.week_spinner.value()
        year = self.year_spinner.value()
        
        if week < 1 or week > 27:
            self._show_status_message("Week must be between 1 and 27", error=True)
            return
        
        if year < 1 or year > 30:
            self._show_status_message("Year must be between 1 and 30", error=True)
            return
        
        # Get franchise info or create if it doesn't exist
        if 'franchise_info' not in self.event_manager.config:
            self.event_manager.config['franchise_info'] = {}
        
        # Update config with new values
        self.event_manager.config['franchise_info']['current_week'] = week
        self.event_manager.config['franchise_info']['current_year'] = year
        
        # Also update the season stage to match the week
        stage = get_season_stage_for_week(week)
        self.event_manager.config['franchise_info']['season_stage'] = stage
        
        # Update the season stage dropdown to reflect the change
        index = self.season_stage_combo.findText(stage)
        if index >= 0:
            self.season_stage_combo.setCurrentIndex(index)
        
        # Save the config
        self.event_manager.data_manager.save_config(self.event_manager.config)
        
        # Emit signal for week/year change
        self.week_year_changed.emit(week, year)
        
        self._show_status_message(f"Week updated to {week}, Year updated to {year}", error=False)
    
    def _update_season_stage(self):
        """Update the season stage in the configuration"""
        stage = self.season_stage_combo.currentText()
        
        # Get franchise info or create if it doesn't exist
        if 'franchise_info' not in self.event_manager.config:
            self.event_manager.config['franchise_info'] = {}
        
        # Update config
        self.event_manager.config['franchise_info']['season_stage'] = stage
        
        # Also update the week to match the season stage
        week = get_week_for_season_stage(stage)
        self.event_manager.config['franchise_info']['current_week'] = week
        
        # Update the week spinner to reflect the change
        self.week_spinner.setValue(week)
        
        # Save config
        self.event_manager.data_manager.save_config(self.event_manager.config)
        
        self._show_status_message(f"Season stage updated to {stage}", error=False)
    
    def _advance_week(self):
        """Advance to the next week, handling year transitions"""
        week = self.week_spinner.value()
        year = self.year_spinner.value()
        
        # Advance to next week
        if week < 27:  # Before end of off-season
            week += 1
        else:
            # If end of off-season, move to pre-season of next year
            week = 1  # First week of pre-season
            year += 1
        
        # Update spinners
        self.week_spinner.setValue(week)
        self.year_spinner.setValue(year)
        
        # Update config
        if 'franchise_info' not in self.event_manager.config:
            self.event_manager.config['franchise_info'] = {}
        
        self.event_manager.config['franchise_info']['current_week'] = week
        self.event_manager.config['franchise_info']['current_year'] = year
        
        # Update season stage
        stage = get_season_stage_for_week(week)
        self.event_manager.config['franchise_info']['season_stage'] = stage
        
        # Update UI
        index = self.season_stage_combo.findText(stage)
        if index >= 0:
            self.season_stage_combo.setCurrentIndex(index)
        
        # Save config
        self.event_manager.data_manager.save_config(self.event_manager.config)
        
        # Emit signal
        self.week_year_changed.emit(week, year)
        
        self._show_status_message(f"Advanced to Week {week}, Year {year}", error=False)
    
    def _update_difficulty(self):
        """Update the difficulty level"""
        index = self.difficulty_combo.currentIndex()
        difficulty_map = ['cupcake', 'rookie', 'pro', 'all-madden', 'diabolical']
        difficulty = difficulty_map[index]
        
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
        # Debug the actual state value we're receiving
        print(f"Raw state value: {state}, Qt.Checked value: {Qt.Checked}")
        
        # In Qt, Checked=2, Unchecked=0, PartiallyChecked=1
        # Sometimes the comparison state == Qt.Checked fails, so we check the raw value
        is_checked = (state == Qt.Checked or state == 2)
        
        # Debug print
        print(f"Auto-save checkbox toggled to: {is_checked}")
        
        # Update the config
        self.event_manager.config['auto_save'] = is_checked
        self.event_manager.data_manager.save_config(self.event_manager.config)
        
        # More debug info
        print(f"Config auto_save value after toggle: {self.event_manager.config.get('auto_save')}")
        
        # Update save file label
        save_file = self.event_manager.config.get('franchise_info', {}).get('save_file', '')
        if save_file:
            # Remove .json extension for display purposes
            display_name = save_file
            if display_name.lower().endswith('.json'):
                display_name = display_name[:-5]  # Remove the .json extension
                
            if is_checked:
                self.save_file_label.setText(f"Current save file: {display_name} (Auto-save ON)")
            else:
                self.save_file_label.setText(f"Current save file: {display_name}")
        
        # Always show the appropriate message based on the checkbox state
        if is_checked:
            # If enabled, try an immediate save
            success, message = self.event_manager._try_auto_save()
            
            if success:
                self._show_status_message("Auto-save is now enabled. Your franchise will be saved automatically when changes are made.")
            else:
                self._show_status_message(
                    f"Auto-save is enabled but couldn't perform initial save: {message}. "
                    "Please save your franchise manually first.",
                    error=True
                )
        else:
            # Auto-save was disabled
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

    def set_week_year(self, week, year):
        """Update the week/year spinners."""
        # Block signals temporarily to avoid triggering update cycles
        self.week_spinner.blockSignals(True)
        self.year_spinner.blockSignals(True)
        
        self.week_spinner.setValue(week)
        self.year_spinner.setValue(year)
        
        # Update season stage to match the week
        stage = get_season_stage_for_week(week)
        self.season_stage_combo.setCurrentText(stage)
        
        # Re-enable signals
        self.week_spinner.blockSignals(False)
        self.year_spinner.blockSignals(False) 