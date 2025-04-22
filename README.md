# Madden 25 Franchise Event Generator

A Python application that generates random events for Madden 25 franchise mode to make gameplay more dynamic and unpredictable.

## Features

- Generate random events that affect your Madden 25 franchise
- Events impact players, coaches, and team circumstances
- Adjustable difficulty levels to control event severity
- Save and load franchise configurations
- Track event history over multiple seasons
- Manage your roster for accurate player references

## Requirements

- Python 3.6+
- PySide6 (Qt for Python)

## Installation

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

## Adding Custom Events

You can add custom events by modifying the `events.json` file in the `madden_franchise_qt/data` directory.

## Cross-Platform Support

This application is built with PySide6 (Qt for Python) to ensure compatibility with:
- macOS
- Windows
- Linux

## License

This project is open source and available under the MIT License.

## Acknowledgments

This tool is designed for use with EA's Madden NFL 25 game but is not affiliated with or endorsed by EA Sports or the NFL.