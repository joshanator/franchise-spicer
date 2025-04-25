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
        
        # Load unrealistic events
        self.unrealistic_events = data_manager.load_unrealistic_events()
        
        # Keep event history in memory, only stored in save files
        self.event_history = self.config.get('event_history', [])
        
        # Remove event_history from config to keep it separate
        if 'event_history' in self.config:
            del self.config['event_history']
            # Don't save here since this will be stored in save files only
        
        # Set default difficulty if not set yet
        if 'difficulty' not in self.config:
            self.config['difficulty'] = 'pro'
            self._save_config()
            
        # Set default unrealistic events setting if not set yet
        if 'unrealistic_events_enabled' not in self.config:
            self.config['unrealistic_events_enabled'] = False
            self._save_config()
    
    def _save_config(self):
        """Helper method to save config and attempt auto-save"""
        self.data_manager.save_config(self.config)
        self._try_auto_save()  # Ignore return value
    
    def get_difficulty(self):
        """Get the current difficulty setting
        
        Returns:
            str: The current difficulty (cupcake, rookie, pro, all-madden, or diabolical)
        """
        return self.config.get('difficulty', 'pro')
    
    def set_difficulty(self, difficulty):
        """Set the difficulty level
        
        Args:
            difficulty: The difficulty level to set (cupcake, rookie, pro, all-madden, or diabolical)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if difficulty not in ['cupcake', 'rookie', 'pro', 'all-madden', 'diabolical']:
            return False
        
        self.config['difficulty'] = difficulty
        self._save_config()
        return True
    
    def are_unrealistic_events_enabled(self):
        """Check if unrealistic events are enabled
        
        Returns:
            bool: True if unrealistic events are enabled, False otherwise
        """
        return self.config.get('unrealistic_events_enabled', False)
    
    def set_unrealistic_events_enabled(self, enabled):
        """Enable or disable unrealistic events
        
        Args:
            enabled: Boolean indicating whether unrealistic events should be enabled
            
        Returns:
            bool: True if successful
        """
        self.config['unrealistic_events_enabled'] = bool(enabled)
        self._save_config()
        return True
    
    def update_franchise_info(self, team_name=None, week=None, year=None):
        """Update franchise information
        
        Args:
            team_name: The team name to set
            week: The week to set
            year: The year to set
        """
        if 'franchise_info' not in self.config:
            self.config['franchise_info'] = {}
            
        if team_name:
            self.config['franchise_info']['team_name'] = team_name
        if week is not None:
            self.config['franchise_info']['current_week'] = week
        if year is not None:
            self.config['franchise_info']['current_year'] = year
        
        self._save_config()
    
    def _ensure_dict_key(self, key):
        """Ensure a dictionary key exists in config
        
        Args:
            key: The key to ensure exists
        """
        if key not in self.config:
            self.config[key] = {}
    
    def update_roster(self, position, player_name):
        """Update a roster position
        
        Args:
            position: The position to update
            player_name: The player name to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        self._ensure_dict_key('roster')
        self.config['roster'][position] = player_name
        self._save_config()
        return True
    
    def update_coach(self, position, coach_name):
        """Update a coach position
        
        Args:
            position: The position to update
            coach_name: The coach name to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        if position not in ['HC', 'OC', 'DC']:
            return False
            
        self._ensure_dict_key('coaches')
        self.config['coaches'][position] = coach_name
        self._save_config()
        return True
    
    def roll_event(self):
        """Roll for a random event
        
        Returns:
            dict: The processed event, or None if no event was selected
        """
        difficulty = self.get_difficulty()
        eligible_events = []
        
        # Get current season stage and allowed stages
        current_season_stage = self.config.get('franchise_info', {}).get('season_stage', 'Pre-Season')
        allowed_stages = self._get_allowed_stages(current_season_stage)
        
        # Filter standard events based on difficulty weights and season stage
        for event in self.events.get('events', []):
            # Check difficulty weight
            weight = event.get('difficulty_weights', {}).get(difficulty, 0.5)
            
            # Check season stage eligibility
            event_stages = event.get('season_stages', ["any"])
            stage_match = any(stage in allowed_stages for stage in event_stages)
            
            # If this event matches both difficulty and season stage, add to eligible events
            if random.random() < weight and stage_match:
                eligible_events.append(event)
        
        # Add unrealistic events if enabled
        if self.config.get('unrealistic_events_enabled', False):
            for event in self.unrealistic_events.get('unrealistic_events', []):
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
    
    def _get_allowed_stages(self, current_stage):
        """Get allowed stages for the current season stage
        
        Args:
            current_stage: The current season stage
            
        Returns:
            list: Allowed stage names for event filtering
        """
        # Define both internal stage names and their mappings
        stage_mapping = {
            # Internal stage names
            "Pre-Season": ["pre-season", "any"],
            "regular-season-start": ["regular-season", "regular-season-start", "any"],
            "regular-season-mid": ["regular-season", "regular-season-mid", "any"],
            "regular-season-end": ["regular-season", "regular-season-end", "any"],
            "Post-Season": ["post-season", "playoffs", "any"],
            "Off-Season": ["off-season", "offseason", "any"],
            # Handle old display names for backward compatibility
            "Regular Season Start": ["regular-season", "regular-season-start", "any"],
            "Regular Season Mid": ["regular-season", "regular-season-mid", "any"],
            "Regular Season End": ["regular-season", "regular-season-end", "any"]
        }
        
        allowed_stages = stage_mapping.get(current_stage, ["any"])
        if allowed_stages == ["any"] and current_stage != "any":
            print(f"WARNING: Unknown season stage '{current_stage}', defaulting to 'any'")
            
        return allowed_stages
    
    def _replace_placeholder(self, text, placeholder, value):
        """Replace a placeholder in text with a value
        
        Args:
            text: The text containing placeholders
            placeholder: The placeholder to replace (without {})
            value: The value to replace with
            
        Returns:
            str: The text with placeholders replaced
        """
        return text.replace(f"{{{placeholder}}}", str(value))
    
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
            # Special case: "All players" means choose any player from the roster
            if len(processed_event['target_options']) == 1 and processed_event['target_options'][0] == "all-players":
                # Get all positions from the roster
                all_positions = list(self.config.get('roster', {}).keys())
                if all_positions:
                    target_position = random.choice(all_positions)
                else:
                    # Fallback if roster is empty
                    target_position = "Unknown"
            else:
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
                
            description = self._replace_placeholder(description, 'target', target_display)
            processed_event['selected_target'] = target_display
        
        # Preserve is_temporary flag
        if 'is_temporary' in event:
            processed_event['is_temporary'] = event['is_temporary']
        
        # Handle player options and their impacts
        if 'trainer_options' in processed_event and 'trainer_impacts' in processed_event:
            # Choose a random trainer from the options
            selected_trainer = random.choice(processed_event['trainer_options'])
            processed_event['selected_trainer'] = selected_trainer
            
            # Get the impact for this trainer
            trainer_impact = processed_event['trainer_impacts'].get(selected_trainer, "")
            
            # Replace trainer and trainer_impact placeholders
            description = self._replace_placeholder(description, 'trainer', selected_trainer)
            
            # Replace impact placeholders
            impact = processed_event.get('impact', '')
            impact = self._replace_placeholder(impact, 'trainer_impact', trainer_impact)
            processed_event['impact'] = impact
            
            # Debug output
            print(f"Selected trainer: {selected_trainer}")
            print(f"Trainer impact: {trainer_impact}")
        
        # Handle simple random selection fields
        for field_type in ['reason_options', 'round_options', 'games_options']:
            if field_type in processed_event:
                chosen_value = random.choice(processed_event[field_type])
                field_name = field_type.replace('_options', '')
                description = self._replace_placeholder(description, field_name, chosen_value)
                processed_event[f'selected_{field_name}'] = chosen_value
        
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
                description = self._replace_placeholder(description, 'result', selected_result['result'])
                impact = processed_event.get('impact', '')
                impact = self._replace_placeholder(impact, 'impact_text', selected_result['impact_text'])
                processed_event['impact'] = impact
                processed_event['selected_result'] = selected_result['result']
        
        # Handle matchups for player callouts
        if 'matchups' in processed_event:
            matchup = random.choice(processed_event['matchups'])
            description = self._replace_placeholder(description, 'position1', matchup['position1'])
            description = self._replace_placeholder(description, 'opponent_position', matchup['opponent_position'])
            processed_event['selected_matchup'] = matchup
            
            # Handle opponent team
            if 'opponent_teams' in processed_event:
                opponent_team = random.choice(processed_event['opponent_teams'])
                description = self._replace_placeholder(description, 'opponent_team', opponent_team)
                processed_event['selected_opponent_team'] = opponent_team
        
        # Handle user options in branching events
        if 'options' in processed_event:
            # Process each option to fill in placeholders
            for option in processed_event['options']:
                # Replace placeholders in option descriptions
                option_description = option.get('description', '')
                
                # Replace target placeholder
                if 'selected_target' in processed_event:
                    option_description = self._replace_placeholder(option_description, 'target', processed_event['selected_target'])
                
                # Replace reason placeholder
                if 'selected_reason' in processed_event:
                    option_description = self._replace_placeholder(option_description, 'reason', processed_event['selected_reason'])
                
                # Store processed description
                option['processed_description'] = option_description
        
        processed_event['processed_description'] = description
        return processed_event
    
    def _add_to_history(self, event, selected_option=None):
        """Add an event to the history
        
        Args:
            event: The event to add to history
            selected_option: The option selected by the user for branching events
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
        
        # Include is_temporary flag if present
        if 'is_temporary' in event:
            history_entry['is_temporary'] = event['is_temporary']
        
        # Add selected option information if this was a branching event
        if selected_option is not None:
            history_entry['selected_option'] = {
                'description': selected_option.get('processed_description', selected_option.get('description', '')),
                'impact': selected_option.get('impact', '')
            }
            
            # Include is_temporary from the selected option if present
            if 'is_temporary' in selected_option:
                if 'selected_option' in history_entry:
                    history_entry['selected_option']['is_temporary'] = selected_option['is_temporary']
                history_entry['is_temporary'] = selected_option['is_temporary']
        
        # Add to in-memory event history (not directly to config)
        self.event_history.append(history_entry)
    
    def select_event_option(self, event, option_index):
        """Select an option for a branching event
        
        Args:
            event: The event being responded to
            option_index: The index of the option selected by user
            
        Returns:
            dict: The processed option with impact details
        """
        if 'options' not in event or option_index >= len(event['options']):
            return None
        
        # Get the selected option
        selected_option = event['options'][option_index]
        
        # Add to history with the selected option
        self._add_to_history(event, selected_option)
        
        # Auto-save if enabled
        self._try_auto_save()
        
        return selected_option
    
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
        self.unrealistic_events = self.data_manager.load_unrealistic_events()
        
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
        """Try to auto-save if enabled and a save file exists
        
        Returns:
            tuple: (success, message) - Success flag and explanation message
        """
        auto_save = self.config.get('auto_save', False)
        save_file = self.config.get('franchise_info', {}).get('save_file', '')
        
        # Check if auto-save is enabled
        if not auto_save:
            return False, "Auto-save is disabled"
            
        # Check if a save file exists
        if not save_file:
            return False, "No save file exists - please save manually first"
        
        # Get the config with event history included
        config_with_history = self.get_config_with_history()
        
        # Ensure auto_save status is included in the save file
        config_with_history['auto_save'] = True
        
        # Save without user interaction
        return self.data_manager.save_franchise(config_with_history, save_file)
    
    def accept_event(self, event):
        """Accept an event and add it to history
        
        Args:
            event: The event to accept and add to history
            
        Returns:
            bool: True if successful
        """
        # For branching events, don't add to history here - wait for option selection
        if 'options' not in event:
            self._add_to_history(event)
            self._try_auto_save()  # Ignore return value, event acceptance is the main task
        
        return True 