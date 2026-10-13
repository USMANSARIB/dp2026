"""
Decorator Pattern — Course Add-On Features.

This module demonstrates the **Decorator** structural design pattern.
Decorators wrap a `Course` instance to add optional features (honours
distinction, lab access, tutoring support, certificates) without modifying
the original class or resorting to deep inheritance hierarchies.

Each decorator:
    1. Forwards the core `Course` interface to the wrapped instance.
    2. Augments `get_description()`, `get_requirements()`, and/or
       `get_total_fee()` with additional behaviour.
    3. Can be stacked (composed) in any combination.

Concrete decorators:
    - HonorsDistinctionDecorator
    - LabAccessPassDecorator
    - TutoringSupportDecorator
    - CertificateDecorator
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.domain.course import Course

if TYPE_CHECKING:
    from src.domain.student import Student
    from src.patterns.strategy import GradingStrategy
    from src.patterns.state import CourseState


class CourseDecorator(Course):
    """Abstract decorator that wraps a `Course` and delegates all calls.

    Subclasses override specific methods to inject additional behaviour
    while preserving the original course's functionality.

    Note:
        Because `Course` is a dataclass ABC, the decorator cannot itself be
        a dataclass — it manually forwards attributes from the wrapped
        course instead.
    """

    def __init__(self, wrapped_course: Course) -> None:
        # Store the wrapped course (the "component")
        self._wrapped = wrapped_course

    # ------------------------------------------------------------------
    # Delegate core dataclass attributes to the wrapped course
    # ------------------------------------------------------------------
    @property
    def course_id(self) -> str:  # type: ignore[override]
        return self._wrapped.course_id

    @course_id.setter
    def course_id(self, value: str) -> None:
        self._wrapped.course_id = value

    @property
    def title(self) -> str:  # type: ignore[override]
        return self._wrapped.title

    @title.setter
    def title(self, value: str) -> None:
        self._wrapped.title = value

    @property
    def credits(self) -> int:  # type: ignore[override]
        return self._wrapped.credits

    @credits.setter
    def credits(self, value: int) -> None:
        self._wrapped.credits = value

    @property
    def max_students(self) -> int:  # type: ignore[override]
        return self._wrapped.max_students

    @max_students.setter
    def max_students(self, value: int) -> None:
        self._wrapped.max_students = value

    @property
    def base_fee(self) -> float:  # type: ignore[override]
        return self._wrapped.base_fee

    @base_fee.setter
    def base_fee(self, value: float) -> None:
        self._wrapped.base_fee = value

    @property
    def enrolled_students(self) -> list["Student"]:  # type: ignore[override]
        return self._wrapped.enrolled_students

    @enrolled_students.setter
    def enrolled_students(self, value: list["Student"]) -> None:
        self._wrapped.enrolled_students = value

    @property
    def grading_strategy(self) -> "GradingStrategy | None":  # type: ignore[override]
        return self._wrapped.grading_strategy

    @grading_strategy.setter
    def grading_strategy(self, value: "GradingStrategy | None") -> None:
        self._wrapped.grading_strategy = value

    @property
    def state(self) -> "CourseState | None":  # type: ignore[override]
        return self._wrapped.state

    @state.setter
    def state(self, value: "CourseState | None") -> None:
        self._wrapped.state = value

    # ------------------------------------------------------------------
    # Forwarded methods to the wrapped course
    # ------------------------------------------------------------------
    def set_state(self, state: "CourseState") -> None:
        self._wrapped.set_state(state)

    def advance_state(self) -> "CourseState":
        return self._wrapped.advance_state()

    def enroll_student(self, student: "Student") -> bool:
        return self._wrapped.enroll_student(student)

    def _do_enroll(self, student: "Student") -> bool:
        return self._wrapped._do_enroll(student)

    def remove_student(self, student: "Student") -> bool:
        return self._wrapped.remove_student(student)

    def _do_remove(self, student: "Student") -> bool:
        return self._wrapped._do_remove(student)

    def set_grading_strategy(self, strategy: "GradingStrategy") -> None:
        self._wrapped.set_grading_strategy(strategy)

    def calculate_grade(self, score: float) -> str:
        return self._wrapped.calculate_grade(score)

    def _do_calculate_grade(self, score: float) -> str:
        return self._wrapped._do_calculate_grade(score)

    # ------------------------------------------------------------------
    # Forwarded abstract methods (default: delegate to wrapped)
    # ------------------------------------------------------------------
    def get_description(self) -> str:
        return self._wrapped.get_description()

    def get_requirements(self) -> list[str]:
        return list(self._wrapped.get_requirements())

    def get_total_fee(self) -> float:
        return self._wrapped.get_total_fee()

    def __str__(self) -> str:
        return self._wrapped.__str__()


# ======================================================================
# Concrete Decorators
# ======================================================================

class HonorsDistinctionDecorator(CourseDecorator):
    """Adds an Honors distinction, extra reading, and a fee surcharge."""

    SURCHARGE = 150.0

    def get_description(self) -> str:
        return self._wrapped.get_description() + " [Honors Section]"

    def get_requirements(self) -> list[str]:
        reqs = list(self._wrapped.get_requirements())
        reqs.extend([
            "Honors thesis proposal",
            "Additional scholarly reading list",
        ])
        return reqs

    def get_total_fee(self) -> float:
        return self._wrapped.get_total_fee() + self.SURCHARGE

    def __str__(self) -> str:
        return (
            f"{self.course_id}: {self.title} ⭐ Honors "
            f"({self.credits} credits, ${self.get_total_fee():.2f})"
        )


class LabAccessPassDecorator(CourseDecorator):
    """Grants 24/7 lab access and adds safety training requirement."""

    SURCHARGE = 100.0

    def get_description(self) -> str:
        return self._wrapped.get_description() + " + 24/7 Lab Access"

    def get_requirements(self) -> list[str]:
        reqs = list(self._wrapped.get_requirements())
        reqs.extend([
            "Lab safety training certification",
            "ID badge for after-hours access",
        ])
        return reqs

    def get_total_fee(self) -> float:
        return self._wrapped.get_total_fee() + self.SURCHARGE

    def __str__(self) -> str:
        return (
            f"{self.course_id}: {self.title} 🔬 Lab Access "
            f"({self.credits} credits, ${self.get_total_fee():.2f})"
        )


class TutoringSupportDecorator(CourseDecorator):
    """Bundles weekly 1-on-1 tutoring sessions."""

    SURCHARGE = 200.0

    def get_description(self) -> str:
        return self._wrapped.get_description() + " + Personal Tutoring"

    def get_requirements(self) -> list[str]:
        reqs = list(self._wrapped.get_requirements())
        reqs.append("Signed tutoring agreement form")
        return reqs

    def get_total_fee(self) -> float:
        return self._wrapped.get_total_fee() + self.SURCHARGE

    def __str__(self) -> str:
        return (
            f"{self.course_id}: {self.title} 📚 Tutoring "
            f"({self.credits} credits, ${self.get_total_fee():.2f})"
        )


class CertificateDecorator(CourseDecorator):
    """Awards an official certificate upon completion."""

    SURCHARGE = 75.0

    def get_description(self) -> str:
        return self._wrapped.get_description() + " + Certificate of Completion"

    def get_requirements(self) -> list[str]:
        reqs = list(self._wrapped.get_requirements())
        reqs.append("Maintain minimum 70% overall grade for certificate eligibility")
        return reqs

    def get_total_fee(self) -> float:
        return self._wrapped.get_total_fee() + self.SURCHARGE

    def __str__(self) -> str:
        return (
            f"{self.course_id}: {self.title} 🎓 Certificate "
            f"({self.credits} credits, ${self.get_total_fee():.2f})"
        )
