import json
import os
import shutil
from datetime import datetime

class DataManager:
    """Handles all data operations for the application"""
    
    def __init__(self, base_dir):
        """Initialize the data manager
        
        Args:
            base_dir: The base directory of the application
        """
        self.base_dir = base_dir
        self.data_dir = os.path.join(base_dir, 'data')
        self.saves_dir = os.path.join(base_dir, 'saves')
        
        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.saves_dir, exist_ok=True)
        
        self.config_path = os.path.join(self.data_dir, 'config.json')
        self.events_path = os.path.join(self.data_dir, 'events.json')
    
    def load_config(self):
        """Load the configuration file
        
        Returns:
            dict: The configuration data
        """
        if not os.path.exists(self.config_path):
            return self._create_default_config()
        
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return self._create_default_config()
    
    def load_events(self):
        """Load the events file
        
        Returns:
            dict: The events data
        """
        if not os.path.exists(self.events_path):
            return {"events": []}
        
        try:
            with open(self.events_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"events": []}
    
    def save_config(self, config):
        """Save the configuration data
        
        Args:
            config: The configuration data to save
        """
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _create_default_config(self):
        """Create a default configuration
        
        Returns:
            dict: The default configuration
        """
        default_config = {
            "difficulty": "medium",
            "franchise_info": {
                "team_name": "",
                "current_week": 1,
                "current_year": 1,
                "season_stage": "Pre-Season",
                "save_file": ""
            },
            "roster": {},
            "coaches": {
                "HC": "",
                "OC": "",
                "DC": ""
            },
            "event_history": []
        }
        
        # Save the default config
        self.save_config(default_config)
        
        return default_config
    
    def list_save_files(self):
        """List all save files
        
        Returns:
            list: List of save filenames
        """
        try:
            return [f for f in os.listdir(self.saves_dir) if f.endswith('.json')]
        except Exception:
            return []
    
    def save_franchise(self, config, filename=None):
        """Save the franchise to a file
        
        Args:
            config: The configuration to save (should include event history)
            filename: Optional filename, if None one will be generated
            
        Returns:
            tuple: (success, message)
        """
        try:
            team_name = config.get('franchise_info', {}).get('team_name', 'Unnamed')
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{team_name}_{timestamp}.json"
            
            # Add extension if not present
            if not filename.endswith('.json'):
                filename += '.json'
            
            save_path = os.path.join(self.saves_dir, filename)
            
            # Save the config to the file (including event history)
            with open(save_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Update the save file reference in the config
            config_without_history = config.copy()
            if 'event_history' in config_without_history:
                del config_without_history['event_history']
            
            config_without_history['franchise_info']['save_file'] = filename
            self.save_config(config_without_history)
            
            return True, f"Franchise saved to {filename}"
        
        except Exception as e:
            return False, f"Error saving franchise: {str(e)}"
    
    def load_franchise(self, filename):
        """Load a franchise from a file
        
        Args:
            filename: The filename to load
            
        Returns:
            tuple: (success, message, config, event_history)
        """
        save_path = os.path.join(self.saves_dir, filename)
        
        if not os.path.exists(save_path):
            return False, f"Save file {filename} does not exist", None, []
        
        try:
            with open(save_path, 'r') as f:
                saved_data = json.load(f)
            
            # Extract event history
            event_history = saved_data.get('event_history', [])
            
            # Create a copy without event history for the config
            config = saved_data.copy()
            if 'event_history' in config:
                del config['event_history']
            
            # Update the save file reference
            config['franchise_info']['save_file'] = filename
            
            # Save the config (without event history)
            self.save_config(config)
            
            return True, f"Franchise loaded from {filename}", config, event_history
        
        except Exception as e:
            return False, f"Error loading franchise: {str(e)}", None, []
    
    def create_new_franchise(self, team_name):
        """Create a new franchise
        
        Args:
            team_name: The name of the team
            
        Returns:
            tuple: (success, message, config, event_history)
        """
        try:
            config = self._create_default_config()
            config['franchise_info']['team_name'] = team_name
            
            # Save the config
            self.save_config(config)
            
            # Generate a save file
            success, message = self.save_franchise(config)
            
            if success:
                return True, f"New franchise '{team_name}' created", config, []
            else:
                return False, f"Created franchise but failed to save: {message}", config, []
        
        except Exception as e:
            return False, f"Error creating new franchise: {str(e)}", None, [] 