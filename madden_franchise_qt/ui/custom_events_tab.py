from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTabWidget, QLineEdit, QComboBox, QTextEdit, QListWidget,
    QFileDialog, QMessageBox, QScrollArea, QSpinBox, QDoubleSpinBox,
    QFormLayout, QCheckBox, QGroupBox, QRadioButton, QInputDialog
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QFont, QIcon

import json
import os
import copy

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
        
        self.events_list = QListWidget()
        self.events_list.currentRowChanged.connect(self.on_event_selected)
        left_layout.addWidget(QLabel("Your Custom Events:"))
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
        
        self.category_input = QComboBox()
        self.category_input.addItems([
            "attribute", "contract", "draft", "free-agency", "injury", 
            "lineup", "roster", "suspension", "team", "trade", "challenge", "penalty"
        ])
        basic_layout.addRow("Category:", self.category_input)
        
        self.is_temporary = QCheckBox("Temporary Event (expires after effect)")
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
            "Offense WR": ["WR1", "WR2", "WR3", "WR4", "WR5"],
            "Offense TE": ["TE1", "TE2", "TE3"],
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
        
        # Options (choices) section
        options_group = QGroupBox("Event Options (Player Choices)")
        options_layout = QVBoxLayout()
        
        self.has_options = QCheckBox("This event has player choices")
        self.has_options.stateChanged.connect(self.toggle_options_section)
        options_layout.addWidget(self.has_options)
        
        self.options_widget = QWidget()
        self.options_layout = QVBoxLayout(self.options_widget)
        
        self.options_list = QListWidget()
        self.options_list.currentRowChanged.connect(self.on_option_selected)
        self.options_layout.addWidget(QLabel("Options:"))
        self.options_layout.addWidget(self.options_list)
        
        options_btn_layout = QHBoxLayout()
        
        self.add_option_btn = QPushButton("Add Option")
        self.add_option_btn.clicked.connect(self.add_option)
        options_btn_layout.addWidget(self.add_option_btn)
        
        self.delete_option_btn = QPushButton("Delete Option")
        self.delete_option_btn.clicked.connect(self.delete_option)
        options_btn_layout.addWidget(self.delete_option_btn)
        
        self.options_layout.addLayout(options_btn_layout)
        
        # Option editor
        self.option_editor = QWidget()
        option_editor_layout = QFormLayout(self.option_editor)
        
        self.option_description = QLineEdit()
        option_editor_layout.addRow("Option Text:", self.option_description)
        
        self.option_impact = QTextEdit()
        self.option_impact.setMaximumHeight(80)
        option_editor_layout.addRow("Option Impact:", self.option_impact)
        
        self.options_layout.addWidget(self.option_editor)
        self.option_editor.hide()  # Hide until an option is selected
        
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
        self.options_widget.setVisible(state == Qt.CheckState.Checked.value)
    
    def enable_editor(self, enabled):
        """Enable or disable the event editor
        
        Args:
            enabled: Whether to enable the editor
        """
        self.editor_widget.setEnabled(enabled)
        self.save_event_btn.setEnabled(enabled)
    
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
        self.events_list.clear()
        for event in self.custom_events:
            self.events_list.addItem(event.get('title', 'Unnamed Event'))
        
        # Disable editor when refreshing
        self.enable_editor(False)
        self.current_event_index = -1
    
    def save_custom_events(self):
        """Save custom events to the config"""
        # Update the config with custom events
        self.event_manager.config['custom_events'] = self.custom_events
        self.event_manager._save_config()  # Save using event manager's method
    
    def on_event_selected(self, row):
        """Handle event selection in the list
        
        Args:
            row: The row index of the selected event
        """
        if row < 0 or row >= len(self.custom_events):
            self.enable_editor(False)
            self.current_event_index = -1
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
        
        # Set options - Fix for TypeError: convert to boolean explicitly
        has_options = False
        if 'options' in event:
            if isinstance(event['options'], list) and len(event['options']) > 0:
                has_options = True
        
        self.has_options.setChecked(has_options)
        self.options_widget.setVisible(has_options)
        
        self.options_list.clear()
        self.option_editor.hide()
        
        if has_options:
            for option in event['options']:
                self.options_list.addItem(option.get('description', 'Unnamed Option'))
        
        # Enable the editor
        self.enable_editor(True)
    
    def on_option_selected(self, row):
        """Handle option selection in the list
        
        Args:
            row: The row index of the selected option
        """
        if row < 0 or self.current_event_index < 0 or not self.has_options.isChecked():
            self.option_editor.hide()
            return
            
        event = self.custom_events[self.current_event_index]
        if 'options' not in event or row >= len(event['options']):
            self.option_editor.hide()
            return
            
        option = event['options'][row]
        
        self.option_description.setText(option.get('description', ''))
        self.option_impact.setText(option.get('impact', ''))
        
        self.option_editor.show()
    
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
            'impact': 'Define the impact of this event.',
            'category': 'attribute',
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
        
        # Update list and select the new event
        self.events_list.addItem(new_event['title'])
        self.events_list.setCurrentRow(len(self.custom_events) - 1)
        
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
        self.events_list.takeItem(self.current_event_index)
        
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
        
        # Handle options
        if self.has_options.isChecked():
            # If there's a currently selected option, save its current state
            option_row = self.options_list.currentRow()
            if option_row >= 0 and 'options' in event and option_row < len(event['options']):
                option = event['options'][option_row]
                option['description'] = self.option_description.text()
                option['impact'] = self.option_impact.toPlainText()
                
                # Update the display in the list
                self.options_list.item(option_row).setText(option['description'])
        else:
            # Remove options if the checkbox is unchecked
            if 'options' in event:
                del event['options']
        
        # Update the list display
        self.events_list.item(self.current_event_index).setText(event['title'])
        
        # Save all custom events
        self.save_custom_events()
        
        QMessageBox.information(self, "Saved", "Event saved successfully!")
    
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