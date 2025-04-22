import random
import json
from datetime import datetime

class EventManager:
    """Manages events and their processing"""
    
    def __init__(self, data_manager):
        """Initialize the event manager
        
        Args:
            data_manager: The data manager instance
        """
        self.data_manager = data_manager
        self.config = data_manager.load_config()
        self.events = data_manager.load_events()
        
        # Keep event history in memory, only stored in save files
        self.event_history = self.config.get('event_history', [])
        
        # Remove event_history from config to keep it separate
        if 'event_history' in self.config:
            del self.config['event_history']
            # Don't save here since this will be stored in save files only
    
    def get_difficulty(self):
        """Get the current difficulty
        
        Returns:
            str: The current difficulty level
        """
        return self.config.get('difficulty', 'medium')
    
    def set_difficulty(self, difficulty):
        """Set the difficulty level
        
        Args:
            difficulty: The difficulty level to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        if difficulty in ['easy', 'medium', 'hard']:
            self.config['difficulty'] = difficulty
            self.data_manager.save_config(self.config)
            self._try_auto_save()
            return True
        return False
    
    def update_franchise_info(self, team_name=None, week=None, year=None):
        """Update franchise information
        
        Args:
            team_name: The team name to set
            week: The week to set
            year: The year to set
        """
        if team_name:
            self.config['franchise_info']['team_name'] = team_name
        if week is not None:
            self.config['franchise_info']['current_week'] = week
        if year is not None:
            self.config['franchise_info']['current_year'] = year
        self.data_manager.save_config(self.config)
        self._try_auto_save()
    
    def update_roster(self, position, player_name):
        """Update a roster position
        
        Args:
            position: The position to update
            player_name: The player name to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        if 'roster' not in self.config:
            self.config['roster'] = {}
        
        self.config['roster'][position] = player_name
        self.data_manager.save_config(self.config)
        self._try_auto_save()
        return True
    
    def update_coach(self, position, coach_name):
        """Update a coach position
        
        Args:
            position: The position to update
            coach_name: The coach name to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        if 'coaches' not in self.config:
            self.config['coaches'] = {}
        
        if position in ['HC', 'OC', 'DC']:
            self.config['coaches'][position] = coach_name
            self.data_manager.save_config(self.config)
            self._try_auto_save()
            return True
        return False
    
    def roll_event(self):
        """Roll for a random event
        
        Returns:
            dict: The processed event, or None if no event was selected
        """
        difficulty = self.get_difficulty()
        eligible_events = []
        
        # Get current season stage
        current_season_stage = self.config.get('franchise_info', {}).get('season_stage', 'Pre-Season')
        
        # Define season stage mapping (allows events to specify multiple stages)
        stage_mapping = {
            "Pre-Season": ["pre-season", "any"],
            "Regular Season (Weeks 1-8)": ["regular-season", "weeks-1-8", "any"],
            "Trade Deadline (Week 8)": ["trade-deadline", "regular-season", "any"],
            "Regular Season (Weeks 9-18)": ["regular-season", "weeks-9-18", "any"],
            "Playoffs": ["playoffs", "any"],
            "Free Agency": ["free-agency", "any"]
        }
        
        # Determine allowed season stages for the current stage
        allowed_stages = stage_mapping.get(current_season_stage, ["any"])
        
        # Filter events based on difficulty weights and season stage
        for event in self.events.get('events', []):
            # Check difficulty weight
            weight = event.get('difficulty_weights', {}).get(difficulty, 0.5)
            
            # Check season stage eligibility
            event_stages = event.get('season_stages', ["any"])
            stage_match = any(stage in allowed_stages for stage in event_stages)
            
            # If this event matches both difficulty and season stage, add to eligible events
            if random.random() < weight and stage_match:
                eligible_events.append(event)
        
        if not eligible_events:
            return None
        
        # Randomly select event from eligible events
        event = random.choice(eligible_events)
        
        # Process the event to fill in placeholders
        processed_event = self._process_event(event)
        
        # No longer adding to history here - will do it when user accepts
        return processed_event
    
    def _process_event(self, event):
        """Process an event by filling in placeholders
        
        Args:
            event: The event to process
            
        Returns:
            dict: The processed event
        """
        processed_event = event.copy()
        
        # Process description to fill in placeholders
        description = processed_event.get('description', '')
        
        # Handle target options
        if 'target_options' in processed_event:
            target_position = random.choice(processed_event['target_options'])
            
            # Store the original target position for later reference
            processed_event['original_target_position'] = target_position
            
            # Try to get player name for this position, fallback to position
            player_name = self.config.get('roster', {}).get(target_position, "")
            
            if player_name and player_name.strip():
                # Use format: "Name (Position)"
                target_display = f"{player_name} ({target_position})"
            else:
                # Just use position if no name available
                target_display = target_position
                
            description = description.replace('{target}', target_display)
            processed_event['selected_target'] = target_display
        
        # Handle reason options
        if 'reason_options' in processed_event:
            reason = random.choice(processed_event['reason_options'])
            description = description.replace('{reason}', reason)
            processed_event['selected_reason'] = reason
        
        # Handle round options for draft picks
        if 'round_options' in processed_event:
            round_pick = random.choice(processed_event['round_options'])
            description = description.replace('{round}', round_pick)
            processed_event['selected_round'] = round_pick
        
        # Handle games options for suspensions
        if 'games_options' in processed_event:
            games = random.choice(processed_event['games_options'])
            description = description.replace('{games}', str(games))
            processed_event['selected_games'] = games
        
        # Handle result options (like for the sprinter challenge)
        if 'result_options' in processed_event:
            # Weight the selection based on probability
            result_options = processed_event['result_options']
            total_prob = sum(opt.get('probability', 1) for opt in result_options)
            rand_val = random.random() * total_prob
            
            cumulative_prob = 0
            selected_result = None
            for opt in result_options:
                cumulative_prob += opt.get('probability', 1)
                if rand_val <= cumulative_prob:
                    selected_result = opt
                    break
            
            if selected_result:
                description = description.replace('{result}', selected_result['result'])
                impact = processed_event.get('impact', '')
                impact = impact.replace('{impact_text}', selected_result['impact_text'])
                processed_event['impact'] = impact
                processed_event['selected_result'] = selected_result['result']
        
        # Handle matchups for player callouts
        if 'matchups' in processed_event:
            matchup = random.choice(processed_event['matchups'])
            description = description.replace('{position1}', matchup['position1'])
            description = description.replace('{opponent_position}', matchup['opponent_position'])
            processed_event['selected_matchup'] = matchup
            
            # Handle opponent team
            if 'opponent_teams' in processed_event:
                opponent_team = random.choice(processed_event['opponent_teams'])
                description = description.replace('{opponent_team}', opponent_team)
                processed_event['selected_opponent_team'] = opponent_team
        
        processed_event['processed_description'] = description
        return processed_event
    
    def _add_to_history(self, event):
        """Add an event to the history
        
        Args:
            event: The event to add to history
        """
        history_entry = {
            'event_id': event['id'],
            'title': event['title'],
            'description': event.get('processed_description', event.get('description', '')),
            'impact': event.get('impact', ''),
            'timestamp': datetime.now().isoformat(),
            'week': self.config['franchise_info']['current_week'],
            'year': self.config['franchise_info']['current_year'],
            'selected_target': event.get('selected_target', 'N/A')  # Include player/position
        }
        
        # Add to in-memory event history (not directly to config)
        self.event_history.append(history_entry)
    
    def get_event_history(self):
        """Get the event history
        
        Returns:
            list: The event history
        """
        return self.event_history
    
    def get_current_week_year(self):
        """Get the current week and year
        
        Returns:
            tuple: (week, year)
        """
        return (
            self.config['franchise_info']['current_week'],
            self.config['franchise_info']['current_year']
        )
    
    def reload_config(self):
        """Reload the configuration"""
        self.config = self.data_manager.load_config()
    
    def reload_events(self):
        """Reload the events data"""
        self.events = self.data_manager.load_events()
        
    def get_config_with_history(self):
        """Get a copy of the config with event history included
        Used for saving the franchise with history
        
        Returns:
            dict: Config with event history
        """
        config_copy = self.config.copy()
        config_copy['event_history'] = self.event_history
        return config_copy
        
    def clear_event_history(self):
        """Clear the event history"""
        self.event_history = []
        
    def set_event_history(self, history):
        """Set the event history
        
        Args:
            history: The history to set
        """
        self.event_history = history
    
    def _try_auto_save(self):
        """Try to auto-save if enabled and a save file exists"""
        auto_save = self.config.get('auto_save', False)
        save_file = self.config.get('franchise_info', {}).get('save_file', '')
        
        if auto_save and save_file:
            # Get the config with event history included
            config_with_history = self.get_config_with_history()
            
            # Save without user interaction
            self.data_manager.save_franchise(config_with_history, save_file)
            return True
        
        return False
    
    def accept_event(self, event):
        """Accept an event and add it to history
        
        Args:
            event: The event to accept and add to history
            
        Returns:
            bool: True if successful
        """
        self._add_to_history(event)
        self._try_auto_save()
        return True 