"""
Strategy Pattern — Grading Algorithms.

This module demonstrates the **Strategy** behavioural design pattern.
Multiple grading algorithms are encapsulated behind a common
`GradingStrategy` abstract interface so that a `Course` can switch its
grading scheme at runtime without altering its own code.

Concrete strategies:
    - StandardGradingStrategy   — classic A/B/C/D/F scale
    - PassFailGradingStrategy   — binary Pass/Fail with configurable threshold
    - CurvedGradingStrategy     — applies a curve boost before grading
    - WeightedGradingStrategy   — weights multiple score components
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


class GradingStrategy(ABC):
    """Abstract interface for grading algorithms.

    Every concrete strategy must implement `calculate_grade(score)` which
    accepts a numeric score (0–100) and returns a letter grade string.
    """

    @abstractmethod
    def calculate_grade(self, score: float) -> str:
        """Convert a numeric score to a letter grade.

        Args:
            score: Numeric score in the range [0, 100].

        Returns:
            A letter-grade string (e.g. ``"A"``, ``"Pass"``).
        """

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Return a human-readable name for this strategy."""


# ======================================================================
# Concrete Strategies
# ======================================================================

class StandardGradingStrategy(GradingStrategy):
    """Classic letter-grade scale: A (≥90), B (≥80), C (≥70), D (≥60), F.

    The thresholds can optionally be customised via the constructor.
    """

    def __init__(
        self,
        a_threshold: float = 90.0,
        b_threshold: float = 80.0,
        c_threshold: float = 70.0,
        d_threshold: float = 60.0,
    ) -> None:
        self._thresholds = [
            (a_threshold, "A"),
            (b_threshold, "B"),
            (c_threshold, "C"),
            (d_threshold, "D"),
        ]

    def calculate_grade(self, score: float) -> str:
        for threshold, grade in self._thresholds:
            if score >= threshold:
                return grade
        return "F"

    def get_strategy_name(self) -> str:
        return "Standard Grading (A-F)"


class PassFailGradingStrategy(GradingStrategy):
    """Binary grading: Pass if score ≥ threshold, Fail otherwise."""

    def __init__(self, pass_threshold: float = 60.0) -> None:
        self._pass_threshold = pass_threshold

    def calculate_grade(self, score: float) -> str:
        return "Pass" if score >= self._pass_threshold else "Fail"

    def get_strategy_name(self) -> str:
        return f"Pass/Fail (threshold={self._pass_threshold})"


class CurvedGradingStrategy(GradingStrategy):
    """Applies a flat curve boost before using a standard A-F scale.

    For example, a ``curve_points=5`` boost turns an 87 into a 92 → A.
    The score is capped at 100 after the boost.
    """

    def __init__(self, curve_points: float = 5.0) -> None:
        self._curve_points = curve_points
        self._standard = StandardGradingStrategy()

    def calculate_grade(self, score: float) -> str:
        curved_score = min(score + self._curve_points, 100.0)
        return self._standard.calculate_grade(curved_score)

    def get_strategy_name(self) -> str:
        return f"Curved Grading (+{self._curve_points} pts)"


@dataclass
class WeightedGradingStrategy(GradingStrategy):
    """Weights multiple assessment components before grading.

    ``weights`` maps component names to their weight (must sum to 1.0).
    Call `calculate_weighted_grade(scores)` with a dict of component → score.
    The plain `calculate_grade(score)` still works for a single overall score.

    Usage::

        strategy = WeightedGradingStrategy(
            weights={"homework": 0.3, "midterm": 0.3, "final": 0.4}
        )
        scores = {"homework": 95, "midterm": 80, "final": 70}
        letter = strategy.calculate_weighted_grade(scores)  # → "B"
    """

    weights: dict[str, float] = field(default_factory=lambda: {
        "homework": 0.3,
        "midterm": 0.3,
        "final": 0.4,
    })

    def __post_init__(self) -> None:
        self._standard = StandardGradingStrategy()

    def calculate_grade(self, score: float) -> str:
        return self._standard.calculate_grade(score)

    def calculate_weighted_grade(self, scores: dict[str, float]) -> str:
        """Calculate a weighted average and convert to a letter grade.

        Args:
            scores: Mapping of component name → numeric score.

        Returns:
            Letter grade based on the weighted average.

        Raises:
            ValueError: If provided component names don't match the weights.
        """
        missing = set(self.weights) - set(scores)
        if missing:
            raise ValueError(f"Missing scores for components: {missing}")

        weighted_sum = sum(
            scores[component] * weight
            for component, weight in self.weights.items()
        )
        return self._standard.calculate_grade(weighted_sum)

    def get_weighted_score(self, scores: dict[str, float]) -> float:
        """Return the raw weighted average (before grade conversion)."""
        return sum(
            scores[component] * weight
            for component, weight in self.weights.items()
        )

    def get_strategy_name(self) -> str:
        components = ", ".join(
            f"{name}={w:.0%}" for name, w in self.weights.items()
        )
        return f"Weighted Grading ({components})"
