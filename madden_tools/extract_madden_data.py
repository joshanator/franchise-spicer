#!/usr/bin/env python3
import sys
import struct
import binascii
import re
import zlib
import io
import os

def analyze_madden_save(filename):
    """Attempt to analyze and extract data from a Madden save file."""
    try:
        with open(filename, 'rb') as f:
            data = f.read()
            
        # Print basic file info
        print(f"File size: {len(data)} bytes")
        
        # Check for FBCHUNKS header
        if data[0:8] == b'FBCHUNKS':
            print("File format: FBCHUNKS")
            
            # Extract version bytes (speculation)
            version = struct.unpack('<I', data[8:12])[0]
            print(f"Possible version: {version}")
            
            # Try to find the game version string
            game_version = re.search(b'Madden-[^\x00]+', data)
            if game_version:
                print(f"Game version: {game_version.group(0).decode('utf-8', errors='ignore')}")
            
            # Extract the NFL teams
            nfl_teams = ['ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', 'DEN', 
                        'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC', 'LAC', 'LAR', 'LV', 'MIA', 
                        'MIN', 'NE', 'NO', 'NYG', 'NYJ', 'PHI', 'PIT', 'SEA', 'SF', 'TB', 'TEN', 'WAS']
            
            # Try to find game schedule data
            print("\nGame Schedule Data:")
            # Look for regular season games
            for week in range(18):  # Up to 17 weeks + 1 for preseason
                week_games = re.findall(f'Week{week:02d}Game\\d+\\s+([A-Z]+)\\s+@\\s+([A-Z]+)'.encode(), data)
                if week_games:
                    print(f"  Week {week:02d}:")
                    for i, (away, home) in enumerate(week_games):
                        print(f"    Game {i}: {away.decode()} @ {home.decode()}")
            
            # Look for playoff games
            playoff_types = ['Wildcard', 'Div', 'Cnf', 'Superbowl']
            for playoff_type in playoff_types:
                playoff_games = re.findall(f'{playoff_type}Week\\d+Game\\d+\\s+.*'.encode(), data)
                if playoff_games:
                    print(f"  {playoff_type} Round:")
                    for game in playoff_games:
                        print(f"    {game.decode('utf-8', errors='ignore')}")
            
            # Try to extract save file elements and organize by category
            print("\nSave File Elements by Category:")
            
            # Categories to search for
            categories = {
                "Draft": re.findall(b'Draft[^\x00]{3,}', data),
                "Free Agency": re.findall(b'FA[^\x00]{3,}', data),
                "Team Management": re.findall(b'Team[^\x00]{3,}|Roster[^\x00]{3,}', data),
                "Player Management": re.findall(b'Player[^\x00]{3,}', data),
                "League Events": re.findall(b'(Week|Season|Playoff|Superbowl)[^\x00]{3,}', data),
                "Requests": re.findall(b'[A-Za-z_]{5,}Request', data),
                "Periods": re.findall(b'[A-Za-z_]{5,}Period', data),
                "Schedulers": re.findall(b'[A-Za-z_]{5,}Scheduler', data)
            }
            
            for category, elements in categories.items():
                if elements:
                    unique_elements = sorted(set(elem.decode('utf-8', errors='ignore') for elem in elements))
                    print(f"  {category} ({len(unique_elements)} items):")
                    for elem in unique_elements[:10]:  # Show first 10 for each category
                        print(f"    {elem}")
                    if len(unique_elements) > 10:
                        print(f"    ... and {len(unique_elements)-10} more")
            
            # Try to find and extract binary structures
            # Look for potential team/player data by finding patterns of repeated data structures
            
            # Create an output directory for any extracted data
            output_dir = "madden_extracted"
            os.makedirs(output_dir, exist_ok=True)
            
            # Try to find and dump any potential "chunk" structures
            # The FBCHUNKS format likely contains multiple chunks with headers
            chunks = []
            pos = 0
            
            # Very simple chunk detection - looking for possible chunk headers
            # This is purely speculative and based on observed patterns
            while pos < len(data) - 8:
                # Look for potential chunk marker patterns (4-byte aligned)
                if pos % 4 == 0 and all(0x20 <= b <= 0x7E for b in data[pos:pos+4]):
                    # This could be an ASCII chunk name
                    potential_chunk_name = data[pos:pos+4].decode('ascii', errors='ignore')
                    if potential_chunk_name.isalpha():
                        # This looks like a valid chunk name
                        chunks.append((pos, potential_chunk_name))
                pos += 4
            
            if chunks:
                print(f"\nIdentified {len(chunks)} potential data chunks")
                print("First 10 potential chunks:")
                for i, (chunk_pos, chunk_name) in enumerate(chunks[:10]):
                    print(f"  Chunk {i}: Pos 0x{chunk_pos:x}, Name: {chunk_name}")
                    
                    # Try to dump the first few bytes of each chunk
                    chunk_data = data[chunk_pos:chunk_pos+64]
                    print(f"    Data: {binascii.hexlify(chunk_data[:32]).decode()}")
                    
                    # Save the chunk data to a file
                    chunk_file = os.path.join(output_dir, f"chunk_{i}_{chunk_name}.bin")
                    with open(chunk_file, 'wb') as f:
                        f.write(chunk_data)
                
            # Try to extract useful text strings in context
            interesting_patterns = [
                b"Player[^\x00]{1,50}",
                b"Team[^\x00]{1,50}",
                b"Roster[^\x00]{1,50}",
                b"Draft[^\x00]{1,50}",
                b"Stat[^\x00]{1,50}",
                b"Award[^\x00]{1,50}",
            ]
            
            print("\nInteresting Data Patterns:")
            for pattern in interesting_patterns:
                matches = re.findall(pattern, data)
                if matches:
                    unique_matches = sorted(set(m.decode('utf-8', errors='ignore') for m in matches))
                    print(f"  Pattern '{pattern.decode('utf-8', errors='ignore').split('[')[0]}' ({len(unique_matches)} items):")
                    for match in unique_matches[:10]:
                        print(f"    {match}")
                    if len(unique_matches) > 10:
                        print(f"    ... and {len(unique_matches)-10} more")
            
        else:
            print("Unknown file format - not a FBCHUNKS header")
            
    except Exception as e:
        print(f"Error analyzing file: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "resources/CAREER-2017BETA"
        
    analyze_madden_save(filename) 