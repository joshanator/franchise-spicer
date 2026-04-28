# Madden Franchise Event Generator - Lightweight Edition

A lightweight, web-based version of the Madden Franchise Event Generator.

## Features

- Generate random events for your Madden franchise
- Multiple difficulty levels (Cupcake, Rookie, Pro, All-Madden, Diabolical)
- Season stage awareness (Pre-Season, Regular Season, Playoffs, Off-Season)
- Roster management with player names
- Event history tracking
- Branching events with choices
- Unrealistic events (optional)
- Adult content filter

## Requirements

- Python 3.9+
- Flask

## Installation

```bash
cd madden_franchise_lite
pip install -r requirements.txt
```

## Usage

```bash
python run.py
```

This will start the web server and open your browser to http://127.0.0.1:5050

## Directory Structure

```
madden_franchise_lite/
├── core/                   # Core engine (no UI dependencies)
│   ├── engine.py          # Event rolling and processing
│   ├── models.py          # Data classes
│   └── storage.py         # File operations
├── web/                   
│   ├── app.py             # Flask app factory
│   ├── routes.py          # API endpoints
│   ├── templates/         # HTML templates
│   └── static/            # CSS and JS
├── data/
│   ├── events.json        # Event definitions
│   └── unrealistic_events.json
├── saves/                  # Franchise save files
├── run.py                  # Entry point
└── requirements.txt
```

## Extending

### Adding New Events

Edit `data/events.json` to add new events. Each event has:

- `id`: Unique identifier
- `title`: Event title
- `description`: Event description (supports `{target}`, `{reason}`, etc. placeholders)
- `impact`: What the player should do in Madden
- `difficulty_weights`: Probability by difficulty level
- `season_stages`: When the event can occur
- `target_options`: Who can be affected (positions or "all-players")

### Building on the Core

The `core` package has no UI dependencies and can be used standalone:

```python
from core import EventEngine, Storage, Franchise

storage = Storage()
engine = EventEngine(storage)
franchise = storage.create_franchise("My Team")

event = engine.roll_event(franchise)
if event:
    engine.accept_event(event, franchise)
    storage.save_franchise(franchise)
```

## Migration from Qt Version

Existing save files from the Qt version are compatible. Place them in the `saves/` directory.

## License

Same as the main project - CC BY-NC 4.0
