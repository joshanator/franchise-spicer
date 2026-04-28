#!/usr/bin/env python3
"""
Madden Franchise Event Generator - Lightweight Edition

A web-based tool to generate random events for Madden franchise mode.
"""

import webbrowser
from threading import Timer

from web import create_app


def open_browser(port: int) -> None:
    """Open the default browser to the app URL."""
    webbrowser.open(f"http://127.0.0.1:{port}")


def main() -> None:
    """Run the application."""
    app = create_app()
    port = 5050  # Using 5050 instead of 5000 (macOS uses 5000 for AirPlay)
    
    print("=" * 50)
    print("Madden Franchise Event Generator - Lightweight Edition")
    print("=" * 50)
    print(f"\nStarting server at http://127.0.0.1:{port}")
    print("Press Ctrl+C to stop the server\n")
    
    # Open browser after a short delay
    Timer(1.0, open_browser, args=[port]).start()
    
    # Run the Flask app
    app.run(host="127.0.0.1", port=port, debug=False)


if __name__ == "__main__":
    main()
