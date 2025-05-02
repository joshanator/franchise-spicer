#!/usr/bin/env python3
import os
import zlib
import binascii
import struct
import re
from io import BytesIO

def extract_zlib_chunk(input_file, output_dir):
    """
    Attempt to extract zlib compressed data from a binary file.
    
    This function uses multiple strategies to identify and extract zlib compressed data.
    
    Args:
        input_file: Path to the input file
        output_dir: Directory to save extracted chunks
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the input file
    with open(input_file, 'rb') as f:
        data = f.read()
    
    print(f"Input file size: {len(data)} bytes")
    
    # Strategy 1: Look for zlib headers (78 9C, 78 DA, 78 5E)
    zlib_headers = [b'x\x9c', b'x\xda', b'x^']
    
    found_chunks = []
    
    # Check for FBCHUNKS header
    if data[:8] == b'FBCHUNKS':
        print("File has FBCHUNKS header")
        
        # Extract header info
        version = struct.unpack('<I', data[8:12])[0]
        print(f"Version: {version}")
        
        # Look for the first zlib header after the FBCHUNKS header
        for header in zlib_headers:
            # Starting from byte 0x50 which is after header
            pos = data.find(header, 0x50)
            if pos != -1:
                print(f"Found zlib header at offset 0x{pos:x}")
                
                # This appears to be a special format - try to extract the entire chunk
                # Instead of using standard zlib decompression, we'll try to recreate the
                # structure based on what we know about Madden files
                
                # In this case, we'll try a few different approaches:
                
                # Method 1: Try to extract a large chunk from this position
                try:
                    # Extract a large chunk and see if it's valid zlib data
                    # We'll try different sizes, starting with 1MB
                    for size in [1024*1024, 2*1024*1024, 4*1024*1024, 8*1024*1024]:
                        if pos + size > len(data):
                            size = len(data) - pos
                        
                        chunk_data = data[pos:pos+size]
                        
                        # First, write the raw chunk to examine
                        raw_output = os.path.join(output_dir, f"raw_chunk_{pos:08x}.bin")
                        with open(raw_output, 'wb') as f:
                            f.write(chunk_data)
                        print(f"Saved raw chunk to {raw_output} ({len(chunk_data)} bytes)")
                        
                        # Try direct zlib decompression
                        try:
                            decompressed = zlib.decompress(chunk_data)
                            output_file = os.path.join(output_dir, f"decompressed_{pos:08x}.bin")
                            with open(output_file, 'wb') as f:
                                f.write(decompressed)
                            print(f"Successfully decompressed chunk (Direct method) to {output_file} ({len(decompressed)} bytes)")
                            found_chunks.append({
                                'offset': hex(pos),
                                'method': 'direct',
                                'decompressed_size': len(decompressed),
                                'output_file': output_file
                            })
                            break
                        except zlib.error as e:
                            print(f"Direct decompression failed: {e}")
                        
                        # Method 2: Try to scan through the chunk to find valid zlib streams
                        # This method looks for potential zlib headers within the chunk
                        sub_pos = 0
                        while sub_pos < len(chunk_data) - 2:
                            for sub_header in zlib_headers:
                                if chunk_data[sub_pos:sub_pos+2] == sub_header:
                                    # Found potential zlib header, try to decompress
                                    for sub_size in [1000, 5000, 10000, 50000, 100000]:
                                        if sub_pos + sub_size > len(chunk_data):
                                            sub_size = len(chunk_data) - sub_pos
                                        
                                        try:
                                            sub_chunk = chunk_data[sub_pos:sub_pos+sub_size]
                                            decompressed = zlib.decompress(sub_chunk)
                                            
                                            # Success! Save the decompressed data
                                            output_file = os.path.join(output_dir, f"decompressed_{pos:08x}_{sub_pos:08x}.bin")
                                            with open(output_file, 'wb') as f:
                                                f.write(decompressed)
                                            
                                            print(f"Successfully decompressed sub-chunk at offset 0x{pos+sub_pos:x} "
                                                  f"(Sub-scan method) to {output_file} ({len(decompressed)} bytes)")
                                            
                                            found_chunks.append({
                                                'offset': hex(pos+sub_pos),
                                                'method': 'sub-scan',
                                                'decompressed_size': len(decompressed),
                                                'output_file': output_file
                                            })
                                            
                                            # Skip ahead past this chunk
                                            sub_pos += sub_size
                                            break
                                        except zlib.error:
                                            continue
                            sub_pos += 1
                        
                        # Method 3: Try to use sliding window decompression
                        # This method tries to decompress data using a sliding window approach
                        window_size = 1024  # 1KB window
                        window_pos = 0
                        
                        while window_pos < len(chunk_data) - window_size:
                            try:
                                window_data = chunk_data[window_pos:window_pos+window_size]
                                decompressed = zlib.decompress(window_data)
                                
                                # Success! Save the decompressed data
                                output_file = os.path.join(output_dir, f"decompressed_{pos:08x}_win_{window_pos:08x}.bin")
                                with open(output_file, 'wb') as f:
                                    f.write(decompressed)
                                
                                print(f"Successfully decompressed window at offset 0x{pos+window_pos:x} "
                                      f"(Window method) to {output_file} ({len(decompressed)} bytes)")
                                
                                found_chunks.append({
                                    'offset': hex(pos+window_pos),
                                    'method': 'window',
                                    'decompressed_size': len(decompressed),
                                    'output_file': output_file
                                })
                                
                                # Skip ahead past this window
                                window_pos += window_size
                            except zlib.error:
                                window_pos += 1  # Slide the window by 1 byte
                except Exception as e:
                    print(f"Error processing main chunk: {e}")
                
                break
    
    print("\nExtraction Results:")
    print(f"Found {len(found_chunks)} decompressed chunks")
    
    for i, chunk in enumerate(found_chunks):
        print(f"Chunk {i+1}:")
        print(f"  Offset: {chunk['offset']}")
        print(f"  Method: {chunk['method']}")
        print(f"  Size: {chunk['decompressed_size']} bytes")
        print(f"  Output: {chunk['output_file']}")
        
        # Try to identify player data in the decompressed chunk
        try:
            with open(chunk['output_file'], 'rb') as f:
                chunk_data = f.read()
            
            # Look for player names (capital letter followed by lowercase, then space, then capital followed by lowercase)
            name_pattern = re.compile(b'[A-Z][a-z]{2,10}\\s+[A-Z][a-z]{2,15}')
            matches = name_pattern.finditer(chunk_data)
            
            names_found = []
            for match in matches:
                name = match.group(0).decode('utf-8', errors='ignore')
                names_found.append(name)
            
            if names_found:
                print(f"  Found {len(names_found)} potential player names:")
                for j, name in enumerate(names_found[:5]):  # Show first 5
                    print(f"    - {name}")
                if len(names_found) > 5:
                    print(f"    - ... and {len(names_found)-5} more")
        except Exception as e:
            print(f"  Error analyzing chunk: {e}")
    
    return found_chunks

if __name__ == "__main__":
    input_file = "resources/CAREER-2017BETA"
    output_dir = "madden_extracted_zlib"
    
    print(f"Attempting to extract zlib data from {input_file}...")
    chunks = extract_zlib_chunk(input_file, output_dir)
    print(f"\nExtraction complete. Check {output_dir} directory for output files.") 