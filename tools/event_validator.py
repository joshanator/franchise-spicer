#!/usr/bin/env python3
"""
Event Validator and Fixer Utility

This tool validates events in the events.json file and can automatically fix common issues.
Run with --fix to apply automatic fixes, or --validate to just report issues.
"""

import json
import os
import argparse
import sys
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Paths to the event files
EVENTS_PATH = PROJECT_ROOT / "madden_franchise_qt" / "data" / "events.json"
UNREALISTIC_EVENTS_PATH = PROJECT_ROOT / "madden_franchise_qt" / "data" / "unrealistic_events.json"

# Required fields for all events
REQUIRED_EVENT_FIELDS = ['id', 'title', 'description', 'difficulty_weights', 'category', 'season_stages']
DIFFICULTY_LEVELS = ["cupcake", "rookie", "pro", "all-madden", "diabolical"]

def validate_events(events_data, events_type="standard", fix=False):
    """
    Validate the events in the provided data and optionally fix issues.
    
    Args:
        events_data (dict): The events data loaded from JSON
        events_type (str): The type of events being validated ('standard' or 'unrealistic')
        fix (bool): Whether to fix issues or just report them
        
    Returns:
        tuple: (fixed_data, num_issues, num_fixed)
    """
    if events_type == "standard":
        events = events_data.get('events', [])
    else:
        events = events_data.get('unrealistic_events', [])
    
    issues_count = 0
    fixed_count = 0
    
    print(f"\nValidating {len(events)} {events_type} events...")
    
    # Process each event
    for event in events:
        event_id = event.get('id', 'unknown')
        title = event.get('title', 'Unknown Event')
        
        # Check for required fields
        for field in REQUIRED_EVENT_FIELDS:
            if field not in event:
                issues_count += 1
                print(f"ERROR: Event {event_id} ({title}) is missing required field: {field}")
                
                # Add default values for fixable fields
                if fix:
                    if field == 'difficulty_weights':
                        event[field] = {level: 0.2 for level in DIFFICULTY_LEVELS}
                        print(f"  FIXED: Added default difficulty_weights to event {event_id}")
                        fixed_count += 1
                    elif field == 'category':
                        event[field] = 'misc'
                        print(f"  FIXED: Added default category 'misc' to event {event_id}")
                        fixed_count += 1
                    elif field == 'season_stages':
                        event[field] = ['pre-season', 'regular-season-mid']
                        print(f"  FIXED: Added default season_stages to event {event_id}")
                        fixed_count += 1
        
        # Check difficulty weights
        if 'difficulty_weights' in event:
            for level in DIFFICULTY_LEVELS:
                if level not in event['difficulty_weights']:
                    issues_count += 1
                    print(f"ERROR: Event {event_id} ({title}) is missing difficulty level: {level}")
                    
                    if fix:
                        event['difficulty_weights'][level] = 0.2
                        print(f"  FIXED: Added default weight for {level} to event {event_id}")
                        fixed_count += 1
        
        # Check result_options
        if 'result_options' in event:
            for i, option in enumerate(event['result_options']):
                # Check for result field
                if 'impact_text' in option and 'result' not in option:
                    issues_count += 1
                    print(f"ERROR: Event {event_id} ({title}) has result_option {i+1} without a 'result' field")
                    
                    if fix:
                        # Create a result identifier based on index
                        if 'success' in option.get('impact_text', '').lower():
                            result_name = 'success'
                        elif 'failure' in option.get('impact_text', '').lower() or 'backfire' in option.get('impact_text', '').lower():
                            result_name = 'failure'
                        else:
                            result_name = f"result_{i+1}"
                        
                        option['result'] = result_name
                        print(f"  FIXED: Added 'result' field to option {i+1} in event {event_id}")
                        fixed_count += 1
                
                # Check for probability field
                if 'probability' not in option:
                    issues_count += 1
                    print(f"ERROR: Event {event_id} ({title}) has result_option {i+1} without a 'probability' field")
                    
                    if fix:
                        # Divide remaining probability evenly
                        total_prob = sum(opt.get('probability', 0) for opt in event['result_options'])
                        remaining = 1.0 - total_prob
                        remaining_options = sum(1 for opt in event['result_options'] if 'probability' not in opt)
                        if remaining_options > 0:
                            option['probability'] = round(remaining / remaining_options, 2)
                            print(f"  FIXED: Added probability {option['probability']} to option {i+1} in event {event_id}")
                            fixed_count += 1
        
        # Check options
        if 'options' in event:
            for i, option in enumerate(event['options']):
                if isinstance(option, dict):
                    if 'description' not in option:
                        issues_count += 1
                        print(f"ERROR: Event {event_id} ({title}) has option {i+1} without a 'description' field")
                    
                    has_impact = 'impact' in option or 'impact_random_options' in option
                    if not has_impact:
                        issues_count += 1
                        print(f"ERROR: Event {event_id} ({title}) has option {i+1} without 'impact' or 'impact_random_options'")
                        
                        if fix:
                            option['impact'] = "No specific impact. Implement game changes as appropriate."
                            print(f"  FIXED: Added default impact to option {i+1} in event {event_id}")
                            fixed_count += 1
    
    print(f"\nValidation Summary for {events_type} events:")
    print(f"  {issues_count} issues found")
    if fix:
        print(f"  {fixed_count} issues fixed")
    
    return events_data, issues_count, fixed_count

def main():
    parser = argparse.ArgumentParser(description="Validate and fix event files")
    parser.add_argument('--validate', action='store_true', help='Validate events without fixing')
    parser.add_argument('--fix', action='store_true', help='Fix issues in events files')
    parser.add_argument('--unrealistic', action='store_true', help='Also process unrealistic events')
    args = parser.parse_args()
    
    if not (args.validate or args.fix):
        parser.print_help()
        sys.exit(1)
    
    # Process standard events
    print(f"Processing events file: {EVENTS_PATH}")
    try:
        with open(EVENTS_PATH, 'r') as f:
            events_data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Events file not found at {EVENTS_PATH}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON in events file at {EVENTS_PATH}")
        sys.exit(1)
    
    fixed_data, issues, fixed = validate_events(events_data, "standard", args.fix)
    
    if args.fix and fixed > 0:
        # Backup original file
        backup_path = str(EVENTS_PATH) + '.backup'
        try:
            with open(backup_path, 'w') as f:
                json.dump(events_data, f, indent=2)
            print(f"Backed up original file to {backup_path}")
        except Exception as e:
            print(f"WARNING: Failed to backup original file: {str(e)}")
        
        # Save fixed file
        try:
            with open(EVENTS_PATH, 'w') as f:
                json.dump(fixed_data, f, indent=2)
            print(f"Saved fixed events to {EVENTS_PATH}")
        except Exception as e:
            print(f"ERROR: Failed to save fixed events: {str(e)}")
            sys.exit(1)
    
    # Process unrealistic events if requested
    if args.unrealistic:
        if not os.path.exists(UNREALISTIC_EVENTS_PATH):
            print(f"\nUnrealistic events file not found at {UNREALISTIC_EVENTS_PATH}")
            print("Skipping unrealistic events validation.")
        else:
            print(f"\nProcessing unrealistic events file: {UNREALISTIC_EVENTS_PATH}")
            try:
                with open(UNREALISTIC_EVENTS_PATH, 'r') as f:
                    unrealistic_data = json.load(f)
            except json.JSONDecodeError:
                print(f"ERROR: Invalid JSON in unrealistic events file at {UNREALISTIC_EVENTS_PATH}")
                sys.exit(1)
            
            fixed_data, issues, fixed = validate_events(unrealistic_data, "unrealistic", args.fix)
            
            if args.fix and fixed > 0:
                # Backup original file
                backup_path = str(UNREALISTIC_EVENTS_PATH) + '.backup'
                try:
                    with open(backup_path, 'w') as f:
                        json.dump(unrealistic_data, f, indent=2)
                    print(f"Backed up original unrealistic events to {backup_path}")
                except Exception as e:
                    print(f"WARNING: Failed to backup original unrealistic events file: {str(e)}")
                
                # Save fixed file
                try:
                    with open(UNREALISTIC_EVENTS_PATH, 'w') as f:
                        json.dump(fixed_data, f, indent=2)
                    print(f"Saved fixed unrealistic events to {UNREALISTIC_EVENTS_PATH}")
                except Exception as e:
                    print(f"ERROR: Failed to save fixed unrealistic events: {str(e)}")
                    sys.exit(1)
    
    print("\nDone!")

if __name__ == "__main__":
    main() 