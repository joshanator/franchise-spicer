from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QTextEdit, QMessageBox,
    QFrame, QSizePolicy, QDialog, QScrollArea, QInputDialog
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize, QTimer
from PySide6.QtGui import QFont, QColor, QPalette

# Import get_week_display function
from madden_franchise_qt.ui.franchise_tab import get_week_display


class EventTab(QWidget):
    """Tab for generating and displaying events"""
    
    def __init__(self, event_manager):
        super().__init__()
        
        self.event_manager = event_manager
        self.current_event = None
        
        # Set up UI
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI components"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create scroll area for all content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Create a container widget for the scroll area
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        scroll_layout.setSpacing(15)
        
        # Status message for feedback
        self.status_message = QLabel("")
        self.status_message.setStyleSheet("QLabel { color: #00529B; background-color: #BDE5F8; padding: 8px; border-radius: 4px; }")
        self.status_message.setWordWrap(True)
        self.status_message.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.status_message.setVisible(False)
        scroll_layout.addWidget(self.status_message)
        
        # Event generation section
        generator_group = QGroupBox("Generate Random Event")
        generator_layout = QVBoxLayout(generator_group)
        
        # Roll button with styling
        self.roll_button = QPushButton("ROLL FOR EVENT")
        self.roll_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.roll_button.setMinimumHeight(50)
        self.roll_button.clicked.connect(self._roll_event)
        generator_layout.addWidget(self.roll_button)
        
        # Current difficulty display
        difficulty_layout = QHBoxLayout()
        difficulty_layout.addWidget(QLabel("Current Difficulty:"))
        self.difficulty_label = QLabel()
        self.difficulty_label.setFont(QFont("Arial", 10, QFont.Bold))
        difficulty_layout.addWidget(self.difficulty_label)
        difficulty_layout.addStretch()
        generator_layout.addLayout(difficulty_layout)
        
        scroll_layout.addWidget(generator_group)
        
        # Event result section
        self.result_group = QGroupBox("Event Result")
        result_layout = QVBoxLayout(self.result_group)
        
        # Event title
        self.event_title = QLabel("No event rolled yet")
        self.event_title.setFont(QFont("Arial", 12, QFont.Bold))
        self.event_title.setWordWrap(True)
        self.event_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        result_layout.addWidget(self.event_title)
        
        # Event description
        result_layout.addWidget(QLabel("Description:"))
        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        self.description_text.setMinimumHeight(50)
        self.description_text.setMaximumHeight(80)
        self.description_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.description_text.setLineWrapMode(QTextEdit.WidgetWidth)
        result_layout.addWidget(self.description_text)
        
        # Event impact
        result_layout.addWidget(QLabel("Impact:"))
        self.impact_text = QTextEdit()
        self.impact_text.setReadOnly(True)
        self.impact_text.setMinimumHeight(30)
        self.impact_text.setMaximumHeight(60)
        self.impact_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.impact_text.setLineWrapMode(QTextEdit.WidgetWidth)
        result_layout.addWidget(self.impact_text)
        
        # Target/affected entity
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Affected Player/Coach:"))
        self.target_label = QLabel()
        self.target_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.target_label.setWordWrap(True)
        target_layout.addWidget(self.target_label)
        target_layout.addStretch()
        result_layout.addLayout(target_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)  # Add spacing between buttons
        
        self.accept_button = QPushButton("Accept Event")
        self.accept_button.clicked.connect(self._accept_event)
        self.accept_button.setEnabled(False)
        buttons_layout.addWidget(self.accept_button)
        
        self.reroll_button = QPushButton("Re-roll Event")
        self.reroll_button.clicked.connect(self._roll_event)
        self.reroll_button.setEnabled(False)
        buttons_layout.addWidget(self.reroll_button)
        
        buttons_layout.addStretch()
        result_layout.addLayout(buttons_layout)
        
        scroll_layout.addWidget(self.result_group)
        
        # Help section
        help_group = QGroupBox("How to Use")
        help_layout = QVBoxLayout(help_group)
        
        help_text = """
        1. Click "ROLL FOR EVENT" to generate a random event based on current difficulty
        2. Review the event details and its impact on your franchise
        3. Accept the event or re-roll for a different one
        4. Implement the changes in your Madden franchise as indicated
        """
        
        help_label = QLabel(help_text)
        help_label.setWordWrap(True)
        help_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        help_layout.addWidget(help_label)
        
        scroll_layout.addWidget(help_group)
        
        # Add stretch to push everything up
        scroll_layout.addStretch()
        
        # Set the scroll content and add to main layout
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # Initialize displays
        self.refresh()
    
    def refresh(self):
        """Refresh tab with current data"""
        # Update difficulty display
        difficulty = self.event_manager.get_difficulty()
        self.difficulty_label.setText(difficulty.capitalize())
        
        # Display current season stage
        current_stage = self.event_manager.config.get('franchise_info', {}).get('season_stage', 'Pre-Season')
        week, year = self.event_manager.get_current_week_year()
        
        # Convert week number to user-friendly display
        week_display = get_week_display(week)
        
        # Include the internal stage name for debugging
        self.status_message.setText(f"Current season stage: {current_stage} - {week_display}, Year {year}")
        self.status_message.setVisible(True)
        
        # Clear event display if no current event
        if not hasattr(self, 'current_event') or not self.current_event:
            self.event_title.setText("No event rolled yet")
            self.description_text.setPlainText("Roll for an event to see what happens to your franchise!")
            self.impact_text.clear()
            self.target_label.clear()
            
            self.accept_button.setEnabled(False)
            self.reroll_button.setEnabled(False)
    
    def _roll_event(self):
        """Generate a random event"""
        event = self.event_manager.roll_event()
        
        if not event:
            current_stage = self.event_manager.config.get('franchise_info', {}).get('season_stage', 'Pre-Season')
            self._show_status_message(
                f"No eligible events found for the current difficulty ({self.event_manager.get_difficulty()}) " +
                f"and season stage ({current_stage}).",
                error=True
            )
            return
        
        self.current_event = event
        
        # Handle options recursively until no more options need to be selected
        while 'options' in event and event['options']:
            event = self._show_options_dialog(event)
            self.current_event = event
        
        # Start update - freeze layout to prevent jumbled appearance
        self.setUpdatesEnabled(False)
        

        # TODO: pull out into a function that updates current_event for all target references
        # Check if this event has a target player without a name
        has_unnamed_player = False
        if event.get('target_options'):
            # Get the selected target position
            target_position = None
            
            # First check if we've already processed and stored the target position
            if 'selected_target' in event:
                # Extract position from "Name (Position)" format or just use as-is if no name
                target_text = event.get('selected_target', '')
                if '(' in target_text and ')' in target_text:
                    # Extract position from parentheses
                    target_position = target_text[target_text.find('(')+1:target_text.find(')')]
                else:
                    # Just the position
                    target_position = target_text
            
            # If we couldn't extract from selected_target, get the original position
            if not target_position and 'original_target_position' in event:
                target_position = event.get('original_target_position')
            
            # If we have a position, check if it has a name
            if target_position:
                player_name = self.event_manager.config.get('roster', {}).get(target_position, "")
                if not player_name or not player_name.strip():
                    has_unnamed_player = True
                    self.unnamed_player_position = target_position
        
        # Update display
        self.event_title.setText(event.get('title', 'Unknown Event'))
        
        # Display description without impact information
        description = event.get('processed_description', event.get('description', ''))
        self.description_text.setPlainText(description)
        
        # Display impact separately
        self.impact_text.setPlainText(event.get('impact', ''))
        
        # Set target if available
        target = event.get('selected_target', '')
        if target:
            self.target_label.setText(target)
        else:
            self.target_label.setText("N/A")
        
        # Enable buttons
        self.accept_button.setEnabled(True)
        self.reroll_button.setEnabled(True)
        
        # If there's an unnamed player, show the add name button
        if has_unnamed_player:
            # Check if we already have the button, if not create it
            if not hasattr(self, 'add_player_name_button'):
                self.add_player_name_button = QPushButton("Add Player Name")
                self.add_player_name_button.clicked.connect(self._add_player_name)
            
            # Find the buttons layout in the result group
            for child in self.result_group.children():
                if isinstance(child, QVBoxLayout):
                    result_layout = child
                    # Find the buttons layout
                    for i in range(result_layout.count()):
                        item = result_layout.itemAt(i)
                        if isinstance(item, QHBoxLayout):
                            # Check if our button is already in the layout
                            button_found = False
                            for j in range(item.count()):
                                if item.itemAt(j).widget() == self.add_player_name_button:
                                    button_found = True
                                    break
                            
                            if not button_found:
                                # Insert our button before the stretch
                                item.insertWidget(item.count()-1, self.add_player_name_button)
                            break
            
            self.add_player_name_button.setVisible(True)
            
            # Show a notification
            self._show_status_message(
                f"This event involves a player at position {self.unnamed_player_position} who doesn't have a name. " 
                "Click 'Add Player Name' to assign a name before accepting.",
                error=False
            )
        elif hasattr(self, 'add_player_name_button'):
            # Hide the button if it exists
            self.add_player_name_button.setVisible(False)
        
        # Re-enable updates and refresh the display
        self.setUpdatesEnabled(True)
        
        # Animate the result (better highlight effect)
        self._animate_result()
    
    def _animate_result(self):
        """Animate the result with a highlight effect"""
        # Use property animation for smoother transition
        animation = QPropertyAnimation(self.result_group, b"styleSheet")
        animation.setDuration(300)  # 300ms duration
        
        # Original style
        original_style = self.result_group.styleSheet()
        
        # Highlight style
        highlight_style = "QGroupBox { background-color: #e0f0ff; border: 2px solid #4477AA; }"
        
        # Set start value
        animation.setStartValue(original_style)
        
        # Set end value (highlight)
        animation.setEndValue(highlight_style)
        
        # Use ease in-out curve for smoother transition
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Start animation
        animation.start()
        
        # Return to original style after animation
        QTimer.singleShot(500, lambda: self.result_group.setStyleSheet(original_style))
    
    def _accept_event(self):
        """Accept the current event"""
        if not self.current_event:
            return
        
        # For normal events, add directly to history
        # For events with options, check if an option has been selected
        has_selected_option = 'selected_option' in self.current_event
        
        if has_selected_option:
            # For events with selected options, pass the option index
            option_index = self.current_event.get('selected_option')
            if self.event_manager.select_event_option(self.current_event, option_index):
                option_desc = self.current_event.get('selected_option_description', '')
                self._show_status_message(f"Event with option '{option_desc}' has been recorded in your franchise history. Make sure to implement the effects in your Madden game!")
            else:
                self._show_status_message("Failed to record event choice to history", error=True)
        else:
            # For events without options, add directly to history
            if self.event_manager.accept_event(self.current_event):
                self._show_status_message("Event has been recorded in your franchise history. Make sure to implement the effects in your Madden game!")
            else:
                self._show_status_message("Failed to record event to history", error=True)
        
        # Reset for next event
        self.current_event = None
        self.accept_button.setEnabled(False)
        self.reroll_button.setEnabled(False)
        
        # Update history tab
        main_window = self.window()
        if hasattr(main_window, 'history_tab') and hasattr(main_window.history_tab, 'refresh'):
            main_window.history_tab.refresh()
    
    def _process_impact_random_options(self, option):
        """Process random impact options from an option
        
        Args:
            option: The option with random impact options
            
        Returns:
            The selected impact text
        """
        import random
        
        # Get the random impact options (dictionary with impact text as keys and probabilities as values)
        impact_options = option.get('impact_random_options', {})
        
        # If no impact options are available, return the standard impact
        if not impact_options:
            return option.get('impact', '')
        
        # Extract the options and their weights
        options = list(impact_options.keys())
        weights = list(impact_options.values())
        
        # Select a random impact based on the provided weights
        # random.choices returns a list, so we take the first item
        selected_impact = random.choices(population=options, weights=weights, k=1)[0]
        
        # Show a status message with the randomly selected impact
        self._show_status_message(f"Random outcome: {selected_impact}")
        
        # Return the selected impact
        return selected_impact
        
    def _show_options_dialog(self, event):
        """Show a dialog with options for the user to choose from and return the modified event
        
        Args:
            event: The event with options
            
        Returns:
            The event with the selected option
        """
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Choose an Option - {event.get('title', 'Event')}")
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(300)
        
        # Create layout
        layout = QVBoxLayout(dialog)
        
        # Add event description
        description = QLabel(event.get('processed_description', event.get('description', '')))
        description.setWordWrap(True)
        description.setStyleSheet("font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(description)
        
        # Create scroll area for options
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        options_layout = QVBoxLayout(scroll_content)
        
        # Store selected option index
        selected_option_index = [None]  # Use list to store by reference
        
        # Function to handle option selection
        def on_option_selected(index):
            selected_option_index[0] = index
            dialog.accept()
        
        # Add options as buttons
        options = event.get('options', [])
        for i, option in enumerate(options):
            option_text = option.get('processed_description', option.get('description', f"Option {i+1}"))
            
            option_button = QPushButton(option_text)
            option_button.setStyleSheet("text-align: left; padding: 10px; font-size: 12px;")
            option_button.setMinimumHeight(60)
            
            # Connect button to option selection
            option_index = i
            option_button.clicked.connect(lambda checked=False, idx=option_index: on_option_selected(idx))
            
            options_layout.addWidget(option_button)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Show dialog and wait for user selection
        dialog.exec()
        
        # If user selected an option, process it
        if selected_option_index[0] is not None:
            option_index = selected_option_index[0]
            option = event.get('options', [])[option_index]
            option_description = option.get('processed_description', option.get('description', ''))
            option_impact = option.get('impact', '')

            if 'impact_random_options' in option:
                option_impact = self._process_impact_random_options(option)

            # Save the selected option details for _accept_event to use
            event['selected_option'] = option_index
            event['selected_option_description'] = option_description
            event['selected_option_impact'] = option_impact
            
            # Update target options if present in the selected option
            if 'target_options' in option and len(option.get('target_options', [])) > 0:
                event['target_options'] = option.get('target_options', [])

            # Handle nested options
            if 'options' in option and len(option.get('options', [])) > 0:
                # Replace event options with the nested options
                event['options'] = option.get('options', [])
                # Update event description to reflect the current choice
                event['processed_description'] = f"{event.get('description', '')}\n\nYou selected: {option_description}"
            else:
                # No more nested options
                event['options'] = None
                
                # Store the selected option in the event
                event['description'] = option_description
                event['impact'] = option_impact
            
            # Only update the UI if this is the final option (no nested options)
            if event['options'] is None:
                # Freeze updates while modifying content
                self.setUpdatesEnabled(False)
                
                # Update the display to show the selected option
                self.event_title.setText(f"{event.get('title', 'Unknown Event')} - Option Selected")
                
                # Update description to include the chosen option
                description = event.get('processed_description', event.get('description', ''))
                self.description_text.setPlainText(f"{description}\n\nYou selected: {option_description}")
                
                # Update impact to show the option's impact
                self.impact_text.setPlainText(option_impact)
                
                # Keep buttons enabled so user can accept or re-roll
                self.accept_button.setEnabled(True)
                self.reroll_button.setEnabled(True)
                
                # Re-enable updates
                self.setUpdatesEnabled(True)
                
                # Show a status message confirming the selection
                self._show_status_message(f"Option selected: {option_description}. Click 'Accept Event' to confirm or 'Re-roll Event' to try again.")
                
                # Animate the result to draw attention to the updated display
                self._animate_result()
        
        return event
    
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
    
    def _add_player_name(self):
        """Add a name for an unnamed player"""
        if not hasattr(self, 'unnamed_player_position') or not self.unnamed_player_position:
            return
            
        # Create an input dialog to get the player name
        player_name, ok = QInputDialog.getText(
            self, 
            "Add Player Name", 
            f"Enter the name for the player at position {self.unnamed_player_position}:"
        )
        
        if ok and player_name.strip():
            # Update the roster with the new name
            if self.event_manager.update_roster(self.unnamed_player_position, player_name):
                # Update the event with the new name
                if self.current_event:
                    target_display = f"{player_name} ({self.unnamed_player_position})"
                    
                    # Update the target label
                    self.target_label.setText(target_display)
                    
                    # Update description if it contains the position
                    desc = self.description_text.toPlainText()
                    if self.unnamed_player_position in desc:
                        desc = desc.replace(self.unnamed_player_position, target_display)
                        self.description_text.setPlainText(desc)
                    
                    # Update the current event
                    self.current_event['selected_target'] = target_display
                    # Store updated description in the event too
                    self.current_event['processed_description'] = desc
                
                # Hide the add name button
                if hasattr(self, 'add_player_name_button'):
                    self.add_player_name_button.setVisible(False)
                
                # Show success message
                self._show_status_message(f"Successfully added name '{player_name}' for position {self.unnamed_player_position}")
                
                # Clear the saved position
                del self.unnamed_player_position
            else:
                self._show_status_message("Failed to update the roster", error=True) 