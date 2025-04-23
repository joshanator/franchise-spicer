# Madden Franchise Event Generator

A Python application that generates random events for Madden franchise mode to make gameplay more dynamic and unpredictable.

## Features

- Generate random events that affect your Madden franchise
- Events impact players, coaches, and team circumstances
- Adjustable difficulty levels to control event severity
- Save and load franchise configurations
- Track event history over multiple seasons
- Manage your roster for accurate player references

## Requirements

- Python 3.6+
- PySide6 (Qt for Python)

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

This will automatically install PySide6 if needed and launch the application.

### Option 2: Standalone Executable

For users who prefer not to install Python, we provide standalone executable options:

1. Download the latest release for your platform from the [Releases](https://github.com/yourusername/franchise-spicer/releases) page
2. Extract the archive (if applicable)
3. Run the executable:
   - Windows: Double-click `Madden Franchise Generator.exe`
   - macOS: Double-click `Madden Franchise Generator.app`
   - Linux: Run `./Madden Franchise Generator`

### Option 3: Build Your Own Executable

If you want to build your own executable:

1. Make sure Python and pip are installed
2. Install PyInstaller (if you don't have it already):

```bash
python3 -m pip install PyInstaller
```

3. Run the build script:

```bash
python3 build_executable.py
```

4. The executable will be created in the `dist` directory

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

## Save File Location

The application stores save files and configuration data in the following locations:

- **When running from source code**: Files are stored in the `madden_franchise_qt/data` and `madden_franchise_qt/saves` directories within the project folder.

- **When running as an executable**:
  - **Windows**: `C:\Users\{username}\AppData\Local\MaddenTools\MaddenFranchiseGenerator`
  - **macOS**: `/Users/{username}/Library/Application Support/MaddenTools/MaddenFranchiseGenerator`
  - **Linux**: `~/.local/share/MaddenTools/MaddenFranchiseGenerator`

## Adding Custom Events

You can add custom events by modifying the `events.json` file in the data directory.

## Cross-Platform Support

This application is built with PySide6 (Qt for Python) to ensure compatibility with:
- macOS
- Windows
- Linux

## License

This project is open source and available under the MIT License.

## Acknowledgments

This tool is designed for use with EA's Madden NFL 25 game but is not affiliated with or endorsed by EA Sports or the NFL.