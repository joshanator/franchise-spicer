"""Event engine for Madden Franchise Event Generator."""

from __future__ import annotations

import random
from datetime import datetime
from typing import Optional

from .models import (
    ALL_POSITIONS,
    Event,
    EventOption,
    Franchise,
    HistoryEntry,
    ProcessedEvent,
)
from .storage import Storage


class EventEngine:
    """Handles event rolling, processing, and history management."""

    # Map season stages to allowed event stage filters
    STAGE_MAPPING = {
        "Pre-Season": ["pre-season", "any"],
        "regular-season-start": ["regular-season", "regular-season-start", "any"],
        "regular-season-mid": ["regular-season", "regular-season-mid", "any"],
        "regular-season-end": ["regular-season", "regular-season-end", "any"],
        "Post-Season": ["post-season", "playoffs", "any"],
        "Off-Season": ["off-season", "offseason", "any"],
        # Backward compatibility
        "Regular Season Start": ["regular-season", "regular-season-start", "any"],
        "Regular Season Mid": ["regular-season", "regular-season-mid", "any"],
        "Regular Season End": ["regular-season", "regular-season-end", "any"],
    }

    def __init__(self, storage: Storage):
        """Initialize the event engine.
        
        Args:
            storage: Storage instance for loading events.
        """
        self.storage = storage
        self._events: list[Event] = []
        self._unrealistic_events: list[Event] = []
        self.reload_events()
    
    def reload_events(self) -> None:
        """Reload events from storage."""
        self._events = self.storage.load_events()
        self._unrealistic_events = self.storage.load_unrealistic_events()
    
    def get_allowed_stages(self, current_stage: str) -> list[str]:
        """Get allowed event stages for filtering.
        
        Args:
            current_stage: The current season stage.
            
        Returns:
            List of stage names that events can have.
        """
        return self.STAGE_MAPPING.get(current_stage, ["any"])
    
    def get_eligible_events(self, franchise: Franchise) -> list[Event]:
        """Get all events eligible for the current franchise state.
        
        Args:
            franchise: The current franchise.
            
        Returns:
            List of eligible events.
        """
        eligible = []
        allowed_stages = self.get_allowed_stages(franchise.season_stage)
        difficulty = franchise.difficulty
        
        # Check standard events
        for event in self._events:
            if self._is_event_eligible(event, difficulty, allowed_stages, franchise):
                eligible.append(event)
        
        # Add unrealistic events if enabled
        if franchise.unrealistic_events_enabled:
            for event in self._unrealistic_events:
                if self._is_event_eligible(event, difficulty, allowed_stages, franchise):
                    eligible.append(event)
        
        # Add custom events
        for event_data in franchise.custom_events:
            event = Event.from_dict(event_data)
            if self._is_event_eligible(event, difficulty, allowed_stages, franchise):
                eligible.append(event)
        
        return eligible
    
    def _is_event_eligible(
        self, 
        event: Event, 
        difficulty: str, 
        allowed_stages: list[str],
        franchise: Franchise
    ) -> bool:
        """Check if an event is eligible based on current settings.
        
        Args:
            event: The event to check.
            difficulty: Current difficulty setting.
            allowed_stages: Allowed season stages.
            franchise: Current franchise.
            
        Returns:
            True if the event is eligible.
        """
        # Check difficulty weight
        weight = event.difficulty_weights.get(difficulty, 0.5)
        if random.random() >= weight:
            return False
        
        # Check season stage
        if not any(stage in allowed_stages for stage in event.season_stages):
            return False
        
        # Check adult content filter
        if event.adult_content and not franchise.adult_content_enabled:
            return False
        
        return True
    
    def roll_event(self, franchise: Franchise) -> Optional[ProcessedEvent]:
        """Roll for a random event.
        
        Args:
            franchise: The current franchise.
            
        Returns:
            A processed event, or None if no eligible events.
        """
        eligible = self.get_eligible_events(franchise)
        
        if not eligible:
            return None
        
        event = random.choice(eligible)
        return self.process_event(event, franchise)
    
    def get_event_by_id(
        self, 
        event_id: int, 
        franchise: Franchise,
        is_unrealistic: bool = False
    ) -> Optional[ProcessedEvent]:
        """Get and process a specific event by ID.
        
        Args:
            event_id: The event ID to find.
            franchise: The current franchise.
            is_unrealistic: Whether to search unrealistic events.
            
        Returns:
            A processed event, or None if not found.
        """
        events = self._unrealistic_events if is_unrealistic else self._events
        
        for event in events:
            if event.id == event_id:
                return self.process_event(event, franchise)
        
        # Also check custom events
        for event_data in franchise.custom_events:
            if event_data.get("id") == event_id:
                event = Event.from_dict(event_data)
                return self.process_event(event, franchise)
        
        return None
    
    def process_event(self, event: Event, franchise: Franchise) -> ProcessedEvent:
        """Process an event by filling in all placeholders.
        
        Args:
            event: The event to process.
            franchise: The current franchise for roster lookups.
            
        Returns:
            A processed event with all placeholders filled.
        """
        description = event.description
        impact = event.impact
        title = event.title
        selected_values: dict[str, str] = {}
        selected_target = ""
        original_position = ""
        
        # Handle target selection
        if event.target_options:
            target_opts = event.target_options
            
            if len(target_opts) == 1 and target_opts[0] == "n/a":
                selected_target = "N/A"
                original_position = "N/A"
            elif len(target_opts) == 1 and target_opts[0] == "all-players":
                position = random.choice(ALL_POSITIONS)
                original_position = position
                player_name = franchise.roster.get(position, "")
                if player_name:
                    selected_target = f"{player_name} ({position})"
                else:
                    selected_target = position
            elif len(target_opts) == 1 and target_opts[0] in ["HC", "OC", "DC"]:
                position = target_opts[0]
                original_position = position
                coach_name = franchise.coaches.get(position, "")
                if coach_name:
                    selected_target = f"{coach_name} ({position})"
                else:
                    selected_target = position
            else:
                position = random.choice(target_opts)
                original_position = position
                player_name = franchise.roster.get(position, "")
                if player_name:
                    selected_target = f"{player_name} ({position})"
                else:
                    selected_target = position
            
            description = self._replace(description, "target", selected_target)
            impact = self._replace(impact, "target", selected_target)
            
            # Handle target-specific impacts
            if event.target_impacts and original_position in event.target_impacts:
                impact_text = event.target_impacts[original_position]
                impact = self._replace(impact, "impact_text", impact_text)
        
        # Handle trainer selection
        if event.trainer_options and event.trainer_impacts:
            trainer = random.choice(event.trainer_options)
            selected_values["trainer"] = trainer
            description = self._replace(description, "trainer", trainer)
            
            trainer_impact = event.trainer_impacts.get(trainer, "")
            impact = self._replace(impact, "trainer_impact", trainer_impact)
        
        # Handle simple random selections
        option_fields = [
            ("reason_options", "reason"),
            ("round_options", "round"),
            ("games_options", "games"),
            ("penalty_options", "penalty"),
            ("position_options", "position"),
            ("school_options", "school"),
            ("player_options", "player"),
            ("award_options", "award"),
            ("stat_options", "stat"),
        ]
        
        for field_name, placeholder in option_fields:
            options = getattr(event, field_name, [])
            if options:
                value = str(random.choice(options))
                selected_values[placeholder] = value
                description = self._replace(description, placeholder, value)
                impact = self._replace(impact, placeholder, value)
                title = self._replace(title, placeholder, value)
        
        # Handle result options (weighted random)
        if event.result_options:
            total_prob = sum(ro.probability for ro in event.result_options)
            rand_val = random.random() * total_prob
            
            cumulative = 0.0
            selected_result = event.result_options[0]
            for ro in event.result_options:
                cumulative += ro.probability
                if rand_val <= cumulative:
                    selected_result = ro
                    break
            
            selected_values["result"] = selected_result.result
            description = self._replace(description, "result", selected_result.result)
            impact = self._replace(impact, "impact_text", selected_result.impact_text)
        
        # Handle matchups
        if event.matchups:
            matchup = random.choice(event.matchups)
            selected_values["position1"] = matchup.position1
            selected_values["opponent_position"] = matchup.opponent_position
            description = self._replace(description, "position1", matchup.position1)
            description = self._replace(description, "opponent_position", matchup.opponent_position)
            
            if event.opponent_teams:
                team = random.choice(event.opponent_teams)
                selected_values["opponent_team"] = team
                description = self._replace(description, "opponent_team", team)
        
        # Process options for branching events
        processed_options = []
        for opt in event.options:
            processed_opt = EventOption(
                description=self._replace(opt.description, "target", selected_target),
                impact=self._replace(opt.impact, "target", selected_target),
                is_temporary=opt.is_temporary,
                impact_random_options=opt.impact_random_options,
                target_options=opt.target_options,
                options=[
                    EventOption(
                        description=self._replace(no.description, "target", selected_target),
                        impact=self._replace(no.impact, "target", selected_target),
                        is_temporary=no.is_temporary,
                        impact_random_options=no.impact_random_options,
                    )
                    for no in opt.options
                ]
            )
            processed_options.append(processed_opt)
        
        return ProcessedEvent(
            id=event.id,
            title=title,
            description=description,
            impact=impact,
            category=event.category,
            selected_target=selected_target,
            original_target_position=original_position,
            is_temporary=event.is_temporary,
            options=processed_options,
            selected_values=selected_values,
        )
    
    def select_option(
        self, 
        event: ProcessedEvent, 
        option_index: int
    ) -> ProcessedEvent:
        """Select an option for a branching event.
        
        Args:
            event: The processed event.
            option_index: Index of the selected option.
            
        Returns:
            Updated processed event with selection recorded.
        """
        if option_index >= len(event.options):
            return event
        
        option = event.options[option_index]
        event.selected_option_index = option_index
        event.selected_option_description = option.description
        
        # Handle random impact options
        if option.impact_random_options:
            options = list(option.impact_random_options.keys())
            weights = list(option.impact_random_options.values())
            event.selected_option_impact = random.choices(options, weights=weights, k=1)[0]
        else:
            event.selected_option_impact = option.impact
        
        # Replace target in impact
        if event.selected_target:
            event.selected_option_impact = self._replace(
                event.selected_option_impact, "target", event.selected_target
            )
        
        # Handle nested options
        if option.options:
            event.options = [
                EventOption(
                    description=no.description,
                    impact=no.impact,
                    is_temporary=no.is_temporary or option.is_temporary,
                    impact_random_options=no.impact_random_options or option.impact_random_options,
                )
                for no in option.options
            ]
            event.selected_option_index = None  # Reset for next selection
        else:
            event.options = []  # No more options
            if option.is_temporary:
                event.is_temporary = True
        
        return event
    
    def accept_event(self, event: ProcessedEvent, franchise: Franchise) -> HistoryEntry:
        """Accept an event and add it to franchise history.
        
        Args:
            event: The processed event to accept.
            franchise: The franchise to update.
            
        Returns:
            The created history entry.
        """
        # Build the final description and impact
        description = event.description
        impact = event.impact
        
        if event.selected_option_description:
            description = f"{description}\n\nYou selected: {event.selected_option_description}"
        
        if event.selected_option_impact:
            impact = event.selected_option_impact
        
        entry = HistoryEntry(
            event_id=event.id,
            title=event.title,
            description=description,
            impact=impact,
            timestamp=datetime.now().isoformat(),
            week=franchise.week,
            year=franchise.year,
            selected_target=event.selected_target,
            category=event.category,
            is_temporary=event.is_temporary,
            selected_option={
                "description": event.selected_option_description,
                "impact": event.selected_option_impact,
            } if event.selected_option_description else None,
        )
        
        franchise.history.append(entry)
        return entry
    
    def _replace(self, text: str, placeholder: str, value: str) -> str:
        """Replace a placeholder in text.
        
        Args:
            text: The text containing placeholders.
            placeholder: The placeholder name (without braces).
            value: The value to replace with.
            
        Returns:
            Text with placeholder replaced.
        """
        return text.replace(f"{{{placeholder}}}", str(value))
