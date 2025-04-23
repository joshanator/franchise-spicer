from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QTextEdit, QTreeWidget,
    QTreeWidgetItem, QComboBox, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from datetime import datetime
from madden_franchise_qt.ui.franchise_tab import get_week_display


class HistoryTab(QWidget):
    """Tab for viewing event history"""
    
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
        
        # Title and controls
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Event History")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(title_label)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Filter by Year:"))
        self.year_combo = QComboBox()
        self.year_combo.addItem("All")
        filter_layout.addWidget(self.year_combo)
        
        filter_layout.addWidget(QLabel("Week:"))
        self.week_combo = QComboBox()
        self.week_combo.addItem("All")
        filter_layout.addWidget(self.week_combo)
        
        self.apply_filter_button = QPushButton("Apply Filter")
        self.apply_filter_button.clicked.connect(self.apply_filter)
        filter_layout.addWidget(self.apply_filter_button)
        
        self.reset_filter_button = QPushButton("Reset")
        self.reset_filter_button.clicked.connect(self.reset_filter)
        filter_layout.addWidget(self.reset_filter_button)
        
        header_layout.addLayout(filter_layout)
        main_layout.addLayout(header_layout)
        
        # History tree
        self.history_tree = QTreeWidget()
        self.history_tree.setColumnCount(5)
        self.history_tree.setHeaderLabels(["Week/Year", "Player/Position", "Event", "Description", "Impact"])
        
        # Configure header
        header = self.history_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        
        self.history_tree.setAlternatingRowColors(True)
        self.history_tree.currentItemChanged.connect(self._on_event_selected)
        
        main_layout.addWidget(self.history_tree)
        
        # Event details section
        details_group = QGroupBox("Event Details")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMinimumHeight(100)
        details_layout.addWidget(self.details_text)
        
        main_layout.addWidget(details_group)
        
        # Load data
        self.refresh()
    
    def refresh(self):
        """Refresh tab with current data"""
        # Load history
        history = self.event_manager.get_event_history()
        
        # Update filter options
        self._update_filter_options(history)
        
        # Apply current filters
        self._populate_history(self._filter_history(history))
    
    def _update_filter_options(self, history):
        """Update the filter dropdown options
        
        Args:
            history: The event history to get options from
        """
        # Get unique years and weeks
        years = set()
        weeks = set()
        
        for event in history:
            if 'year' in event:
                years.add(str(event['year']))
            if 'week' in event:
                weeks.add(event['week'])  # Store actual week number
        
        # Save current selections
        current_year = self.year_combo.currentText()
        current_week = self.week_combo.currentText()
        
        # Clear and repopulate
        self.year_combo.clear()
        self.week_combo.clear()
        
        # Add "All" option
        self.year_combo.addItem("All")
        self.week_combo.addItem("All")
        
        # Add sorted options
        for year in sorted(years):
            self.year_combo.addItem(year)
        
        # Create a mapping of display values to actual week numbers
        self.week_display_map = {}
        
        # Add sorted weeks with user-friendly display
        for week in sorted(weeks):
            week_display = get_week_display(week)
            self.week_combo.addItem(week_display)
            self.week_display_map[week_display] = week
        
        # Restore selections if they still exist
        year_index = self.year_combo.findText(current_year)
        if year_index >= 0:
            self.year_combo.setCurrentIndex(year_index)
        
        # Try to find by week display or fall back to "All"
        week_index = self.week_combo.findText(current_week)
        if week_index < 0:
            self.week_combo.setCurrentIndex(0)  # Default to "All"
        else:
            self.week_combo.setCurrentIndex(week_index)
    
    def _filter_history(self, history):
        """Filter history based on selected criteria
        
        Args:
            history: The full event history
            
        Returns:
            list: The filtered history
        """
        year_filter = self.year_combo.currentText()
        week_display_filter = self.week_combo.currentText()
        
        if year_filter == "All" and week_display_filter == "All":
            return history
        
        filtered = []
        for event in history:
            year_match = year_filter == "All" or str(event.get('year', '')) == year_filter
            
            # Handle week filter using the display map
            if week_display_filter == "All":
                week_match = True
            else:
                # Get the actual week number for the selected display
                week_num = self.week_display_map.get(week_display_filter)
                week_match = event.get('week') == week_num if week_num is not None else False
            
            if year_match and week_match:
                filtered.append(event)
        
        return filtered
    
    def _populate_history(self, history):
        """Populate the history tree with events
        
        Args:
            history: The event history to display
        """
        # Clear current items
        self.history_tree.clear()
        
        # Add events
        for event in reversed(history):  # Show newest first
            item = QTreeWidgetItem()
            
            # Week/Year with user-friendly week display
            week = event.get('week', '')
            year = event.get('year', '')
            if week:
                week_display = get_week_display(week)
                item.setText(0, f"{week_display}, Year {year}")
            else:
                item.setText(0, f"Y{year}")
            
            # Player/Position instead of Date
            player_position = event.get('player_position', '')
            if not player_position:
                # Try to get it from the event's selected_target
                player_position = event.get('selected_target', 'N/A')
            item.setText(1, player_position)
            
            # Event title
            item.setText(2, event.get('title', ''))
            
            # Description
            item.setText(3, event.get('description', '')[:100] + '...' if len(event.get('description', '')) > 100 else event.get('description', ''))
            
            # Impact
            item.setText(4, event.get('impact', '')[:100] + '...' if len(event.get('impact', '')) > 100 else event.get('impact', ''))
            
            self.history_tree.addTopLevelItem(item)
        
        # Auto-resize columns
        for i in range(5):
            self.history_tree.resizeColumnToContents(i)
    
    def apply_filter(self):
        """Apply the current filter settings"""
        self.refresh()
    
    def reset_filter(self):
        """Reset filters to show all events"""
        self.year_combo.setCurrentIndex(0)  # "All"
        self.week_combo.setCurrentIndex(0)  # "All"
        self.refresh()
    
    def _on_event_selected(self, current, previous):
        """Handle event selection
        
        Args:
            current: The currently selected item
            previous: The previously selected item
        """
        if not current:
            self.details_text.clear()
            return
        
        # Build detail text
        detail_text = f"<h3>{current.text(2)}</h3>"  # Event title
        detail_text += f"<p><b>Time:</b> {current.text(0)}</p>"
        detail_text += f"<p><b>Player/Position:</b> {current.text(1)}</p>"
        detail_text += f"<p><b>Description:</b> {current.text(3)}</p>"
        detail_text += f"<p><b>Impact:</b> {current.text(4)}</p>"
        
        self.details_text.setHtml(detail_text) 