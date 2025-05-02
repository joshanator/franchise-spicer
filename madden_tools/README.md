# Madden Franchise File Tools

These are all in progress, I vibe coded them so I wouldnt use them for anything yet

This directory contains various tools for decoding, analyzing, and extracting data from Madden franchise save files.

## Tool Overview

### Basic Extractors

- **extract_madden_data.py**: Extracts basic data from Madden franchise files.
- **extract_madden_players.py**: Specifically targets player data extraction from franchise files.
- **extract_zlib.py**: Focused tool for extracting zlib-compressed data chunks with multiple decompression strategies.

### Decoders

- **decode_madden_json.py**: Converts Madden franchise binary data into JSON format.
- **decode_madden_improved.py**: Enhanced version with better player extraction and improved decompression.

### Advanced Tools

- **advanced_franchise_decoder.py**: Comprehensive decoder that extracts schedule data, teams, player info, and other franchise elements.
- **advanced_zlib_extractor.py**: Specialized tool for extracting and analyzing zlib chunks using multiple approaches.

## Usage

Most scripts can be run with the franchise file as an argument:

```bash
python madden_tools/decode_madden_improved.py
```

By default, the scripts look for franchise files in the `resources/` directory and typically output results to their respective directories (e.g., `madden_extracted_data/`, `zlib_extracted_chunks/`).

## Output Files

The tools produce various output files:

- **JSON files**: Decoded franchise data (`*_decoded.json`, `*_improved.json`)
- **Binary files**: Extracted raw and decompressed chunks (`.bin` files)
- **Analysis results**: Extraction statistics, common strings, and data patterns

All output directories and files are ignored in git through the `.gitignore` configuration. 