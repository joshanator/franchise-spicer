from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QTabWidget, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from datetime import datetime

from madden_franchise_qt.ui.franchise_tab import get_week_display, get_season_stage_for_week


class EffectsTab(QWidget):
    """Tab for viewing all active effects"""
    
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
        
        # Title
        title_label = QLabel("Effect Tracker")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        main_layout.addWidget(title_label)
        
        # Create tabs for different effect views
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create individual tabs
        self._create_season_effects_tab()
        self._create_temporary_effects_tab()
        
        # Refresh button at the bottom
        refresh_button = QPushButton("Refresh Effects")
        refresh_button.clicked.connect(self.refresh)
        main_layout.addWidget(refresh_button)
        
        # Load data initially
        self.refresh()
    
    def _create_season_effects_tab(self):
        """Create the tab for season-related effects"""
        season_tab = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(season_tab)
        
        # Layout for the season effects tab
        layout = QVBoxLayout(season_tab)
        
        # Season effects tree
        self.season_tree = QTreeWidget()
        self.season_tree.setColumnCount(4)
        self.season_tree.setHeaderLabels(["Season Stage", "Player/Position", "Effect Description", "Impact"])
        
        # Configure header
        header = self.season_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        
        self.season_tree.setAlternatingRowColors(True)
        layout.addWidget(self.season_tree)
        
        self.tab_widget.addTab(scroll_area, "Season Effects")
    
    def _create_temporary_effects_tab(self):
        """Create the tab for temporary effects"""
        temp_tab = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(temp_tab)
        
        # Layout for the temporary effects tab
        layout = QVBoxLayout(temp_tab)
        
        # Temporary effects tree
        self.temp_tree = QTreeWidget()
        self.temp_tree.setColumnCount(6)
        self.temp_tree.setHeaderLabels(["Player/Position", "Effect Type", "Description", "Impact", "Started", "Time Remaining"])
        
        # Configure header
        header = self.temp_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        self.temp_tree.setAlternatingRowColors(True)
        layout.addWidget(self.temp_tree)
        
        self.tab_widget.addTab(scroll_area, "Temporary Effects")
    
    def refresh(self):
        """Refresh tab with current data"""
        # Get current week and year
        try:
            current_week, current_year = self.event_manager.get_current_week_year()
        except:
            current_week, current_year = 1, 1
        
        # Get the current season stage
        current_stage = get_season_stage_for_week(current_week)
        
        # Load history
        history = self.event_manager.get_event_history()
        
        # Process effects
        self._populate_season_effects(history, current_stage)
        self._populate_temporary_effects(history, current_week, current_year)
    
    def _populate_season_effects(self, history, current_stage):
        """Populate the season effects tree
        
        Args:
            history: The event history
            current_stage: The current season stage
        """
        self.season_tree.clear()
        
        # Group events by season stage
        stage_events = {}
        
        for event in history:
            # Skip events with no impact
            if not event.get('impact'):
                continue
                
            # Extract event data
            title = event.get('title', '')
            impact = event.get('impact', '')
            target = event.get('selected_target', 'N/A')
            
            # Get event data from event_id if available
            # This would require loading the original event data
            # For now, we'll just use the history data
            
            # Add to appropriate stage
            # Simplified approach - show all events with season stage relevance
            if "season" in impact.lower() or "stage" in impact.lower() or "year" in impact.lower():
                stage = current_stage
                if stage not in stage_events:
                    stage_events[stage] = []
                stage_events[stage].append({
                    'title': title,
                    'impact': impact,
                    'target': target
                })
        
        # Add stage groups to tree
        for stage, events in stage_events.items():
            stage_item = QTreeWidgetItem(self.season_tree)
            stage_item.setText(0, stage)
            stage_item.setFont(0, QFont("Arial", 10, QFont.Bold))
            
            for event in events:
                event_item = QTreeWidgetItem(stage_item)
                event_item.setText(0, "")  # No stage in child item
                event_item.setText(1, event['target'])
                event_item.setText(2, event['title'])
                event_item.setText(3, event['impact'])
        
        self.season_tree.expandAll()
    
    def _populate_temporary_effects(self, history, current_week, current_year):
        """Populate the temporary effects tree
        
        Args:
            history: The event history
            current_week: The current week
            current_year: The current year
        """
        self.temp_tree.clear()
        
        # Look for temporary effects marked with is_temporary tag
        temp_effects = []
        
        for event in history:
            # Skip events with no impact
            if not event.get('impact'):
                continue
                
            # Extract event data
            title = event.get('title', '')
            impact = event.get('impact', '')
            target = event.get('selected_target', 'N/A')
            week = event.get('week', 0)
            year = event.get('year', 0)
            category = "Attribute"  # Default category
            
            # First check if the event has the is_temporary flag
            is_temporary = event.get('is_temporary', False)
            
            # If not found directly, check for temporary keywords in impact
            if not is_temporary:
                temp_keywords = ["game", "week", "match", "next", "temp", "suspend", "for the"]
                if any(keyword in impact.lower() for keyword in temp_keywords):
                    is_temporary = True
            
            # If the event has a selected_option, check if that option has is_temporary
            if not is_temporary and 'selected_option' in event and isinstance(event['selected_option'], dict):
                is_temporary = event['selected_option'].get('is_temporary', False)
            
            # Determine the category
            if "suspend" in impact.lower():
                category = "Suspension"
            elif "+1" in impact or "+2" in impact or "+3" in impact or "-1" in impact or "-2" in impact or "-3" in impact:
                category = "Attribute"
            elif "lineup" in impact.lower() or "start" in impact.lower():
                category = "Lineup"
            elif "injur" in impact.lower():
                category = "Injury"
            
            # Calculate time remaining
            time_remaining = "Unknown"
            started = f"Week {week}, Year {year}"
            
            # Check if this effect is still active
            is_active = False
            if is_temporary:
                import re
                
                # Check for specific duration in impact text
                duration_match = re.search(r'(\d+)\s+(week|game|match)', impact.lower())
                duration = int(duration_match.group(1)) if duration_match else 0
                
                # Check for "next game" in impact text
                if "next game" in impact.lower():
                    duration = 1
                
                # Calculate weeks passed and time remaining
                weeks_passed = 0
                if year == current_year:
                    weeks_passed = current_week - week
                
                # Determine if still active
                if duration == 0:  # No specific duration found
                    is_active = (year == current_year and (current_week - week) <= 8)
                    time_remaining = "Unknown"
                else:
                    is_active = weeks_passed < duration
                    if is_active:
                        time_remaining = f"{duration - weeks_passed} games/weeks"
                    else:
                        time_remaining = "Expired"
            
            # Add recent temporary effects
            if is_temporary and is_active:
                temp_effects.append({
                    'target': target,
                    'category': category,
                    'title': title,
                    'impact': impact,
                    'started': started,
                    'time_remaining': time_remaining
                })
        
        # Add temporary effects to tree
        for effect in temp_effects:
            item = QTreeWidgetItem(self.temp_tree)
            item.setText(0, effect['target'])
            item.setText(1, effect['category'])
            item.setText(2, effect['title'])
            item.setText(3, effect['impact'])
            item.setText(4, effect['started'])
            item.setText(5, effect['time_remaining'])
        
        # Group by player/position
        self.temp_tree.sortItems(0, Qt.AscendingOrder) 