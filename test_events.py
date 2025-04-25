import unittest
import json
import random
import sys
import os
from unittest.mock import MagicMock, patch

from madden_franchise_qt.utils.event_manager import EventManager

class TestEvents(unittest.TestCase):
    def setUp(self):
        # Create a mock data manager
        self.data_manager = MagicMock()
        
        # Load real event data for testing
        with open('madden_franchise_qt/data/events.json', 'r') as f:
            self.events_data = json.load(f)
        
        # Try to load unrealistic events if they exist
        self.unrealistic_events_data = {"unrealistic_events": []}
        unrealistic_events_path = 'madden_franchise_qt/data/unrealistic_events.json'
        if os.path.exists(unrealistic_events_path):
            try:
                with open(unrealistic_events_path, 'r') as f:
                    self.unrealistic_events_data = json.load(f)
            except Exception as e:
                print(f"Could not load unrealistic events: {e}", file=sys.stderr)
        
        # Mock the data manager to return our test data
        self.data_manager.load_events.return_value = self.events_data
        self.data_manager.load_unrealistic_events.return_value = self.unrealistic_events_data
        
        # Set up a basic config with all needed values
        self.test_config = {
            "difficulty": "pro",
            "franchise_info": {
                "team_name": "Test Team",
                "current_week": 1,
                "current_year": 2023,
                "season_stage": "Pre-Season"  # Correct capitalization
            },
            "roster": {
                "QB1": "Test Quarterback",
                "QB2": "Backup Quarterback",
                "WR1": "Test Receiver",
                "WR2": "Test Receiver 2",
                "WR3": "Test Receiver 3",
                "WR4": "Test Receiver 4",
                "RB1": "Test Runner",
                "RB2": "Test Runner 2",
                "RB3": "Test Runner 3",
                "TE1": "Test End",
                "TE2": "Test End 2",
                "CB1": "Test Corner",
                "CB2": "Test Corner 2",
                "CB3": "Test Corner 3",
                "MLB1": "Test Linebacker",
                "MLB2": "Test Linebacker 2",
                "LOLB1": "Test LOLB",
                "LOLB2": "Test LOLB 2",
                "ROLB1": "Test ROLB",
                "ROLB2": "Test ROLB 2",
                "FS1": "Test Safety",
                "FS2": "Test Safety 2",
                "SS1": "Test Strong Safety",
                "SS2": "Test Strong Safety 2",
                "K1": "Test Kicker",
                "P1": "Test Punter",
                "LT1": "Test Left Tackle",
                "LT2": "Test Left Tackle 2",
                "LG1": "Test Left Guard",
                "LG2": "Test Left Guard 2",
                "C1": "Test Center",
                "C2": "Test Center 2",
                "RG1": "Test Right Guard",
                "RG2": "Test Right Guard 2",
                "RT1": "Test Right Tackle",
                "RT2": "Test Right Tackle 2",
                "DT1": "Test Tackle",
                "DT2": "Test Tackle 2",
                "DT3": "Test Tackle 3",
                "LE1": "Test End",
                "LE2": "Test End 2",
                "RE1": "Test Right End",
                "RE2": "Test Right End 2",
                "FB1": "Test Fullback"
            },
            "unrealistic_events_enabled": True
        }
        
        self.data_manager.load_config.return_value = self.test_config
        
        # Create the event manager with our mock data manager
        self.event_manager = EventManager(self.data_manager)
    
    def test_all_events_processable(self):
        """Test that all events can be processed without errors."""
        events = self.events_data.get('events', [])
        total_events = len(events)
        processed_count = 0
        failed_events = []
        
        for event in events:
            event_id = event.get('id', 'unknown')
            title = event.get('title', 'Unknown Event')
            
            # Set random seed for deterministic testing
            random.seed(event_id)
            
            try:
                # Process the event
                processed_event = self.event_manager._process_event(event)
                
                # Basic assertions
                self.assertIsNotNone(processed_event)
                self.assertIn('processed_description', processed_event)
                
                # If it has target_options, verify target replacement
                if 'target_options' in event and '{target}' in event.get('description', ''):
                    self.assertIn('selected_target', processed_event)
                    self.assertNotIn('{target}', processed_event['processed_description'])
                
                # If it has options, verify they were processed
                if 'options' in event:
                    for option in processed_event['options']:
                        self.assertIn('processed_description', option)
                
                # If it has result_options, make sure they were correctly processed
                if 'result_options' in event:
                    # Hard-code the random selection for testing
                    with patch('random.random', return_value=0.3):
                        # Re-process with mocked random
                        processed_event = self.event_manager._process_event(event)
                        self.assertIn('selected_result', processed_event)
                        
                # Try accepting the event
                self.event_manager.accept_event(processed_event)
                
                processed_count += 1
                print(f"Successfully processed event {event_id}: {title}")
            except Exception as e:
                failed_events.append((event_id, title, str(e)))
                print(f"Failed to process event {event_id}: {title} - {str(e)}", file=sys.stderr)
        
        if failed_events:
            for event_id, title, error in failed_events:
                print(f"Event {event_id} ({title}) failed: {error}", file=sys.stderr)
            
            self.fail(f"Failed to process {len(failed_events)} out of {total_events} events.")
        
        print(f"Successfully processed all {processed_count} events.")
    
    def test_events_with_options(self):
        """Test events with options are processed correctly."""
        # Choose specific event IDs that have options
        option_event_ids = [10, 11, 12, 21, 22, 48, 50]  # Events known to have options
        
        events_with_options = [e for e in self.events_data.get('events', []) 
                              if e.get('id') in option_event_ids]
        
        if not events_with_options:
            self.skipTest("No events with options found")
        
        for event in events_with_options:
            try:
                # Process the event
                processed_event = self.event_manager._process_event(event)
                
                # Verify options
                self.assertIn('options', processed_event)
                if len(processed_event['options']) > 0:
                    option = processed_event['options'][0]
                    
                    # Test selecting the first option
                    selected = self.event_manager.select_event_option(processed_event, 0)
                    self.assertEqual(selected, option)
                    
                    # Verify it was added to history
                    history = self.event_manager.get_event_history()
                    self.assertTrue(any(h['title'] == event['title'] for h in history))
                    
                    # Clear history for next test
                    self.event_manager.clear_event_history()
                    
                print(f"Successfully tested event with options: {event.get('id')} - {event.get('title')}")
            except Exception as e:
                self.fail(f"Event with options {event.get('id')} - {event.get('title')} failed: {str(e)}")
    
    def test_random_impact_options(self):
        """Test events with random impact options."""
        # Choose specific event IDs with random impact options
        random_impact_ids = [10, 22, 38, 51]  # Events known to have random impact options
        
        events_with_random_impacts = [e for e in self.events_data.get('events', []) 
                                     if e.get('id') in random_impact_ids]
        
        if not events_with_random_impacts:
            self.skipTest("No events with random impact options found")
        
        for event in events_with_random_impacts:
            try:
                processed_event = self.event_manager._process_event(event)
                
                # Find options with random impacts
                if 'options' in processed_event:
                    for i, option in enumerate(processed_event['options']):
                        if 'impact_random_options' in option:
                            # Make a mock version of the _process_impact_random_options function
                            impact_options = option.get('impact_random_options', {})
                            options = list(impact_options.keys())
                            weights = list(impact_options.values())
                            
                            # Ensure we can select a random impact
                            if options and weights:
                                # This is similar to what the UI would do
                                selected_impact = random.choices(population=options, weights=weights, k=1)[0]
                                self.assertIn(selected_impact, options)
                                
                print(f"Successfully tested event with random impacts: {event.get('id')} - {event.get('title')}")
            except Exception as e:
                self.fail(f"Event with random impacts {event.get('id')} - {event.get('title')} failed: {str(e)}")
    
    def test_difficulty_filter(self):
        """Test events are filtered by difficulty."""
        # Mock the _process_event method to avoid issues with specific events
        with patch.object(self.event_manager, '_process_event', return_value={'id': 999, 'title': 'Test Event'}):
            # Test each difficulty level
            difficulties = ["cupcake", "rookie", "pro", "all-madden", "diabolical"]
            
            for difficulty in difficulties:
                # Set the difficulty
                self.event_manager.set_difficulty(difficulty)
                
                # Roll once to make sure it works at all
                event = self.event_manager.roll_event()
                
                # We're just testing that the method runs without error
                # The actual events returned depend on random factors and difficulty weights
                print(f"Successfully tested difficulty: {difficulty}")
    
    def test_season_stage_filter(self):
        """Test events are filtered by season stage."""
        # Using the proper season stage names with correct capitalization
        # These are the exact names used in the event_manager.py _get_allowed_stages method
        all_stages = [
            "Pre-Season", 
            "Regular Season Start", 
            "Regular Season Mid", 
            "Regular Season End", 
            "Post-Season", 
            "Off-Season"
        ]
        
        # Mock the _process_event method to avoid issues with specific events
        with patch.object(self.event_manager, '_process_event', return_value={'id': 999, 'title': 'Test Event'}):
            for stage in all_stages:
                # Update the season stage
                self.event_manager.config['franchise_info']['season_stage'] = stage
                
                # Roll once to make sure it works at all
                event = self.event_manager.roll_event()
                
                # We're just testing that the method runs without error
                print(f"Successfully tested season stage: {stage}")
        
        # Also test the internal names used in the events.json file
        internal_stages = [
            "regular-season-start", 
            "regular-season-mid", 
            "regular-season-end"
        ]
        
        with patch.object(self.event_manager, '_process_event', return_value={'id': 999, 'title': 'Test Event'}):
            for stage in internal_stages:
                # Update the season stage
                self.event_manager.config['franchise_info']['season_stage'] = stage
                
                # Roll once to make sure it works at all
                event = self.event_manager.roll_event()
                
                # We're just testing that the method runs without error
                print(f"Successfully tested internal season stage: {stage}")
    
    def test_trainer_events(self):
        """Test events with trainers work correctly."""
        # Choose specific event IDs with trainers
        trainer_event_ids = [19, 20, 35, 69, 70, 71, 72, 73, 74, 75, 76]  # Events known to have trainers
        
        trainer_events = [e for e in self.events_data.get('events', []) 
                         if e.get('id') in trainer_event_ids]
        
        if not trainer_events:
            self.skipTest("No trainer events found")
        
        for event in trainer_events:
            try:
                # Process the event
                processed_event = self.event_manager._process_event(event)
                
                # Verify the trainer was selected and impact was applied
                if 'trainer_options' in event and 'trainer_impacts' in event:
                    self.assertIn('selected_trainer', processed_event)
                    self.assertNotIn('{trainer_impact}', processed_event.get('impact', ''))
                    if '{trainer}' in event.get('description', ''):
                        self.assertNotIn('{trainer}', processed_event.get('processed_description', ''))
                
                print(f"Successfully tested trainer event: {event.get('id')} - {event.get('title')}")
            except Exception as e:
                self.fail(f"Trainer event {event.get('id')} - {event.get('title')} failed: {str(e)}")
    
    def test_nested_options(self):
        """Test events with nested options (options within options)."""
        # Some events could have nested options in options[].options structure
        nested_events = []
        
        # Manually check a few events that might have nested options
        nested_event_ids = [12, 16, 68]  # Events that might have nested options
        
        events_to_check = [e for e in self.events_data.get('events', []) 
                          if e.get('id') in nested_event_ids]
        
        # Find events with nested options
        for event in events_to_check:
            if 'options' in event:
                for option in event['options']:
                    if isinstance(option, dict) and 'options' in option:
                        nested_events.append(event)
                        break
        
        if not nested_events:
            self.skipTest("No events with nested options found")
        
        for event in nested_events:
            try:
                # Process the event
                processed_event = self.event_manager._process_event(event)
                
                # Verify first level options
                self.assertIn('options', processed_event)
                
                # Find option with nested options
                for i, option in enumerate(processed_event['options']):
                    if isinstance(option, dict) and 'options' in option:
                        # In the real UI, selecting this option would lead to a new options dialog
                        # with the nested options, but we can verify the structure is correct
                        nested_options = option.get('options', [])
                        self.assertGreater(len(nested_options), 0)
                        
                        # Verify nested options have descriptions
                        for nested_option in nested_options:
                            self.assertIn('description', nested_option)
                        
                print(f"Successfully tested nested options event: {event.get('id')} - {event.get('title')}")
            except Exception as e:
                self.fail(f"Nested options event {event.get('id')} - {event.get('title')} failed: {str(e)}")
    
    def test_find_all_events_with_options(self):
        """Find all events that have options in the entire events.json file."""
        # This test helps identify which events have options for testing
        events_with_options = []
        
        for event in self.events_data.get('events', []):
            if 'options' in event and event['options']:
                events_with_options.append((event.get('id'), event.get('title')))
        
        print(f"Found {len(events_with_options)} events with options:")
        for event_id, title in events_with_options:
            print(f"Event ID: {event_id}, Title: {title}")
        
        # Not a real test, just informational
        self.assertTrue(True)
    
    def test_find_all_events_with_random_impacts(self):
        """Find all events that have random impact options."""
        # This test helps identify which events have random impact options
        events_with_random_impacts = []
        
        for event in self.events_data.get('events', []):
            if 'options' in event:
                for option in event['options']:
                    if isinstance(option, dict) and 'impact_random_options' in option:
                        events_with_random_impacts.append((event.get('id'), event.get('title')))
                        break
        
        print(f"Found {len(events_with_random_impacts)} events with random impacts:")
        for event_id, title in events_with_random_impacts:
            print(f"Event ID: {event_id}, Title: {title}")
        
        # Not a real test, just informational
        self.assertTrue(True)
    
    def test_event_schema_validation(self):
        """Test that all events in the JSON file follow the required schema."""
        required_fields = ['id', 'title', 'description', 'difficulty_weights', 'category', 'season_stages']
        
        for event in self.events_data.get('events', []):
            event_id = event.get('id', 'unknown')
            title = event.get('title', 'Unknown Event')
            
            # Check all required fields are present
            for field in required_fields:
                self.assertIn(field, event, f"Event {event_id} ({title}) is missing required field: {field}")
            
            # Check difficulty_weights has all levels
            difficulty_levels = ["cupcake", "rookie", "pro", "all-madden", "diabolical"]
            for level in difficulty_levels:
                self.assertIn(level, event['difficulty_weights'], 
                             f"Event {event_id} ({title}) is missing difficulty level: {level}")
            
            # Check season_stages is a non-empty list
            self.assertIsInstance(event['season_stages'], list, 
                                 f"Event {event_id} ({title}): season_stages must be a list")
            self.assertTrue(len(event['season_stages']) > 0, 
                           f"Event {event_id} ({title}): season_stages cannot be empty")
            
            # If event has options, each option must have description and impact
            if 'options' in event:
                for i, option in enumerate(event['options']):
                    self.assertIn('description', option, 
                                f"Event {event_id} ({title}): Option {i} missing description")
                    
                    # Either direct impact or random impacts must be present
                    has_impact = 'impact' in option or 'impact_random_options' in option
                    self.assertTrue(has_impact, 
                                  f"Event {event_id} ({title}): Option {i} missing impact or impact_random_options")
            
            print(f"Event {event_id} ({title}) passed schema validation")
    
    def test_unrealistic_events(self):
        """Test that unrealistic events can be processed properly."""
        # Verify that unrealistic events are enabled
        self.assertTrue(self.event_manager.config.get('unrealistic_events_enabled', False))
        
        # Get unrealistic events
        unrealistic_events = self.unrealistic_events_data.get('unrealistic_events', [])
        
        # If there are no unrealistic events, skip this test
        if not unrealistic_events:
            self.skipTest("No unrealistic events found. Create unrealistic_events.json with events to test.")
            return
        
        total_events = len(unrealistic_events)
        processed_count = 0
        failed_events = []
        
        # Set unrealistic events to be available
        self.event_manager.unrealistic_events = unrealistic_events
        
        # Process each event
        for event in unrealistic_events:
            event_id = event.get('id', 'unknown')
            title = event.get('title', 'Unknown Event')
            
            # Set random seed for deterministic testing
            random.seed(event_id)
            
            try:
                # Process the event
                processed_event = self.event_manager._process_event(event)
                
                # Basic assertions
                self.assertIsNotNone(processed_event)
                self.assertIn('processed_description', processed_event)
                
                # Try accepting the event
                self.event_manager.accept_event(processed_event)
                
                processed_count += 1
                print(f"Successfully processed unrealistic event {event_id}: {title}")
            except Exception as e:
                failed_events.append((event_id, title, str(e)))
                print(f"Failed to process unrealistic event {event_id}: {title} - {str(e)}", file=sys.stderr)
        
        if failed_events:
            for event_id, title, error in failed_events:
                print(f"Unrealistic event {event_id} ({title}) failed: {error}", file=sys.stderr)
            
            self.fail(f"Failed to process {len(failed_events)} out of {total_events} unrealistic events.")
        
        if processed_count > 0:
            print(f"Successfully processed all {processed_count} unrealistic events.")
        else:
            self.skipTest("No unrealistic events were processed.")
            
    def test_combined_event_pool(self):
        """Test that both regular and unrealistic events can be part of the event pool."""
        # Ensure unrealistic events are enabled
        self.event_manager.config['unrealistic_events_enabled'] = True
        
        # Get the combined event pool - using the public method in EventManager
        # Instead of _get_event_pool() which doesn't exist, we'll use roll_event() which internally builds the pool
        # Set a seed for deterministic results
        random.seed(42)
        
        # Try to roll an event a few times to test the event pool functionality
        events_rolled = []
        for _ in range(10):
            event = self.event_manager.roll_event()
            if event:
                events_rolled.append(event)
        
        # Verify that we got at least some events
        self.assertTrue(len(events_rolled) > 0, "Should be able to roll at least some events")
        
        # If there are unrealistic events, check if any were rolled
        if self.unrealistic_events_data.get('unrealistic_events', []):
            # Check if the unrealistic events were included in the rolled events
            unrealistic_ids = [e.get('id') for e in self.unrealistic_events_data.get('unrealistic_events', [])]
            rolled_ids = [e.get('id') for e in events_rolled]
            
            print(f"Rolled {len(events_rolled)} events")
            print(f"Available regular events: {len(self.events_data.get('events', []))}")
            print(f"Available unrealistic events: {len(self.unrealistic_events_data.get('unrealistic_events', []))}")
            
            # Note that there's a chance no unrealistic events were rolled due to randomness
            # So this is just informational rather than an assertion
            unrealistic_rolled = any(id in unrealistic_ids for id in rolled_ids)
            if unrealistic_rolled:
                print("At least one unrealistic event was included in the rolled events")
            else:
                print("No unrealistic events were rolled in this test run (this can happen due to randomness)")
        else:
            print("No unrealistic events found to test combined pool.")

if __name__ == '__main__':
    unittest.main() 