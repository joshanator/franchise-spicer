import os
import zlib
import struct
import json
import re
from collections import defaultdict
import binascii

class MaddenFranchiseDecoder:
    def __init__(self, file_path):
        self.file_path = file_path
        self.decoded_data = {
            "header": {},
            "chunks": [],
            "decompressed_data": {},
            "players": [],
            "teams": [],
            "schedule": {"preseason": [], "regular_season": []},
            "common_strings": {},
            "rating_clusters": {},
            "player_positions": defaultdict(int),
            "nfl_teams": defaultdict(int),
            "player_stats": {}
        }
        
    def decode(self):
        """Decode the Madden franchise file"""
        with open(self.file_path, 'rb') as f:
            file_data = f.read()
            
        file_size = len(file_data)
        self.decoded_data["file_size"] = file_size
        
        # Check for FBCHUNKS header
        if file_data[:8] == b'FBCHUNKS':
            self.decoded_data["header"]["signature"] = "FBCHUNKS"
            self.decoded_data["header"]["version"] = struct.unpack(">I", file_data[8:12])[0]
            
            # Extract the game version
            game_version_offset = struct.unpack(">I", file_data[12:16])[0]
            if game_version_offset > 0 and game_version_offset < file_size:
                # Find null-terminated string
                end_offset = file_data.find(b'\x00', game_version_offset)
                if end_offset > game_version_offset:
                    self.decoded_data["header"]["game_version"] = file_data[game_version_offset:end_offset].decode('utf-8', errors='ignore')
            
            # Process schedule data if present
            self._extract_schedule_data(file_data)
            
            # Find and decompress zlib chunks
            self._decompress_chunks(file_data)
            
            # Extract player information from decompressed data
            self._extract_player_info()
            
            # Extract team information
            self._extract_team_info()
            
            # Extract rating clusters
            self._extract_rating_clusters(file_data)
            
            # Find common strings
            self._extract_common_strings(file_data)
        else:
            self.decoded_data["error"] = "Not a valid FBCHUNKS file"
            
        return self.decoded_data
    
    def _extract_schedule_data(self, file_data):
        """Extract schedule data from the file"""
        # Look for common schedule patterns
        preseason_pattern = re.compile(b'Preseason Week ([0-9]+)')
        regular_season_pattern = re.compile(b'Week ([0-9]+)')
        
        preseason_matches = list(preseason_pattern.finditer(file_data))
        regular_season_matches = list(regular_season_pattern.finditer(file_data))
        
        # Process preseason games
        for i, match in enumerate(preseason_matches):
            week_num = int(match.group(1))
            start_pos = match.start()
            # Extract surrounding data to identify game info
            surrounding_data = file_data[start_pos-100:start_pos+100]
            
            # Look for team names near the match
            team_pattern = re.compile(b'(Chiefs|49ers|Cowboys|Patriots|Ravens|Bengals|Bears|Packers|Raiders|Steelers|Browns|Bills|Broncos|Cardinals|Chargers|Colts|Dolphins|Eagles|Falcons|Giants|Jaguars|Jets|Lions|Panthers|Rams|Saints|Seahawks|Texans|Titans|Commanders|Vikings)')
            teams = list(team_pattern.finditer(surrounding_data))
            
            if len(teams) >= 2:
                game_info = {
                    "week": week_num,
                    "game_number": i + 1,
                    "away_team": teams[0].group(1).decode('utf-8'),
                    "home_team": teams[1].group(1).decode('utf-8'),
                    "offset": hex(start_pos)
                }
                self.decoded_data["schedule"]["preseason"].append(game_info)
        
        # Process regular season games (similar approach)
        for i, match in enumerate(regular_season_matches):
            if i < len(preseason_matches):  # Skip if this is likely a preseason match
                continue
                
            week_num = int(match.group(1))
            start_pos = match.start()
            surrounding_data = file_data[start_pos-100:start_pos+100]
            
            team_pattern = re.compile(b'(Chiefs|49ers|Cowboys|Patriots|Ravens|Bengals|Bears|Packers|Raiders|Steelers|Browns|Bills|Broncos|Cardinals|Chargers|Colts|Dolphins|Eagles|Falcons|Giants|Jaguars|Jets|Lions|Panthers|Rams|Saints|Seahawks|Texans|Titans|Commanders|Vikings)')
            teams = list(team_pattern.finditer(surrounding_data))
            
            if len(teams) >= 2:
                game_info = {
                    "week": week_num,
                    "game_number": i + 1,
                    "away_team": teams[0].group(1).decode('utf-8'),
                    "home_team": teams[1].group(1).decode('utf-8'),
                    "offset": hex(start_pos)
                }
                self.decoded_data["schedule"]["regular_season"].append(game_info)
    
    def _decompress_chunks(self, file_data):
        """Find and decompress zlib chunks"""
        # Look for zlib headers: 78 9C, 78 DA, or 78 5E
        zlib_headers = [b'\x78\x9c', b'\x78\xda', b'\x78\x5e']
        
        for header in zlib_headers:
            offset = 0
            while True:
                offset = file_data.find(header, offset)
                if offset == -1:
                    break
                
                # Try to decompress from this offset
                chunk_info = {
                    "offset": hex(offset),
                    "header": binascii.hexlify(header).decode('utf-8'),
                    "decompression_successful": False
                }
                
                # Try with different chunk sizes
                for chunk_size in [50000, 100000, 500000, 1000000]:
                    try:
                        # Skip the first two bytes (header) for the decompressor
                        chunk_data = file_data[offset:offset+chunk_size]
                        decompressed_data = zlib.decompress(chunk_data)
                        
                        chunk_info["decompression_successful"] = True
                        chunk_info["decompressed_size"] = len(decompressed_data)
                        chunk_info["compression_ratio"] = len(decompressed_data) / len(chunk_data)
                        
                        # Save decompressed data
                        chunk_id = f"chunk_{offset:08x}"
                        self.decoded_data["decompressed_data"][chunk_id] = {
                            "size": len(decompressed_data),
                            "first_bytes": binascii.hexlify(decompressed_data[:32]).decode('utf-8')
                        }
                        
                        # Write decompressed data to file for further analysis
                        output_dir = "madden_extracted_data"
                        os.makedirs(output_dir, exist_ok=True)
                        with open(f"{output_dir}/decompressed_{offset:08x}.bin", 'wb') as f:
                            f.write(decompressed_data)
                        
                        break  # Successfully decompressed
                    except Exception as e:
                        # Try next chunk size
                        continue
                
                self.decoded_data["chunks"].append(chunk_info)
                offset += 1  # Move past this occurrence
    
    def _extract_player_info(self):
        """Extract player information from decompressed data"""
        # Process all decompressed chunks
        output_dir = "madden_extracted_data"
        player_pattern = re.compile(rb'([A-Z][a-z]+)\s+([A-Z][a-z]+)\s+([0-9]{2})\s+([A-Z]{2})')
        
        for filename in os.listdir(output_dir):
            if filename.startswith("decompressed_") and filename.endswith(".bin"):
                file_path = os.path.join(output_dir, filename)
                with open(file_path, 'rb') as f:
                    data = f.read()
                
                # Look for player entries
                for match in player_pattern.finditer(data):
                    first_name = match.group(1).decode('utf-8')
                    last_name = match.group(2).decode('utf-8')
                    number = match.group(3).decode('utf-8')
                    position = match.group(4).decode('utf-8')
                    
                    # Extract additional data (ratings, etc.) from nearby content
                    start_pos = max(0, match.start() - 100)
                    end_pos = min(len(data), match.end() + 300)
                    surrounding_data = data[start_pos:end_pos]
                    
                    # Look for numbers that might be ratings
                    rating_pattern = re.compile(rb'([A-Z]{3})\s+([0-9]{2})')
                    ratings = {}
                    
                    for rating_match in rating_pattern.finditer(surrounding_data):
                        rating_type = rating_match.group(1).decode('utf-8')
                        rating_value = int(rating_match.group(2).decode('utf-8'))
                        ratings[rating_type] = rating_value
                    
                    # Look for team affiliation
                    team_pattern = re.compile(rb'(Chiefs|49ers|Cowboys|Patriots|Ravens|Bengals|Bears|Packers|Raiders|Steelers|Browns|Bills|Broncos|Cardinals|Chargers|Colts|Dolphins|Eagles|Falcons|Giants|Jaguars|Jets|Lions|Panthers|Rams|Saints|Seahawks|Texans|Titans|Commanders|Vikings)')
                    team_match = team_pattern.search(surrounding_data)
                    team = team_match.group(1).decode('utf-8') if team_match else "Unknown"
                    
                    player_info = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "number": number,
                        "position": position,
                        "team": team,
                        "ratings": ratings,
                        "offset": hex(match.start())
                    }
                    
                    self.decoded_data["players"].append(player_info)
        
        # Also look for player data using common name patterns
        # Process player names extracted from strings
        for output_file in os.listdir(output_dir):
            if output_file.startswith("decompressed_") and output_file.endswith(".bin"):
                file_path = os.path.join(output_dir, output_file)
                
                # Use strings command to extract readable strings
                common_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Thomas", "Moore", "Allen", "Young", "Wright", "Hill", "Davis", "Wilson", "Jackson", "White", "Harris", "Martin"]
                first_names = ["Michael", "Christopher", "Matthew", "Joshua", "David", "James", "Daniel", "Robert", "John", "Joseph", "Justin", "Ryan", "Brandon", "Aaron", "Patrick", "Travis", "Tom"]
                
                with open(file_path, 'rb') as f:
                    data = f.read()
                    
                # Extract all readable strings
                strings_data = []
                current_string = bytearray()
                for byte in data:
                    if 32 <= byte <= 126:  # ASCII printable
                        current_string.append(byte)
                    else:
                        if len(current_string) >= 4:  # Only keep strings of reasonable length
                            strings_data.append(current_string.decode('ascii', errors='ignore'))
                        current_string = bytearray()
                
                # Look for patterns that might indicate player records
                for i, s in enumerate(strings_data):
                    if s in common_names and i > 0:
                        # Check if previous string might be a first name
                        if strings_data[i-1] in first_names:
                            first_name = strings_data[i-1]
                            last_name = s
                            
                            # Look ahead for potential position
                            position = "Unknown"
                            for j in range(i+1, min(i+10, len(strings_data))):
                                if strings_data[j] in ["QB", "HB", "FB", "WR", "TE", "LT", "LG", "C", "RG", "RT", "LE", "DT", "RE", "LOLB", "MLB", "ROLB", "CB", "FS", "SS", "K", "P"]:
                                    position = strings_data[j]
                                    break
                            
                            # Look for team
                            team = "Unknown"
                            team_names = ["Chiefs", "49ers", "Cowboys", "Patriots", "Ravens", "Bengals", "Bears", "Packers", "Raiders", "Steelers", "Browns", "Bills", "Broncos", "Cardinals", "Chargers", "Colts", "Dolphins", "Eagles", "Falcons", "Giants", "Jaguars", "Jets", "Lions", "Panthers", "Rams", "Saints", "Seahawks", "Texans", "Titans", "Commanders", "Vikings"]
                            
                            for j in range(max(0, i-10), i+10):
                                if j < len(strings_data) and strings_data[j] in team_names:
                                    team = strings_data[j]
                                    break
                            
                            # Add to player list if not a duplicate
                            player_exists = False
                            for p in self.decoded_data["players"]:
                                if p["first_name"] == first_name and p["last_name"] == last_name:
                                    player_exists = True
                                    break
                            
                            if not player_exists:
                                player_info = {
                                    "first_name": first_name,
                                    "last_name": last_name,
                                    "position": position,
                                    "team": team,
                                    "source": "string_analysis"
                                }
                                self.decoded_data["players"].append(player_info)
    
    def _extract_team_info(self):
        """Extract team information"""
        team_names = ["Chiefs", "49ers", "Cowboys", "Patriots", "Ravens", "Bengals", "Bears", "Packers", "Raiders", "Steelers", "Browns", "Bills", "Broncos", "Cardinals", "Chargers", "Colts", "Dolphins", "Eagles", "Falcons", "Giants", "Jaguars", "Jets", "Lions", "Panthers", "Rams", "Saints", "Seahawks", "Texans", "Titans", "Commanders", "Vikings"]
        
        output_dir = "madden_extracted_data"
        for filename in os.listdir(output_dir):
            if filename.startswith("decompressed_") and filename.endswith(".bin"):
                file_path = os.path.join(output_dir, filename)
                with open(file_path, 'rb') as f:
                    data = f.read()
                    
                for team_name in team_names:
                    team_pattern = re.compile(team_name.encode('utf-8'))
                    team_matches = list(team_pattern.finditer(data))
                    
                    if team_matches:
                        team_info = {
                            "name": team_name,
                            "mentions": len(team_matches),
                            "offsets": [hex(match.start()) for match in team_matches[:5]]  # First 5 occurrences
                        }
                        
                        # Look for team ratings
                        for match in team_matches:
                            start_pos = max(0, match.start() - 100)
                            end_pos = min(len(data), match.end() + 300)
                            surrounding_data = data[start_pos:end_pos]
                            
                            # Extract potential team stats/ratings
                            rating_pattern = re.compile(rb'([A-Z]{3})\s+([0-9]{2})')
                            for rating_match in rating_pattern.finditer(surrounding_data):
                                rating_type = rating_match.group(1).decode('utf-8')
                                rating_value = int(rating_match.group(2).decode('utf-8'))
                                
                                if "ratings" not in team_info:
                                    team_info["ratings"] = {}
                                    
                                if rating_type not in team_info["ratings"]:
                                    team_info["ratings"][rating_type] = rating_value
                        
                        self.decoded_data["teams"].append(team_info)
    
    def _extract_rating_clusters(self, file_data):
        """Extract rating clusters (groups of ratings)"""
        # Look for patterns of consecutive numbers that might be ratings
        rating_pattern = re.compile(b'([4-9][0-9]){5,}')  # Look for 5+ consecutive 2-digit numbers between 40-99
        
        for match in rating_pattern.finditer(file_data):
            start_pos = match.start()
            raw_data = match.group(0)
            
            # Try to parse these as ratings
            ratings = []
            for i in range(0, len(raw_data), 2):
                if i+1 < len(raw_data):
                    rating = int(raw_data[i:i+2])
                    if 40 <= rating <= 99:  # Valid rating range
                        ratings.append(rating)
            
            if len(ratings) >= 5:  # Only include if we have enough ratings
                cluster_id = f"cluster_{start_pos:x}"
                self.decoded_data["rating_clusters"][cluster_id] = {
                    "offset": hex(start_pos),
                    "ratings": ratings
                }
    
    def _extract_common_strings(self, file_data):
        """Extract common strings from the file"""
        common_keywords = [
            "Draft", "Player", "Team", "Roster", "Schedule", "Trade", "Contract", 
            "Stat", "Rating", "Owner", "Coach", "Week", "Preseason", "Season", 
            "Playoff", "Super Bowl", "Game", "League", "Franchise", "Cap", "Salary"
        ]
        
        for keyword in common_keywords:
            pattern = re.compile(keyword.encode('utf-8') + b'[A-Za-z_]+')
            matches = list(pattern.finditer(file_data))
            
            if matches:
                self.decoded_data["common_strings"][keyword] = [
                    match.group(0).decode('utf-8', errors='ignore') 
                    for match in matches
                ]
    
    def save_to_json(self, output_file):
        """Save the decoded data to a JSON file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.decoded_data, f, indent=2)
        
        print(f"Decoded data saved to {output_file}")
        
        # Print summary
        print("\nSummary of findings:")
        print(f"File type: {self.decoded_data.get('header', {}).get('signature', 'Unknown')}")
        print(f"Game version: {self.decoded_data.get('header', {}).get('game_version', 'Unknown')}")
        print(f"Schedule: {len(self.decoded_data['schedule']['preseason'])} preseason games, {len(self.decoded_data['schedule']['regular_season'])} regular season games")
        print(f"Teams found: {len(self.decoded_data['teams'])}")
        print(f"Players found: {len(self.decoded_data['players'])}")
        
        # Show sample of player names
        if self.decoded_data['players']:
            print("\nSample players found:")
            for player in self.decoded_data['players'][:5]:
                print(f"  - {player.get('first_name', '')} {player.get('last_name', '')} ({player.get('position', 'Unknown')}, {player.get('team', 'Unknown')})")
        
        # Show decompressed chunks info
        successful_chunks = sum(1 for chunk in self.decoded_data["chunks"] if chunk["decompression_successful"])
        print(f"\nDecompressed chunks: {successful_chunks} out of {len(self.decoded_data['chunks'])}")
        
        print("\nCheck the output JSON file for complete details.")

if __name__ == "__main__":
    # Specify the path to your Madden franchise file
    franchise_file = "resources/CAREER-2017BETA"
    
    # Create output directory if it doesn't exist
    os.makedirs("madden_extracted_data", exist_ok=True)
    
    # Decode the franchise file
    decoder = MaddenFranchiseDecoder(franchise_file)
    decoded_data = decoder.decode()
    
    # Save to JSON
    output_file = "advanced_franchise_decoded.json"
    decoder.save_to_json(output_file) 