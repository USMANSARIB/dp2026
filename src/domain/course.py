"""
Course entity module.

Defines the abstract base `Course` class and the `CourseType` enumeration.
Concrete course subclasses are created via the Factory Method pattern
(see `src/patterns/factory.py`).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.student import Student
    from src.patterns.strategy import GradingStrategy


class CourseType(Enum):
    """Supported course delivery formats."""

    LECTURE = "lecture"
    LAB = "lab"
    ONLINE = "online"
    SEMINAR = "seminar"


@dataclass
class Course(ABC):
    """Abstract base class for all courses.

    Every concrete course must implement `get_description()` and
    `get_requirements()`.  The `base_fee` represents the tuition
    cost *before* any decorator add-ons.

    Attributes:
        course_id: Unique identifier (e.g., "CS201").
        title: Human-readable course title.
        credits: Number of credit hours.
        max_students: Enrollment cap.
        base_fee: Tuition fee in USD before add-ons.
        enrolled_students: Students currently enrolled.
        grading_strategy: The pluggable grading algorithm (Strategy pattern).
    """

    course_id: str
    title: str
    credits: int
    max_students: int = 30
    base_fee: float = 500.0
    enrolled_students: list["Student"] = field(default_factory=list, repr=False)
    grading_strategy: "GradingStrategy | None" = field(default=None, repr=False)

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------
    @abstractmethod
    def get_description(self) -> str:
        """Return a human-readable description of the course format."""

    @abstractmethod
    def get_requirements(self) -> list[str]:
        """Return a list of requirements/resources for this course type."""

    # ------------------------------------------------------------------
    # Enrollment
    # ------------------------------------------------------------------
    def enroll_student(self, student: "Student") -> bool:
        """Enroll a student if the course is not full.

        Returns:
            True if enrolled successfully, False if the course is full.
        """
        if len(self.enrolled_students) >= self.max_students:
            return False
        if student not in self.enrolled_students:
            self.enrolled_students.append(student)
            student.enroll(self.course_id)
        return True

    def remove_student(self, student: "Student") -> bool:
        """Remove a student from the course.

        Returns:
            True if the student was removed, False if not found.
        """
        if student in self.enrolled_students:
            self.enrolled_students.remove(student)
            student.drop(self.course_id)
            return True
        return False

    # ------------------------------------------------------------------
    # Grading (Strategy pattern hook)
    # ------------------------------------------------------------------
    def set_grading_strategy(self, strategy: "GradingStrategy") -> None:
        """Attach a grading strategy at runtime."""
        self.grading_strategy = strategy

    def calculate_grade(self, score: float) -> str:
        """Delegate grade calculation to the attached strategy.

        Args:
            score: Numeric score (0-100).

        Returns:
            Letter grade string produced by the strategy.

        Raises:
            ValueError: If no grading strategy has been set.
        """
        if self.grading_strategy is None:
            raise ValueError(
                f"No grading strategy set for course '{self.course_id}'. "
                "Assign one via set_grading_strategy() first."
            )
        return self.grading_strategy.calculate_grade(score)

    # ------------------------------------------------------------------
    # Fee (used by Decorator pattern)
    # ------------------------------------------------------------------
    def get_total_fee(self) -> float:
        """Return the total fee for the course.

        Base implementation returns `base_fee`; decorators override this
        to add surcharges.
        """
        return self.base_fee

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------
    def __str__(self) -> str:
        return (
            f"{self.course_id}: {self.title} "
            f"({self.credits} credits, ${self.get_total_fee():.2f})"
        )
