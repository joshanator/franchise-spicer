#!/usr/bin/env python3
import zlib
import struct
import json
import os
import binascii
import re
from collections import OrderedDict

def decode_franchise_to_json(file_path, output_json_path=None):
    """
    Decode a Madden franchise file to a JSON format with improved player extraction
    and decompression techniques.
    
    Args:
        file_path: Path to the Madden franchise file
        output_json_path: Optional path to save JSON output
    
    Returns:
        Dict containing the decoded franchise data
    """
    with open(file_path, 'rb') as f:
        data = f.read()
    
    # Create a structure to hold our decoded data
    franchise_data = OrderedDict()
    
    # Store basic file info
    franchise_data['file_info'] = {
        'original_file_size': len(data),
        'original_file_path': file_path,
        'file_type': 'unknown'
    }
    
    # Check for FBCHUNKS header
    if data[:8] == b'FBCHUNKS':
        franchise_data['file_info']['file_type'] = 'FBCHUNKS'
        franchise_data['header'] = {
            'signature': 'FBCHUNKS',
            'version': struct.unpack('<I', data[8:12])[0],
            'header_bytes': binascii.hexlify(data[:0x50]).decode('ascii')
        }
        
        # Extract game version if present
        game_version_match = re.search(b'Madden-[^\x00]+', data)
        if game_version_match:
            franchise_data['header']['game_version'] = game_version_match.group(0).decode('utf-8', errors='ignore')
        
        # Extract schedule data
        franchise_data['schedule'] = parse_schedule_data(data)
        
        # Extract team data
        franchise_data['teams'] = parse_team_mentions(data)
        
        # Extract position mentions
        franchise_data['positions'] = parse_position_mentions(data)
        
        # Extract potential player names using improved methods
        franchise_data['players'] = find_player_names(data)
        
        # Extract rating clusters
        franchise_data['rating_clusters'] = parse_rating_clusters(data)
        
        # Try to find and decompress chunks with improved methods
        decompressed_chunks = advanced_decompress_chunks(data)
        franchise_data['decompressed_chunks'] = decompressed_chunks
        
        # Look for common strings in the file and decompressed chunks
        franchise_data['common_strings'] = find_common_strings(data)
        
        # Look for player data in decompressed chunks
        if decompressed_chunks and any(chunk.get('decompression_successful', False) for chunk in decompressed_chunks):
            player_data_from_chunks = extract_player_data_from_chunks(decompressed_chunks)
            if player_data_from_chunks:
                franchise_data['player_data_from_chunks'] = player_data_from_chunks
    
    # Save JSON output if path provided
    if output_json_path:
        with open(output_json_path, 'w') as f:
            json.dump(franchise_data, f, indent=2)
    
    return franchise_data

def parse_schedule_data(data):
    """Extract game schedule data from the file"""
    schedule = {
        'preseason': [],
        'regular_season': [],
        'playoffs': [],
        'superbowl': []
    }
    
    # Look for preseason and regular season games
    for week in range(18):  # Up to 17 weeks + 1 for preseason
        week_games = re.findall(f'Week{week:02d}Game\\d+\\s+([A-Z]+)\\s+@\\s+([A-Z]+)'.encode(), data)
        if week_games:
            week_type = 'preseason' if week == 0 else 'regular_season'
            for i, (away, home) in enumerate(week_games):
                schedule[week_type].append({
                    'week': week,
                    'game_num': i,
                    'away_team': away.decode(),
                    'home_team': home.decode()
                })
    
    # Look for playoff games
    playoff_types = ['Wildcard', 'Div', 'Cnf', 'Superbowl']
    for playoff_type in playoff_types:
        playoff_games = re.findall(f'{playoff_type}Week\\d+Game\\d+\\s+.*'.encode(), data)
        if playoff_games:
            game_type = 'playoffs' if playoff_type != 'Superbowl' else 'superbowl'
            for i, game in enumerate(playoff_games):
                game_text = game.decode('utf-8', errors='ignore')
                schedule[game_type].append({
                    'game_num': i,
                    'type': playoff_type,
                    'raw_text': game_text
                })
    
    return schedule

def parse_team_mentions(data):
    """Find mentions of NFL teams in the file"""
    nfl_teams = ['ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', 'DEN', 
                'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC', 'LAC', 'LAR', 'LV', 'MIA', 
                'MIN', 'NE', 'NO', 'NYG', 'NYJ', 'PHI', 'PIT', 'SEA', 'SF', 'TB', 'TEN', 'WAS']
    
    team_mentions = {}
    for team in nfl_teams:
        team_bytes = team.encode('ascii')
        positions = [m.start() for m in re.finditer(team_bytes, data)]
        if positions:
            team_mentions[team] = {
                'count': len(positions),
                'positions': [hex(pos) for pos in positions[:10]]  # First 10 positions
            }
    
    return team_mentions

def parse_position_mentions(data):
    """Find mentions of NFL positions in the file"""
    positions = ['QB', 'RB', 'FB', 'WR', 'TE', 'LT', 'LG', 'C', 'RG', 'RT', 
                'LE', 'RE', 'DT', 'LOLB', 'MLB', 'ROLB', 'CB', 'FS', 'SS', 'K', 'P']
    
    position_mentions = {}
    for pos in positions:
        pos_bytes = pos.encode('ascii')
        positions_found = [m.start() for m in re.finditer(pos_bytes, data)]
        if positions_found:
            position_mentions[pos] = {
                'count': len(positions_found),
                'positions': [hex(p) for p in positions_found[:10]]  # First 10 positions
            }
    
    return position_mentions

def parse_rating_clusters(data):
    """Find potential player rating clusters in the file"""
    rating_clusters = []
    
    # Look for sequences of bytes where each byte could represent a rating (40-99)
    for i in range(0, len(data) - 20):
        # Check if we have a sequence of potential ratings
        ratings = data[i:i+20]
        if all(40 <= b <= 99 for b in ratings):
            rating_clusters.append({
                'offset': hex(i),
                'values': list(ratings)
            })
            # Skip ahead to avoid overlapping clusters
            i += 20
    
    # Limit to first 20 clusters for brevity
    return rating_clusters[:20]

def find_player_names(data):
    """
    Attempt to find player names in the file using multiple approaches
    """
    player_name_candidates = []
    
    # Common NFL player first names
    common_first_names = ['Aaron', 'Adrian', 'Antonio', 'Baker', 'Brandon', 'Brady', 'Brian', 'Calvin', 
                          'Cameron', 'Carson', 'Chad', 'Chris', 'Christian', 'Davante', 'David', 'Dak', 
                          'Dalvin', 'Derrick', 'Deshaun', 'DeVonta', 'Ezekiel', 'Frank', 'George', 
                          'Jalen', 'Jameis', 'Jason', 'Jaylen', 'Justin', 'Kyler', 'Lamar', 'Larry', 
                          'Mark', 'Marshawn', 'Matthew', 'Michael', 'Mike', 'Nick', 'Odell', 'Patrick', 
                          'Peyton', 'Reggie', 'Russell', 'Ryan', 'Sam', 'Saquon', 'Stefon', 'Tom', 'Travis', 
                          'Trevor', 'Tyreek', 'Zach']
    
    # Common NFL player last names
    common_last_names = ['Adams', 'Allen', 'Beckham', 'Brady', 'Brown', 'Burrow', 'Cook', 'Cooper', 
                          'Diggs', 'Elliott', 'Fitzpatrick', 'Gordon', 'Gronkowski', 'Hill', 'Jackson', 
                          'Johnson', 'Jones', 'Kelce', 'Lawrence', 'Mahomes', 'Manning', 'Metcalf', 
                          'Murray', 'Prescott', 'Rodgers', 'Smith', 'Stafford', 'Thomas', 'Watson', 
                          'Wilson']
    
    # Approach 1: Look for common player name patterns
    # Looking for strings that match [First Name] [Last Name] pattern
    for first_name in common_first_names:
        for last_name in common_last_names:
            full_name = f"{first_name} {last_name}".encode('utf-8')
            positions = [m.start() for m in re.finditer(full_name, data)]
            
            if positions:
                # Found a potential player name
                for pos in positions:
                    # Look at surrounding data for context
                    context_start = max(0, pos - 20)
                    context_end = min(len(data), pos + len(full_name) + 20)
                    context = data[context_start:context_end]
                    
                    # Look for player position nearby
                    position_codes = ['QB', 'RB', 'WR', 'TE', 'OL', 'DL', 'LB', 'CB', 'S', 'K', 'P']
                    position_found = None
                    
                    for code in position_codes:
                        if code.encode('utf-8') in context:
                            position_found = code
                            break
                    
                    # Look for rating values nearby
                    rating_values = []
                    for i in range(len(context) - 5):
                        potential_ratings = context[i:i+5]
                        if all(40 <= b <= 99 for b in potential_ratings):
                            rating_values.extend(list(potential_ratings))
                    
                    player_name_candidates.append({
                        'name': f"{first_name} {last_name}",
                        'offset': hex(pos),
                        'position': position_found,
                        'nearby_ratings': rating_values[:10] if rating_values else None,
                        'context': binascii.hexlify(context).decode('ascii')
                    })
    
    # Approach 2: Look for capital letters followed by lowercase (potential names)
    # This regex looks for name-like patterns: Capital letter followed by lowercase letters, then space, then capital followed by lowercase
    name_pattern = re.compile(b'[A-Z][a-z]{2,10}\\s+[A-Z][a-z]{2,15}')
    matches = name_pattern.finditer(data)
    
    for match in matches:
        potential_name = match.group(0).decode('utf-8', errors='ignore')
        pos = match.start()
        
        # Don't include if it's already in our list
        if not any(candidate['offset'] == hex(pos) for candidate in player_name_candidates):
            # Check if this looks like a real name (not something like "Reset Salary")
            first_last = potential_name.split()
            if len(first_last) == 2 and len(first_last[0]) >= 3 and len(first_last[1]) >= 3:
                # Look at surrounding data for context
                context_start = max(0, pos - 20)
                context_end = min(len(data), pos + len(potential_name.encode('utf-8')) + 20)
                context = data[context_start:context_end]
                
                # Check for ratings nearby
                rating_values = []
                for i in range(len(context) - 5):
                    potential_ratings = context[i:i+5]
                    if all(40 <= b <= 99 for b in potential_ratings):
                        rating_values.extend(list(potential_ratings))
                
                player_name_candidates.append({
                    'name': potential_name,
                    'offset': hex(pos),
                    'nearby_ratings': rating_values[:10] if rating_values else None,
                    'context': binascii.hexlify(context).decode('ascii')
                })
    
    # Sort by offset and remove duplicates
    sorted_candidates = sorted(player_name_candidates, key=lambda x: int(x['offset'], 16))
    
    # Return the candidates
    return sorted_candidates

def advanced_decompress_chunks(data):
    """
    Advanced method to find and decompress zlib chunks in the file.
    Uses multiple strategies to identify chunks and determine their sizes.
    """
    chunks = []
    
    # Strategy 1: Look for common zlib headers (78 9C, 78 DA, 78 5E)
    zlib_headers = [b'x\x9c', b'x\xda', b'x^']
    
    for header in zlib_headers:
        positions = [i for i in range(len(data)) if data[i:i+2] == header]
        
        for pos in positions:
            chunk_info = {
                'offset': hex(pos),
                'header': binascii.hexlify(header).decode('ascii'),
                'decompression_successful': False
            }
            
            # Try various decompression strategies
            # Strategy A: Try larger chunk sizes
            for size in [1000, 5000, 10000, 50000, 100000]:
                if pos + size > len(data):
                    size = len(data) - pos
                
                try:
                    chunk_data = data[pos:pos+size]
                    decompressed = zlib.decompress(chunk_data)
                    
                    chunk_info['decompression_successful'] = True
                    chunk_info['compressed_size'] = size
                    chunk_info['decompressed_size'] = len(decompressed)
                    
                    # Save a sample of the decompressed data
                    if len(decompressed) > 0:
                        sample_size = min(200, len(decompressed))
                        chunk_info['sample'] = binascii.hexlify(decompressed[:sample_size]).decode('ascii')
                        
                        # Try to interpret as text if it seems like text
                        try:
                            text_sample = decompressed[:sample_size].decode('utf-8', errors='ignore')
                            printable_ratio = sum(c.isprintable() for c in text_sample) / len(text_sample)
                            if printable_ratio > 0.7:  # If more than 70% is printable
                                chunk_info['text_sample'] = text_sample
                        except:
                            pass
                    
                    # Extract the decompressed data to a file for further analysis
                    output_dir = "madden_chunks"
                    os.makedirs(output_dir, exist_ok=True)
                    chunk_file = os.path.join(output_dir, f"chunk_{pos:08x}.bin")
                    with open(chunk_file, 'wb') as f:
                        f.write(decompressed)
                    chunk_info['output_file'] = chunk_file
                    
                    break  # Successfully decompressed
                except zlib.error:
                    continue
            
            # Strategy B: Try to find zlib end marker and decompress just that segment
            if not chunk_info['decompression_successful']:
                # Look for potential end markers within a reasonable distance
                for end_pos in range(pos + 100, min(pos + 500000, len(data)), 100):
                    try:
                        chunk_data = data[pos:end_pos]
                        decompressed = zlib.decompress(chunk_data)
                        
                        chunk_info['decompression_successful'] = True
                        chunk_info['compressed_size'] = end_pos - pos
                        chunk_info['decompressed_size'] = len(decompressed)
                        
                        # Save a sample of the decompressed data
                        if len(decompressed) > 0:
                            sample_size = min(200, len(decompressed))
                            chunk_info['sample'] = binascii.hexlify(decompressed[:sample_size]).decode('ascii')
                            
                            # Try to interpret as text if it seems like text
                            try:
                                text_sample = decompressed[:sample_size].decode('utf-8', errors='ignore')
                                printable_ratio = sum(c.isprintable() for c in text_sample) / len(text_sample)
                                if printable_ratio > 0.7:  # If more than 70% is printable
                                    chunk_info['text_sample'] = text_sample
                            except:
                                pass
                        
                        # Extract the decompressed data to a file for further analysis
                        output_dir = "madden_chunks"
                        os.makedirs(output_dir, exist_ok=True)
                        chunk_file = os.path.join(output_dir, f"chunk_{pos:08x}.bin")
                        with open(chunk_file, 'wb') as f:
                            f.write(decompressed)
                        chunk_info['output_file'] = chunk_file
                        
                        break  # Successfully decompressed
                    except zlib.error:
                        continue
            
            # Only add to our list if we succeeded or if this is an interesting failure
            # (to avoid too many uninteresting failed chunks)
            if chunk_info['decompression_successful'] or (pos < 0x1000):  # Include early chunks even if failed
                chunks.append(chunk_info)
    
    # Sort chunks by offset
    sorted_chunks = sorted(chunks, key=lambda x: int(x['offset'], 16))
    
    # Limit to a reasonable number if there are too many
    if len(sorted_chunks) > 20:
        # Prioritize successful chunks
        successful_chunks = [c for c in sorted_chunks if c['decompression_successful']]
        failed_chunks = [c for c in sorted_chunks if not c['decompression_successful']]
        
        # Return all successful chunks plus some failed ones if needed to reach 20
        if len(successful_chunks) < 20:
            return successful_chunks + failed_chunks[:20-len(successful_chunks)]
        else:
            return successful_chunks[:20]
    
    return sorted_chunks

def extract_player_data_from_chunks(chunks):
    """
    Try to extract player data from decompressed chunks
    """
    player_data = []
    
    for chunk in chunks:
        if not chunk.get('decompression_successful', False) or 'output_file' not in chunk:
            continue
        
        try:
            # Read the decompressed chunk file
            with open(chunk['output_file'], 'rb') as f:
                decompressed_data = f.read()
            
            # Look for potential player records
            # First, look for sequences that might be names
            name_pattern = re.compile(b'[A-Z][a-z]{2,10}\\s+[A-Z][a-z]{2,15}')
            name_matches = name_pattern.finditer(decompressed_data)
            
            for match in name_matches:
                name = match.group(0).decode('utf-8', errors='ignore')
                pos = match.start()
                
                # Check if this looks like a player name
                first_last = name.split()
                if len(first_last) == 2 and len(first_last[0]) >= 3 and len(first_last[1]) >= 3:
                    # Look for player attributes nearby
                    context_start = max(0, pos - 30)
                    context_end = min(len(decompressed_data), pos + len(name.encode('utf-8')) + 70)
                    context = decompressed_data[context_start:context_end]
                    
                    # Look for numbers that might be ratings
                    ratings = []
                    for i in range(len(context) - 10):
                        rating_bytes = context[i:i+10]
                        if all(40 <= b <= 99 for b in rating_bytes):
                            ratings.append(list(rating_bytes))
                    
                    # Look for position codes
                    position_codes = ['QB', 'RB', 'WR', 'TE', 'OL', 'DL', 'LB', 'CB', 'S', 'K', 'P']
                    positions_found = []
                    
                    for code in position_codes:
                        if code.encode('utf-8') in context:
                            positions_found.append(code)
                    
                    # Look for team codes
                    team_codes = ['ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', 'DEN', 
                                 'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC', 'LAC', 'LAR', 'LV', 'MIA', 
                                 'MIN', 'NE', 'NO', 'NYG', 'NYJ', 'PHI', 'PIT', 'SEA', 'SF', 'TB', 'TEN', 'WAS']
                    teams_found = []
                    
                    for code in team_codes:
                        if code.encode('utf-8') in context:
                            teams_found.append(code)
                    
                    # Only include if we found some player-like attributes
                    if positions_found or teams_found or ratings:
                        player_data.append({
                            'name': name,
                            'offset_in_chunk': hex(pos),
                            'chunk_offset': chunk['offset'],
                            'positions': positions_found,
                            'teams': teams_found,
                            'ratings': ratings[:3] if ratings else None,  # Limit to first 3 rating clusters
                            'context': binascii.hexlify(context).decode('ascii')
                        })
        except Exception as e:
            print(f"Error processing chunk at {chunk['offset']}: {e}")
    
    return player_data

def find_common_strings(data):
    """Extract common text strings from the file"""
    # Look for interesting patterns in the file
    patterns = [
        b'Player[^\x00]{1,50}',
        b'Team[^\x00]{1,50}',
        b'Roster[^\x00]{1,50}',
        b'Draft[^\x00]{1,50}',
        b'Stat[^\x00]{1,50}',
        b'Period',
        b'Request',
        b'Scheduler'
    ]
    
    common_strings = {}
    for pattern in patterns:
        matches = re.findall(pattern, data)
        if matches:
            pattern_name = pattern.decode('utf-8', errors='ignore').split('[')[0]
            unique_matches = sorted(set(m.decode('utf-8', errors='ignore') for m in matches))
            common_strings[pattern_name] = unique_matches[:20]  # Limit to first 20 matches
    
    return common_strings

if __name__ == "__main__":
    file_path = "resources/CAREER-2017BETA"
    output_json_path = "career_2017beta_improved.json"
    
    print(f"Decoding {file_path} with improved methods...")
    print("This may take a few minutes for the advanced decompression...")
    decode_franchise_to_json(file_path, output_json_path)
    print(f"Improved JSON data saved to {output_json_path}")
    
    # Show a summary of what was found
    with open(output_json_path, 'r') as f:
        data = json.load(f)
        
        print("\n=== Summary of Findings ===")
        print(f"File type: {data['file_info']['file_type']}")
        print(f"Game version: {data['header'].get('game_version', 'Unknown')}")
        
        print(f"\nSchedule: {len(data['schedule']['preseason'])} preseason games, "
              f"{len(data['schedule']['regular_season'])} regular season games")
        
        print(f"\nTeams mentioned: {len(data['teams'])} NFL teams")
        
        print(f"\nPotential player names found: {len(data['players'])}")
        if data['players']:
            print("Sample player names:")
            for player in data['players'][:5]:
                print(f"  - {player['name']} (at {player['offset']})")
        
        decompressed = [c for c in data.get('decompressed_chunks', []) if c.get('decompression_successful')]
        print(f"\nSuccessfully decompressed {len(decompressed)} data chunks out of {len(data.get('decompressed_chunks', []))}")
        
        if 'player_data_from_chunks' in data:
            print(f"\nExtracted {len(data['player_data_from_chunks'])} potential player records from decompressed chunks")
            if data['player_data_from_chunks']:
                print("Sample players from chunks:")
                for player in data['player_data_from_chunks'][:5]:
                    print(f"  - {player['name']} (Teams: {', '.join(player['teams']) if player['teams'] else 'None'}, "
                          f"Positions: {', '.join(player['positions']) if player['positions'] else 'None'})")
        
        print("\nCheck the full JSON file for complete details.") 