from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QTextEdit, QMessageBox,
    QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QFont, QColor, QPalette


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
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Status message for feedback
        self.status_message = QLabel("")
        self.status_message.setStyleSheet("QLabel { color: #00529B; background-color: #BDE5F8; padding: 8px; border-radius: 4px; }")
        self.status_message.setWordWrap(True)
        self.status_message.setVisible(False)
        main_layout.addWidget(self.status_message)
        
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
        
        main_layout.addWidget(generator_group)
        
        # Event result section
        self.result_group = QGroupBox("Event Result")
        result_layout = QVBoxLayout(self.result_group)
        
        # Event title
        self.event_title = QLabel("No event rolled yet")
        self.event_title.setFont(QFont("Arial", 12, QFont.Bold))
        result_layout.addWidget(self.event_title)
        
        # Event description
        result_layout.addWidget(QLabel("Description:"))
        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        self.description_text.setMinimumHeight(100)
        result_layout.addWidget(self.description_text)
        
        # Event impact
        result_layout.addWidget(QLabel("Impact:"))
        self.impact_text = QTextEdit()
        self.impact_text.setReadOnly(True)
        self.impact_text.setMinimumHeight(60)
        result_layout.addWidget(self.impact_text)
        
        # Target/affected entity
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Affected Player/Coach:"))
        self.target_label = QLabel()
        self.target_label.setFont(QFont("Arial", 10, QFont.Bold))
        target_layout.addWidget(self.target_label)
        target_layout.addStretch()
        result_layout.addLayout(target_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
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
        
        main_layout.addWidget(self.result_group)
        
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
        help_layout.addWidget(help_label)
        
        main_layout.addWidget(help_group)
        
        # Add stretch to push everything up
        main_layout.addStretch()
        
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
        self.status_message.setText(f"Current season stage: {current_stage} - Week {week}, Year {year}")
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
            self._show_status_message(
                f"No eligible events found for the current difficulty and season stage ({self.event_manager.config.get('franchise_info', {}).get('season_stage', 'Pre-Season')}).",
                error=True
            )
            return
        
        self.current_event = event
        
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
        
        # Animate the result (simple highlight effect)
        self._animate_result()
    
    def _animate_result(self):
        """Animate the result with a highlight effect"""
        # Flash the result group to draw attention
        original_style = self.result_group.styleSheet()
        
        # Set highlight
        self.result_group.setStyleSheet(
            "QGroupBox { background-color: #e0f0ff; border: 2px solid #4477AA; }"
        )
        
        # Reset after a delay
        def reset_style():
            self.result_group.setStyleSheet(original_style)
        
        # Use single-shot timer to reset
        from PySide6.QtCore import QTimer
        QTimer.singleShot(300, reset_style)
    
    def _accept_event(self):
        """Accept the current event"""
        if not self.current_event:
            return
        
        # Add the event to history only when accepted
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
        from PySide6.QtCore import QTimer
        QTimer.singleShot(5000, lambda: self.status_message.setVisible(False))
    
    def _add_player_name(self):
        """Add a name for an unnamed player"""
        if not hasattr(self, 'unnamed_player_position') or not self.unnamed_player_position:
            return
            
        # Create an input dialog to get the player name
        from PySide6.QtWidgets import QInputDialog
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