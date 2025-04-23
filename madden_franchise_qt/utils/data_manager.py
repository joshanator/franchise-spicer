import json
import os
import shutil
import sys
import appdirs
from datetime import datetime

class DataManager:
    """Handles all data operations for the application"""
    
    def __init__(self, base_dir):
        """Initialize the data manager
        
        Args:
            base_dir: The base directory of the application
        """
        # Determine if we're running from a PyInstaller bundle
        if getattr(sys, 'frozen', False):
            # Running as executable - use user's home directory
            self.base_dir = appdirs.user_data_dir("MaddenFranchiseGenerator", "MaddenTools")
        else:
            # Running from source code - use provided directory
            self.base_dir = base_dir
            
        # Define data and saves directories
        self.data_dir = os.path.join(self.base_dir, 'data')
        self.saves_dir = os.path.join(self.base_dir, 'saves')
        
        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.saves_dir, exist_ok=True)
        
        self.config_path = os.path.join(self.data_dir, 'config.json')
        self.events_path = os.path.join(self.data_dir, 'events.json')
        
        # Set up events.json if it doesn't exist
        self._ensure_events_file_exists(base_dir)
    
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
        # If config.json exists, make a backup before overwriting
        if os.path.exists(self.config_path):
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = os.path.join(self.data_dir, f'config_backup_{timestamp}.json')
                shutil.copy2(self.config_path, backup_path)
            except Exception:
                # Continue even if backup fails
                pass
        
        default_config = {
            "difficulty": "medium",
            "auto_save": False,  # Auto-save is disabled by default
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
            # If filename is provided and already has the .json extension, use it directly
            if filename and filename.endswith('.json'):
                save_path = os.path.join(self.saves_dir, filename)
            else:
                team_name = config.get('franchise_info', {}).get('team_name', 'Unnamed')
                
                # Generate filename if not provided
                if not filename:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{team_name}_{timestamp}.json"
                # Add extension if not present
                elif not filename.endswith('.json'):
                    filename += '.json'
                
                save_path = os.path.join(self.saves_dir, filename)
            
            # Save the config to the file (including event history)
            with open(save_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Update the save file reference in the config
            config_without_history = config.copy()
            if 'event_history' in config_without_history:
                del config_without_history['event_history']
            
            config_without_history['franchise_info']['save_file'] = os.path.basename(save_path)
            self.save_config(config_without_history)
            
            # Get display name without .json extension
            display_name = os.path.basename(save_path)
            if display_name.lower().endswith('.json'):
                display_name = display_name[:-5]
            
            return True, f"Franchise saved to {display_name}"
        
        except Exception as e:
            return False, f"Error saving franchise: {str(e)}"
    
    def load_franchise(self, filename):
        """Load a franchise from a save file
        
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
            
            # Extract auto-save status
            auto_save = saved_data.get('auto_save', False)
            
            # Create a copy without event history for the config
            config = saved_data.copy()
            if 'event_history' in config:
                del config['event_history']
            
            # Preserve auto-save status in config
            config['auto_save'] = auto_save
            
            # Update the save file reference
            config['franchise_info']['save_file'] = filename
            
            # Save the config (without event history)
            self.save_config(config)
            
            # Print debug info
            print(f"Loaded config with auto_save={config.get('auto_save')}")
            
            # Get display name without .json extension
            display_name = filename
            if display_name.lower().endswith('.json'):
                display_name = display_name[:-5]
            
            return True, f"Franchise loaded from {display_name}", config, event_history
        
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
    
    def _ensure_events_file_exists(self, source_dir):
        """Make sure events.json exists in the data directory
        
        Args:
            source_dir: Original source directory to copy from if needed
        """
        if not os.path.exists(self.events_path):
            # Try to copy from the source directory or bundled resources
            try:
                # First check in the source directory
                source_events_path = os.path.join(source_dir, 'data', 'events.json')
                if os.path.exists(source_events_path):
                    shutil.copy2(source_events_path, self.events_path)
                    return
                
                # If running as executable, the file might be in a different location
                if getattr(sys, 'frozen', False):
                    # PyInstaller places data files relative to the executable
                    if hasattr(sys, '_MEIPASS'):
                        # PyInstaller's temp folder with bundled data
                        bundled_events_path = os.path.join(sys._MEIPASS, 'madden_franchise_qt', 'data', 'events.json')
                        if os.path.exists(bundled_events_path):
                            shutil.copy2(bundled_events_path, self.events_path)
                            return
                    
                    # Try relative to the executable
                    exe_dir = os.path.dirname(sys.executable)
                    exe_events_path = os.path.join(exe_dir, 'madden_franchise_qt', 'data', 'events.json')
                    if os.path.exists(exe_events_path):
                        shutil.copy2(exe_events_path, self.events_path)
                        return
            except Exception as e:
                print(f"Warning: Could not copy events.json template: {e}")
            
            # If we couldn't find the template, create a minimal one
            with open(self.events_path, 'w') as f:
                json.dump({"events": []}, f) 