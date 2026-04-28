"""Route handlers for Madden Franchise Event Generator."""

from __future__ import annotations

from flask import (
    Flask,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from typing import Optional

from core import EventEngine, Storage
from core.models import ALL_POSITIONS, DIFFICULTIES, SEASON_STAGES, Franchise, ProcessedEvent


def get_storage() -> Storage:
    """Get storage instance from app context."""
    return current_app.storage


def get_engine() -> EventEngine:
    """Get engine instance from app context."""
    return current_app.engine


def get_current_franchise() -> Optional[Franchise]:
    """Get the current franchise from session."""
    save_name = session.get("current_franchise")
    if save_name:
        return get_storage().load_franchise(save_name)
    return None


def save_current_franchise(franchise: Franchise) -> bool:
    """Save the current franchise and update session."""
    if franchise.save_file:
        success, _ = get_storage().save_franchise(franchise, franchise.save_file)
        return success
    return False


def register_routes(app: Flask) -> None:
    """Register all routes with the Flask app."""
    
    @app.route("/")
    def index():
        """Home page - franchise selection/creation."""
        franchise = get_current_franchise()
        saves = get_storage().list_saves()
        return render_template(
            "index.html",
            franchise=franchise,
            saves=saves,
            difficulties=DIFFICULTIES,
            season_stages=SEASON_STAGES,
        )
    
    @app.route("/franchise/new", methods=["POST"])
    def new_franchise():
        """Create a new franchise."""
        team_name = request.form.get("team_name", "").strip()
        if not team_name:
            flash("Team name is required", "error")
            return redirect(url_for("index"))
        
        franchise = get_storage().create_franchise(team_name)
        success, name = get_storage().save_franchise(franchise)
        
        if success:
            session["current_franchise"] = name + ".json"
            flash(f"Created franchise '{team_name}'", "success")
        else:
            flash(f"Failed to create franchise: {name}", "error")
        
        return redirect(url_for("index"))
    
    @app.route("/franchise/load/<name>")
    def load_franchise(name: str):
        """Load an existing franchise."""
        franchise = get_storage().load_franchise(name)
        if franchise:
            session["current_franchise"] = franchise.save_file
            flash(f"Loaded franchise '{franchise.team_name}'", "success")
        else:
            flash(f"Failed to load franchise '{name}'", "error")
        
        return redirect(url_for("index"))
    
    @app.route("/franchise/save", methods=["POST"])
    def save_franchise():
        """Save the current franchise."""
        franchise = get_current_franchise()
        if not franchise:
            flash("No franchise loaded", "error")
            return redirect(url_for("index"))
        
        success, msg = get_storage().save_franchise(franchise, franchise.save_file)
        if success:
            flash("Franchise saved", "success")
        else:
            flash(f"Failed to save: {msg}", "error")
        
        return redirect(url_for("index"))
    
    @app.route("/franchise/update", methods=["POST"])
    def update_franchise():
        """Update franchise settings."""
        franchise = get_current_franchise()
        if not franchise:
            flash("No franchise loaded", "error")
            return redirect(url_for("index"))
        
        # Update fields from form
        if "week" in request.form:
            try:
                franchise.week = int(request.form["week"])
            except ValueError:
                pass
        
        if "year" in request.form:
            try:
                franchise.year = int(request.form["year"])
            except ValueError:
                pass
        
        if "season_stage" in request.form:
            franchise.season_stage = request.form["season_stage"]
        
        if "difficulty" in request.form:
            franchise.difficulty = request.form["difficulty"]
        
        if "unrealistic_events" in request.form:
            franchise.unrealistic_events_enabled = request.form["unrealistic_events"] == "on"
        else:
            franchise.unrealistic_events_enabled = False
        
        if "adult_content" in request.form:
            franchise.adult_content_enabled = request.form["adult_content"] == "on"
        else:
            franchise.adult_content_enabled = False
        
        save_current_franchise(franchise)
        flash("Settings updated", "success")
        
        return redirect(url_for("index"))
    
    @app.route("/events")
    def events():
        """Event rolling page."""
        franchise = get_current_franchise()
        if not franchise:
            flash("Please load or create a franchise first", "error")
            return redirect(url_for("index"))
        
        # Check for pending event in session
        pending_event = session.get("pending_event")
        
        return render_template(
            "events.html",
            franchise=franchise,
            pending_event=pending_event,
        )
    
    @app.route("/events/roll", methods=["POST"])
    def roll_event():
        """Roll for a random event."""
        franchise = get_current_franchise()
        if not franchise:
            return jsonify({"error": "No franchise loaded"}), 400
        
        event = get_engine().roll_event(franchise)
        if not event:
            return jsonify({"error": "No eligible events found"}), 404
        
        # Store in session for later acceptance
        session["pending_event"] = event_to_dict(event)
        
        return redirect(url_for("events"))
    
    @app.route("/events/select-option", methods=["POST"])
    def select_option():
        """Select an option for a branching event."""
        franchise = get_current_franchise()
        if not franchise:
            return jsonify({"error": "No franchise loaded"}), 400
        
        pending = session.get("pending_event")
        if not pending:
            return jsonify({"error": "No pending event"}), 400
        
        try:
            option_index = int(request.form.get("option_index", 0))
        except ValueError:
            option_index = 0
        
        # Reconstruct event and select option
        event = dict_to_event(pending)
        event = get_engine().select_option(event, option_index)
        
        session["pending_event"] = event_to_dict(event)
        
        return redirect(url_for("events"))
    
    @app.route("/events/accept", methods=["POST"])
    def accept_event():
        """Accept the current event."""
        franchise = get_current_franchise()
        if not franchise:
            flash("No franchise loaded", "error")
            return redirect(url_for("index"))
        
        pending = session.get("pending_event")
        if not pending:
            flash("No pending event to accept", "error")
            return redirect(url_for("events"))
        
        event = dict_to_event(pending)
        get_engine().accept_event(event, franchise)
        save_current_franchise(franchise)
        
        session.pop("pending_event", None)
        flash("Event accepted and recorded in history", "success")
        
        return redirect(url_for("events"))
    
    @app.route("/events/dismiss", methods=["POST"])
    def dismiss_event():
        """Dismiss the current event without recording."""
        session.pop("pending_event", None)
        flash("Event dismissed", "info")
        return redirect(url_for("events"))
    
    @app.route("/roster")
    def roster():
        """Roster management page."""
        franchise = get_current_franchise()
        if not franchise:
            flash("Please load or create a franchise first", "error")
            return redirect(url_for("index"))
        
        return render_template(
            "roster.html",
            franchise=franchise,
            positions=ALL_POSITIONS,
        )
    
    @app.route("/roster/update", methods=["POST"])
    def update_roster():
        """Update roster entries."""
        franchise = get_current_franchise()
        if not franchise:
            flash("No franchise loaded", "error")
            return redirect(url_for("index"))
        
        # Update all positions from form
        for position in ALL_POSITIONS:
            player_name = request.form.get(f"roster_{position}", "").strip()
            franchise.roster[position] = player_name
        
        # Update coaches
        for coach in ["HC", "OC", "DC"]:
            coach_name = request.form.get(f"coach_{coach}", "").strip()
            franchise.coaches[coach] = coach_name
        
        save_current_franchise(franchise)
        flash("Roster updated", "success")
        
        return redirect(url_for("roster"))
    
    @app.route("/history")
    def history():
        """Event history page."""
        franchise = get_current_franchise()
        if not franchise:
            flash("Please load or create a franchise first", "error")
            return redirect(url_for("index"))
        
        # Reverse to show newest first
        entries = list(reversed(franchise.history))
        
        return render_template(
            "history.html",
            franchise=franchise,
            history=entries,
        )
    
    @app.route("/history/clear", methods=["POST"])
    def clear_history():
        """Clear event history."""
        franchise = get_current_franchise()
        if not franchise:
            flash("No franchise loaded", "error")
            return redirect(url_for("index"))
        
        franchise.history = []
        save_current_franchise(franchise)
        flash("History cleared", "success")
        
        return redirect(url_for("history"))


def event_to_dict(event: ProcessedEvent) -> dict:
    """Convert ProcessedEvent to dict for session storage."""
    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "impact": event.impact,
        "category": event.category,
        "selected_target": event.selected_target,
        "original_target_position": event.original_target_position,
        "is_temporary": event.is_temporary,
        "options": [
            {
                "description": o.description,
                "impact": o.impact,
                "is_temporary": o.is_temporary,
                "impact_random_options": o.impact_random_options,
            }
            for o in event.options
        ],
        "selected_option_index": event.selected_option_index,
        "selected_option_description": event.selected_option_description,
        "selected_option_impact": event.selected_option_impact,
        "selected_values": event.selected_values,
    }


def dict_to_event(data: dict) -> ProcessedEvent:
    """Convert dict back to ProcessedEvent."""
    from core.models import EventOption
    
    return ProcessedEvent(
        id=data["id"],
        title=data["title"],
        description=data["description"],
        impact=data["impact"],
        category=data.get("category", ""),
        selected_target=data.get("selected_target", ""),
        original_target_position=data.get("original_target_position", ""),
        is_temporary=data.get("is_temporary", False),
        options=[
            EventOption(
                description=o["description"],
                impact=o.get("impact", ""),
                is_temporary=o.get("is_temporary", False),
                impact_random_options=o.get("impact_random_options", {}),
            )
            for o in data.get("options", [])
        ],
        selected_option_index=data.get("selected_option_index"),
        selected_option_description=data.get("selected_option_description", ""),
        selected_option_impact=data.get("selected_option_impact", ""),
        selected_values=data.get("selected_values", {}),
    )
