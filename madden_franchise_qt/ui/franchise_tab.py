from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSpinBox, QLineEdit, QGroupBox,
    QRadioButton, QMessageBox, QButtonGroup, QComboBox,
    QCheckBox, QFormLayout, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont

# Add direct version handling
import os
import sys

# Function to get version directly
def get_version_directly():
    """Get version from version.txt file"""
    try:
        # Read from version.txt
        version_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'version.txt')
        print(f"Version path: {version_path}")
        
        if os.path.exists(version_path):
            with open(version_path, 'r') as f:
                version = f.read().strip()
            print(f"Version read from file: {version}")
            return version
    except Exception as e:
        print(f"Error reading version: {e}")
    print("Using default version 1.0")
    return "1.0"  # Default fallback version

# Season stages
PRE_SEASON = "Pre-Season"
REGULAR_SEASON_START = "regular-season-start"
REGULAR_SEASON_MID = "regular-season-mid"
REGULAR_SEASON_END = "regular-season-end"
POST_SEASON = "Post-Season"
OFF_SEASON = "Off-Season"

# Display values for season stages
PRE_SEASON_DISPLAY = "Pre-Season (Weeks 1-4)"
REGULAR_SEASON_START_DISPLAY = "Regular Season (Weeks 1-8)"
REGULAR_SEASON_MID_DISPLAY = "Trade Deadline (Week 8)"
REGULAR_SEASON_END_DISPLAY = "Regular Season (Weeks 9-18)"
POST_SEASON_DISPLAY = "Playoffs (Weeks 19-22)"
OFF_SEASON_DISPLAY = "Off-Season (Week 23+)"

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

def get_display_for_season_stage(stage):
    """Convert backend season stage value to display value"""
    if stage == PRE_SEASON:
        return PRE_SEASON_DISPLAY
    elif stage == REGULAR_SEASON_START:
        return REGULAR_SEASON_START_DISPLAY
    elif stage == REGULAR_SEASON_MID:
        return REGULAR_SEASON_MID_DISPLAY
    elif stage == REGULAR_SEASON_END:
        return REGULAR_SEASON_END_DISPLAY
    elif stage == POST_SEASON:
        return POST_SEASON_DISPLAY
    elif stage == OFF_SEASON:
        return OFF_SEASON_DISPLAY
    else:
        return stage  # Fallback to the stage name itself

def get_season_stage_from_display(display_value):
    """Convert display value back to backend season stage value"""
    if display_value == PRE_SEASON_DISPLAY:
        return PRE_SEASON
    elif display_value == REGULAR_SEASON_START_DISPLAY:
        return REGULAR_SEASON_START
    elif display_value == REGULAR_SEASON_MID_DISPLAY:
        return REGULAR_SEASON_MID
    elif display_value == REGULAR_SEASON_END_DISPLAY:
        return REGULAR_SEASON_END
    elif display_value == POST_SEASON_DISPLAY:
        return POST_SEASON
    elif display_value == OFF_SEASON_DISPLAY:
        return OFF_SEASON
    else:
        return display_value  # Fallback to the value itself

def get_week_display(week):
    """Convert numeric week to user-friendly display string"""
    if week <= 4:
        return f"Pre-Season Week {week}"
    elif week <= 22:
        return f"Week {week - 4}"  # Regular season weeks are numbered 1-18 in-game
    elif week <= 26:
        return f"Playoff Week {week - 22}"  # Playoff weeks numbered 1-4
    else:
        return f"Off-Season"

def get_week_for_season_stage(stage):
    """Map a season stage to a default week"""
    if stage == PRE_SEASON:
        return 1
    elif stage == REGULAR_SEASON_START:
        return 5
    elif stage == REGULAR_SEASON_MID:
        return 12
    elif stage == REGULAR_SEASON_END:
        return 13
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
        self.version = get_version_directly()  # Get the correct version
        
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
        
        # Create a scroll area to contain all content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)  # Remove the frame
        
        # Create a container widget for the scroll area
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        
        # Create franchise info section
        info_group = QGroupBox("Franchise Information")
        info_layout = QFormLayout()
        info_layout.setSpacing(10)  # Add spacing between form rows
        info_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)  # Allow fields to expand
        info_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Align labels to the left
        info_group.setLayout(info_layout)
        
        # Team name
        team_widget = QWidget()
        team_layout = QVBoxLayout(team_widget)
        team_layout.setContentsMargins(0, 0, 0, 0)
        team_layout.setSpacing(10)
        
        # Team name in a single row with update button
        team_name_layout = QHBoxLayout()
        team_name_layout.setSpacing(5)
        
        team_name_label = QLabel("Team Name:")
        team_name_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        team_name_layout.addWidget(team_name_label)
        
        self.team_name_edit = QLineEdit()
        self.team_name_edit.setMinimumHeight(30)  # Consistent height
        self.team_name_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        team_name_layout.addWidget(self.team_name_edit)
        
        self.update_team_button = QPushButton("Update")
        self.update_team_button.setMinimumHeight(30)  # Consistent height
        self.update_team_button.clicked.connect(self._update_team_name)
        team_name_layout.addWidget(self.update_team_button)
        
        team_layout.addLayout(team_name_layout)
        
        info_layout.addRow("", team_widget)
        
        # Week and year
        week_year_widget = QWidget()
        week_year_layout = QVBoxLayout(week_year_widget)  # Changed to vertical for better small window handling
        week_year_layout.setSpacing(10)
        week_year_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        
        # Week
        week_layout = QHBoxLayout()
        week_layout.setSpacing(5)
        week_label = QLabel("Current Week:")
        week_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        week_layout.addWidget(week_label)
        
        # Replace spinner with combo box for user-friendly display
        self.week_combo = QComboBox()
        self.week_combo.setMinimumHeight(30)
        self.week_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # Populate with all possible weeks and their display names
        self._populate_week_combo()
        self.week_combo.currentIndexChanged.connect(self._on_week_combo_changed)
        week_layout.addWidget(self.week_combo)
        week_year_layout.addLayout(week_layout)
        
        # Year
        year_layout = QHBoxLayout()
        year_layout.setSpacing(5)
        year_label = QLabel("Current Year:")
        year_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        year_layout.addWidget(year_label)
        self.year_spinner = QSpinBox()
        self.year_spinner.setRange(1, 30)
        self.year_spinner.setValue(1)
        self.year_spinner.setMinimumHeight(30)
        self.year_spinner.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        year_layout.addWidget(self.year_spinner)
        week_year_layout.addLayout(year_layout)
        
        # Update button in the same row as year
        self.update_week_year_button = QPushButton("Update Week/Year")
        self.update_week_year_button.setMinimumHeight(30)
        self.update_week_year_button.clicked.connect(self._update_week_year)
        year_layout.addWidget(self.update_week_year_button)
        
        info_layout.addRow("", week_year_widget)
        
        # Season stage dropdown
        season_stage_widget = QWidget()
        season_stage_layout = QVBoxLayout(season_stage_widget)
        season_stage_layout.setContentsMargins(0, 0, 0, 0)
        season_stage_layout.setSpacing(10)
        
        # Label and dropdown in one row with update button
        stage_layout = QHBoxLayout()
        stage_layout.setSpacing(10)
        
        season_stage_label = QLabel("Current Season Stage:")
        season_stage_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        stage_layout.addWidget(season_stage_label)
        
        self.season_stage_combo = QComboBox()
        self.season_stage_combo.setMinimumHeight(30)
        self.season_stage_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.season_stage_combo.addItems([
            PRE_SEASON_DISPLAY,
            REGULAR_SEASON_START_DISPLAY,
            REGULAR_SEASON_MID_DISPLAY,
            REGULAR_SEASON_END_DISPLAY,
            POST_SEASON_DISPLAY,
            OFF_SEASON_DISPLAY
        ])
        self.season_stage_combo.currentTextChanged.connect(self._on_season_stage_changed)
        stage_layout.addWidget(self.season_stage_combo)
        
        self.update_season_stage_button = QPushButton("Update Season Stage")
        self.update_season_stage_button.setMinimumHeight(30)
        self.update_season_stage_button.clicked.connect(self._update_season_stage)
        stage_layout.addWidget(self.update_season_stage_button)
        
        season_stage_layout.addLayout(stage_layout)
        
        info_layout.addRow("", season_stage_widget)
        
        # Advance week button - in its own row
        advance_layout = QHBoxLayout()
        self.advance_button = QPushButton("Advance to Next Week")
        self.advance_button.setMinimumHeight(30)
        self.advance_button.clicked.connect(self._advance_week)
        advance_layout.addWidget(self.advance_button)
        advance_layout.addStretch(1)  # Push button to the left
        info_layout.addRow("", advance_layout)
        
        scroll_layout.addWidget(info_group)
        
        # Difficulty section
        difficulty_group = QGroupBox("Event Difficulty")
        difficulty_layout = QVBoxLayout(difficulty_group)
        difficulty_layout.setSpacing(15)
        difficulty_layout.setContentsMargins(15, 20, 15, 20)
        
        # Create horizontal layout for difficulty selection with update button
        difficulty_selection_layout = QHBoxLayout()
        difficulty_selection_layout.setSpacing(10)
        
        # Create dropdown for difficulty
        difficulty_label = QLabel("Select difficulty level:")
        difficulty_label.setFont(QFont("Arial", 10))
        difficulty_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
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
        self.difficulty_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        difficulty_selection_layout.addWidget(self.difficulty_combo)
        
        # Update button
        self.update_difficulty_button = QPushButton("Update Difficulty")
        self.update_difficulty_button.setMinimumHeight(30)
        self.update_difficulty_button.clicked.connect(self._update_difficulty)
        difficulty_selection_layout.addWidget(self.update_difficulty_button)
        
        # Add the selection layout to the main difficulty layout
        difficulty_layout.addLayout(difficulty_selection_layout)
        
        # Add unrealistic events checkbox
        unrealistic_events_layout = QHBoxLayout()
        self.unrealistic_events_checkbox = QCheckBox("Enable unrealistic events")
        self.unrealistic_events_checkbox.setMinimumHeight(30)
        self.unrealistic_events_checkbox.setToolTip("Include wacky, 'unrealistic' events in the event pool")
        self.unrealistic_events_checkbox.setTristate(False)  # Make it a two-state checkbox
        self.unrealistic_events_checkbox.setCheckState(Qt.Unchecked)  # Start unchecked
        self.unrealistic_events_checkbox.stateChanged.connect(self._toggle_unrealistic_events)
        unrealistic_events_layout.addWidget(self.unrealistic_events_checkbox)
        unrealistic_events_layout.addStretch(1)  # Push checkbox to the left
        difficulty_layout.addLayout(unrealistic_events_layout)
        
        scroll_layout.addWidget(difficulty_group)
        
        # Save management section
        save_group = QGroupBox("Save Management")
        save_layout = QVBoxLayout(save_group)
        save_layout.setSpacing(15)
        save_layout.setContentsMargins(15, 20, 15, 20)
        
        # Buttons layout - make buttons wrap when window is small
        buttons_widget = QWidget()
        buttons_flow_layout = QVBoxLayout(buttons_widget)  # Changed to vertical layout for better small window handling
        buttons_flow_layout.setSpacing(10)
        buttons_flow_layout.setContentsMargins(0, 0, 0, 0)
        
        # First row of buttons
        buttons_row1 = QHBoxLayout()
        self.new_franchise_button = QPushButton("New Franchise")
        self.new_franchise_button.clicked.connect(self._new_franchise)
        buttons_row1.addWidget(self.new_franchise_button)
        
        self.save_franchise_button = QPushButton("Save")
        self.save_franchise_button.clicked.connect(self._save_franchise)
        buttons_row1.addWidget(self.save_franchise_button)
        buttons_row1.addStretch(1)
        buttons_flow_layout.addLayout(buttons_row1)
        
        # Second row of buttons
        buttons_row2 = QHBoxLayout()
        self.save_as_franchise_button = QPushButton("Save As...")
        self.save_as_franchise_button.clicked.connect(self._save_franchise_as)
        buttons_row2.addWidget(self.save_as_franchise_button)
        
        self.load_franchise_button = QPushButton("Load Franchise")
        self.load_franchise_button.clicked.connect(self._load_franchise)
        buttons_row2.addWidget(self.load_franchise_button)
        buttons_row2.addStretch(1)
        buttons_flow_layout.addLayout(buttons_row2)
        
        # Make buttons consistent height
        self.new_franchise_button.setMinimumHeight(30)
        self.save_franchise_button.setMinimumHeight(30)
        self.save_as_franchise_button.setMinimumHeight(30)
        self.load_franchise_button.setMinimumHeight(30)
        
        save_layout.addWidget(buttons_widget)
        
        # Auto-save checkbox layout
        auto_save_layout = QHBoxLayout()
        self.auto_save_checkbox = QCheckBox("Auto-save when changes are made")
        self.auto_save_checkbox.setMinimumHeight(30)
        self.auto_save_checkbox.setToolTip("Automatically save the franchise file when making any changes")
        # Make sure we set the initial state correctly
        self.auto_save_checkbox.setTristate(False)  # Make it a two-state checkbox (not tristate)
        self.auto_save_checkbox.setCheckState(Qt.Unchecked)  # Start unchecked
        # Connect to our handler
        self.auto_save_checkbox.stateChanged.connect(self._toggle_auto_save)
        auto_save_layout.addWidget(self.auto_save_checkbox)
        auto_save_layout.addStretch(1)  # Push checkbox to the left
        save_layout.addLayout(auto_save_layout)
        
        # Current save file layout
        save_file_layout = QHBoxLayout()
        self.save_file_label = QLabel("No save file loaded")
        self.save_file_label.setMinimumHeight(30)
        self.save_file_label.setWordWrap(True)  # Allow long filenames to wrap
        save_file_layout.addWidget(self.save_file_label)
        save_file_layout.addStretch(1)  # Push label to the left
        save_layout.addLayout(save_file_layout)
        
        scroll_layout.addWidget(save_group)
        
        # Instructions
        instructions_group = QGroupBox("Instructions")
        instructions_layout = QVBoxLayout(instructions_group)
        instructions_layout.setSpacing(15)
        instructions_layout.setContentsMargins(15, 20, 15, 20)
        
        # Add version label at the top of instructions
        version_label = QLabel(f"TheChumpiest's Franchise Event Generator - Version {self.version}")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setFont(QFont("Arial", 10, QFont.Bold))
        instructions_layout.addWidget(version_label)
        
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
        instructions.setFont(QFont("Arial", 10))
        instructions.setStyleSheet("padding: 5px;")
        instructions.setMinimumHeight(120)  # Give enough height for the text
        instructions_layout.addWidget(instructions)
        
        scroll_layout.addWidget(instructions_group)
        
        # Set the scroll content as the scroll area's widget
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # Set minimum size for whole tab
        self.setMinimumWidth(500)  # Minimum width that looks reasonable
        
        # Load current data
        self.refresh()
        
        # Ensure group boxes have better visual separation
        info_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 12px; }")
        difficulty_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 12px; }")
        save_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 12px; }")
        instructions_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 12px; }")
    
    def _populate_week_combo(self):
        """Populate the week combo box with all possible weeks and their display names"""
        self.week_combo.clear()
        
        # Maps display text to actual week number
        self.week_map = {}
        
        # Add all possible weeks (1-27)
        for week in range(1, 28):
            display_text = get_week_display(week)
            self.week_combo.addItem(display_text)
            self.week_map[display_text] = week
    
    def refresh(self):
        """Refresh tab with current data"""
        # Update franchise info
        franchise_info = self.event_manager.config.get('franchise_info', {})
        self.team_name_edit.setText(franchise_info.get('team_name', ''))
        
        # Get current week and year
        current_week = franchise_info.get('current_week', 1)
        current_year = franchise_info.get('current_year', 1)
        
        # Make sure the week combo is populated
        if self.week_combo.count() == 0:
            self._populate_week_combo()
        
        # Update week display
        week_display = get_week_display(current_week)
        index = self.week_combo.findText(week_display)
        if index >= 0:
            # Block signals to prevent triggering the update callback
            self.week_combo.blockSignals(True)
            self.week_combo.setCurrentIndex(index)
            self.week_combo.blockSignals(False)
        
        # Update year display - block signals here too
        self.year_spinner.blockSignals(True)
        self.year_spinner.setValue(current_year)
        self.year_spinner.blockSignals(False)
        
        # Get auto-save status for later
        auto_save = self.event_manager.config.get('auto_save', False)
        
        # Get unrealistic events status
        unrealistic_events_enabled = self.event_manager.config.get('unrealistic_events_enabled', False)
        
        # Set auto-save checkbox based on config
        # Don't block signals as we want this to trigger display update
        self.auto_save_checkbox.setCheckState(Qt.Checked if auto_save else Qt.Unchecked)
        
        # Set unrealistic events checkbox based on config
        self.unrealistic_events_checkbox.setCheckState(Qt.Checked if unrealistic_events_enabled else Qt.Unchecked)
        
        # Update season stage display
        current_stage = franchise_info.get('season_stage', 'Pre-Season')
        stage_display = get_display_for_season_stage(current_stage)
        
        # Block signals to prevent triggering the update callback
        self.season_stage_combo.blockSignals(True)
        
        index = self.season_stage_combo.findText(stage_display)
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
            if display_name.lower().endswith('.json'):
                display_name = display_name[:-5]  # Remove the .json extension
                
            label_text = f"Current save file: {display_name}"
            
            # Add status flags
            status_flags = []
            if auto_save:
                status_flags.append("Auto-save ON")
            else:
                status_flags.append("Auto-save OFF")
                
            if unrealistic_events_enabled:
                status_flags.append("Unrealistic events ON")
                
            if status_flags:
                label_text += f" ({', '.join(status_flags)})"
                
            self.save_file_label.setText(label_text)
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
    
    def _on_week_combo_changed(self, index):
        """Handle week combo box selection change"""
        if index < 0:
            return
            
        # Get the display text
        display_text = self.week_combo.currentText()
        
        # Get the actual week number
        week = self.week_map.get(display_text, 1)
        
        # Update season stage based on week
        self._on_week_changed(week)
    
    def _on_week_changed(self, week):
        """Update season stage when week changes"""
        # Block signals temporarily to avoid recursive loop
        self.season_stage_combo.blockSignals(True)
        
        # Update the season stage dropdown
        stage = get_season_stage_for_week(week)
        stage_display = get_display_for_season_stage(stage)
        index = self.season_stage_combo.findText(stage_display)
        if index >= 0:
            self.season_stage_combo.setCurrentIndex(index)
            
        # Re-enable signals
        self.season_stage_combo.blockSignals(False)
    
    def _on_season_stage_changed(self, stage_display):
        """Update week when season stage changes"""
        # Convert display value to backend value
        stage = get_season_stage_from_display(stage_display)
        
        # Get the week corresponding to the selected season stage
        week = get_week_for_season_stage(stage)
        
        # Block signals temporarily to avoid recursive loop
        self.week_combo.blockSignals(True)
        
        # Update the week combo to match
        week_display = get_week_display(week)
        index = self.week_combo.findText(week_display)
        if index >= 0:
            self.week_combo.setCurrentIndex(index)
        
        self.week_combo.blockSignals(False)
        
        # Also update the franchise info if auto-save is enabled
        if self.event_manager.config.get('auto_save', False):
            if 'franchise_info' not in self.event_manager.config:
                self.event_manager.config['franchise_info'] = {}
            
            self.event_manager.config['franchise_info']['current_week'] = week
            self.event_manager.config['franchise_info']['season_stage'] = stage  # Store internal value
            self.event_manager.data_manager.save_config(self.event_manager.config)
    
    def _update_week_year(self):
        """Update the current week and year in the configuration"""
        # Get the display text
        display_text = self.week_combo.currentText()
        
        # Get the actual week number from our map
        week = self.week_map.get(display_text, 1)
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
        self.event_manager.config['franchise_info']['season_stage'] = stage  # Store internal value
        
        # Update the season stage dropdown to reflect the change
        stage_display = get_display_for_season_stage(stage)
        index = self.season_stage_combo.findText(stage_display)
        if index >= 0:
            self.season_stage_combo.setCurrentIndex(index)
        
        # Save the config
        self.event_manager.data_manager.save_config(self.event_manager.config)
        
        # Emit signal for week/year change
        self.week_year_changed.emit(week, year)
        
        # Use user-friendly week display in status message
        self._show_status_message(f"Updated to {display_text}, Year {year}", error=False)
    
    def _update_season_stage(self):
        """Update the season stage in the configuration"""
        stage_display = self.season_stage_combo.currentText()
        stage = get_season_stage_from_display(stage_display)
        
        # Get franchise info or create if it doesn't exist
        if 'franchise_info' not in self.event_manager.config:
            self.event_manager.config['franchise_info'] = {}
        
        # Update config
        self.event_manager.config['franchise_info']['season_stage'] = stage  # Store internal value
        
        # Also update the week to match the season stage
        week = get_week_for_season_stage(stage)
        self.event_manager.config['franchise_info']['current_week'] = week
        
        # Update the week combo to reflect the change
        week_display = get_week_display(week)
        index = self.week_combo.findText(week_display)
        if index >= 0:
            self.week_combo.blockSignals(True)
            self.week_combo.setCurrentIndex(index)
            self.week_combo.blockSignals(False)
        
        # Save config
        self.event_manager.data_manager.save_config(self.event_manager.config)
        
        self._show_status_message(f"Season stage updated to {stage_display}", error=False)
    
    def _advance_week(self):
        """Advance to the next week, handling year transitions"""
        # Get the display text
        display_text = self.week_combo.currentText()
        
        # Get the actual week number from our map
        week = self.week_map.get(display_text, 1)
        year = self.year_spinner.value()
        
        # Advance to next week
        if week < 27:  # Before end of off-season
            week += 1
        else:
            # If end of off-season, move to pre-season of next year
            week = 1  # First week of pre-season
            year += 1
        
        # Update week combo
        week_display = get_week_display(week)
        index = self.week_combo.findText(week_display)
        if index >= 0:
            self.week_combo.blockSignals(True)
            self.week_combo.setCurrentIndex(index)
            self.week_combo.blockSignals(False)
        
        # Update year spinner
        self.year_spinner.setValue(year)
        
        # Update config
        if 'franchise_info' not in self.event_manager.config:
            self.event_manager.config['franchise_info'] = {}
        
        self.event_manager.config['franchise_info']['current_week'] = week
        self.event_manager.config['franchise_info']['current_year'] = year
        
        # Update season stage
        stage = get_season_stage_for_week(week)
        self.event_manager.config['franchise_info']['season_stage'] = stage  # Store internal value
        
        # Update UI
        stage_display = get_display_for_season_stage(stage)
        index = self.season_stage_combo.findText(stage_display)
        if index >= 0:
            self.season_stage_combo.setCurrentIndex(index)
        
        # Save config
        self.event_manager.data_manager.save_config(self.event_manager.config)
        
        # Emit signal
        self.week_year_changed.emit(week, year)
        
        # Use user-friendly week display in status message
        self._show_status_message(f"Advanced to {week_display}, Year {year}", error=False)
    
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
        # In Qt, Checked=2, Unchecked=0, PartiallyChecked=1
        is_checked = (state == 2)
        
        # Update the config
        self.event_manager.config['auto_save'] = is_checked
        self.event_manager.data_manager.save_config(self.event_manager.config)
        
        # Update save file label
        save_file = self.event_manager.config.get('franchise_info', {}).get('save_file', '')
        if save_file:
            # Remove .json extension for display purposes
            display_name = save_file
            if display_name.lower().endswith('.json'):
                display_name = display_name[:-5]  # Remove the .json extension
            
            # Get unrealistic events status
            unrealistic_events_enabled = self.event_manager.config.get('unrealistic_events_enabled', False)
            
            label_text = f"Current save file: {display_name}"
            
            # Add status flags
            status_flags = []
            if is_checked:
                status_flags.append("Auto-save ON")
            else:
                status_flags.append("Auto-save OFF")
                
            if unrealistic_events_enabled:
                status_flags.append("Unrealistic events ON")
                
            if status_flags:
                label_text += f" ({', '.join(status_flags)})"
                
            self.save_file_label.setText(label_text)
        
        # Show status message
        if is_checked:
            self._show_status_message("Auto-save is now enabled.")
        else:
            self._show_status_message("Auto-save is now disabled.")
    
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
        self.week_combo.blockSignals(True)
        self.year_spinner.blockSignals(True)
        
        # Find and select the correct week
        week_display = get_week_display(week)
        index = self.week_combo.findText(week_display)
        if index >= 0:
            self.week_combo.setCurrentIndex(index)
            
        self.year_spinner.setValue(year)
        
        # Update season stage to match the week
        stage = get_season_stage_for_week(week)
        stage_display = get_display_for_season_stage(stage)
        self.season_stage_combo.setCurrentText(stage_display)
        
        # Re-enable signals
        self.week_combo.blockSignals(False)
        self.year_spinner.blockSignals(False)

    def _toggle_unrealistic_events(self, state):
        """Toggle unrealistic events feature
        
        Args:
            state: The checkbox state
        """
        # In Qt, Checked=2, Unchecked=0, PartiallyChecked=1
        is_checked = (state == 2)
        
        # Update the config directly
        self.event_manager.config['unrealistic_events_enabled'] = is_checked
        self.event_manager.data_manager.save_config(self.event_manager.config)
        
        # Update save file label
        save_file = self.event_manager.config.get('franchise_info', {}).get('save_file', '')
        if save_file:
            # Remove .json extension for display purposes
            display_name = save_file
            if display_name.lower().endswith('.json'):
                display_name = display_name[:-5]  # Remove the .json extension
            
            # Get auto-save status
            auto_save = self.event_manager.config.get('auto_save', False)
            
            label_text = f"Current save file: {display_name}"
            
            # Add status flags
            status_flags = []
            if auto_save:
                status_flags.append("Auto-save ON")
            else:
                status_flags.append("Auto-save OFF")
                
            if is_checked:
                status_flags.append("Unrealistic events ON")
                
            if status_flags:
                label_text += f" ({', '.join(status_flags)})"
                
            self.save_file_label.setText(label_text)
        
        # Show status message
        if is_checked:
            self._show_status_message("Unrealistic events are now enabled.")
        else:
            self._show_status_message("Unrealistic events are now disabled.") 