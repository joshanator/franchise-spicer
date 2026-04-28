"""Flask application factory for Madden Franchise Event Generator."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

# Ensure the parent package is importable
_package_dir = Path(__file__).parent.parent
if str(_package_dir) not in sys.path:
    sys.path.insert(0, str(_package_dir))

from flask import Flask

from core import EventEngine, Storage


def create_app(base_dir: Optional[str] = None) -> Flask:
    """Create and configure the Flask application.
    
    Args:
        base_dir: Base directory for data storage. Defaults to package directory.
        
    Returns:
        Configured Flask application.
    """
    if base_dir is None:
        base_dir = str(Path(__file__).parent.parent)
    
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).parent / "templates"),
        static_folder=str(Path(__file__).parent / "static"),
    )
    
    app.secret_key = "madden-franchise-generator-secret-key"
    
    # Initialize core components
    storage = Storage(base_dir)
    engine = EventEngine(storage)
    
    # Store in app context
    app.storage = storage
    app.engine = engine
    
    # Register routes
    from . import routes
    routes.register_routes(app)
    
    return app
