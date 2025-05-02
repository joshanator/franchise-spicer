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
    Decode a Madden franchise file to a JSON format.
    
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
        
        # Extract rating clusters
        franchise_data['rating_clusters'] = parse_rating_clusters(data)
        
        # Try to find compressed chunks
        franchise_data['compressed_chunks'] = find_compressed_chunks(data)
        
        # Look for common strings in the file
        franchise_data['common_strings'] = find_common_strings(data)
    
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
    
    # Look for sequences of at least 10 bytes where each byte is in the range 40-99
    for i in range(0, len(data) - 10):
        # Check for potential ratings (values 40-99 are common for Madden player ratings)
        ratings = data[i:i+10]
        if all(40 <= b <= 99 for b in ratings):
            rating_clusters.append({
                'offset': hex(i),
                'values': list(ratings)
            })
            # Skip ahead to avoid overlapping clusters
            i += 10
    
    # Limit to first 20 clusters for brevity
    return rating_clusters[:20]

def find_compressed_chunks(data):
    """Try to find and extract zlib compressed chunks"""
    chunks = []
    
    # Look for common zlib header (78 9C)
    zlib_positions = [i for i in range(len(data)) if data[i:i+2] == b'x\x9c']
    
    for i, pos in enumerate(zlib_positions[:5]):  # Limit to first 5 potential chunks
        chunk_info = {
            'index': i,
            'offset': hex(pos),
            'header': '789C',  # Hex representation of the zlib header
            'decompression_attempt': 'failed'
        }
        
        # Try to decompress with different chunk sizes
        for size in [100, 1000, 10000]:
            if pos + size > len(data):
                size = len(data) - pos
            
            try:
                chunk_data = data[pos:pos+size]
                decompressed = zlib.decompress(chunk_data)
                
                chunk_info['decompression_attempt'] = 'success'
                chunk_info['compressed_size'] = size
                chunk_info['decompressed_size'] = len(decompressed)
                
                # Show a sample of the decompressed data
                if len(decompressed) > 0:
                    sample_size = min(100, len(decompressed))
                    chunk_info['sample'] = binascii.hexlify(decompressed[:sample_size]).decode('ascii')
                
                break  # Successfully decompressed, no need to try larger sizes
            except zlib.error:
                continue
        
        chunks.append(chunk_info)
    
    return chunks

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
    output_json_path = "career_2017beta_decoded.json"
    
    print(f"Decoding {file_path} to JSON...")
    decode_franchise_to_json(file_path, output_json_path)
    print(f"JSON data saved to {output_json_path}")
    
    # Show a preview of the JSON data
    with open(output_json_path, 'r') as f:
        data = json.load(f)
        print("\nJSON Preview:")
        print(json.dumps(data, indent=2)[:1000] + "...")  # Show first 1000 chars 