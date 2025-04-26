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
        self.unrealistic_events_path = os.path.join(self.data_dir, 'unrealistic_events.json')
        
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
        """Load the events file directly from the embedded resources
        
        Returns:
            dict: The events data
        """
        # First try to find the embedded events file
        source_events_path = None
        
        if getattr(sys, 'frozen', False):
            # For PyInstaller onedir mode
            exe_path = os.path.abspath(sys.executable)
            exe_dir = os.path.dirname(exe_path)
            
            # Try various locations
            possible_paths = [
                # PyInstaller's temp folder with bundled data (for onefile mode)
                os.path.join(sys._MEIPASS, 'madden_franchise_qt', 'data', 'events.json') if hasattr(sys, '_MEIPASS') else None,
                # Adjacent to executable in the same directory (for onedir mode)
                os.path.join(exe_dir, 'madden_franchise_qt', 'data', 'events.json'),
                # In parent directory (for macOS app bundles)
                os.path.join(os.path.dirname(exe_dir), 'madden_franchise_qt', 'data', 'events.json'),
                # Directly in the executable directory
                os.path.join(exe_dir, 'events.json')
            ]
            
            # Try each path
            for path in possible_paths:
                if path and os.path.exists(path):
                    source_events_path = path
                    print(f"Found embedded events.json at {path}")
                    break
        else:
            # When running from source code, check in the source directory
            potential_source = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'events.json')
            if os.path.exists(potential_source):
                source_events_path = potential_source
        
        # Load from the source if found
        if source_events_path and os.path.exists(source_events_path):
            try:
                with open(source_events_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Error decoding events file: {source_events_path}")
        
        # Fallback to user data directory if embedded file not found
        if os.path.exists(self.events_path):
            try:
                with open(self.events_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        
        # If all else fails, return empty events
        return {"events": []}
    
    def load_unrealistic_events(self):
        """Load the unrealistic events file directly from the embedded resources
        
        Returns:
            dict: The unrealistic events data
        """
        # First try to find the embedded events file
        source_events_path = None
        
        if getattr(sys, 'frozen', False):
            # For PyInstaller onedir mode
            exe_path = os.path.abspath(sys.executable)
            exe_dir = os.path.dirname(exe_path)
            
            # Try various locations
            possible_paths = [
                # PyInstaller's temp folder with bundled data (for onefile mode)
                os.path.join(sys._MEIPASS, 'madden_franchise_qt', 'data', 'unrealistic_events.json') if hasattr(sys, '_MEIPASS') else None,
                # Adjacent to executable in the same directory (for onedir mode)
                os.path.join(exe_dir, 'madden_franchise_qt', 'data', 'unrealistic_events.json'),
                # In parent directory (for macOS app bundles)
                os.path.join(os.path.dirname(exe_dir), 'madden_franchise_qt', 'data', 'unrealistic_events.json'),
                # Directly in the executable directory
                os.path.join(exe_dir, 'unrealistic_events.json')
            ]
            
            # Try each path
            for path in possible_paths:
                if path and os.path.exists(path):
                    source_events_path = path
                    print(f"Found embedded unrealistic_events.json at {path}")
                    break
        else:
            # When running from source code, check in the source directory
            potential_source = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'unrealistic_events.json')
            if os.path.exists(potential_source):
                source_events_path = potential_source
        
        # Load from the source if found
        if source_events_path and os.path.exists(source_events_path):
            try:
                with open(source_events_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Error decoding unrealistic events file: {source_events_path}")
        
        # Fallback to user data directory if embedded file not found
        if os.path.exists(self.unrealistic_events_path):
            try:
                with open(self.unrealistic_events_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        
        # If all else fails, return empty events
        return {"unrealistic_events": []}
    
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
            "custom_events": [],  # Array for user-created events
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
            
            # Extract custom events
            custom_events = saved_data.get('custom_events', [])
            
            # Create a copy without event history for the config
            config = saved_data.copy()
            if 'event_history' in config:
                del config['event_history']
            
            # Preserve auto-save status in config
            config['auto_save'] = auto_save
            
            # Preserve custom events in config
            config['custom_events'] = custom_events
            
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
        """Make sure events.json exists in the data directory and is up to date
        
        Args:
            source_dir: Original source directory to copy from if needed
        """
        source_events_path = None
        source_events_found = False
        
        # Try to locate the source events file
        try:
            # First check in the source directory
            potential_source = os.path.join(source_dir, 'data', 'events.json')
            if os.path.exists(potential_source):
                source_events_path = potential_source
                source_events_found = True
            
            # If running as executable, the file might be in a different location
            if getattr(sys, 'frozen', False) and not source_events_found:
                # For PyInstaller onedir mode
                exe_path = os.path.abspath(sys.executable)
                exe_dir = os.path.dirname(exe_path)
                
                # Try various locations
                possible_paths = [
                    # PyInstaller's temp folder with bundled data (for onefile mode)
                    os.path.join(sys._MEIPASS, 'madden_franchise_qt', 'data', 'events.json') if hasattr(sys, '_MEIPASS') else None,
                    # Adjacent to executable in the same directory (for onedir mode)
                    os.path.join(exe_dir, 'madden_franchise_qt', 'data', 'events.json'),
                    # In parent directory (for macOS app bundles)
                    os.path.join(os.path.dirname(exe_dir), 'madden_franchise_qt', 'data', 'events.json'),
                    # Directly in the executable directory
                    os.path.join(exe_dir, 'events.json')
                ]
                
                # Try each path
                for path in possible_paths:
                    if path and os.path.exists(path):
                        source_events_path = path
                        source_events_found = True
                        print(f"Found events.json at {path}")
                        break
                
                if not source_events_found:
                    print(f"Warning: Could not find events.json in any of the expected locations: {possible_paths}")
            
            # Now determine if we should copy the file
            should_copy = False
            
            # If the destination doesn't exist, we need to copy
            if not os.path.exists(self.events_path):
                should_copy = True
            # If the source is newer than the destination, we should update
            elif source_events_found:
                # Compare modification times
                source_mtime = os.path.getmtime(source_events_path)
                dest_mtime = os.path.getmtime(self.events_path)
                
                if source_mtime > dest_mtime:
                    print(f"Source events file is newer ({source_mtime} vs {dest_mtime}), updating...")
                    should_copy = True
                
                # Also compare content to detect changes
                if not should_copy:
                    try:
                        with open(source_events_path, 'r') as f_source:
                            source_content = f_source.read()
                        with open(self.events_path, 'r') as f_dest:
                            dest_content = f_dest.read()
                        
                        if source_content != dest_content:
                            print("Events file content has changed, updating...")
                            should_copy = True
                    except Exception as e:
                        print(f"Error comparing file contents: {e}")
            
            # Copy if needed
            if should_copy and source_events_found:
                shutil.copy2(source_events_path, self.events_path)
                print(f"Updated events.json from {source_events_path}")
                return
                
        except Exception as e:
            print(f"Warning: Error handling events.json file: {e}")
        
        # If we get here and the file still doesn't exist, create a minimal one
        if not os.path.exists(self.events_path):
            print("Creating a minimal empty events.json file")
            with open(self.events_path, 'w') as f:
                json.dump({"events": []}, f) 