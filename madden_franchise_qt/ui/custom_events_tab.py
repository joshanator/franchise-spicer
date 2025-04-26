from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTabWidget, QLineEdit, QComboBox, QTextEdit, QListWidget, QListWidgetItem,
    QFileDialog, QMessageBox, QScrollArea, QSpinBox, QDoubleSpinBox,
    QFormLayout, QCheckBox, QGroupBox, QRadioButton, QInputDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QStyledItemDelegate, QStyleOptionViewItem
)
from PySide6.QtCore import Qt, QSize, Signal, QRect
from PySide6.QtGui import QFont, QIcon, QColor, QPixmap, QPainter, QPen
from PySide6.QtWidgets import QApplication

import json
import os
import copy

class CheckBoxDelegate(QStyledItemDelegate):
    """Custom delegate to properly center checkboxes in table cells"""
    
    def paint(self, painter, option, index):
        """Paint the checkbox centered in the cell
        
        Args:
            painter: The painter
            option: The style options
            index: The model index
        """
        # Create a copy of the options
        opt = QStyleOptionViewItem(option)
        
        # Set alignment to center
        opt.displayAlignment = Qt.AlignCenter
        
        # Let the default implementation handle the drawing
        QStyledItemDelegate.paint(self, painter, opt, index)

class CustomEventsTab(QWidget):
    """Tab for creating, editing, importing, and exporting custom events"""
    
    refresh_signal = Signal()
    
    def __init__(self, event_manager):
        """Initialize the custom events tab
        
        Args:
            event_manager: The event manager instance
        """
        super().__init__()
        self.event_manager = event_manager
        self.custom_events = []
        self._init_ui()
        self.current_event_index = -1
        self.current_option_index = -1
        self.current_result_index = -1
        self.current_nested_option_index = -1
        self.current_nested_suboption_index = -1
        self.current_nested_random_impact_index = -1
        self.load_custom_events()
    
    def _init_ui(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Custom Events")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Info text
        info_label = QLabel("Create your own events or import/export event collections")
        info_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(info_label)
        
        # Help button for explanations
        help_btn = QPushButton("How Custom Events Work")
        help_btn.clicked.connect(self.show_help)
        main_layout.addWidget(help_btn)
        
        # Buttons for import/export
        import_export_layout = QHBoxLayout()
        
        self.import_btn = QPushButton("Import Events")
        self.import_btn.clicked.connect(self.import_events)
        import_export_layout.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("Export Events")
        self.export_btn.clicked.connect(self.export_events)
        import_export_layout.addWidget(self.export_btn)
        
        main_layout.addLayout(import_export_layout)
        
        # Split into left and right panels
        content_layout = QHBoxLayout()
        
        # Left panel - list of custom events
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        left_layout.addWidget(QLabel("Your Custom Events:"))
        
        # Create table widget for events with improved layout
        self.events_list = QTableWidget()
        self.events_list.setColumnCount(2)
        self.events_list.setHorizontalHeaderLabels(["Event Name", "Enabled"])
        
        # Center header for enabled column
        enabled_header = QTableWidgetItem("Enabled")
        enabled_header.setTextAlignment(Qt.AlignCenter)
        self.events_list.setHorizontalHeaderItem(1, enabled_header)
        
        # Set column properties
        self.events_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # Event name stretches
        self.events_list.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)    # Enabled column fixed width
        self.events_list.setColumnWidth(1, 60)  # Make the enabled column thinner
        
        # Set appearance
        self.events_list.setSelectionBehavior(QTableWidget.SelectRows)  # Select entire row
        self.events_list.setEditTriggers(QTableWidget.NoEditTriggers)   # Make read-only
        self.events_list.setAlternatingRowColors(True)                  # Alternate row colors
        self.events_list.setShowGrid(True)                              # Show grid lines
        
        # Set delegate for better checkbox centering
        checkbox_delegate = CheckBoxDelegate()
        self.events_list.setItemDelegateForColumn(1, checkbox_delegate)
        
        # Connect signals
        self.events_list.cellClicked.connect(self.on_event_selected)
        
        left_layout.addWidget(self.events_list)
        
        # Buttons for event management
        event_buttons_layout = QHBoxLayout()
        
        self.new_event_btn = QPushButton("New Event")
        self.new_event_btn.clicked.connect(self.create_new_event)
        event_buttons_layout.addWidget(self.new_event_btn)
        
        self.delete_event_btn = QPushButton("Delete Event")
        self.delete_event_btn.clicked.connect(self.delete_event)
        event_buttons_layout.addWidget(self.delete_event_btn)
        
        # Add save button next to other event buttons
        self.save_event_btn = QPushButton("Save Event")
        self.save_event_btn.clicked.connect(self.save_current_event)
        event_buttons_layout.addWidget(self.save_event_btn)
        
        left_layout.addLayout(event_buttons_layout)
        
        # Right panel - event editor
        self.right_panel = QScrollArea()
        self.right_panel.setWidgetResizable(True)
        
        self.editor_widget = QWidget()
        self.editor_layout = QVBoxLayout(self.editor_widget)
        
        # Basic event properties
        basic_group = QGroupBox("Basic Event Properties")
        basic_layout = QFormLayout()
        
        self.title_input = QLineEdit()
        basic_layout.addRow("Title:", self.title_input)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        basic_layout.addRow("Description:", self.description_input)
        
        self.impact_input = QTextEdit()
        self.impact_input.setMaximumHeight(80)
        basic_layout.addRow("Impact:", self.impact_input)
        
        # Remove enabled checkbox from here, as it will be in the list
        
        self.category_input = QComboBox()
        self.category_input.addItems([
            "attribute", "contract", "draft", "free-agency", "injury", 
            "lineup", "roster", "suspension", "team", "trade", "penalty", "mini-challenge", "random-challenge", "season-challenge"
        ])
        basic_layout.addRow("Category:", self.category_input)
        
        self.is_temporary = QCheckBox("Temporary Event (allows event to show in effects tracker)")
        basic_layout.addRow("", self.is_temporary)
        
        basic_group.setLayout(basic_layout)
        self.editor_layout.addWidget(basic_group)
        
        # Season stages
        season_group = QGroupBox("Season Stages")
        season_layout = QVBoxLayout()
        
        # Create two horizontal layouts for season stages
        season_row1 = QHBoxLayout()
        season_row2 = QHBoxLayout()
        
        self.pre_season = QCheckBox("Pre-Season")
        season_row1.addWidget(self.pre_season)
        
        self.regular_season_start = QCheckBox("Regular Season Start")
        season_row1.addWidget(self.regular_season_start)
        
        self.regular_season_mid = QCheckBox("Regular Season Mid")
        season_row1.addWidget(self.regular_season_mid)
        
        self.regular_season_end = QCheckBox("Regular Season End")
        season_row2.addWidget(self.regular_season_end)
        
        self.playoffs = QCheckBox("Playoffs")
        season_row2.addWidget(self.playoffs)
        
        self.off_season = QCheckBox("Off-Season")
        season_row2.addWidget(self.off_season)
        
        season_layout.addLayout(season_row1)
        season_layout.addLayout(season_row2)
        
        season_group.setLayout(season_layout)
        self.editor_layout.addWidget(season_group)
        
        # Options (choices) section - MOVED ABOVE TARGET OPTIONS
        options_group = QGroupBox("Event Options (Player Choices)")
        options_layout = QVBoxLayout()
        
        # Options row for mutually exclusive choices
        options_row = QHBoxLayout()
        
        self.has_options = QCheckBox("This event has player choices")
        self.has_options.stateChanged.connect(self.toggle_options_section)
        options_row.addWidget(self.has_options)
        
        # Add random results checkbox to options group
        self.has_results = QCheckBox("This event has random results")
        self.has_results.stateChanged.connect(self.toggle_results_section)
        options_row.addWidget(self.has_results)
        
        options_layout.addLayout(options_row)
        
        # Create a widget to hold both the options list and results widgets
        self.options_widget = QWidget()
        self.options_layout = QVBoxLayout(self.options_widget)
        
        # Player choice options section
        self.player_options_widget = QWidget()
        player_options_layout = QVBoxLayout(self.player_options_widget)
        
        player_options_layout.addWidget(QLabel("Options:"))
        self.options_list = QListWidget()
        self.options_list.currentRowChanged.connect(self.on_option_selected)
        player_options_layout.addWidget(self.options_list)
        
        options_btn_layout = QHBoxLayout()
        
        self.add_option_btn = QPushButton("Add Option")
        self.add_option_btn.clicked.connect(self.add_option)
        options_btn_layout.addWidget(self.add_option_btn)
        
        self.delete_option_btn = QPushButton("Delete Option")
        self.delete_option_btn.clicked.connect(self.delete_option)
        options_btn_layout.addWidget(self.delete_option_btn)
        
        player_options_layout.addLayout(options_btn_layout)
        
        # Option editor
        self.option_editor = QWidget()
        option_editor_layout = QVBoxLayout(self.option_editor)
        
        basic_option_layout = QFormLayout()
        self.option_description = QLineEdit()
        basic_option_layout.addRow("Option Text:", self.option_description)
        
        self.option_impact = QTextEdit()
        self.option_impact.setMaximumHeight(80)
        basic_option_layout.addRow("Option Impact:", self.option_impact)
        
        option_editor_layout.addLayout(basic_option_layout)
        
        # Random impact options
        self.has_random_impacts = QCheckBox("This option has random outcomes")
        self.has_random_impacts.stateChanged.connect(self.toggle_random_impacts)
        option_editor_layout.addWidget(self.has_random_impacts)
        
        self.random_impacts_widget = QWidget()
        random_impacts_layout = QVBoxLayout(self.random_impacts_widget)
        
        random_impacts_layout.addWidget(QLabel("Random Outcomes:"))
        self.random_impacts_list = QListWidget()
        self.random_impacts_list.currentRowChanged.connect(self.on_random_impact_selected)
        random_impacts_layout.addWidget(self.random_impacts_list)
        
        random_impacts_btn_layout = QHBoxLayout()
        self.add_random_impact_btn = QPushButton("Add Outcome")
        self.add_random_impact_btn.clicked.connect(self.add_random_impact)
        random_impacts_btn_layout.addWidget(self.add_random_impact_btn)
        
        self.delete_random_impact_btn = QPushButton("Delete Outcome")
        self.delete_random_impact_btn.clicked.connect(self.delete_random_impact)
        random_impacts_btn_layout.addWidget(self.delete_random_impact_btn)
        
        random_impacts_layout.addLayout(random_impacts_btn_layout)
        
        self.random_impact_editor = QWidget()
        random_impact_editor_layout = QFormLayout(self.random_impact_editor)
        
        self.random_impact_text = QTextEdit()
        self.random_impact_text.setMaximumHeight(80)
        random_impact_editor_layout.addRow("Outcome Text:", self.random_impact_text)
        
        self.random_impact_probability = QDoubleSpinBox()
        self.random_impact_probability.setRange(0, 1)
        self.random_impact_probability.setSingleStep(0.05)
        self.random_impact_probability.setDecimals(2)
        random_impact_editor_layout.addRow("Probability:", self.random_impact_probability)
        
        random_impacts_layout.addWidget(self.random_impact_editor)
        
        # Nested options
        self.has_nested_options = QCheckBox("This option has sub-options")
        self.has_nested_options.stateChanged.connect(self.toggle_nested_options)
        option_editor_layout.addWidget(self.has_nested_options)
        
        self.nested_options_widget = QWidget()
        nested_options_layout = QVBoxLayout(self.nested_options_widget)
        
        nested_options_layout.addWidget(QLabel("Sub-Options:"))
        self.nested_options_list = QListWidget()
        self.nested_options_list.currentRowChanged.connect(self.on_nested_option_selected)
        nested_options_layout.addWidget(self.nested_options_list)
        
        nested_options_btn_layout = QHBoxLayout()
        self.add_nested_option_btn = QPushButton("Add Sub-Option")
        self.add_nested_option_btn.clicked.connect(self.add_nested_option)
        nested_options_btn_layout.addWidget(self.add_nested_option_btn)
        
        self.delete_nested_option_btn = QPushButton("Delete Sub-Option")
        self.delete_nested_option_btn.clicked.connect(self.delete_nested_option)
        nested_options_btn_layout.addWidget(self.delete_nested_option_btn)
        
        nested_options_layout.addLayout(nested_options_btn_layout)
        
        # Nested option editor - integrated into the same widget
        self.nested_option_editor = QWidget()
        nested_option_editor_layout = QVBoxLayout(self.nested_option_editor)
        
        nested_basic_layout = QFormLayout()
        self.nested_option_description = QLineEdit()
        nested_basic_layout.addRow("Sub-Option Text:", self.nested_option_description)
        
        self.nested_option_impact = QTextEdit()
        self.nested_option_impact.setMaximumHeight(80)
        nested_basic_layout.addRow("Sub-Option Impact:", self.nested_option_impact)
        
        nested_option_editor_layout.addLayout(nested_basic_layout)
        
        # Add support for deeper nesting (recursive sub-options)
        self.has_nested_suboptions = QCheckBox("This sub-option has its own sub-options")
        self.has_nested_suboptions.stateChanged.connect(self.toggle_nested_suboptions)
        nested_option_editor_layout.addWidget(self.has_nested_suboptions)
        
        self.nested_suboptions_widget = QWidget()
        nested_suboptions_layout = QVBoxLayout(self.nested_suboptions_widget)
        
        nested_suboptions_layout.addWidget(QLabel("Sub-Sub-Options:"))
        self.nested_suboptions_list = QListWidget()
        self.nested_suboptions_list.currentRowChanged.connect(self.on_nested_suboption_selected)
        nested_suboptions_layout.addWidget(self.nested_suboptions_list)
        
        nested_suboptions_btn_layout = QHBoxLayout()
        self.add_nested_suboption_btn = QPushButton("Add Sub-Sub-Option")
        self.add_nested_suboption_btn.clicked.connect(self.add_nested_suboption)
        nested_suboptions_btn_layout.addWidget(self.add_nested_suboption_btn)
        
        self.delete_nested_suboption_btn = QPushButton("Delete Sub-Sub-Option")
        self.delete_nested_suboption_btn.clicked.connect(self.delete_nested_suboption)
        nested_suboptions_btn_layout.addWidget(self.delete_nested_suboption_btn)
        
        nested_suboptions_layout.addLayout(nested_suboptions_btn_layout)
        
        nested_option_editor_layout.addWidget(self.nested_suboptions_widget)
        
        # Add support for random impacts in nested options too
        self.has_nested_random_impacts = QCheckBox("This sub-option has random outcomes")
        self.has_nested_random_impacts.stateChanged.connect(self.toggle_nested_random_impacts)
        nested_option_editor_layout.addWidget(self.has_nested_random_impacts)
        
        self.nested_random_impacts_widget = QWidget()
        nested_random_impacts_layout = QVBoxLayout(self.nested_random_impacts_widget)
        
        nested_random_impacts_layout.addWidget(QLabel("Random Outcomes:"))
        self.nested_random_impacts_list = QListWidget()
        self.nested_random_impacts_list.currentRowChanged.connect(self.on_nested_random_impact_selected)
        nested_random_impacts_layout.addWidget(self.nested_random_impacts_list)
        
        nested_random_impacts_btn_layout = QHBoxLayout()
        self.add_nested_random_impact_btn = QPushButton("Add Outcome")
        self.add_nested_random_impact_btn.clicked.connect(self.add_nested_random_impact)
        nested_random_impacts_btn_layout.addWidget(self.add_nested_random_impact_btn)
        
        self.delete_nested_random_impact_btn = QPushButton("Delete Outcome")
        self.delete_nested_random_impact_btn.clicked.connect(self.delete_nested_random_impact)
        nested_random_impacts_btn_layout.addWidget(self.delete_nested_random_impact_btn)
        
        nested_random_impacts_layout.addLayout(nested_random_impacts_btn_layout)
        
        self.nested_random_impact_editor = QWidget()
        nested_random_impact_editor_layout = QFormLayout(self.nested_random_impact_editor)
        
        self.nested_random_impact_text = QTextEdit()
        self.nested_random_impact_text.setMaximumHeight(80)
        nested_random_impact_editor_layout.addRow("Outcome Text:", self.nested_random_impact_text)
        
        self.nested_random_impact_probability = QDoubleSpinBox()
        self.nested_random_impact_probability.setRange(0, 1)
        self.nested_random_impact_probability.setSingleStep(0.05)
        self.nested_random_impact_probability.setDecimals(2)
        nested_random_impact_editor_layout.addRow("Probability:", self.nested_random_impact_probability)
        
        nested_random_impacts_layout.addWidget(self.nested_random_impact_editor)
        nested_option_editor_layout.addWidget(self.nested_random_impacts_widget)
        
        # Integrate the nested option editor directly below the list
        nested_options_layout.addWidget(self.nested_option_editor)
        
        # Add the nested options widget to option editor layout
        option_editor_layout.addWidget(self.nested_options_widget)
        option_editor_layout.addWidget(self.random_impacts_widget)
        
        # Add the editor to the player options layout
        player_options_layout.addWidget(self.option_editor)
        
        # Add the player options widget to the options layout
        self.options_layout.addWidget(self.player_options_widget)
        
        # Results widget for event random results
        self.results_widget = QWidget()
        results_layout = QVBoxLayout(self.results_widget)
        
        results_layout.addWidget(QLabel("Possible Results:"))
        self.results_list = QListWidget()
        self.results_list.currentRowChanged.connect(self.on_result_selected)
        results_layout.addWidget(self.results_list)
        
        results_btn_layout = QHBoxLayout()
        self.add_result_btn = QPushButton("Add Result")
        self.add_result_btn.clicked.connect(self.add_result)
        results_btn_layout.addWidget(self.add_result_btn)
        
        self.delete_result_btn = QPushButton("Delete Result")
        self.delete_result_btn.clicked.connect(self.delete_result)
        results_btn_layout.addWidget(self.delete_result_btn)
        
        results_layout.addLayout(results_btn_layout)
        
        self.result_editor = QWidget()
        result_editor_layout = QFormLayout(self.result_editor)
        
        self.result_text = QLineEdit()
        result_editor_layout.addRow("Result Text:", self.result_text)
        
        self.impact_text = QTextEdit()
        self.impact_text.setMaximumHeight(80)
        result_editor_layout.addRow("Impact Text:", self.impact_text)
        
        self.result_probability = QDoubleSpinBox()
        self.result_probability.setRange(0, 1)
        self.result_probability.setSingleStep(0.05)
        self.result_probability.setDecimals(2)
        result_editor_layout.addRow("Probability:", self.result_probability)
        
        results_layout.addWidget(self.result_editor)
        
        # Add results widget to options widget
        self.options_layout.addWidget(self.results_widget)
        
        # Finalize options group
        self.options_widget.setLayout(self.options_layout)
        options_layout.addWidget(self.options_widget)
        
        options_group.setLayout(options_layout)
        self.editor_layout.addWidget(options_group)
        
        # Target options
        target_group = QGroupBox("Target Options")
        target_layout = QVBoxLayout()
        
        # Top options layout for "All Players" and "N/A"
        top_options_layout = QHBoxLayout()
        
        self.all_players = QCheckBox("All Players")
        self.all_players.stateChanged.connect(self.update_target_options)
        top_options_layout.addWidget(self.all_players)
        
        self.na_option = QCheckBox("N/A (No Target)")
        self.na_option.stateChanged.connect(self.update_target_options)
        top_options_layout.addWidget(self.na_option)
        
        target_layout.addLayout(top_options_layout)
        
        # Coach options
        coach_layout = QHBoxLayout()
        coach_layout.addWidget(QLabel("Coaches:"))
        
        self.coach_checkboxes = {}
        for coach in ["HC", "OC", "DC"]:
            cb = QCheckBox(coach)
            self.coach_checkboxes[coach] = cb
            coach_layout.addWidget(cb)
        
        # Add spacer to push coaches to the left
        coach_layout.addStretch()
        
        target_layout.addLayout(coach_layout)
        
        self.target_selections = QWidget()
        target_selections_layout = QVBoxLayout(self.target_selections)
        
        # Common positions in more compact layout
        positions = {
            "Offense QB": ["QB1", "QB2", "QB3"],
            "Offense RB": ["RB1", "RB2", "RB3", "FB1"],
            "Offense WR": ["WR1", "WR2", "WR3", "WR4"],
            "Offense TE": ["TE1", "TE2"],
            "Offense Line": ["LT1", "LT2", "LG1", "LG2", "C1", "C2", "RG1", "RG2", "RT1", "RT2"],
            "Defense Line": ["LE1", "LE2", "DT1", "DT2", "DT3", "RE1", "RE2"],
            "Defense LB": ["LOLB1", "LOLB2", "MLB1", "MLB2", "ROLB1", "ROLB2"],
            "Defense Secondary": ["CB1", "CB2", "CB3", "CB4", "FS1", "FS2", "SS1", "SS2"],
            "Special Teams": ["K1", "P1"]
        }
        
        self.position_checkboxes = {}
        
        # Create a more compact UI for positions
        for category, pos_list in positions.items():
            category_row = QHBoxLayout()
            category_row.addWidget(QLabel(f"{category}:"))
            
            # Create a flow layout for positions
            positions_layout = QHBoxLayout()
            for pos in pos_list:
                cb = QCheckBox(pos)
                self.position_checkboxes[pos] = cb
                positions_layout.addWidget(cb)
            
            # Add spacer to push everything to the left
            positions_layout.addStretch()
            
            # Add to category row
            category_row.addLayout(positions_layout)
            category_row.setStretchFactor(positions_layout, 4)
            
            # Add completed row to main layout
            target_selections_layout.addLayout(category_row)
        
        target_layout.addWidget(self.target_selections)
        target_group.setLayout(target_layout)
        self.editor_layout.addWidget(target_group)
        
        # Difficulty weights
        difficulty_group = QGroupBox("Difficulty Weights")
        difficulty_layout = QHBoxLayout()
        
        self.difficulty_weights = {}
        for difficulty in ["cupcake", "rookie", "pro", "all-madden", "diabolical"]:
            weight_layout = QVBoxLayout()
            weight_layout.addWidget(QLabel(f"{difficulty.capitalize()}:"))
            
            spinner = QDoubleSpinBox()
            spinner.setRange(0, 1)
            spinner.setSingleStep(0.05)
            spinner.setValue(0.2)  # Default value
            spinner.setDecimals(2)
            self.difficulty_weights[difficulty] = spinner
            weight_layout.addWidget(spinner)
            
            difficulty_layout.addLayout(weight_layout)
        
        difficulty_group.setLayout(difficulty_layout)
        self.editor_layout.addWidget(difficulty_group)
        
        # Initialize hidden widgets
        self.option_editor.hide()  # Hide until an option is selected
        self.random_impacts_widget.hide()  # Hide until random impacts are enabled
        self.random_impact_editor.hide()  # Hide until a random impact is selected
        self.nested_options_widget.hide()  # Hide until nested options are enabled
        self.nested_option_editor.hide()  # Hide until a nested option is selected
        self.nested_suboptions_widget.hide()  # Hide until nested suboptions are enabled
        self.nested_random_impacts_widget.hide()  # Hide until nested random impacts are enabled
        self.nested_random_impact_editor.hide()  # Hide until a nested random impact is selected
        
        # Make sure these are initially hidden
        self.player_options_widget.hide()
        self.results_widget.hide()
        self.options_widget.hide()
        
        self.options_widget.setLayout(self.options_layout)
        options_layout.addWidget(self.options_widget)
        self.options_widget.setVisible(False)  # Hide initially
        
        options_group.setLayout(options_layout)
        self.editor_layout.addWidget(options_group)
        
        # Finalize layout
        self.right_panel.setWidget(self.editor_widget)
        
        # Add panels to content layout
        content_layout.addWidget(left_panel, 1)
        content_layout.addWidget(self.right_panel, 2)
        
        main_layout.addLayout(content_layout)
        
        # Initially disable the editor until an event is selected
        self.enable_editor(False)
    
    def toggle_options_section(self, state):
        """Toggle visibility of the options section based on checkbox state"""
        is_checked = state == Qt.CheckState.Checked.value
        
        # Make options and random results mutually exclusive
        if is_checked:
            self.has_results.setChecked(False)
        
        # Update visibility
        self.options_widget.setVisible(is_checked)
        self.player_options_widget.setVisible(is_checked)
        self.results_widget.hide()
        
        # Force UI refresh
        QApplication.processEvents()
    
    def toggle_results_section(self, state):
        """Toggle visibility of the results section based on checkbox state"""
        is_checked = state == Qt.CheckState.Checked.value
        
        # Make options and random results mutually exclusive
        if is_checked:
            self.has_options.setChecked(False)
        
        # Update visibility
        self.options_widget.setVisible(is_checked)
        self.results_widget.setVisible(is_checked)
        self.player_options_widget.hide()
        
        # Force UI refresh
        QApplication.processEvents()
    
    def enable_editor(self, enabled):
        """Enable or disable the event editor
        
        Args:
            enabled: Whether to enable the editor
        """
        self.editor_widget.setEnabled(enabled)
        self.save_event_btn.setEnabled(enabled)
        
        # Reset visibility of option sections when enabling/disabling editor
        if enabled:
            # Show only what's needed based on checkboxes
            self.options_widget.setVisible(self.has_options.isChecked() or self.has_results.isChecked())
            self.player_options_widget.setVisible(self.has_options.isChecked())
            self.results_widget.setVisible(self.has_results.isChecked())
        else:
            # Hide all when disabling
            self.options_widget.hide()
            self.player_options_widget.hide()
            self.results_widget.hide()
    
    def update_target_options(self, state):
        """Update target options based on selection state"""
        # If "All Players" is checked, disable other selections
        all_checked = self.all_players.isChecked()
        na_checked = self.na_option.isChecked()
        
        # If either global option is selected, disable position selections
        should_disable = all_checked or na_checked
        
        # If both are checked, uncheck the other one
        if state == Qt.CheckState.Checked.value:
            if all_checked and na_checked and self.sender() == self.all_players:
                self.na_option.setChecked(False)
            elif all_checked and na_checked and self.sender() == self.na_option:
                self.all_players.setChecked(False)
        
        self.target_selections.setEnabled(not should_disable)
        
        # Also disable coach checkboxes
        for cb in self.coach_checkboxes.values():
            cb.setEnabled(not should_disable)
    
    def refresh(self):
        """Refresh the tab data"""
        self.load_custom_events()
    
    def import_events(self):
        """Import events from a JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Events", "", "JSON Files (*.json)"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if 'events' not in data:
                QMessageBox.warning(self, "Invalid Format", "The file does not contain an 'events' array.")
                return
                
            events_to_import = data['events']
            
            # Check if any events are missing required fields
            invalid_events = []
            for event in events_to_import:
                if 'id' not in event or 'title' not in event or 'description' not in event:
                    invalid_events.append(event.get('title', 'Unnamed Event'))
            
            if invalid_events:
                msg = "The following events are missing required fields and will be skipped:\n\n"
                msg += "\n".join(invalid_events)
                QMessageBox.warning(self, "Invalid Events", msg)
                
                # Filter out invalid events
                events_to_import = [e for e in events_to_import if 'id' in e and 'title' in e and 'description' in e]
            
            if not events_to_import:
                QMessageBox.information(self, "No Valid Events", "No valid events found to import.")
                return
                
            # Add the events to the custom events
            for event in events_to_import:
                # Make sure event has an id that doesn't conflict
                if not self.custom_events:
                    max_id = 0
                else:
                    max_id = max(e.get('id', 0) for e in self.custom_events)
                
                event['id'] = max_id + 1
                self.custom_events.append(event)
            
            # Save and refresh
            self.save_custom_events()
            self.load_custom_events()
            
            QMessageBox.information(
                self, "Import Successful", f"Successfully imported {len(events_to_import)} events."
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Error importing events: {str(e)}")
    
    def export_events(self):
        """Export custom events to a JSON file"""
        if not self.custom_events:
            QMessageBox.information(self, "No Events", "There are no custom events to export.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Events", "", "JSON Files (*.json)"
        )
        
        if not file_path:
            return
            
        # Make sure it has .json extension
        if not file_path.lower().endswith('.json'):
            file_path += '.json'
            
        try:
            export_data = {'events': self.custom_events}
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
                
            QMessageBox.information(
                self, "Export Successful", f"Successfully exported {len(self.custom_events)} events."
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Error exporting events: {str(e)}")
    
    def load_custom_events(self):
        """Load custom events from the user's save file"""
        # Get custom events from event manager's config
        config = self.event_manager.config
        self.custom_events = config.get('custom_events', [])
        
        # Update the events list
        self.events_list.setRowCount(0)  # Clear the table
        
        for i, event in enumerate(self.custom_events):
            title = event.get('title', 'Unnamed Event')
            is_enabled = event.get('enabled', True)
            
            # Insert a new row
            self.events_list.insertRow(i)
            
            # Create title item
            title_item = QTableWidgetItem(title)
            self.events_list.setItem(i, 0, title_item)
            
            # Update the enabled cell
            self.update_enabled_cell(i, is_enabled)
        
        # Adjust column widths
        self.events_list.setColumnWidth(0, 260)  # Event name column
        self.events_list.setColumnWidth(1, 50)   # Enabled column
        
        # Disable editor when refreshing
        self.enable_editor(False)
        self.current_event_index = -1
    
    def update_enabled_cell(self, row, is_enabled):
        """Update the enabled cell with a checkbox
        
        Args:
            row: The row to update
            is_enabled: Whether the event is enabled
        """
        # Create a new item for the enabled column
        enabled_item = QTableWidgetItem()
        
        # Make sure the item is only checkable
        enabled_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable)
        
        # Set checked state
        enabled_item.setCheckState(Qt.CheckState.Checked if is_enabled else Qt.CheckState.Unchecked)
        
        # Add to table
        self.events_list.setItem(row, 1, enabled_item)
    
    def save_custom_events(self):
        """Save custom events to the config"""
        # Update the config with custom events
        self.event_manager.config['custom_events'] = self.custom_events
        self.event_manager._save_config()  # Save using event manager's method
    
    def on_event_selected(self, row, column):
        """Handle event selection in the table
        
        Args:
            row: The row index of the selected event
            column: The column that was clicked
        """
        if row < 0 or row >= len(self.custom_events):
            self.enable_editor(False)
            self.current_event_index = -1
            return
        
        # If user clicked the "Enabled" column, toggle the checkbox
        if column == 1:
            # Get the checkbox item
            self.toggle_event_enabled(row)
            return
            
        self.current_event_index = row
        event = self.custom_events[row]
        
        # Load event data into the editor
        self.title_input.setText(event.get('title', ''))
        self.description_input.setText(event.get('description', ''))
        self.impact_input.setText(event.get('impact', ''))
        
        category = event.get('category', 'attribute')
        index = self.category_input.findText(category)
        self.category_input.setCurrentIndex(index if index >= 0 else 0)
        
        self.is_temporary.setChecked(event.get('is_temporary', False))
        
        # Set season stages
        stages = event.get('season_stages', [])
        self.pre_season.setChecked('pre-season' in stages)
        self.regular_season_start.setChecked('regular-season-start' in stages)
        self.regular_season_mid.setChecked('regular-season-mid' in stages)
        self.regular_season_end.setChecked('regular-season-end' in stages)
        self.playoffs.setChecked(any(s in stages for s in ['playoffs', 'post-season']))
        self.off_season.setChecked(any(s in stages for s in ['off-season', 'offseason']))
        
        # Set target options
        target_options = event.get('target_options', [])
        self.all_players.setChecked('all-players' in target_options)
        self.na_option.setChecked('n/a' in target_options)
        
        # Update target selection enabled state
        is_global_target = 'all-players' in target_options or 'n/a' in target_options
        self.target_selections.setEnabled(not is_global_target)
        
        # Set coach checkboxes
        for coach, checkbox in self.coach_checkboxes.items():
            checkbox.setChecked(coach in target_options)
            checkbox.setEnabled(not is_global_target)
        
        # Set player position checkboxes
        for pos, checkbox in self.position_checkboxes.items():
            checkbox.setChecked(pos in target_options)
        
        # Set difficulty weights
        weights = event.get('difficulty_weights', {})
        for difficulty, spinner in self.difficulty_weights.items():
            spinner.setValue(weights.get(difficulty, 0.2))
        
        # Set result options
        has_results = 'result_options' in event and isinstance(event['result_options'], list) and len(event['result_options']) > 0
        self.has_results.setChecked(has_results)
        self.results_widget.setVisible(has_results)
        
        if has_results:
            self.results_list.clear()
            self.result_editor.hide()
            self.current_result_index = -1
            
            for result in event['result_options']:
                result_text = result.get('result', 'Unnamed Result')
                self.results_list.addItem(result_text)
        
        # Set options - Fix for TypeError: convert to boolean explicitly
        has_options = False
        if 'options' in event:
            if isinstance(event['options'], list) and len(event['options']) > 0:
                has_options = True
        
        self.has_options.setChecked(has_options)
        
        # Ensure proper visibility
        self.options_widget.setVisible(has_options or has_results)
        self.player_options_widget.setVisible(has_options)
        self.results_widget.setVisible(has_results)
        
        if has_options:
            self.options_list.clear()
            self.option_editor.hide()
            self.current_option_index = -1
            
            for option in event['options']:
                self.options_list.addItem(option.get('description', 'Unnamed Option'))
        
        # Force UI refresh
        QApplication.processEvents()
        
        # Enable the editor
        self.enable_editor(True)
    
    def toggle_event_enabled(self, row):
        """Toggle the enabled state of an event
        
        Args:
            row: The row index of the event to toggle
        """
        if row < 0 or row >= len(self.custom_events):
            return
            
        # Get the item from the "Enabled" column
        enabled_item = self.events_list.item(row, 1)
        if not enabled_item:
            # Create one if it doesn't exist
            enabled_item = QTableWidgetItem()
            enabled_item.setTextAlignment(Qt.AlignCenter)
            self.events_list.setItem(row, 1, enabled_item)
            
        # Toggle the enabled state
        event = self.custom_events[row]
        is_enabled = event.get('enabled', True)
        event['enabled'] = not is_enabled
        
        # Update checkbox display
        self.update_enabled_cell(row, not is_enabled)
        
        # Save changes
        self.save_custom_events()
    
    def on_option_selected(self, row):
        """Handle option selection in the list
        
        Args:
            row: The row index of the selected option
        """
        if row < 0 or self.current_event_index < 0 or not self.has_options.isChecked():
            self.option_editor.hide()
            self.current_option_index = -1
            return
            
        event = self.custom_events[self.current_event_index]
        if 'options' not in event or row >= len(event['options']):
            self.option_editor.hide()
            self.current_option_index = -1
            return
            
        option = event['options'][row]
        self.current_option_index = row
        
        self.option_description.setText(option.get('description', ''))
        self.option_impact.setText(option.get('impact', ''))
        
        # Check for random impacts
        has_random_impacts = 'impact_random_options' in option and isinstance(option['impact_random_options'], dict)
        self.has_random_impacts.setChecked(has_random_impacts)
        self.random_impacts_widget.setVisible(has_random_impacts)
        
        if has_random_impacts:
            self.random_impacts_list.clear()
            for impact_text, probability in option['impact_random_options'].items():
                self.random_impacts_list.addItem(f"{impact_text} ({probability:.2f})")
        
        # Check for nested options
        has_nested_options = 'options' in option and isinstance(option['options'], list) and len(option['options']) > 0
        self.has_nested_options.setChecked(has_nested_options)
        self.nested_options_widget.setVisible(has_nested_options)
        
        if has_nested_options:
            self.nested_options_list.clear()
            for nested_option in option['options']:
                self.nested_options_list.addItem(nested_option.get('description', 'Unnamed Sub-Option'))
        
        self.option_editor.show()
    
    def on_random_impact_selected(self, row):
        """Handle random impact selection in the list
        
        Args:
            row: The row index of the selected random impact
        """
        if row < 0 or self.current_option_index < 0 or not self.has_random_impacts.isChecked():
            self.random_impact_editor.hide()
            return
            
        event = self.custom_events[self.current_event_index]
        option = event['options'][self.current_option_index]
        
        if 'impact_random_options' not in option:
            self.random_impact_editor.hide()
            return
            
        # Get the impact text and probability
        impact_texts = list(option['impact_random_options'].keys())
        if row >= len(impact_texts):
            self.random_impact_editor.hide()
            return
            
        impact_text = impact_texts[row]
        probability = option['impact_random_options'][impact_text]
        
        self.random_impact_text.setText(impact_text)
        self.random_impact_probability.setValue(probability)
        
        self.random_impact_editor.show()
    
    def on_nested_option_selected(self, row):
        """Handle nested option selection in the list
        
        Args:
            row: The row index of the selected nested option
        """
        if row < 0 or self.current_option_index < 0 or not self.has_nested_options.isChecked():
            self.nested_option_editor.hide()
            self.current_nested_option_index = -1
            return
            
        event = self.custom_events[self.current_event_index]
        option = event['options'][self.current_option_index]
        
        if 'options' not in option or row >= len(option['options']):
            self.nested_option_editor.hide()
            self.current_nested_option_index = -1
            return
            
        nested_option = option['options'][row]
        self.current_nested_option_index = row
        
        self.nested_option_description.setText(nested_option.get('description', ''))
        self.nested_option_impact.setText(nested_option.get('impact', ''))
        
        # Check for nested sub-options (recursive)
        has_nested_suboptions = 'options' in nested_option and isinstance(nested_option['options'], list) and len(nested_option['options']) > 0
        self.has_nested_suboptions.setChecked(has_nested_suboptions)
        self.nested_suboptions_widget.setVisible(has_nested_suboptions)
        
        if has_nested_suboptions:
            self.nested_suboptions_list.clear()
            for suboption in nested_option['options']:
                self.nested_suboptions_list.addItem(suboption.get('description', 'Unnamed Sub-Sub-Option'))
        
        # Check for random impacts in nested option
        has_nested_random_impacts = 'impact_random_options' in nested_option and isinstance(nested_option['impact_random_options'], dict)
        self.has_nested_random_impacts.setChecked(has_nested_random_impacts)
        self.nested_random_impacts_widget.setVisible(has_nested_random_impacts)
        
        if has_nested_random_impacts:
            self.nested_random_impacts_list.clear()
            for impact_text, probability in nested_option['impact_random_options'].items():
                self.nested_random_impacts_list.addItem(f"{impact_text} ({probability:.2f})")
        
        # Show editor (integrated in the same view instead of as a popup)
        self.nested_option_editor.show()
        
        # Force UI refresh
        QApplication.processEvents()
    
    def on_nested_suboption_selected(self, row):
        """Handle nested sub-option selection in the list"""
        if row < 0 or self.current_nested_option_index < 0 or not self.has_nested_suboptions.isChecked():
            return
            
        event = self.custom_events[self.current_event_index]
        option = event['options'][self.current_option_index]
        nested_option = option['options'][self.current_nested_option_index]
        
        if 'options' not in nested_option or row >= len(nested_option['options']):
            return
            
        self.current_nested_suboption_index = row
        # We could add more levels of editing here if needed
    
    def on_nested_random_impact_selected(self, row):
        """Handle nested random impact selection in the list"""
        if row < 0 or self.current_nested_option_index < 0 or not self.has_nested_random_impacts.isChecked():
            self.nested_random_impact_editor.hide()
            return
            
        event = self.custom_events[self.current_event_index]
        option = event['options'][self.current_option_index]
        nested_option = option['options'][self.current_nested_option_index]
        
        if 'impact_random_options' not in nested_option:
            self.nested_random_impact_editor.hide()
            return
            
        # Get the impact text and probability
        impact_texts = list(nested_option['impact_random_options'].keys())
        if row >= len(impact_texts):
            self.nested_random_impact_editor.hide()
            return
            
        impact_text = impact_texts[row]
        probability = nested_option['impact_random_options'][impact_text]
        
        self.nested_random_impact_text.setText(impact_text)
        self.nested_random_impact_probability.setValue(probability)
        
        self.nested_random_impact_editor.show()
        self.current_nested_random_impact_index = row
    
    def on_result_selected(self, row):
        """Handle result selection in the list
        
        Args:
            row: The row index of the selected result
        """
        if row < 0 or self.current_event_index < 0 or not self.has_results.isChecked():
            self.result_editor.hide()
            self.current_result_index = -1
            return
            
        event = self.custom_events[self.current_event_index]
        if 'result_options' not in event or row >= len(event['result_options']):
            self.result_editor.hide()
            self.current_result_index = -1
            return
            
        result = event['result_options'][row]
        self.current_result_index = row
        
        self.result_text.setText(result.get('result', ''))
        self.impact_text.setText(result.get('impact_text', ''))
        self.result_probability.setValue(result.get('probability', 0.5))
        
        self.result_editor.show()
    
    def create_new_event(self):
        """Create a new custom event"""
        # Generate a new ID
        if not self.custom_events:
            new_id = 1
        else:
            new_id = max(e.get('id', 0) for e in self.custom_events) + 1
            
        # Create a basic event template
        new_event = {
            'id': new_id,
            'title': 'New Custom Event',
            'description': 'This is a custom event. Edit this description.',
            'impact': 'Define the impact of this event. If impact is random or allow player choices add those at bottm of this page',
            'category': 'attribute',
            'enabled': True,
            'season_stages': ['pre-season', 'regular-season-mid'],
            'target_options': ['all-players'],
            'difficulty_weights': {
                'cupcake': 0.2,
                'rookie': 0.2,
                'pro': 0.2,
                'all-madden': 0.2,
                'diabolical': 0.2
            }
        }
        
        # Add to custom events
        self.custom_events.append(new_event)
        
        # Add new row to table
        row = self.events_list.rowCount()
        self.events_list.insertRow(row)
        
        # Set name in first column
        title_item = QTableWidgetItem(new_event['title'])
        self.events_list.setItem(row, 0, title_item)
        
        # Set enabled status in second column
        self.update_enabled_cell(row, True)
        
        # Select the new row
        self.events_list.setCurrentCell(row, 0)
        
        # Save
        self.save_custom_events()
    
    def delete_event(self):
        """Delete the currently selected custom event"""
        if self.current_event_index < 0:
            return
            
        # Ask for confirmation
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this event?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
            
        # Remove the event
        del self.custom_events[self.current_event_index]
        
        # Update list
        self.events_list.removeRow(self.current_event_index)
        
        # Save
        self.save_custom_events()
        
        # Reset selection
        self.current_event_index = -1
        self.enable_editor(False)
    
    def add_option(self):
        """Add a new option to the current event"""
        if self.current_event_index < 0:
            return
            
        # Add option to the event
        event = self.custom_events[self.current_event_index]
        
        if 'options' not in event:
            event['options'] = []
            
        new_option = {
            'description': 'New Option',
            'impact': 'Define the impact of this option.'
        }
        
        event['options'].append(new_option)
        
        # Update the list
        self.options_list.addItem(new_option['description'])
        self.options_list.setCurrentRow(len(event['options']) - 1)
    
    def add_random_impact(self):
        """Add a new random impact to the current option"""
        if self.current_event_index < 0 or self.current_option_index < 0:
            return
            
        event = self.custom_events[self.current_event_index]
        option = event['options'][self.current_option_index]
        
        if 'impact_random_options' not in option:
            option['impact_random_options'] = {}
            
        # Add a new random impact
        new_impact = "New random outcome"
        option['impact_random_options'][new_impact] = 0.5
        
        # Update the list
        self.random_impacts_list.addItem(f"{new_impact} (0.50)")
        self.random_impacts_list.setCurrentRow(len(option['impact_random_options']) - 1)
    
    def add_nested_option(self):
        """Add a new nested option to the current option"""
        if self.current_event_index < 0 or self.current_option_index < 0:
            return
            
        event = self.custom_events[self.current_event_index]
        option = event['options'][self.current_option_index]
        
        if 'options' not in option:
            option['options'] = []
            
        # Add a new nested option
        new_nested_option = {
            'description': 'New Sub-Option',
            'impact': 'Define the impact of this sub-option.'
        }
        
        option['options'].append(new_nested_option)
        
        # Update the list
        self.nested_options_list.addItem(new_nested_option['description'])
        self.nested_options_list.setCurrentRow(len(option['options']) - 1)
    
    def add_result(self):
        """Add a new result to the current event"""
        if self.current_event_index < 0:
            return
            
        event = self.custom_events[self.current_event_index]
        
        if 'result_options' not in event:
            event['result_options'] = []
            
        # Add a new result
        new_result = {
            'result': 'New Result',
            'impact_text': 'Define the impact of this result.',
            'probability': 0.5
        }
        
        event['result_options'].append(new_result)
        
        # Update the list
        self.results_list.addItem(new_result['result'])
        self.results_list.setCurrentRow(len(event['result_options']) - 1)
    
    def delete_option(self):
        """Delete the currently selected option"""
        if self.current_event_index < 0:
            return
            
        row = self.options_list.currentRow()
        if row < 0:
            return
            
        # Ask for confirmation
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this option?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
            
        # Remove the option
        event = self.custom_events[self.current_event_index]
        if 'options' in event and row < len(event['options']):
            del event['options'][row]
            
            # Update list
            self.options_list.takeItem(row)
            
            # Hide option editor
            self.option_editor.hide()
    
    def delete_random_impact(self):
        """Delete the currently selected random impact"""
        if self.current_event_index < 0 or self.current_option_index < 0:
            return
            
        row = self.random_impacts_list.currentRow()
        if row < 0:
            return
            
        # Ask for confirmation
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this random outcome?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
            
        # Remove the random impact
        event = self.custom_events[self.current_event_index]
        option = event['options'][self.current_option_index]
        
        if 'impact_random_options' in option:
            impact_texts = list(option['impact_random_options'].keys())
            if row < len(impact_texts):
                del option['impact_random_options'][impact_texts[row]]
                
                # Update list
                self.random_impacts_list.takeItem(row)
                
                # Hide editor if last item was removed
                if len(option['impact_random_options']) == 0:
                    del option['impact_random_options']
                    self.random_impact_editor.hide()
    
    def delete_nested_option(self):
        """Delete the currently selected nested option"""
        if self.current_event_index < 0 or self.current_option_index < 0:
            return
            
        row = self.nested_options_list.currentRow()
        if row < 0:
            return
            
        # Ask for confirmation
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this sub-option?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
            
        # Remove the nested option
        event = self.custom_events[self.current_event_index]
        option = event['options'][self.current_option_index]
        
        if 'options' in option and row < len(option['options']):
            del option['options'][row]
            
            # Update list
            self.nested_options_list.takeItem(row)
            
            # Hide editor if last item was removed
            if len(option['options']) == 0:
                del option['options']
                self.nested_option_editor.hide()
    
    def delete_result(self):
        """Delete the currently selected result"""
        if self.current_event_index < 0:
            return
            
        row = self.results_list.currentRow()
        if row < 0:
            return
            
        # Ask for confirmation
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this result?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
            
        # Remove the result
        event = self.custom_events[self.current_event_index]
        if 'result_options' in event and row < len(event['result_options']):
            del event['result_options'][row]
            
            # Update list
            self.results_list.takeItem(row)
            
            # Hide editor if last item was removed
            if len(event['result_options']) == 0:
                del event['result_options']
                self.result_editor.hide()
    
    def save_current_event(self):
        """Save the current event"""
        if self.current_event_index < 0:
            return
            
        # Get the current event
        event = self.custom_events[self.current_event_index]
        
        # Update with form values
        event['title'] = self.title_input.text()
        event['description'] = self.description_input.toPlainText()
        event['impact'] = self.impact_input.toPlainText()
        event['category'] = self.category_input.currentText()
        event['is_temporary'] = self.is_temporary.isChecked()
        
        # Get enabled state from the checkbox in the table
        enabled_item = self.events_list.item(self.current_event_index, 1)
        if enabled_item:
            event['enabled'] = enabled_item.checkState() == Qt.CheckState.Checked
        
        # Get season stages
        stages = []
        if self.pre_season.isChecked():
            stages.append('pre-season')
        if self.regular_season_start.isChecked():
            stages.append('regular-season-start')
        if self.regular_season_mid.isChecked():
            stages.append('regular-season-mid')
        if self.regular_season_end.isChecked():
            stages.append('regular-season-end')
        if self.playoffs.isChecked():
            stages.append('playoffs')
        if self.off_season.isChecked():
            stages.append('off-season')
            
        event['season_stages'] = stages
        
        # Get target options
        targets = []
        if self.all_players.isChecked():
            targets.append('all-players')
        elif self.na_option.isChecked():
            targets.append('n/a')
        else:
            # Add selected coaches
            for coach, checkbox in self.coach_checkboxes.items():
                if checkbox.isChecked():
                    targets.append(coach)
                    
            # Add selected player positions
            for pos, checkbox in self.position_checkboxes.items():
                if checkbox.isChecked():
                    targets.append(pos)
                    
        event['target_options'] = targets
        
        # Get difficulty weights
        weights = {}
        for difficulty, spinner in self.difficulty_weights.items():
            weights[difficulty] = spinner.value()
            
        event['difficulty_weights'] = weights
        
        # Handle result options
        if self.has_results.isChecked():
            # If there's a currently selected result, save its current state
            if self.current_result_index >= 0:
                if 'result_options' not in event:
                    event['result_options'] = []
                
                if self.current_result_index < len(event['result_options']):
                    result = event['result_options'][self.current_result_index]
                    result['result'] = self.result_text.text()
                    result['impact_text'] = self.impact_text.toPlainText()
                    result['probability'] = self.result_probability.value()
                    
                    # Update display in the list
                    self.results_list.item(self.current_result_index).setText(result['result'])
        else:
            # Remove results if the checkbox is unchecked
            if 'result_options' in event:
                del event['result_options']
        
        # Handle options
        if self.has_options.isChecked():
            # If there's a currently selected option, save its current state
            if self.current_option_index >= 0:
                if 'options' not in event:
                    event['options'] = []
                
                if self.current_option_index < len(event['options']):
                    option = event['options'][self.current_option_index]
                    option['description'] = self.option_description.text()
                    option['impact'] = self.option_impact.toPlainText()
                    
                    # Handle random impacts - we now support this together with nested options
                    if self.has_random_impacts.isChecked():
                        if self.random_impacts_list.currentRow() >= 0:
                            # Save the current random impact
                            if 'impact_random_options' not in option:
                                option['impact_random_options'] = {}
                            
                            impact_texts = list(option.get('impact_random_options', {}).keys())
                            current_row = self.random_impacts_list.currentRow()
                            
                            if current_row < len(impact_texts):
                                old_impact_text = impact_texts[current_row]
                                probability = option['impact_random_options'].pop(old_impact_text, 0.5)
                                
                                new_impact_text = self.random_impact_text.toPlainText()
                                new_probability = self.random_impact_probability.value()
                                
                                option['impact_random_options'][new_impact_text] = new_probability
                                
                                # Update the list display
                                self.random_impacts_list.item(current_row).setText(f"{new_impact_text} ({new_probability:.2f})")
                    else:
                        # Remove random impacts if the checkbox is unchecked
                        if 'impact_random_options' in option:
                            del option['impact_random_options']
                    
                    # Handle nested options - can coexist with random impacts now
                    if self.has_nested_options.isChecked():
                        if self.current_nested_option_index >= 0:
                            # Save the current nested option
                            if 'options' not in option:
                                option['options'] = []
                            
                            if self.current_nested_option_index < len(option['options']):
                                nested_option = option['options'][self.current_nested_option_index]
                                nested_option['description'] = self.nested_option_description.text()
                                nested_option['impact'] = self.nested_option_impact.toPlainText()
                                
                                # Handle nested sub-options (recursive)
                                if self.has_nested_suboptions.isChecked():
                                    # We don't need to save sub-sub-option details here
                                    # as they're only edited/viewed, not changed in this form
                                    pass
                                else:
                                    # Remove nested sub-options if the checkbox is unchecked
                                    if 'options' in nested_option:
                                        del nested_option['options']
                                
                                # Handle nested random impacts
                                if self.has_nested_random_impacts.isChecked():
                                    if self.current_nested_random_impact_index >= 0:
                                        # Save the current nested random impact
                                        if 'impact_random_options' not in nested_option:
                                            nested_option['impact_random_options'] = {}
                                        
                                        impact_texts = list(nested_option.get('impact_random_options', {}).keys())
                                        if self.current_nested_random_impact_index < len(impact_texts):
                                            old_impact_text = impact_texts[self.current_nested_random_impact_index]
                                            nested_option['impact_random_options'].pop(old_impact_text, 0.5)
                                            
                                            new_impact_text = self.nested_random_impact_text.toPlainText()
                                            new_probability = self.nested_random_impact_probability.value()
                                            
                                            nested_option['impact_random_options'][new_impact_text] = new_probability
                                            
                                            # Update the list display
                                            self.nested_random_impacts_list.item(self.current_nested_random_impact_index).setText(
                                                f"{new_impact_text} ({new_probability:.2f})"
                                            )
                                else:
                                    # Remove nested random impacts if checkbox is unchecked
                                    if 'impact_random_options' in nested_option:
                                        del nested_option['impact_random_options']
                                
                                # Update the list display
                                self.nested_options_list.item(self.current_nested_option_index).setText(nested_option['description'])
                    else:
                        # Remove nested options if the checkbox is unchecked
                        if 'options' in option:
                            del option['options']
                    
                    # Update the display in the list
                    self.options_list.item(self.current_option_index).setText(option['description'])
        else:
            # Remove options if the checkbox is unchecked
            if 'options' in event:
                del event['options']
        
        # Update the title in the first column
        title_item = self.events_list.item(self.current_event_index, 0)
        if title_item:
            title_item.setText(event['title'])
        
        # Update the enabled state visual
        self.update_enabled_cell(self.current_event_index, event['enabled'])
        
        # Save all custom events
        self.save_custom_events()
        
        QMessageBox.information(self, "Saved", "Event saved successfully!")
    
    def toggle_random_impacts(self, state):
        """Toggle visibility of the random impacts section based on checkbox state"""
        is_checked = state == Qt.CheckState.Checked.value
        self.random_impacts_widget.setVisible(is_checked)
        
        # Make sub-options and random impacts mutually exclusive
        if is_checked:
            self.has_nested_options.setChecked(False)
            self.nested_options_widget.setVisible(False)
            self.nested_option_editor.hide()
        
        if state != Qt.CheckState.Checked.value:
            self.random_impact_editor.hide()
    
    def toggle_nested_options(self, state):
        """Toggle visibility of the nested options section based on checkbox state"""
        is_checked = state == Qt.CheckState.Checked.value
        self.nested_options_widget.setVisible(is_checked)
        
        # Make sub-options and random impacts mutually exclusive
        if is_checked:
            self.has_random_impacts.setChecked(False)
            self.random_impacts_widget.setVisible(False)
            self.random_impact_editor.hide()
            
        if state != Qt.CheckState.Checked.value:
            self.nested_option_editor.hide()
    
    def toggle_nested_suboptions(self, state):
        """Toggle visibility of the nested sub-options section based on checkbox state"""
        is_checked = state == Qt.CheckState.Checked.value
        self.nested_suboptions_widget.setVisible(is_checked)
        
        # Make sub-sub-options and random impacts mutually exclusive
        if is_checked:
            self.has_nested_random_impacts.setChecked(False)
            self.nested_random_impacts_widget.setVisible(False)
            self.nested_random_impact_editor.hide()
    
    def toggle_nested_random_impacts(self, state):
        """Toggle visibility of the nested random impacts section based on checkbox state"""
        is_checked = state == Qt.CheckState.Checked.value
        self.nested_random_impacts_widget.setVisible(is_checked)
        
        # Make sub-sub-options and random impacts mutually exclusive
        if is_checked:
            self.has_nested_suboptions.setChecked(False)
            self.nested_suboptions_widget.setVisible(False)
            
        if state != Qt.CheckState.Checked.value:
            self.nested_random_impact_editor.hide()
    
    def show_help(self):
        """Show help dialog explaining custom events"""
        help_text = """
        <h3>How Custom Events Work</h3>
        
        <p>Custom events use the same format as built-in events, but you can create your own to add to the event pool.</p>
        
        <h4>Key Components:</h4>
        <ul>
            <li><b>Basic Properties</b>: Title, description, and impact define what the event is called, what happens, and its effect.</li>
            <li><b>Season Stages</b>: Determines when the event can occur in your franchise season.</li>
            <li><b>Target Options</b>: Which players or coaches can be affected by this event.</li>
            <li><b>Difficulty Weights</b>: Controls how likely the event is to be added to the elligable event pool at different difficulty levels (0-1 scale).</li>
            <li><b>Player Choices</b>: Options the player can select when the event occurs.</li>
        </ul>
        
        <h4>Placeholder Variables:</h4>
        <p>Use these in your descriptions and impacts:</p>
        <ul>
            <li><b>{target}</b>: Will be replaced with the selected player/position</li>
        </ul>
        
        <h4>How Events Are Selected:</h4>
        <p>When you roll for an event, the game:</p>
        <ol>
            <li>Filters events based on your current season stage</li>
            <li>Uses difficulty weights as probability checks</li>
            <li>Randomly selects from eligible events (including custom ones)</li>
            <li>Processes the event by replacing placeholders</li>
        </ol>
        
        <h4>Tips:</h4>
        <ul>
            <li>Set realistic difficulty weights (lower = less likely to occur)</li>
            <li>Test your events by saving and rolling for events</li>
            <li>Use the import/export feature to share your events with others</li>
        </ul>
        """
        
        QMessageBox.information(self, "Custom Events Help", help_text)

    def add_nested_suboption(self):
        """Add a new nested sub-option to the current nested option"""
        if self.current_event_index < 0 or self.current_option_index < 0 or self.current_nested_option_index < 0:
            return
            
        event = self.custom_events[self.current_event_index]
        option = event['options'][self.current_option_index]
        nested_option = option['options'][self.current_nested_option_index]
        
        if 'options' not in nested_option:
            nested_option['options'] = []
            
        # Add a new nested sub-option
        new_suboption = {
            'description': 'New Sub-Sub-Option',
            'impact': 'Define the impact of this sub-sub-option.'
        }
        
        nested_option['options'].append(new_suboption)
        
        # Update the list
        self.nested_suboptions_list.addItem(new_suboption['description'])
        self.nested_suboptions_list.setCurrentRow(len(nested_option['options']) - 1)
    
    def delete_nested_suboption(self):
        """Delete the currently selected nested sub-option"""
        if (self.current_event_index < 0 or self.current_option_index < 0 or 
            self.current_nested_option_index < 0 or self.current_nested_suboption_index < 0):
            return
            
        # Ask for confirmation
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this sub-sub-option?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
            
        event = self.custom_events[self.current_event_index]
        option = event['options'][self.current_option_index]
        nested_option = option['options'][self.current_nested_option_index]
        
        if 'options' in nested_option and self.current_nested_suboption_index < len(nested_option['options']):
            del nested_option['options'][self.current_nested_suboption_index]
            
            # Update list
            self.nested_suboptions_list.takeItem(self.current_nested_suboption_index)
            self.current_nested_suboption_index = -1
            
            # Remove options array if empty
            if len(nested_option['options']) == 0:
                del nested_option['options']
    
    def add_nested_random_impact(self):
        """Add a new random impact to the current nested option"""
        if self.current_event_index < 0 or self.current_option_index < 0 or self.current_nested_option_index < 0:
            return
            
        event = self.custom_events[self.current_event_index]
        option = event['options'][self.current_option_index]
        nested_option = option['options'][self.current_nested_option_index]
        
        if 'impact_random_options' not in nested_option:
            nested_option['impact_random_options'] = {}
            
        # Add a new random impact
        new_impact = "New nested random outcome"
        nested_option['impact_random_options'][new_impact] = 0.5
        
        # Update the list
        self.nested_random_impacts_list.addItem(f"{new_impact} (0.50)")
        self.nested_random_impacts_list.setCurrentRow(len(nested_option['impact_random_options']) - 1)
    
    def delete_nested_random_impact(self):
        """Delete the currently selected nested random impact"""
        if (self.current_event_index < 0 or self.current_option_index < 0 or 
            self.current_nested_option_index < 0 or self.current_nested_random_impact_index < 0):
            return
            
        # Ask for confirmation
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this nested random outcome?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
            
        event = self.custom_events[self.current_event_index]
        option = event['options'][self.current_option_index]
        nested_option = option['options'][self.current_nested_option_index]
        
        if 'impact_random_options' in nested_option:
            impact_texts = list(nested_option['impact_random_options'].keys())
            if self.current_nested_random_impact_index < len(impact_texts):
                del nested_option['impact_random_options'][impact_texts[self.current_nested_random_impact_index]]
                
                # Update list
                self.nested_random_impacts_list.takeItem(self.current_nested_random_impact_index)
                self.current_nested_random_impact_index = -1
                
                # Remove impacts dict if empty
                if len(nested_option['impact_random_options']) == 0:
                    del nested_option['impact_random_options']
                    self.nested_random_impact_editor.hide()
    
    def add_option(self):
        """Add a new option to the current event"""
        if self.current_event_index < 0:
            return
            
        # Add option to the event
        event = self.custom_events[self.current_event_index]
        
        if 'options' not in event:
            event['options'] = []
            
        new_option = {
            'description': 'New Option',
            'impact': 'Define the impact of this option.'
        }
        
        event['options'].append(new_option)
        
        # Update the list
        self.options_list.addItem(new_option['description'])
        self.options_list.setCurrentRow(len(event['options']) - 1) 