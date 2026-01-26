"""
Scoring System - Gamification for BCI Experiments
Handles score calculation, tracking, and leaderboard management
"""

import json
import os
from typing import List, Tuple, Optional
from datetime import datetime


class ScoreEntry:
    """Represents a single score entry."""

    def __init__(self, score: int, name: str = "", timestamp: Optional[datetime] = None):
        self.score = score
        self.name = name
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "score": self.score,
            "name": self.name,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ScoreEntry':
        """Create ScoreEntry from dictionary."""
        return cls(
            score=data["score"],
            name=data.get("name", ""),
            timestamp=datetime.fromisoformat(data["timestamp"])
        )

    def __str__(self) -> str:
        return f"{self.name}: {self.score} points"


class ScoringSystem:
    """
    Handles scoring for BCI experiments.

    Tracks instruction changes, calculates points based on intention averages,
    and manages the leaderboard.
    """

    def __init__(self, leaderboard_file: str = "airobo_trainer/leaderboard.json"):
        self.leaderboard_file = leaderboard_file
        self.current_score = 0
        self.instruction_periods = []  # List of (start_time, end_time, mode, intention_values)
        self.current_period_start = None
        self.current_mode = "relax"
        self.intention_history = []  # List of (timestamp, left_intention, right_intention)

        # Load existing leaderboard
        self.leaderboard = self._load_leaderboard()

    def _load_leaderboard(self) -> List[ScoreEntry]:
        """Load leaderboard from file."""
        if os.path.exists(self.leaderboard_file):
            try:
                with open(self.leaderboard_file, 'r') as f:
                    data = json.load(f)
                    return [ScoreEntry.from_dict(entry) for entry in data]
            except (json.JSONDecodeError, KeyError):
                pass
        return []

    def _save_leaderboard(self):
        """Save leaderboard to file."""
        os.makedirs(os.path.dirname(self.leaderboard_file), exist_ok=True)
        with open(self.leaderboard_file, 'w') as f:
            json.dump([entry.to_dict() for entry in self.leaderboard], f, indent=2)

    def start_experiment(self):
        """Reset scoring for a new experiment."""
        self.current_score = 0
        self.instruction_periods = []
        self.current_period_start = datetime.now()
        self.current_mode = "relax"
        self.intention_history = []

    def update_intention(self, left_intention: int, right_intention: int):
        """
        Update intention values for current period.

        Args:
            left_intention: Left hand intention (0-100)
            right_intention: Right hand intention (0-100)
        """
        now = datetime.now()
        self.intention_history.append((now, left_intention, right_intention))

    def change_instruction(self, new_mode: str):
        """
        Handle instruction mode change (relax -> left/right or left -> right).

        Awards points based on the previous instruction period's average intention.

        Args:
            new_mode: New instruction mode ("left", "right", or "relax")
        """
        if self.current_period_start is None:
            return

        # Award points for transitions TO left/right from other modes, or FROM left/right TO relax
        # (relax -> left/right, left -> right, right -> left, or left/right -> relax)
        should_award_points = (
            (self.current_mode == "relax" and new_mode in ["left", "right"]) or
            (self.current_mode in ["left", "right"] and new_mode in ["left", "right"] and self.current_mode != new_mode) or
            (self.current_mode in ["left", "right"] and new_mode == "relax")
        )

        if should_award_points:
            # Calculate average intention for the relevant arm during this period
            period_intentions = []
            end_time = datetime.now()

            for timestamp, left_int, right_int in self.intention_history:
                if self.current_period_start <= timestamp <= end_time:
                    if self.current_mode == "left":
                        period_intentions.append(left_int)
                    elif self.current_mode == "right":
                        period_intentions.append(right_int)

            if period_intentions:
                avg_intention = sum(period_intentions) / len(period_intentions)
                points = self._calculate_points(avg_intention)
                self.current_score += points

                # Store period data
                self.instruction_periods.append({
                    'start': self.current_period_start,
                    'end': end_time,
                    'mode': self.current_mode,
                    'avg_intention': avg_intention,
                    'points': points
                })

        # Start new period
        self.current_mode = new_mode
        self.current_period_start = datetime.now()

    def _calculate_points(self, avg_intention: float) -> int:
        """
        Calculate points based on average intention level.

        Args:
            avg_intention: Average intention (0-100)

        Returns:
            Points awarded
        """
        if avg_intention >= 90:
            return 100
        elif avg_intention >= 80:
            return 75
        elif avg_intention >= 70:
            return 50
        elif avg_intention >= 60:
            return 25
        elif avg_intention >= 50:
            return 10
        else:
            return 0

    def end_experiment(self) -> int:
        """
        End the experiment and calculate final bonus points.

        Returns:
            Final total score
        """
        # Calculate average intention across all left/right periods
        all_left_right_intentions = []

        for period in self.instruction_periods:
            if period['mode'] in ['left', 'right']:
                # Find intention values for this period
                period_start = period['start']
                period_end = period['end']

                period_intentions = []
                for timestamp, left_int, right_int in self.intention_history:
                    if period_start <= timestamp <= period_end:
                        if period['mode'] == 'left':
                            period_intentions.append(left_int)
                        elif period['mode'] == 'right':
                            period_intentions.append(right_int)

                if period_intentions:
                    period_avg = sum(period_intentions) / len(period_intentions)
                    all_left_right_intentions.append(period_avg)

        # Award bonus points if overall average > 90%
        if all_left_right_intentions:
            overall_avg = sum(all_left_right_intentions) / len(all_left_right_intentions)
            if overall_avg > 90:
                bonus_points = 200  # Extra points
                self.current_score += bonus_points

        return self.current_score

    def get_current_score(self) -> int:
        """Get the current score."""
        return self.current_score

    def submit_score(self, name: str) -> bool:
        """
        Submit score to leaderboard.

        Args:
            name: Player name

        Returns:
            True if score made it to top 10
        """
        entry = ScoreEntry(self.current_score, name)
        self.leaderboard.append(entry)

        # Sort by score descending
        self.leaderboard.sort(key=lambda x: x.score, reverse=True)

        # Keep only top 10
        self.leaderboard = self.leaderboard[:10]

        # Save to file
        self._save_leaderboard()

        # Check if this score made it to the leaderboard
        return entry in self.leaderboard

    def get_leaderboard(self) -> List[ScoreEntry]:
        """Get the current leaderboard."""
        return self.leaderboard.copy()

    def is_top_10_score(self, score: int) -> bool:
        """
        Check if a score would make it to the top 10.

        Args:
            score: Score to check

        Returns:
            True if score would be in top 10
        """
        if len(self.leaderboard) < 10:
            return True

        return score > min(entry.score for entry in self.leaderboard)
