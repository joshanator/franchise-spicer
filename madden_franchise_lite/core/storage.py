"""Storage operations for Madden Franchise Event Generator."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from .models import Event, Franchise


class Storage:
    """Handles all file operations for the application."""

    def __init__(self, base_dir: Optional[str] = None):
        """Initialize storage with base directory.
        
        Args:
            base_dir: Base directory for data. If None, uses the package directory.
        """
        if base_dir is None:
            base_dir = str(Path(__file__).parent.parent)
        
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / "data"
        self.saves_dir = self.base_dir / "saves"
        
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.saves_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def events_path(self) -> Path:
        return self.data_dir / "events.json"
    
    @property
    def unrealistic_events_path(self) -> Path:
        return self.data_dir / "unrealistic_events.json"
    
    def load_events(self) -> list[Event]:
        """Load all events from events.json.
        
        Returns:
            List of Event objects.
        """
        events = []
        
        if self.events_path.exists():
            try:
                with open(self.events_path, "r") as f:
                    data = json.load(f)
                    for event_data in data.get("events", []):
                        events.append(Event.from_dict(event_data))
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading events: {e}")
        
        return events
    
    def load_unrealistic_events(self) -> list[Event]:
        """Load unrealistic events from unrealistic_events.json.
        
        Returns:
            List of Event objects.
        """
        events = []
        
        if self.unrealistic_events_path.exists():
            try:
                with open(self.unrealistic_events_path, "r") as f:
                    data = json.load(f)
                    for event_data in data.get("unrealistic_events", []):
                        events.append(Event.from_dict(event_data))
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading unrealistic events: {e}")
        
        return events
    
    def list_saves(self) -> list[str]:
        """List all save files.
        
        Returns:
            List of save file names (without .json extension).
        """
        saves = []
        if self.saves_dir.exists():
            for f in self.saves_dir.iterdir():
                if f.suffix == ".json":
                    saves.append(f.stem)
        return sorted(saves)
    
    def load_franchise(self, name: str) -> Optional[Franchise]:
        """Load a franchise from a save file.
        
        Args:
            name: Save file name (with or without .json extension).
            
        Returns:
            Franchise object or None if not found.
        """
        if not name.endswith(".json"):
            name = f"{name}.json"
        
        save_path = self.saves_dir / name
        
        if not save_path.exists():
            return None
        
        try:
            with open(save_path, "r") as f:
                data = json.load(f)
                franchise = Franchise.from_dict(data)
                franchise.save_file = name
                return franchise
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading franchise: {e}")
            return None
    
    def save_franchise(self, franchise: Franchise, name: Optional[str] = None) -> tuple[bool, str]:
        """Save a franchise to a file.
        
        Args:
            franchise: The franchise to save.
            name: Optional save name. If None, generates from team name and timestamp.
            
        Returns:
            Tuple of (success, message/filename).
        """
        try:
            if name:
                if not name.endswith(".json"):
                    name = f"{name}.json"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_team = franchise.team_name.replace(" ", "_")
                name = f"{safe_team}_{timestamp}.json"
            
            franchise.save_file = name
            save_path = self.saves_dir / name
            
            with open(save_path, "w") as f:
                json.dump(franchise.to_dict(), f, indent=2)
            
            return True, name.replace(".json", "")
        except IOError as e:
            return False, str(e)
    
    def delete_franchise(self, name: str) -> bool:
        """Delete a franchise save file.
        
        Args:
            name: Save file name.
            
        Returns:
            True if deleted, False otherwise.
        """
        if not name.endswith(".json"):
            name = f"{name}.json"
        
        save_path = self.saves_dir / name
        
        try:
            if save_path.exists():
                save_path.unlink()
                return True
        except IOError:
            pass
        
        return False
    
    def create_franchise(self, team_name: str) -> Franchise:
        """Create a new franchise with default values.
        
        Args:
            team_name: Name of the team.
            
        Returns:
            New Franchise object.
        """
        return Franchise(team_name=team_name)
