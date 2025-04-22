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
            return True
        return False
    
    def roll_event(self):
        """Roll for a random event
        
        Returns:
            dict: The processed event, or None if no event was selected
        """
        difficulty = self.get_difficulty()
        eligible_events = []
        
        # Filter events based on difficulty weights
        for event in self.events.get('events', []):
            weight = event.get('difficulty_weights', {}).get(difficulty, 0.5)
            # Use the weight as probability to include the event
            if random.random() < weight:
                eligible_events.append(event)
        
        if not eligible_events:
            return None
        
        # Randomly select event from eligible events
        event = random.choice(eligible_events)
        
        # Process the event to fill in placeholders
        processed_event = self._process_event(event)
        
        # Add to history
        self._add_to_history(processed_event)
        
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
            target = random.choice(processed_event['target_options'])
            description = description.replace('{target}', target)
            processed_event['selected_target'] = target
        
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
            'year': self.config['franchise_info']['current_year']
        }
        
        if 'event_history' not in self.config:
            self.config['event_history'] = []
        
        self.config['event_history'].append(history_entry)
        self.data_manager.save_config(self.config)
    
    def get_event_history(self):
        """Get the event history
        
        Returns:
            list: The event history
        """
        return self.config.get('event_history', [])
    
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