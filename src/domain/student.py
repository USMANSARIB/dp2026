"""
Student entity module.

The Student class also implements the Observer interface, allowing students
to receive notifications when courses they are enrolled in publish updates.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.patterns.observer import EventType


@dataclass
class Student:
    """Represents a student in the course management system.

    A Student acts as a *concrete observer* in the Observer pattern —
    it registers with courses and receives notification callbacks
    whenever an event of interest is published.

    Attributes:
        student_id: Unique identifier for the student.
        name: Full name of the student.
        email: Contact email address.
        notifications: Running log of all received notifications.
        enrolled_course_ids: Set of course IDs the student is enrolled in.
        grades: Mapping of course_id → numeric score (0-100).
    """

    student_id: str
    name: str
    email: str
    notifications: list[str] = field(default_factory=list, repr=False)
    enrolled_course_ids: set[str] = field(default_factory=set, repr=False)
    grades: dict[str, float] = field(default_factory=dict, repr=False)

    # ------------------------------------------------------------------
    # Observer interface
    # ------------------------------------------------------------------
    def update(self, event_type: "EventType", message: str) -> None:
        """Called by the subject (CourseNotificationManager) when an event
        occurs on a course the student is observing.

        Args:
            event_type: The category of the event.
            message: Human-readable description of the event.
        """
        formatted = f"[{event_type.value}] {message}"
        self.notifications.append(formatted)

    # ------------------------------------------------------------------
    # Enrollment helpers
    # ------------------------------------------------------------------
    def enroll(self, course_id: str) -> None:
        """Enroll the student in a course."""
        self.enrolled_course_ids.add(course_id)

    def drop(self, course_id: str) -> None:
        """Drop the student from a course."""
        self.enrolled_course_ids.discard(course_id)

    def record_grade(self, course_id: str, score: float) -> None:
        """Record or update a numeric score for a given course."""
        self.grades[course_id] = score

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------
    def __str__(self) -> str:
        return f"Student({self.student_id}, {self.name})"
