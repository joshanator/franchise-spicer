import os
import zlib
import struct
import binascii
import json
from io import BytesIO

class ZlibChunkExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.chunks = []
        self.decompressed_chunks = []
        
    def extract_chunks(self):
        """Extract and decompress zlib chunks"""
        # Read the entire file
        with open(self.file_path, 'rb') as f:
            file_data = f.read()
            
        file_size = len(file_data)
        print(f"File size: {file_size} bytes")
        
        # Check for FBCHUNKS header
        is_fbchunks = False
        if file_data[:8] == b'FBCHUNKS':
            print("Found FBCHUNKS header")
            is_fbchunks = True
            version = struct.unpack(">I", file_data[8:12])[0]
            print(f"Version: {version}")
            
            # Extract the game version
            game_version_offset = struct.unpack(">I", file_data[12:16])[0]
            if game_version_offset > 0 and game_version_offset < file_size:
                # Find null-terminated string
                end_offset = file_data.find(b'\x00', game_version_offset)
                if end_offset > game_version_offset:
                    game_version = file_data[game_version_offset:end_offset].decode('utf-8', errors='ignore')
                    print(f"Game version: {game_version}")
        
        # Find all potential zlib headers
        zlib_headers = [b'\x78\x9c', b'\x78\xda', b'\x78\x5e']
        chunks_found = 0
        
        # Create output directory
        output_dir = "zlib_extracted_chunks"
        os.makedirs(output_dir, exist_ok=True)
        
        for header in zlib_headers:
            offset = 0
            while True:
                offset = file_data.find(header, offset)
                if offset == -1:
                    break
                
                # Record this chunk
                chunk_info = {
                    "offset": offset,
                    "offset_hex": hex(offset),
                    "header": binascii.hexlify(header).decode('utf-8'),
                    "decompressed": False,
                    "size": 0
                }
                self.chunks.append(chunk_info)
                
                # Save the raw chunk for reference
                raw_chunk_file = f"{output_dir}/raw_chunk_{offset:08x}.bin"
                with open(raw_chunk_file, 'wb') as f:
                    f.write(file_data[offset:offset+100])  # Just the first 100 bytes
                
                # Move to next potential chunk
                offset += 1
                chunks_found += 1
        
        print(f"Found {chunks_found} potential zlib chunks")
        
        # Now try different strategies to decompress them
        successful_chunks = 0
        
        # Strategy 1: Try to decompress directly with wbits
        for i, chunk in enumerate(self.chunks):
            offset = chunk["offset"]
            print(f"Attempting decompression of chunk at offset {hex(offset)} ({i+1}/{len(self.chunks)})")
            
            # Try with different window bits
            for wbits in [15, 31, 47, -15]:
                try:
                    # Try to determine chunk end (looking for 10-20MB of data)
                    # This is a heuristic, might need adjustment
                    max_chunk_size = min(file_size - offset, 10 * 1024 * 1024)
                    chunk_data = file_data[offset:offset+max_chunk_size]
                    
                    # Initialize a decompression object
                    decompressor = zlib.decompressobj(wbits)
                    decompressed_data = decompressor.decompress(chunk_data)
                    
                    # If we get here, decompression succeeded
                    chunk["decompressed"] = True
                    chunk["size"] = len(decompressed_data)
                    chunk["method"] = f"direct_wbits_{wbits}"
                    
                    # Save the decompressed data
                    output_file = f"{output_dir}/decompressed_{offset:08x}.bin"
                    with open(output_file, 'wb') as f:
                        f.write(decompressed_data)
                    
                    print(f"  Success! Decompressed {len(decompressed_data):,} bytes")
                    self.decompressed_chunks.append({
                        "offset": offset,
                        "size": len(decompressed_data),
                        "output_file": output_file
                    })
                    
                    successful_chunks += 1
                    break  # Success, move to next chunk
                except Exception as e:
                    # Try next method
                    pass
            
            # If direct decompression failed, try the sliding window approach
            if not chunk["decompressed"]:
                try:
                    # Create a sliding window to find valid compressed data
                    max_window = min(file_size - offset, 5 * 1024 * 1024)  # 5MB max window
                    
                    # Start with a small window and increase
                    for window_size in [1024, 4096, 16384, 65536, 262144, 1048576]:
                        if offset + window_size > file_size:
                            break
                            
                        chunk_data = file_data[offset:offset+window_size]
                        try:
                            # Try to decompress with a sliding window
                            decompressor = zlib.decompressobj(15)  # Standard 15-bit window
                            decompressed_data = decompressor.decompress(chunk_data)
                            
                            # If we get here, found a valid zlib stream
                            if len(decompressed_data) > 1000:  # Only consider if decompressed data is substantial
                                chunk["decompressed"] = True
                                chunk["size"] = len(decompressed_data)
                                chunk["method"] = f"sliding_window_{window_size}"
                                
                                # Save the decompressed data
                                output_file = f"{output_dir}/decompressed_{offset:08x}_sliding.bin"
                                with open(output_file, 'wb') as f:
                                    f.write(decompressed_data)
                                
                                print(f"  Success (sliding window)! Decompressed {len(decompressed_data):,} bytes")
                                self.decompressed_chunks.append({
                                    "offset": offset,
                                    "size": len(decompressed_data),
                                    "output_file": output_file
                                })
                                
                                successful_chunks += 1
                                break  # Success, move to next chunk
                        except Exception as e:
                            # Try next window size
                            continue
                except Exception as e:
                    # Skip this chunk if it all fails
                    pass
        
        print(f"\nSuccessfully decompressed {successful_chunks} out of {chunks_found} chunks")
        
        # Strategy 3: Try custom size headers
        # This approach looks for possible size values that might precede zlib headers
        # Many formats store the decompressed size before the compressed data
        if successful_chunks == 0:
            print("\nTrying alternative size header approach...")
            
            for i, chunk in enumerate(self.chunks[:10]):  # Try just the first few
                offset = chunk["offset"]
                
                # Try looking for size headers before the zlib header
                for size_offset in range(offset-8, offset):
                    if size_offset >= 0:
                        try:
                            # Try different size formats (4-byte and 8-byte integers)
                            for fmt in [">I", ">Q", "<I", "<Q"]:
                                size_bytes = file_data[size_offset:size_offset+struct.calcsize(fmt)]
                                if len(size_bytes) == struct.calcsize(fmt):
                                    try:
                                        decompressed_size = struct.unpack(fmt, size_bytes)[0]
                                        if 100000 <= decompressed_size <= 50 * 1024 * 1024:  # Reasonable size range (100KB to 50MB)
                                            # Size seems reasonable, try to decompress
                                            try:
                                                # Determine a reasonable compressed size (compressed data is usually smaller)
                                                max_compressed_size = min(file_size - offset, decompressed_size // 2)
                                                
                                                chunk_data = file_data[offset:offset+max_compressed_size]
                                                decompressed_data = zlib.decompress(chunk_data)
                                                
                                                # If successful and close to expected size
                                                if abs(len(decompressed_data) - decompressed_size) / decompressed_size < 0.1:  # Within 10%
                                                    chunk["decompressed"] = True
                                                    chunk["size"] = len(decompressed_data)
                                                    chunk["method"] = f"size_header_{fmt}"
                                                    
                                                    # Save the decompressed data
                                                    output_file = f"{output_dir}/decompressed_{offset:08x}_sized.bin"
                                                    with open(output_file, 'wb') as f:
                                                        f.write(decompressed_data)
                                                    
                                                    print(f"  Success (size header)! Decompressed {len(decompressed_data):,} bytes")
                                                    self.decompressed_chunks.append({
                                                        "offset": offset,
                                                        "size": len(decompressed_data),
                                                        "output_file": output_file
                                                    })
                                                    
                                                    successful_chunks += 1
                                                    break  # Success
                                            except Exception:
                                                # Try next size
                                                pass
                                    except Exception:
                                        # Try next size format
                                        pass
                        except Exception:
                            # Continue with next offset
                            pass
        
        # Strategy 4: Try for specific EA Sports zlib format
        # EA sports games often use a custom compression format that includes:
        # - 4 byte header
        # - 4 byte decompressed size
        # - zlib compressed data
        if successful_chunks == 0:
            print("\nTrying EA Sports specific format...")
            
            for i, chunk in enumerate(self.chunks[:10]):  # Try just the first few
                offset = chunk["offset"]
                
                # Look for possible EA header (preceding the zlib header)
                for header_offset in range(max(0, offset-16), offset):
                    # Check for 'FrTk' or similar header
                    possible_headers = [b'FrTk', b'EASF', b'EAHd']
                    for ea_header in possible_headers:
                        header_pos = file_data.find(ea_header, header_offset, offset)
                        if header_pos != -1 and header_pos + 8 <= offset:
                            try:
                                # Try to read size value (4 bytes after header)
                                size_pos = header_pos + 4
                                size_bytes = file_data[size_pos:size_pos+4]
                                decompressed_size = struct.unpack(">I", size_bytes)[0]
                                
                                if 100000 <= decompressed_size <= 50 * 1024 * 1024:  # Reasonable size
                                    # Try decompression with this offset
                                    try:
                                        # Use the size to determine how much to read
                                        max_compressed_size = min(file_size - offset, decompressed_size)
                                        
                                        chunk_data = file_data[offset:offset+max_compressed_size]
                                        decompressed_data = zlib.decompress(chunk_data)
                                        
                                        # If successful and close to expected size
                                        if abs(len(decompressed_data) - decompressed_size) / decompressed_size < 0.1:  # Within 10%
                                            chunk["decompressed"] = True
                                            chunk["size"] = len(decompressed_data)
                                            chunk["method"] = f"ea_header"
                                            
                                            # Save the decompressed data
                                            output_file = f"{output_dir}/decompressed_{offset:08x}_ea.bin"
                                            with open(output_file, 'wb') as f:
                                                f.write(decompressed_data)
                                            
                                            print(f"  Success (EA header)! Decompressed {len(decompressed_data):,} bytes")
                                            self.decompressed_chunks.append({
                                                "offset": offset,
                                                "size": len(decompressed_data),
                                                "output_file": output_file
                                            })
                                            
                                            successful_chunks += 1
                                            break  # Success
                                    except Exception:
                                        # Try next
                                        pass
                            except Exception:
                                # Try next header
                                pass
        
        # Special handling for FBCHUNKS format
        if is_fbchunks and successful_chunks == 0:
            print("\nTrying FBCHUNKS specific format...")
            
            # In FBCHUNKS, often there's a table of offsets pointing to compressed data
            # Try to find such table
            
            # First, check if we have a sequence of increasing offset values stored as 4-byte integers
            for base_offset in range(0, min(file_size-100, 1000), 4):  # Check first 1000 bytes, stepping by 4
                try:
                    # Check if we have a sequence of at least 4 increasing offsets
                    values = []
                    for i in range(5):  # Check 5 consecutive values
                        if base_offset + i*4 + 4 <= file_size:
                            value = struct.unpack(">I", file_data[base_offset+i*4:base_offset+i*4+4])[0]
                            values.append(value)
                    
                    # Check if these are increasing offsets within file
                    if all(0 < values[i] < file_size and values[i] < values[i+1] for i in range(len(values)-1)):
                        print(f"Found potential offset table at {hex(base_offset)}: {[hex(v) for v in values]}")
                        
                        # Try these offsets as potential compression locations
                        for offset_value in values:
                            # Check if there's a zlib header at or near this offset
                            for check_offset in range(max(0, offset_value-16), min(file_size, offset_value+16)):
                                # Check for zlib headers
                                for header in zlib_headers:
                                    if check_offset + len(header) <= file_size and file_data[check_offset:check_offset+len(header)] == header:
                                        print(f"  Found zlib header at {hex(check_offset)}, trying decompression...")
                                        
                                        try:
                                            # Attempt decompression (try both wbits)
                                            max_size = min(file_size - check_offset, 10 * 1024 * 1024)
                                            chunk_data = file_data[check_offset:check_offset+max_size]
                                            
                                            for wbits in [15, 31, 47, -15]:
                                                try:
                                                    decompressor = zlib.decompressobj(wbits)
                                                    decompressed_data = decompressor.decompress(chunk_data)
                                                    
                                                    if len(decompressed_data) > 1000:  # Only consider if substantial
                                                        # Save the decompressed data
                                                        output_file = f"{output_dir}/decompressed_{check_offset:08x}_table.bin"
                                                        with open(output_file, 'wb') as f:
                                                            f.write(decompressed_data)
                                                        
                                                        print(f"    Success! Decompressed {len(decompressed_data):,} bytes")
                                                        self.decompressed_chunks.append({
                                                            "offset": check_offset,
                                                            "size": len(decompressed_data),
                                                            "output_file": output_file
                                                        })
                                                        
                                                        successful_chunks += 1
                                                        break  # Success
                                                except Exception:
                                                    # Try next wbits
                                                    continue
                                        except Exception:
                                            # Continue to next offset
                                            pass
                except Exception:
                    # Try next base offset
                    continue
        
        print(f"\nFinal result: Successfully decompressed {successful_chunks} out of {chunks_found} chunks")
        
        # Save results to JSON
        results = {
            "file_path": self.file_path,
            "file_size": file_size,
            "is_fbchunks": is_fbchunks,
            "chunks_found": chunks_found,
            "chunks_decompressed": successful_chunks,
            "chunks": self.chunks,
            "decompressed_chunks": self.decompressed_chunks
        }
        
        with open(f"{output_dir}/extraction_results.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to {output_dir}/extraction_results.json")
        return results

def analyze_decompressed_data(output_dir):
    """Analyze the decompressed data for common patterns"""
    decompressed_files = [f for f in os.listdir(output_dir) if f.startswith("decompressed_")]
    print(f"Analyzing {len(decompressed_files)} decompressed files")
    
    for filename in decompressed_files:
        file_path = os.path.join(output_dir, filename)
        file_size = os.path.getsize(file_path)
        print(f"\nAnalyzing {filename} ({file_size:,} bytes)")
        
        # Skip very small files
        if file_size < 1000:
            print("  File too small, skipping")
            continue
        
        # Look for header signature
        with open(file_path, 'rb') as f:
            data = f.read(16)  # Read first 16 bytes
            header_hex = binascii.hexlify(data).decode('utf-8')
            print(f"  Header: {header_hex}")
        
        # Extract strings to look for patterns
        try:
            os.system(f"strings {file_path} | head -20 > {output_dir}/{filename}_strings.txt")
            print(f"  Top strings saved to {output_dir}/{filename}_strings.txt")
            
            # Check for player names
            os.system(f"strings {file_path} | grep -E '[A-Z][a-z]+ [A-Z][a-z]+' | head -10 > {output_dir}/{filename}_names.txt")
            
            # Check for team names
            team_check = "strings " + file_path + " | grep -E 'Chiefs|49ers|Cowboys|Patriots|Ravens|Bengals|Bears|Packers|Raiders|Steelers|Browns|Bills|Broncos|Cardinals|Chargers|Colts|Dolphins|Eagles|Falcons|Giants|Jaguars|Jets|Lions|Panthers|Rams|Saints|Seahawks|Texans|Titans|Commanders|Vikings' | head -10 > " + output_dir + "/" + filename + "_teams.txt"
            os.system(team_check)
            
            # Check for positional data
            os.system(f"strings {file_path} | grep -E 'QB|RB|WR|TE|OL|DL|LB|CB|S|K|P' | head -10 > {output_dir}/{filename}_positions.txt")
        except Exception as e:
            print(f"  Error extracting strings: {e}")

if __name__ == "__main__":
    franchise_file = "resources/CAREER-2017BETA"
    
    extractor = ZlibChunkExtractor(franchise_file)
    results = extractor.extract_chunks()
    
    # Analyze the decompressed data
    analyze_decompressed_data("zlib_extracted_chunks") 