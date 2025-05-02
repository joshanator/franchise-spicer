# Madden Franchise Event Generator

[![Tests](https://github.com/joshanator/franchise-spicer/actions/workflows/tests.yml/badge.svg)](https://github.com/joshanator/franchise-spicer/actions/workflows/tests.yml)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/joshanator/franchise-spicer/releases)
[![Unique Scenarios](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/joshanator/d5a0161486a7d8a2f2d63fe591cedb75/raw/scenario_count.json)](https://github.com/joshanator/franchise-spicer)
[![License](https://img.shields.io/badge/license-CC--BY--NC--4.0-green.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Python](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/)

A Python application that generates random events for Madden franchise mode to make gameplay more dynamic and unpredictable.

## Features

- Events impact players, coaches, and team circumstances
- Adjustable difficulty levels to control event severity
- Save and load franchise configurations
- Track event history over multiple seasons
- Manage your roster for accurate player references
- Create and manage custom events
- Cross-platform support (Windows, macOS, Linux)

## Requirements

- Python 3.6+
- PySide6 (Qt for Python)
- appdirs (Cross-platform directory handling)

## Installation Options

### Option 1: Run with Python

1. Clone or download this repository
2. Navigate to the project directory

```bash
cd franchise-spicer
```

3. Run the application using the launcher script:

```bash
python3 run_madden_events.py
```

This will automatically install PySide6 and appdirs if needed and launch the application.

### Option 2: Standalone Executable

For users who prefer not to install Python, we provide standalone executable options:

1. Download the latest release for your platform from the [Releases](https://github.com/joshanator/franchise-spicer/releases) page
2. Extract the ZIP archive to any location
3. Run the application:
   - Windows: Open the extracted folder and double-click the `.exe` file
   - macOS: Double-click the extracted `.app` file (right-click and select "Open" if you get a security warning)
   - Linux: Navigate to the extracted folder and run the executable (`chmod +x` first if needed)

The application is fully portable - you can copy the extracted folder to any location, including a USB drive, and it will run properly. Your save files will always be stored in your user data directory (see [Save File Location](#save-file-location) section).

### Option 3: Build Your Own Executable

If you want to build your own executable:

1. Make sure Python and pip are installed
2. Install PyInstaller (if you don't have it already):

```bash
python3 -m pip install PyInstaller appdirs
```

3. Run the build script:

```bash
python3 build_executable.py
```

4. The executable will be created in the `builds/{version}/{platform}/` directory
5. A ZIP archive will also be created for easy distribution

The build script creates executables for all platforms, generating build instructions for platforms other than your current one. To create a complete distribution, run the script on Windows, macOS, and Linux systems.

#### Notes for macOS Users:
- You may need to give the app permission to run by right-clicking and selecting "Open"
- If you encounter issues with the build script, you can run PyInstaller directly:
  ```bash
  python3 -m PyInstaller --name "Madden Franchise Generator" --windowed --onefile run_madden_events.py
  ```

## How to Use

1. Create a new franchise or load an existing one
2. Set your current week and year to match your Madden franchise
3. Go to the Events tab and click "Roll for Event" to generate random events
4. Review the event details and its impact on your franchise
5. Implement the changes in your Madden game as indicated
6. Update your roster in the Roster tab to keep it synchronized with your game
7. View your event history in the History tab
8. Create custom events in the Custom Events tab

## Event Difficulty

The difficulty setting affects the types of events that can occur:

- **Easy**: More positive events, less negative
- **Medium**: Balanced mix of events
- **Hard**: More challenges and negative events

## Example Events

- Early retirement of players
- Draft pick penalties
- Player holdouts
- Conditioning issues
- Suspensions
- Player callouts and challenges
- Season-long performance challenges
- Contract negotiations
- Team chemistry situations
- Staff and coaching changes
- Unrealistic events (optional)

## Madden Franchise File Analysis Tools

This project includes a collection of tools for analyzing, decoding, and extracting data from Madden franchise save files. These tools are organized in the `madden_tools/` directory and can be run using the `decode_franchise.py` launcher script.

### Available Tools

- **Basic Extractors**: Tools for extracting general data and player information
- **Decoders**: Convert binary franchise files to JSON format for analysis
- **Advanced Tools**: Comprehensive decoders and specialized zlib extractors

### Using the Analysis Tools

To see all available tools:

```bash
python decode_franchise.py --list
```

To list available franchise files:

```bash
python decode_franchise.py --files
```

To run a specific tool:

```bash
python decode_franchise.py decode-improved
```

For more information about these tools, see the [madden_tools/README.md](madden_tools/README.md) file.

## Save File Location

The application stores save files and configuration data in the following locations:

- **When running from source code**: Files are stored in the `madden_franchise_qt/data` and `madden_franchise_qt/saves` directories within the project folder.

- **When running as an executable**:
  - **Windows**: `C:\Users\{username}\AppData\Local\MaddenTools\MaddenFranchiseGenerator`
  - **macOS**: `/Users/{username}/Library/Application Support/MaddenTools/MaddenFranchiseGenerator`
  - **Linux**: `~/.local/share/MaddenTools/MaddenFranchiseGenerator`

## Adding Custom Events

You can add, edit, and manage custom events directly within the application using the Custom Events tab. This provides a user-friendly interface for creating and organizing your own events.

For more advanced users, you can also manually modify the `events.json` file in the data directory.

## Cross-Platform Support

This application is built with PySide6 (Qt for Python) to ensure compatibility with:
- macOS
- Windows
- Linux

## Build Status

[![Tests](https://github.com/joshanator/franchise-spicer/actions/workflows/tests.yml/badge.svg)](https://github.com/joshanator/franchise-spicer/actions/workflows/tests.yml)

The project uses GitHub Actions for continuous integration testing. The test workflow:
- Runs on both Python 3.9 and 3.10
- Tests all regular events
- Tests unrealistic events (if present)
- Verifies combined event pools
- Validates the event schema

For more details on the testing framework, see [./README_TESTS.md](./README_TESTS.md).

## Version History

- **v0.1** - Initial release with complete event system and UI
- **v1.0** - Added custom events editor, unrealistic events, improved UI, and expanded event pools

## License

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International License** (CC BY-NC 4.0).

### What this means:

- ✅ **You are free to**:
  - **Share** — copy and redistribute the material in any medium or format
  - **Adapt** — remix, transform, and build upon the material

- ❌ **Under the following terms**:
  - **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made
  - **NonCommercial** — You may not use the material for commercial purposes
  - **No additional restrictions** — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits

The full license text can be found at: [Creative Commons BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/legalcode)

### In simple terms:

You can freely use, modify, and share this code for non-commercial purposes as long as you give credit to the original project. However, you cannot sell this software or use it in any commercial product or service without explicit permission.

## Project Testing

For information about the test suite and how to run tests, see [./README_TESTS.md](./README_TESTS.md).

## Acknowledgments

This tool is designed for use with EA's Madden NFL game but is not affiliated with or endorsed by EA Sports or the NFL.