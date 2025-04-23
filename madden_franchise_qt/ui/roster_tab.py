from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QTabWidget, QScrollArea,
    QMessageBox, QFormLayout, QGridLayout, QGroupBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont


class RosterTab(QWidget):
    """Tab for managing the team roster"""
    
    def __init__(self, event_manager):
        super().__init__()
        
        self.event_manager = event_manager
        
        # Entry dictionaries to store references to UI elements
        self.offense_entries = {}
        self.defense_entries = {}
        self.special_entries = {}
        self.coaches_entries = {}
        
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
        
        # Create inner tab widget
        roster_tabs = QTabWidget()
        
        # Create tabs for different position groups
        self._create_offense_tab(roster_tabs)
        self._create_defense_tab(roster_tabs)
        self._create_special_tab(roster_tabs)
        self._create_coaches_tab(roster_tabs)
        
        main_layout.addWidget(roster_tabs)
        
        # Add note section
        note_group = QGroupBox("Note")
        note_layout = QVBoxLayout(note_group)
        
        note_text = """
        Update your roster to match your actual Madden franchise.
        This will help the event generator to accurately reference your players and coaches.
        """
        
        note_label = QLabel(note_text)
        note_label.setWordWrap(True)
        note_layout.addWidget(note_label)
        
        main_layout.addWidget(note_group)
        
        # Load current data
        self.refresh()
    
    def _create_offense_tab(self, parent):
        """Create the offense tab
        
        Args:
            parent: The parent widget
        """
        offense_tab = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(offense_tab)
        
        # Layout for the offense tab
        offense_layout = QVBoxLayout(offense_tab)
        
        # Position entries using a grid layout
        grid_layout = QGridLayout()
        grid_layout.setColumnStretch(1, 1)  # Make entry column stretch
        grid_layout.setColumnStretch(2, 0)  # Button column doesn't stretch
        
        offense_positions = [
            ("QB1", "Quarterback 1"),
            ("QB2", "Quarterback 2"),
            ("RB1", "Running Back 1"),
            ("RB2", "Running Back 2"),
            ("RB3", "Running Back 3"),
            ("WR1", "Wide Receiver 1"),
            ("WR2", "Wide Receiver 2"),
            ("WR3", "Wide Receiver 3"),
            ("WR4", "Wide Receiver 4"),
            ("TE1", "Tight End 1"),
            ("TE2", "Tight End 2"),
            ("LT1", "Left Tackle 1"),
            ("LT2", "Left Tackle 2"),
            ("LG1", "Left Guard 1"),
            ("LG2", "Left Guard 2"),
            ("C1", "Center 1"),
            ("C2", "Center 2"),
            ("RG1", "Right Guard 1"),
            ("RG2", "Right Guard 2"),
            ("RT1", "Right Tackle 1"),
            ("RT2", "Right Tackle 2")
        ]
        
        for i, (pos_code, pos_name) in enumerate(offense_positions):
            # Label
            label = QLabel(f"{pos_name} ({pos_code}):")
            grid_layout.addWidget(label, i, 0)
            
            # Entry
            entry = QLineEdit()
            grid_layout.addWidget(entry, i, 1)
            
            # Button
            update_btn = QPushButton("Update")
            update_btn.clicked.connect(lambda checked=False, pc=pos_code, e=entry: self._update_player(pc, e))
            grid_layout.addWidget(update_btn, i, 2)
            
            # Store reference
            self.offense_entries[pos_code] = entry
        
        offense_layout.addLayout(grid_layout)
        offense_layout.addStretch()
        
        parent.addTab(scroll_area, "Offense")
    
    def _create_defense_tab(self, parent):
        """Create the defense tab
        
        Args:
            parent: The parent widget
        """
        defense_tab = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(defense_tab)
        
        # Layout for the defense tab
        defense_layout = QVBoxLayout(defense_tab)
        
        # Position entries using a grid layout
        grid_layout = QGridLayout()
        grid_layout.setColumnStretch(1, 1)  # Make entry column stretch
        grid_layout.setColumnStretch(2, 0)  # Button column doesn't stretch
        
        defense_positions = [
            ("LE1", "Left Defensive End 1"),
            ("LE2", "Left Defensive End 2"),
            ("RE1", "Right Defensive End 1"),
            ("RE2", "Right Defensive End 2"),
            ("DT1", "Defensive Tackle 1"),
            ("DT2", "Defensive Tackle 2"),
            ("DT3", "Defensive Tackle 3"),
            ("LOLB1", "Left Outside Linebacker 1"),
            ("LOLB2", "Left Outside Linebacker 2"),
            ("MLB1", "Middle Linebacker 1"),
            ("MLB2", "Middle Linebacker 2"),
            ("ROLB1", "Right Outside Linebacker 1"),
            ("ROLB2", "Right Outside Linebacker 2"),
            ("CB1", "Cornerback 1"),
            ("CB2", "Cornerback 2"),
            ("CB3", "Cornerback 3"),
            ("CB4", "Cornerback 4"),
            ("FS1", "Free Safety 1"),
            ("FS2", "Free Safety 2"),
            ("SS1", "Strong Safety 1"),
            ("SS2", "Strong Safety 2")
        ]
        
        for i, (pos_code, pos_name) in enumerate(defense_positions):
            # Label
            label = QLabel(f"{pos_name} ({pos_code}):")
            grid_layout.addWidget(label, i, 0)
            
            # Entry
            entry = QLineEdit()
            grid_layout.addWidget(entry, i, 1)
            
            # Button
            update_btn = QPushButton("Update")
            update_btn.clicked.connect(lambda checked=False, pc=pos_code, e=entry: self._update_player(pc, e))
            grid_layout.addWidget(update_btn, i, 2)
            
            # Store reference
            self.defense_entries[pos_code] = entry
        
        defense_layout.addLayout(grid_layout)
        defense_layout.addStretch()
        
        parent.addTab(scroll_area, "Defense")
    
    def _create_special_tab(self, parent):
        """Create the special teams tab
        
        Args:
            parent: The parent widget
        """
        special_tab = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(special_tab)
        
        # Layout for the special teams tab
        special_layout = QVBoxLayout(special_tab)
        
        # Position entries using a grid layout
        grid_layout = QGridLayout()
        grid_layout.setColumnStretch(1, 1)  # Make entry column stretch
        grid_layout.setColumnStretch(2, 0)  # Button column doesn't stretch
        
        special_positions = [
            ("K", "Kicker"),
            ("P", "Punter")
        ]
        
        for i, (pos_code, pos_name) in enumerate(special_positions):
            # Label
            label = QLabel(f"{pos_name} ({pos_code}):")
            grid_layout.addWidget(label, i, 0)
            
            # Entry
            entry = QLineEdit()
            grid_layout.addWidget(entry, i, 1)
            
            # Button
            update_btn = QPushButton("Update")
            update_btn.clicked.connect(lambda checked=False, pc=pos_code, e=entry: self._update_player(pc, e))
            grid_layout.addWidget(update_btn, i, 2)
            
            # Store reference
            self.special_entries[pos_code] = entry
        
        special_layout.addLayout(grid_layout)
        special_layout.addStretch()
        
        parent.addTab(scroll_area, "Special Teams")
    
    def _create_coaches_tab(self, parent):
        """Create the coaches tab
        
        Args:
            parent: The parent widget
        """
        coaches_tab = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(coaches_tab)
        
        # Layout for the coaches tab
        coaches_layout = QVBoxLayout(coaches_tab)
        
        # Position entries using a grid layout
        grid_layout = QGridLayout()
        grid_layout.setColumnStretch(1, 1)  # Make entry column stretch
        grid_layout.setColumnStretch(2, 0)  # Button column doesn't stretch
        
        coaches_positions = [
            ("HC", "Head Coach"),
            ("OC", "Offensive Coordinator"),
            ("DC", "Defensive Coordinator")
        ]
        
        for i, (pos_code, pos_name) in enumerate(coaches_positions):
            # Label
            label = QLabel(f"{pos_name} ({pos_code}):")
            grid_layout.addWidget(label, i, 0)
            
            # Entry
            entry = QLineEdit()
            grid_layout.addWidget(entry, i, 1)
            
            # Button
            update_btn = QPushButton("Update")
            update_btn.clicked.connect(lambda checked=False, pc=pos_code, e=entry: self._update_coach(pc, e))
            grid_layout.addWidget(update_btn, i, 2)
            
            # Store reference
            self.coaches_entries[pos_code] = entry
        
        coaches_layout.addLayout(grid_layout)
        coaches_layout.addStretch()
        
        parent.addTab(scroll_area, "Coaches")
    
    def refresh(self):
        """Refresh tab with current data"""
        # Update entries from config
        roster = self.event_manager.config.get('roster', {})
        coaches = self.event_manager.config.get('coaches', {})
        
        # Update offense entries
        for pos_code, entry in self.offense_entries.items():
            entry.setText(roster.get(pos_code, ''))
        
        # Update defense entries
        for pos_code, entry in self.defense_entries.items():
            entry.setText(roster.get(pos_code, ''))
        
        # Update special teams entries
        for pos_code, entry in self.special_entries.items():
            entry.setText(roster.get(pos_code, ''))
        
        # Update coaches entries
        for pos_code, entry in self.coaches_entries.items():
            entry.setText(coaches.get(pos_code, ''))
    
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
    
    def _update_player(self, position, entry):
        """Update a player in the roster
        
        Args:
            position: The position to update
            entry: The entry field to get the name from
        """
        player_name = entry.text().strip()
        
        if not player_name:
            self._show_status_message(f"Please enter a name for {position}", error=True)
            return
        
        if self.event_manager.update_roster(position, player_name):
            self._show_status_message(f"Updated {position} to {player_name}")
        else:
            self._show_status_message(f"Failed to update {position}", error=True)
    
    def _update_coach(self, position, entry):
        """Update a coach in the roster
        
        Args:
            position: The position to update
            entry: The entry field to get the name from
        """
        coach_name = entry.text().strip()
        
        if not coach_name:
            self._show_status_message(f"Please enter a name for {position}", error=True)
            return
        
        if self.event_manager.update_coach(position, coach_name):
            self._show_status_message(f"Updated {position} to {coach_name}")
        else:
            self._show_status_message(f"Failed to update {position}", error=True) 