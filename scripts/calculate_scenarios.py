#!/usr/bin/env python3
import json
import os
import re
import sys
from pathlib import Path

def count_scenarios_in_option(option):
    """Count scenarios in a single option, including nested options."""
    try:
        base_count = 1
        
        # If there are nested options, count them
        if 'options' in option:
            nested_count = sum(count_scenarios_in_option(nested_opt) for nested_opt in option['options'])
            return base_count * nested_count
        
        # If there are random impact options, count them
        if 'impact_random_options' in option:
            return base_count * len(option['impact_random_options'])
        
        # Simple option with no nested choices
        return base_count
    except Exception as e:
        print(f"Error counting scenarios in option: {e}", file=sys.stderr)
        return 1  # Default to 1 on error

def count_event_scenarios(event):
    """Count all possible scenarios for a single event."""
    try:
        base_count = 1
        
        # Account for target options
        if 'target_options' in event and event['target_options']:
            # Special case: if 'all-players' is one of the options, this represents all players
            # For simplicity, we'll use a standard roster size
            if 'all-players' in event['target_options']:
                base_count *= 53  # Standard NFL roster size
            else:
                base_count *= len(event['target_options'])
        
        # Account for reason options
        if 'reason_options' in event and event['reason_options']:
            base_count *= len(event['reason_options'])
        
        # Account for games options (suspension length, etc.)
        if 'games_options' in event and event['games_options']:
            base_count *= len(event['games_options'])
        
        # Account for position options
        if 'position_options' in event and event['position_options']:
            base_count *= len(event['position_options'])
        
        # Account for trainer options and their impacts
        if 'trainer_options' in event and event['trainer_options']:
            # Check if these are simple strings or objects
            if isinstance(event['trainer_options'][0], str):
                base_count *= len(event['trainer_options'])
            else:
                # Complex objects
                base_count *= len(event['trainer_options'])
        
        # Account for trainer impacts
        if 'trainer_impacts' in event and event['trainer_impacts']:
            # We don't multiply by this since it's tied to trainer_options
            pass
        
        # Account for award options
        if 'award_options' in event and event['award_options']:
            base_count *= len(event['award_options'])
        
        # Account for stat options
        if 'stat_options' in event and event['stat_options']:
            base_count *= len(event['stat_options'])
        
        # Account for round options
        if 'round_options' in event and event['round_options']:
            base_count *= len(event['round_options'])
        
        # Account for result options
        if 'result_options' in event and event['result_options']:
            # Check if these are simple values or objects with probabilities
            if isinstance(event['result_options'], list):
                base_count *= len(event['result_options'])
        
        # Account for target impacts (specific effects based on target)
        if 'target_impacts' in event and event['target_impacts']:
            # We don't multiply by this since it's tied to target_options
            pass
        
        # Account for direct options - these create branching paths
        if 'options' in event and event['options']:
            options_count = sum(count_scenarios_in_option(option) for option in event['options'])
            if options_count > 0:
                base_count *= options_count
        
        return base_count
    except Exception as e:
        event_id = event.get('id', 'unknown')
        event_title = event.get('title', 'untitled')
        print(f"Error counting scenarios for event {event_id} ({event_title}): {e}", file=sys.stderr)
        return 1  # Default to 1 on error

def calculate_total_scenarios():
    """Calculate the total number of unique scenarios across all events."""
    try:
        # Define paths
        base_dir = Path(__file__).resolve().parent.parent
        regular_events_path = base_dir / 'madden_franchise_qt' / 'data' / 'events.json'
        unrealistic_events_path = base_dir / 'madden_franchise_qt' / 'data' / 'unrealistic_events.json'
        
        # Load the event files
        with open(regular_events_path, 'r') as f:
            regular_events = json.load(f)['events']
            
        with open(unrealistic_events_path, 'r') as f:
            unrealistic_events = json.load(f)['unrealistic_events']
        
        # Calculate scenarios for each event
        regular_scenario_counts = [count_event_scenarios(event) for event in regular_events]
        unrealistic_scenario_counts = [count_event_scenarios(event) for event in unrealistic_events]
        
        # Calculate totals
        regular_scenario_count = sum(regular_scenario_counts)
        unrealistic_scenario_count = sum(unrealistic_scenario_counts)
        total_scenario_count = regular_scenario_count + unrealistic_scenario_count
        
        # Print detailed info
        print(f"Regular events: {len(regular_events)} events with {regular_scenario_count} scenarios")
        print(f"Unrealistic events: {len(unrealistic_events)} events with {unrealistic_scenario_count} scenarios")
        print(f"Total: {len(regular_events) + len(unrealistic_events)} events with {total_scenario_count} scenarios")
        
        return {
            'regular_events': len(regular_events),
            'regular_scenarios': regular_scenario_count,
            'unrealistic_events': len(unrealistic_events),
            'unrealistic_scenarios': unrealistic_scenario_count,
            'total_events': len(regular_events) + len(unrealistic_events),
            'total_scenarios': total_scenario_count
        }
    except Exception as e:
        print(f"Error calculating total scenarios: {e}", file=sys.stderr)
        # Return default values in case of error
        return {
            'regular_events': 0,
            'regular_scenarios': 0,
            'unrealistic_events': 0,
            'unrealistic_scenarios': 0,
            'total_events': 0,
            'total_scenarios': 0
        }

if __name__ == "__main__":
    try:
        scenario_counts = calculate_total_scenarios()
        # Print just the final number for GitHub Actions to capture
        print(scenario_counts['total_scenarios'])
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1) 