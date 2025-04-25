#!/usr/bin/env python3
import json
import os

# Problematic event IDs identified from tests
PROBLEMATIC_EVENT_IDS = [24, 29, 43, 52, 54, 55, 58]

def fix_events_json():
    """Fix events that have result_options without a 'result' field"""
    # Path to the events.json file
    events_path = 'madden_franchise_qt/data/events.json'
    
    # Load the file
    with open(events_path, 'r') as f:
        data = json.load(f)
    
    events = data.get('events', [])
    fixed_count = 0
    
    # Process each event
    for event in events:
        event_id = event.get('id')
        
        # Check if this is one of our problematic events with result_options
        if event_id in PROBLEMATIC_EVENT_IDS and 'result_options' in event:
            print(f"Fixing event {event_id}: {event.get('title')}")
            
            # Process each result option
            for i, option in enumerate(event['result_options']):
                # If it has impact_text but no result, add a result field
                if 'impact_text' in option and 'result' not in option:
                    # Create a short result identifier based on index
                    if 'success' in option['impact_text'].lower():
                        result_name = 'success'
                    elif 'failure' in option['impact_text'].lower() or 'backfire' in option['impact_text'].lower():
                        result_name = 'failure'
                    else:
                        result_name = f"result_{i+1}"
                    
                    option['result'] = result_name
                    fixed_count += 1
                    print(f"  Added 'result' field to option {i+1}")
    
    # Save the updated file
    with open(events_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\nUpdated {fixed_count} options in {len(PROBLEMATIC_EVENT_IDS)} events.")
    print(f"Events JSON saved to {events_path}")

if __name__ == "__main__":
    fix_events_json() 