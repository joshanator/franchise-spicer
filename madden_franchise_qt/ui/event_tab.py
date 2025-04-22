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
            QMessageBox.information(
                self, "No Events", 
                "No eligible events found for the current difficulty."
            )
            return
        
        self.current_event = event
        
        # Update display
        self.event_title.setText(event.get('title', 'Unknown Event'))
        
        self.description_text.setPlainText(
            event.get('processed_description', event.get('description', ''))
        )
        
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
        
        # Event is already added to history in the roll_event method of EventManager
        QMessageBox.information(
            self, "Event Accepted", 
            "Event has been recorded in your franchise history.\n"
            "Make sure to implement the effects in your Madden game!"
        )
        
        # Reset for next event
        self.current_event = None
        self.accept_button.setEnabled(False)
        self.reroll_button.setEnabled(False)
        
        # Update history tab
        main_window = self.window()
        if hasattr(main_window, 'history_tab') and hasattr(main_window.history_tab, 'refresh'):
            main_window.history_tab.refresh() 