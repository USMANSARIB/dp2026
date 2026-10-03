"""
Factory Method Pattern — Course Creation.

This module demonstrates the **Factory Method** creational design pattern.
A `CourseFactory` class centralises the logic for instantiating the correct
`Course` subclass based on a `CourseType` enum value, so client code never
needs to depend on concrete course classes directly.

Concrete products:
    - LectureCourse
    - LabCourse
    - OnlineCourse
    - SeminarCourse
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.domain.course import Course, CourseType


# ======================================================================
# Concrete Course Products
# ======================================================================

@dataclass
class LectureCourse(Course):
    """A traditional in-person lecture course."""

    def get_description(self) -> str:
        return (
            f"'{self.title}' is a traditional lecture course held in a "
            f"classroom setting with up to {self.max_students} students."
        )

    def get_requirements(self) -> list[str]:
        return [
            "Classroom with projector",
            "Textbook (required)",
            "Notebook for in-class exercises",
        ]


@dataclass
class LabCourse(Course):
    """A hands-on laboratory course."""

    def get_description(self) -> str:
        return (
            f"'{self.title}' is a hands-on laboratory course where students "
            f"work on practical experiments and projects."
        )

    def get_requirements(self) -> list[str]:
        return [
            "Lab equipment and safety gear",
            "Lab manual",
            "Personal protective equipment (PPE)",
            "Pre-lab report templates",
        ]


@dataclass
class OnlineCourse(Course):
    """An asynchronous / synchronous online course."""

    def get_description(self) -> str:
        return (
            f"'{self.title}' is an online course accessible from anywhere "
            f"with recorded lectures and virtual office hours."
        )

    def get_requirements(self) -> list[str]:
        return [
            "Stable internet connection",
            "Webcam and microphone",
            "Learning Management System (LMS) account",
        ]


@dataclass
class SeminarCourse(Course):
    """A discussion-based seminar course with limited enrollment."""

    def get_description(self) -> str:
        return (
            f"'{self.title}' is an intimate seminar course capped at "
            f"{self.max_students} students, focusing on discussion and "
            f"critical analysis."
        )

    def get_requirements(self) -> list[str]:
        return [
            "Assigned readings before each session",
            "Weekly discussion posts",
            "Participation in peer reviews",
        ]


# ======================================================================
# Factory
# ======================================================================

# Registry mapping CourseType → concrete class
_COURSE_REGISTRY: dict[CourseType, type[Course]] = {
    CourseType.LECTURE: LectureCourse,
    CourseType.LAB: LabCourse,
    CourseType.ONLINE: OnlineCourse,
    CourseType.SEMINAR: SeminarCourse,
}


class CourseFactory:
    """Factory Method that produces `Course` instances by type.

    Usage::

        course = CourseFactory.create_course(
            course_type=CourseType.LAB,
            course_id="CHEM301",
            title="Organic Chemistry Lab",
            credits=2,
            max_students=20,
            base_fee=750.00,
        )

    Raises:
        ValueError: If the supplied `course_type` is not registered.
    """

    @staticmethod
    def create_course(
        course_type: CourseType,
        course_id: str,
        title: str,
        credits: int,
        max_students: int = 30,
        base_fee: float = 500.0,
        **kwargs: Any,
    ) -> Course:
        """Create and return a course of the requested type.

        Args:
            course_type: The delivery format to instantiate.
            course_id: Unique course identifier.
            title: Human-readable course title.
            credits: Number of credit hours.
            max_students: Enrollment cap (default 30).
            base_fee: Tuition in USD before add-ons (default 500).
            **kwargs: Forwarded to the concrete constructor.

        Returns:
            A fully initialised concrete `Course` instance.
        """
        course_class = _COURSE_REGISTRY.get(course_type)
        if course_class is None:
            raise ValueError(
                f"Unknown course type: {course_type!r}. "
                f"Registered types: {list(_COURSE_REGISTRY.keys())}"
            )
        return course_class(
            course_id=course_id,
            title=title,
            credits=credits,
            max_students=max_students,
            base_fee=base_fee,
            **kwargs,
        )

    @staticmethod
    def get_available_types() -> list[CourseType]:
        """Return all registered course types."""
        return list(_COURSE_REGISTRY.keys())
