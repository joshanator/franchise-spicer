#!/usr/bin/env python3
import sys
import struct
import binascii
import re
import zlib
import os
import json
from collections import defaultdict

def find_player_data(filename):
    """
    Attempt to find and extract player data from a Madden save file.
    This uses specialized heuristics to identify potential player records.
    """
    try:
        with open(filename, 'rb') as f:
            data = f.read()
            
        print(f"Analyzing file: {filename} ({len(data)} bytes)")
        
        # NFL teams for reference
        nfl_teams = ['ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', 'DEN', 
                    'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC', 'LAC', 'LAR', 'LV', 'MIA', 
                    'MIN', 'NE', 'NO', 'NYG', 'NYJ', 'PHI', 'PIT', 'SEA', 'SF', 'TB', 'TEN', 'WAS']
        
        # Common NFL player positions
        positions = ['QB', 'RB', 'FB', 'WR', 'TE', 'LT', 'LG', 'C', 'RG', 'RT', 
                     'LE', 'RE', 'DT', 'LOLB', 'MLB', 'ROLB', 'CB', 'FS', 'SS', 'K', 'P']
        
        # Create output directory
        output_dir = "madden_players"
        os.makedirs(output_dir, exist_ok=True)
        
        # Try different approaches to find player data
        
        # 1. Look for player names - common in NFL rosters (this is speculative)
        # Names typically follow patterns, but without knowing the exact format
        # we can try to look for sequences that might resemble name fields
        
        # Words that might be found near player names in data structures
        potential_player_markers = [
            b'Player', b'NAME', b'Roster', b'Name', b'First', b'Last', 
            b'Position', b'Rating', b'OVR', b'Team', b'Height', b'Weight',
            b'Contract', b'Stats'
        ]
        
        player_sections = []
        
        # Search for regions that might contain player data
        for marker in potential_player_markers:
            # Find all occurrences of the marker
            positions_found = [m.start() for m in re.finditer(marker, data)]
            
            for pos in positions_found:
                # Extract a chunk of data that might contain player info
                # (arbitrary size, but large enough to capture typical player record)
                chunk = data[pos:pos+1000]
                player_sections.append((pos, chunk))
                
        print(f"Found {len(player_sections)} potential player data sections")
        
        # 2. Look for repeated patterns that might be player records
        # Player records typically follow the same structure for each player
        
        # Find sequences of bytes that appear multiple times
        # These might represent common values in player records
        pattern_counts = defaultdict(int)
        
        # Look for 4-byte patterns that might be field markers
        for i in range(0, len(data) - 4, 4):
            pattern = data[i:i+4]
            if all(32 <= b <= 126 for b in pattern):  # ASCII text
                pattern_counts[pattern] += 1
        
        # Sort patterns by frequency
        common_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
        print("\nMost common 4-byte ASCII patterns (potential field markers):")
        for pattern, count in common_patterns[:20]:
            if count > 10:  # Only show patterns that appear frequently
                print(f"  {pattern.decode('ascii', errors='ignore')}: {count} occurrences")
        
        # 3. Look for player attributes (numbers that might represent ratings)
        # Madden games typically use ratings from 0-99 for player attributes
        
        # Look for sequences of bytes where each byte could represent a rating
        rating_clusters = []
        for i in range(0, len(data) - 20):
            # Check if we have a sequence of potential ratings (values 40-99 are most common for starters)
            ratings = data[i:i+20]
            if all(40 <= b <= 99 for b in ratings):
                rating_clusters.append((i, ratings))
        
        print(f"\nFound {len(rating_clusters)} potential player rating clusters")
        if rating_clusters:
            print("Sample rating clusters:")
            for i, (pos, ratings) in enumerate(rating_clusters[:5]):
                print(f"  Cluster {i} at 0x{pos:x}: {', '.join(str(b) for b in ratings)}")
        
        # 4. Look for text that might be player names
        # Find sequences that look like names (capital letter followed by lowercase)
        
        name_pattern = re.compile(b'[A-Z][a-z]{1,20}\\s+[A-Z][a-z]{1,20}')
        potential_names = name_pattern.finditer(data)
        
        names_found = []
        for match in potential_names:
            name = match.group(0).decode('utf-8', errors='ignore')
            pos = match.start()
            names_found.append((pos, name))
        
        print(f"\nFound {len(names_found)} potential player names")
        if names_found:
            print("Sample names:")
            for pos, name in sorted(names_found)[:20]:
                # Look at surrounding data for context
                context = data[pos-10:pos+len(name)+10]
                printable = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in context)
                print(f"  0x{pos:x}: {name} (Context: {printable})")
        
        # 5. Look for NFL team names
        team_mentions = []
        for team in nfl_teams:
            team_bytes = team.encode('ascii')
            team_positions = [m.start() for m in re.finditer(team_bytes, data)]
            for pos in team_positions:
                team_mentions.append((pos, team))
        
        print(f"\nFound {len(team_mentions)} mentions of NFL teams")
        
        # 6. Look for position codes
        position_mentions = []
        for position in positions:
            pos_bytes = position.encode('ascii')
            pos_positions = [m.start() for m in re.finditer(pos_bytes, data)]
            for p in pos_positions:
                position_mentions.append((p, position))
        
        print(f"\nFound {len(position_mentions)} mentions of player positions")
        
        # Try to correlate team, position, and name mentions to find actual player records
        player_records = []
        
        # Very speculative approach - look for name, team, position within reasonable proximity
        for name_pos, name in names_found:
            # Look for team mentions nearby
            nearby_teams = [(t_pos, team) for t_pos, team in team_mentions 
                           if abs(t_pos - name_pos) < 200]
            
            # Look for positions nearby
            nearby_positions = [(p_pos, pos) for p_pos, pos in position_mentions 
                               if abs(p_pos - name_pos) < 200]
            
            if nearby_teams or nearby_positions:
                player_records.append({
                    'name': name,
                    'name_pos': name_pos,
                    'nearby_teams': nearby_teams,
                    'nearby_positions': nearby_positions
                })
        
        print(f"\nIdentified {len(player_records)} potential player records")
        if player_records:
            print("Sample player records:")
            for i, record in enumerate(player_records[:10]):
                print(f"  Player {i+1}:")
                print(f"    Name: {record['name']} (at 0x{record['name_pos']:x})")
                if record['nearby_teams']:
                    teams = ', '.join(f"{team} (0x{pos:x})" for pos, team in record['nearby_teams'][:3])
                    print(f"    Nearby teams: {teams}")
                if record['nearby_positions']:
                    positions = ', '.join(f"{pos} (0x{pos_pos:x})" for pos_pos, pos in record['nearby_positions'][:3])
                    print(f"    Nearby positions: {positions}")
        
        # Save any findings to files
        if player_records:
            with open(os.path.join(output_dir, 'potential_players.json'), 'w') as f:
                # Convert to a serializable format
                serializable_records = []
                for record in player_records:
                    serializable_record = {
                        'name': record['name'],
                        'name_pos': hex(record['name_pos']),
                        'nearby_teams': [(hex(pos), team) for pos, team in record['nearby_teams']],
                        'nearby_positions': [(hex(pos), position) for pos, position in record['nearby_positions']]
                    }
                    serializable_records.append(serializable_record)
                json.dump(serializable_records, f, indent=2)
            print(f"\nSaved {len(player_records)} potential player records to {output_dir}/potential_players.json")
        
    except Exception as e:
        print(f"Error analyzing file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "resources/CAREER-2017BETA"
        
    find_player_data(filename) 