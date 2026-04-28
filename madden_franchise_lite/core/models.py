"""Data models for Madden Franchise Event Generator."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# All possible football positions
ALL_POSITIONS = [
    "QB1", "QB2",
    "RB1", "RB2", "RB3", "FB1",
    "WR1", "WR2", "WR3", "WR4",
    "TE1", "TE2",
    "LT1", "LT2", "LG1", "LG2", "C1", "C2", "RG1", "RG2", "RT1", "RT2",
    "LE1", "LE2", "DT1", "DT2", "DT3", "RE1", "RE2",
    "LOLB1", "LOLB2", "MLB1", "MLB2", "ROLB1", "ROLB2",
    "CB1", "CB2", "CB3", "CB4", "FS1", "FS2", "SS1", "SS2",
    "K1", "P1"
]

DIFFICULTIES = ["cupcake", "rookie", "pro", "all-madden", "diabolical"]

SEASON_STAGES = [
    "Pre-Season",
    "regular-season-start",
    "regular-season-mid",
    "regular-season-end",
    "Post-Season",
    "Off-Season"
]


@dataclass
class ResultOption:
    """A possible result for events with random outcomes."""
    result: str
    impact_text: str
    probability: float = 1.0


@dataclass
class Matchup:
    """A matchup for player callout events."""
    position1: str
    opponent_position: str


@dataclass
class EventOption:
    """An option for branching events."""
    description: str
    impact: str = ""
    is_temporary: bool = False
    options: list["EventOption"] = field(default_factory=list)
    impact_random_options: dict[str, float] = field(default_factory=dict)
    target_options: list[str] = field(default_factory=list)


@dataclass
class Event:
    """An event that can occur in a franchise."""
    id: int
    title: str
    description: str
    impact: str
    difficulty_weights: dict[str, float]
    category: str = ""
    season_stages: list[str] = field(default_factory=lambda: ["any"])
    target_options: list[str] = field(default_factory=list)
    reason_options: list[str] = field(default_factory=list)
    round_options: list[str] = field(default_factory=list)
    games_options: list[int] = field(default_factory=list)
    penalty_options: list[str] = field(default_factory=list)
    position_options: list[str] = field(default_factory=list)
    school_options: list[str] = field(default_factory=list)
    player_options: list[str] = field(default_factory=list)
    award_options: list[str] = field(default_factory=list)
    stat_options: list[str] = field(default_factory=list)
    trainer_options: list[str] = field(default_factory=list)
    trainer_impacts: dict[str, str] = field(default_factory=dict)
    result_options: list[ResultOption] = field(default_factory=list)
    matchups: list[Matchup] = field(default_factory=list)
    opponent_teams: list[str] = field(default_factory=list)
    options: list[EventOption] = field(default_factory=list)
    target_impacts: dict[str, str] = field(default_factory=dict)
    is_temporary: bool = False
    adult_content: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> "Event":
        """Create an Event from a dictionary."""
        result_options = [
            ResultOption(**ro) for ro in data.get("result_options", [])
        ]
        matchups = [
            Matchup(**m) for m in data.get("matchups", [])
        ]
        options = [
            EventOption(
                description=o.get("description", ""),
                impact=o.get("impact", ""),
                is_temporary=o.get("is_temporary", False),
                impact_random_options=o.get("impact_random_options", {}),
                target_options=o.get("target_options", []),
                options=[
                    EventOption(
                        description=no.get("description", ""),
                        impact=no.get("impact", ""),
                        is_temporary=no.get("is_temporary", False),
                        impact_random_options=no.get("impact_random_options", {}),
                    )
                    for no in o.get("options", [])
                ]
            )
            for o in data.get("options", [])
        ]
        
        return cls(
            id=data.get("id", 0),
            title=data.get("title", ""),
            description=data.get("description", ""),
            impact=data.get("impact", ""),
            difficulty_weights=data.get("difficulty_weights", {}),
            category=data.get("category", ""),
            season_stages=data.get("season_stages", ["any"]),
            target_options=data.get("target_options", []),
            reason_options=data.get("reason_options", []),
            round_options=data.get("round_options", []),
            games_options=data.get("games_options", []),
            penalty_options=data.get("penalty_options", []),
            position_options=data.get("position_options", []),
            school_options=data.get("school_options", []),
            player_options=data.get("player_options", []),
            award_options=data.get("award_options", []),
            stat_options=data.get("stat_options", []),
            trainer_options=data.get("trainer_options", []),
            trainer_impacts=data.get("trainer_impacts", {}),
            result_options=result_options,
            matchups=matchups,
            opponent_teams=data.get("opponent_teams", []),
            options=options,
            target_impacts=data.get("target_impacts", {}),
            is_temporary=data.get("is_temporary", False),
            adult_content=data.get("adult_content", False),
        )


@dataclass
class ProcessedEvent:
    """An event after processing with all placeholders filled."""
    id: int
    title: str
    description: str
    impact: str
    category: str = ""
    selected_target: str = ""
    original_target_position: str = ""
    is_temporary: bool = False
    options: list[EventOption] = field(default_factory=list)
    selected_option_index: Optional[int] = None
    selected_option_description: str = ""
    selected_option_impact: str = ""
    
    # Store all selected random values for history
    selected_values: dict[str, str] = field(default_factory=dict)


@dataclass
class HistoryEntry:
    """A recorded event in franchise history."""
    event_id: int
    title: str
    description: str
    impact: str
    timestamp: str
    week: int
    year: int
    selected_target: str = ""
    category: str = ""
    is_temporary: bool = False
    selected_option: Optional[dict] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "event_id": self.event_id,
            "title": self.title,
            "description": self.description,
            "impact": self.impact,
            "timestamp": self.timestamp,
            "week": self.week,
            "year": self.year,
            "selected_target": self.selected_target,
            "category": self.category,
        }
        if self.is_temporary:
            result["is_temporary"] = True
        if self.selected_option:
            result["selected_option"] = self.selected_option
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "HistoryEntry":
        """Create a HistoryEntry from a dictionary."""
        return cls(
            event_id=data.get("event_id", 0),
            title=data.get("title", ""),
            description=data.get("description", ""),
            impact=data.get("impact", ""),
            timestamp=data.get("timestamp", ""),
            week=data.get("week", 1),
            year=data.get("year", 1),
            selected_target=data.get("selected_target", ""),
            category=data.get("category", ""),
            is_temporary=data.get("is_temporary", False),
            selected_option=data.get("selected_option"),
        )


@dataclass
class Franchise:
    """A franchise save with all its data."""
    team_name: str
    week: int = 1
    year: int = 1
    season_stage: str = "Pre-Season"
    difficulty: str = "pro"
    roster: dict[str, str] = field(default_factory=dict)
    coaches: dict[str, str] = field(default_factory=lambda: {"HC": "", "OC": "", "DC": ""})
    history: list[HistoryEntry] = field(default_factory=list)
    custom_events: list[dict] = field(default_factory=list)
    unrealistic_events_enabled: bool = False
    adult_content_enabled: bool = False
    auto_save: bool = False
    save_file: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "franchise_info": {
                "team_name": self.team_name,
                "current_week": self.week,
                "current_year": self.year,
                "season_stage": self.season_stage,
                "save_file": self.save_file,
            },
            "difficulty": self.difficulty,
            "roster": self.roster,
            "coaches": self.coaches,
            "event_history": [h.to_dict() for h in self.history],
            "custom_events": self.custom_events,
            "unrealistic_events_enabled": self.unrealistic_events_enabled,
            "adult_content_enabled": self.adult_content_enabled,
            "auto_save": self.auto_save,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Franchise":
        """Create a Franchise from a dictionary."""
        franchise_info = data.get("franchise_info", {})
        history = [
            HistoryEntry.from_dict(h) 
            for h in data.get("event_history", [])
        ]
        
        return cls(
            team_name=franchise_info.get("team_name", ""),
            week=franchise_info.get("current_week", 1),
            year=franchise_info.get("current_year", 1),
            season_stage=franchise_info.get("season_stage", "Pre-Season"),
            difficulty=data.get("difficulty", "pro"),
            roster=data.get("roster", {}),
            coaches=data.get("coaches", {"HC": "", "OC": "", "DC": ""}),
            history=history,
            custom_events=data.get("custom_events", []),
            unrealistic_events_enabled=data.get("unrealistic_events_enabled", False),
            adult_content_enabled=data.get("adult_content_enabled", False),
            auto_save=data.get("auto_save", False),
            save_file=franchise_info.get("save_file", ""),
        )
