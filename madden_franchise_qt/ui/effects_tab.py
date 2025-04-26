from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QTabWidget, QScrollArea, QSizePolicy, QTextEdit
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
        self._create_season_challenges_tab()
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
        # Connect selection change event
        self.season_tree.currentItemChanged.connect(self._on_season_effect_selected)
        layout.addWidget(self.season_tree)
        
        # Event details section
        details_group = QGroupBox("Effect Details")
        details_layout = QVBoxLayout(details_group)
        
        self.season_details_text = QTextEdit()
        self.season_details_text.setReadOnly(True)
        self.season_details_text.setMinimumHeight(100)
        details_layout.addWidget(self.season_details_text)
        
        layout.addWidget(details_group)
        
        self.tab_widget.addTab(scroll_area, "Season Effects - (not fully working)")
    
    def _create_season_challenges_tab(self):
        """Create the tab for season challenges"""
        challenges_tab = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(challenges_tab)
        
        # Layout for the season challenges tab
        layout = QVBoxLayout(challenges_tab)
        
        # Season challenges tree
        self.challenges_tree = QTreeWidget()
        self.challenges_tree.setColumnCount(5)
        self.challenges_tree.setHeaderLabels(["Player/Position", "Challenge", "Description", "Goal", "Reward/Consequence"])
        
        # Configure header
        header = self.challenges_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        
        self.challenges_tree.setAlternatingRowColors(True)
        # Connect selection change event
        self.challenges_tree.currentItemChanged.connect(self._on_challenge_selected)
        layout.addWidget(self.challenges_tree)
        
        # Event details section
        details_group = QGroupBox("Challenge Details")
        details_layout = QVBoxLayout(details_group)
        
        self.challenge_details_text = QTextEdit()
        self.challenge_details_text.setReadOnly(True)
        self.challenge_details_text.setMinimumHeight(100)
        details_layout.addWidget(self.challenge_details_text)
        
        layout.addWidget(details_group)
        
        self.tab_widget.addTab(scroll_area, "Season Challenges")
    
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
        # Connect selection change event
        self.temp_tree.currentItemChanged.connect(self._on_temp_effect_selected)
        layout.addWidget(self.temp_tree)
        
        # Event details section
        details_group = QGroupBox("Effect Details")
        details_layout = QVBoxLayout(details_group)
        
        self.temp_details_text = QTextEdit()
        self.temp_details_text.setReadOnly(True)
        self.temp_details_text.setMinimumHeight(100)
        details_layout.addWidget(self.temp_details_text)
        
        layout.addWidget(details_group)
        
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
        self._populate_season_challenges(history, current_week, current_year)
        self._populate_temporary_effects(history, current_week, current_year)
    
    def _populate_season_effects(self, history, current_stage):
        """Populate the season effects tree
        
        Args:
            history: The event history
            current_stage: The current season stage
        """
        self.season_tree.clear()
        
        # Track stored events for details view
        self.season_effects = {}
        
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
                    'target': target,
                    'event': event  # Store the full event
                })
        
        # Add stage groups to tree
        for stage, events in stage_events.items():
            stage_item = QTreeWidgetItem(self.season_tree)
            stage_item.setText(0, stage)
            stage_item.setFont(0, QFont("Arial", 10, QFont.Bold))
            
            for event_data in events:
                event_item = QTreeWidgetItem(stage_item)
                event_item.setText(0, "")  # No stage in child item
                event_item.setText(1, event_data['target'])
                event_item.setText(2, event_data['title'])
                event_item.setText(3, event_data['impact'])
                
                # Store the full event data with the item using a unique key
                event_key = f"{event_data['target']}_{event_data['title']}"
                event_item.setData(0, Qt.UserRole, event_key)
                self.season_effects[event_key] = event_data['event']
        
        self.season_tree.expandAll()
    
    def _populate_season_challenges(self, history, current_week, current_year):
        """Populate the season challenges tree
        
        Args:
            history: The event history
            current_week: The current week
            current_year: The current year
        """
        self.challenges_tree.clear()
        
        # Track stored events for details view
        self.challenge_events = {}
        
        # Look for events with category "season-challenge"
        for event in history:
            # We need to find events from the current year only
            event_year = event.get('year', 0)
            if event_year != current_year:
                continue
                
            # Skip events with no impact
            if not event.get('impact'):
                continue
                
            # Check if this is a season challenge by category
            category = event.get('category', '')
            
            # Only process events with season-challenge category
            if category == "season-challenge":
                title = event.get('title', '')
                description = event.get('description', '')
                target = event.get('selected_target', 'N/A')
                impact = event.get('impact', '')
                
                # Extract goal and reward from the impact text if possible
                goal = ""
                reward = ""
                
                # Try to parse options for better details
                if 'selected_option' in event and isinstance(event['selected_option'], dict):
                    option = event['selected_option']
                    description = option.get('description', description)
                    # Make sure to use the impact from the selected option
                    impact = option.get('impact', impact)
                
                # Extract goal and reward from impact text
                if "if" in impact.lower():
                    parts = impact.lower().split("if")
                    if len(parts) > 1:
                        condition_parts = parts[1].split(",")
                        if len(condition_parts) > 0:
                            goal = condition_parts[0].strip()
                            reward = impact  # Use the full impact text for better context
                    else:
                        goal = "Complete season challenge"
                        reward = impact
                else:
                    # Simple approach - just display the impact
                    goal = "Complete season challenge"
                    reward = impact
                
                # Make sure reward is not empty
                if not reward.strip():
                    reward = impact
                
                # Add to tree
                item = QTreeWidgetItem(self.challenges_tree)
                item.setText(0, target)
                item.setText(1, title)
                item.setText(2, description)
                item.setText(3, goal)
                item.setText(4, reward)
                
                # Store the full event data with the item using a unique key
                event_key = f"{target}_{title}_{event_year}"
                item.setData(0, Qt.UserRole, event_key)
                self.challenge_events[event_key] = event
                
                # Debug print to help diagnose issues
                print(f"Season Challenge - {title} for {target}")
                print(f"  Impact: {impact}")
                print(f"  Reward set to: {reward}")
        
        # Sort by player/position
        self.challenges_tree.sortItems(0, Qt.AscendingOrder)
    
    def _populate_temporary_effects(self, history, current_week, current_year):
        """Populate the temporary effects tree
        
        Args:
            history: The event history
            current_week: The current week
            current_year: The current year
        """
        self.temp_tree.clear()
        
        # Track stored events for details view
        self.temp_effects = {}
        
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
                effect_data = {
                    'target': target,
                    'category': category,
                    'title': title,
                    'impact': impact,
                    'started': started,
                    'time_remaining': time_remaining,
                    'event': event  # Store the original event
                }
                temp_effects.append(effect_data)
        
        # Add temporary effects to tree
        for effect in temp_effects:
            item = QTreeWidgetItem(self.temp_tree)
            item.setText(0, effect['target'])
            item.setText(1, effect['category'])
            item.setText(2, effect['title'])
            item.setText(3, effect['impact'])
            item.setText(4, effect['started'])
            item.setText(5, effect['time_remaining'])
            
            # Store the full event data with the item using a unique key
            event_key = f"{effect['target']}_{effect['title']}_{effect['started']}"
            item.setData(0, Qt.UserRole, event_key)
            self.temp_effects[event_key] = effect['event']
        
        # Group by player/position
        self.temp_tree.sortItems(0, Qt.AscendingOrder)
    
    def _on_challenge_selected(self, current, previous):
        """Handle selection change in challenges tree"""
        if not current:
            self.challenge_details_text.clear()
            return
            
        # Get the event key and retrieve full event data
        event_key = current.data(0, Qt.UserRole)
        event = self.challenge_events.get(event_key)
        
        if not event:
            # Fallback to display if no event data stored
            player_position = current.text(0)
            challenge = current.text(1)
            description = current.text(2)
            goal = current.text(3)
            reward = current.text(4)
            
            detail_html = f"""
            <h3>{challenge}</h3>
            <p><b>Player/Position:</b> {player_position}</p>
            <p><b>Description:</b> {description}</p>
            <p><b>Goal:</b> {goal}</p>
            <p><b>Reward/Consequence:</b> {reward}</p>
            """
        else:
            # Format using full event data
            title = event.get('title', '')
            description = event.get('description', '')
            target = event.get('selected_target', 'N/A')
            impact = event.get('impact', '')
            week = event.get('week', 0)
            year = event.get('year', 0)
            
            # Get selected option details if available
            option_desc = ""
            if 'selected_option' in event and isinstance(event['selected_option'], dict):
                option = event['selected_option']
                option_desc = option.get('description', '')
                
            # Build rich HTML detail display
            detail_html = f"""
            <h3>{title}</h3>
            <p><b>Player/Position:</b> {target}</p>
            <p><b>Week/Year:</b> Week {week}, Year {year}</p>
            <p><b>Description:</b> {description}</p>
            """
            
            if option_desc:
                detail_html += f"<p><b>Selected Option:</b> {option_desc}</p>"
                
            detail_html += f"""
            <p><b>Challenge Impact:</b> {impact}</p>
            """
            
            # Add advice on how to track
            detail_html += """
            <p><b>How to track:</b> Make note of this challenge and track the player's 
            performance in Madden to see if they meet the goal.</p>
            """
        
        # Set the formatted HTML
        self.challenge_details_text.setHtml(detail_html)
    
    def _on_temp_effect_selected(self, current, previous):
        """Handle selection change in temporary effects tree"""
        if not current:
            self.temp_details_text.clear()
            return
            
        # Get the event key and retrieve full event data
        event_key = current.data(0, Qt.UserRole)
        event = self.temp_effects.get(event_key)
        
        if not event:
            # Fallback to display if no event data stored
            player_position = current.text(0)
            effect_type = current.text(1)
            description = current.text(2)
            impact = current.text(3)
            time_remaining = current.text(5)
            
            detail_html = f"""
            <h3>{effect_type}</h3>
            <p><b>Player/Position:</b> {player_position}</p>
            <p><b>Description:</b> {description}</p>
            <p><b>Impact:</b> {impact}</p>
            <p><b>Time Remaining:</b> {time_remaining}</p>
            """
        else:
            # Format using full event data
            title = event.get('title', '')
            description = event.get('description', '')
            target = event.get('selected_target', 'N/A')
            impact = event.get('impact', '')
            week = event.get('week', 0)
            year = event.get('year', 0)
            
            # Get selected option details if available
            option_desc = ""
            if 'selected_option' in event and isinstance(event['selected_option'], dict):
                option = event['selected_option']
                option_desc = option.get('description', '')
                
            # Build rich HTML detail display
            detail_html = f"""
            <h3>{title}</h3>
            <p><b>Player/Position:</b> {target}</p>
            <p><b>Week/Year:</b> Week {week}, Year {year}</p>
            <p><b>Description:</b> {description}</p>
            """
            
            if option_desc:
                detail_html += f"<p><b>Selected Option:</b> {option_desc}</p>"
                
            detail_html += f"""
            <p><b>Effect Impact:</b> {impact}</p>
            """
            
            # Add advice on how to track
            detail_html += """
            <p><b>How to track:</b> Make note of this effect and monitor the player's 
            performance in Madden to see if it impacts the team.</p>
            """
        
        # Set the formatted HTML
        self.temp_details_text.setHtml(detail_html)
    
    def _on_season_effect_selected(self, current, previous):
        """Handle selection change in season effects tree"""
        if not current:
            self.season_details_text.clear()
            return
            
        # Get the event key and retrieve full event data
        event_key = current.data(0, Qt.UserRole)
        event = self.season_effects.get(event_key)
        
        if not event:
            # Fallback to display if no event data stored
            season_stage = current.parent().text(0) if current.parent() else current.text(0)
            player_position = current.text(1)
            effect_description = current.text(2)
            impact = current.text(3)
            
            detail_html = f"""
            <h3>{effect_description}</h3>
            <p><b>Season Stage:</b> {season_stage}</p>
            <p><b>Player/Position:</b> {player_position}</p>
            <p><b>Impact:</b> {impact}</p>
            """
        else:
            # Format using full event data
            title = event.get('title', '')
            description = event.get('description', '')
            target = event.get('selected_target', 'N/A')
            impact = event.get('impact', '')
            
            # Build rich HTML detail display
            detail_html = f"""
            <h3>{title}</h3>
            <p><b>Player/Position:</b> {target}</p>
            <p><b>Description:</b> {description}</p>
            <p><b>Impact:</b> {impact}</p>
            """
        
        # Set the formatted HTML
        self.season_details_text.setHtml(detail_html) 