#!/usr/bin/env python3
"""
Madden Franchise File Analyzer Launcher

This script provides a command-line interface to run any of the available
madden franchise file analysis tools.
"""

import os
import sys
import argparse
import importlib.util
import glob

# List of available tools
TOOLS = {
    'extract': 'madden_tools/extract_madden_data.py',
    'extract-players': 'madden_tools/extract_madden_players.py',
    'extract-zlib': 'madden_tools/extract_zlib.py',
    'decode': 'madden_tools/decode_madden_json.py',
    'decode-improved': 'madden_tools/decode_madden_improved.py',
    'advanced-decode': 'madden_tools/advanced_franchise_decoder.py',
    'advanced-zlib': 'madden_tools/advanced_zlib_extractor.py',
}

def list_tools():
    """List all available tools with descriptions."""
    print("\nAvailable tools:")
    print("-" * 80)
    descriptions = {
        'extract': 'Basic extractor for Madden franchise files',
        'extract-players': 'Extract player data from franchise files',
        'extract-zlib': 'Extract zlib-compressed data chunks',
        'decode': 'Decode franchise binary data to JSON',
        'decode-improved': 'Enhanced decoder with better player extraction',
        'advanced-decode': 'Comprehensive franchise decoder',
        'advanced-zlib': 'Advanced zlib chunk extraction and analysis'
    }
    
    for name, path in TOOLS.items():
        print(f"{name:20} - {descriptions.get(name, 'No description available')}")
        print(f"{' ':20}   Path: {path}")
    print("-" * 80)

def list_franchise_files():
    """List available franchise files in the resources directory."""
    files = glob.glob("resources/CAREER*")
    if not files:
        print("No franchise files found in the resources directory.")
        return
    
    print("\nAvailable franchise files:")
    print("-" * 80)
    for i, file in enumerate(files):
        size = os.path.getsize(file)
        size_str = f"{size:,} bytes"
        print(f"{i+1}. {os.path.basename(file):30} ({size_str})")
    print("-" * 80)

def run_tool(tool_name, args):
    """Run the specified tool with given arguments."""
    if tool_name not in TOOLS:
        print(f"Error: Unknown tool '{tool_name}'")
        list_tools()
        return 1
    
    tool_path = TOOLS[tool_name]
    if not os.path.exists(tool_path):
        print(f"Error: Tool script not found at {tool_path}")
        return 1
    
    # Import the tool module
    spec = importlib.util.spec_from_file_location("tool_module", tool_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Most tools have a main function or direct execution
    print(f"Running {tool_name} from {tool_path}...")
    
    # Modify sys.argv to pass arguments to the imported module
    original_argv = sys.argv.copy()
    sys.argv = [tool_path] + args
    
    # Execute the module's main block
    if hasattr(module, 'main'):
        module.main()
    else:
        # The tool might be designed to run when imported
        print("Tool executed via import (no explicit main function found)")
    
    # Restore original argv
    sys.argv = original_argv
    
    print(f"\nTool {tool_name} completed")
    return 0

def main():
    """Main entry point for the launcher."""
    parser = argparse.ArgumentParser(description="Madden Franchise File Analyzer")
    parser.add_argument('tool', nargs='?', help='Tool to run')
    parser.add_argument('tool_args', nargs=argparse.REMAINDER, help='Arguments to pass to the tool')
    parser.add_argument('--list', '-l', action='store_true', help='List available tools')
    parser.add_argument('--files', '-f', action='store_true', help='List available franchise files')
    
    args = parser.parse_args()
    
    if args.list:
        list_tools()
        return 0
    
    if args.files:
        list_franchise_files()
        return 0
    
    if not args.tool:
        parser.print_help()
        list_tools()
        list_franchise_files()
        return 0
    
    return run_tool(args.tool, args.tool_args)

if __name__ == "__main__":
    sys.exit(main()) 