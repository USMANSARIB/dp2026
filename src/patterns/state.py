"""
State Pattern — Course Lifecycle Management.

This module demonstrates the **State** behavioural design pattern.
A course's lifecycle transitions across distinct phases:
    1. **DraftState**: Course is being drafted. Enrollment and grading are disabled.
    2. **OpenRegistrationState**: Registration open. Students may enroll and drop.
    3. **InProgressState**: Term is underway. Enrollment is closed; grading and
       assignments are active.
    4. **CompletedState**: Term concluded. Grades are finalized and archived.
       No further mutations are allowed.

Instead of monolithic conditional checks (`if state == ...`), each phase is
encapsulated in its own `CourseState` subclass that defines permitted actions
and manages state transitions.

Key participants:
    - **Context**: `Course` (holds a reference to its current `CourseState`).
    - **State (ABC)**: `CourseState` declaring lifecycle operations.
    - **Concrete States**:
        - `DraftState`
        - `OpenRegistrationState`
        - `InProgressState`
        - `CompletedState`
    - **Exception**: `CourseStateError` raised upon prohibited actions.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.course import Course
    from src.domain.student import Student


# ======================================================================
# Exception
# ======================================================================

class CourseStateError(Exception):
    """Raised when an operation is prohibited in the current course state."""


# ======================================================================
# Abstract State
# ======================================================================

class CourseState(ABC):
    """Abstract base class representing a course lifecycle state.

    Subclasses define what operations are allowed during that state and
    how the course transitions to subsequent states.
    """

    name: str = "ABSTRACT"
    can_enroll: bool = False
    can_drop: bool = False
    can_grade: bool = False
    can_modify_details: bool = False

    @abstractmethod
    def enroll_student(self, course: "Course", student: "Student") -> bool:
        """Attempt to enroll a student into the course."""

    @abstractmethod
    def remove_student(self, course: "Course", student: "Student") -> bool:
        """Attempt to remove/drop a student from the course."""

    @abstractmethod
    def calculate_grade(self, course: "Course", score: float) -> str:
        """Attempt to calculate/release a grade for the course."""

    @abstractmethod
    def advance(self, course: "Course") -> "CourseState":
        """Advance the course to its next lifecycle state."""

    @abstractmethod
    def get_status_description(self) -> str:
        """Return a human-readable summary of this state."""

    def __str__(self) -> str:
        return self.name


# ======================================================================
# Concrete States
# ======================================================================

class DraftState(CourseState):
    """Course syllabus and schedule are being planned.

    Enrollment and grading are prohibited while details are being edited.
    """

    name: str = "DRAFT"
    can_enroll: bool = False
    can_drop: bool = False
    can_grade: bool = False
    can_modify_details: bool = True

    def enroll_student(self, course: "Course", student: "Student") -> bool:
        raise CourseStateError(
            f"Cannot enroll in '{course.course_id}': course is currently in DRAFT state."
        )

    def remove_student(self, course: "Course", student: "Student") -> bool:
        raise CourseStateError(
            f"Cannot remove student from '{course.course_id}': course is in DRAFT state."
        )

    def calculate_grade(self, course: "Course", score: float) -> str:
        raise CourseStateError(
            f"Cannot calculate grade for '{course.course_id}': course is in DRAFT state."
        )

    def advance(self, course: "Course") -> CourseState:
        next_state = OpenRegistrationState()
        course.set_state(next_state)
        return next_state

    def get_status_description(self) -> str:
        return "Drafting curriculum; not open for enrollment or grading."


class OpenRegistrationState(CourseState):
    """Course is published and actively accepting student enrollments.

    Students may enroll and drop. Grading is not yet permitted because
    the term has not officially commenced.
    """

    name: str = "OPEN_REGISTRATION"
    can_enroll: bool = True
    can_drop: bool = True
    can_grade: bool = False
    can_modify_details: bool = False

    def enroll_student(self, course: "Course", student: "Student") -> bool:
        return course._do_enroll(student)

    def remove_student(self, course: "Course", student: "Student") -> bool:
        return course._do_remove(student)

    def calculate_grade(self, course: "Course", score: float) -> str:
        raise CourseStateError(
            f"Cannot calculate grade for '{course.course_id}': registration is open "
            "but lectures have not commenced."
        )

    def advance(self, course: "Course") -> CourseState:
        next_state = InProgressState()
        course.set_state(next_state)
        return next_state

    def get_status_description(self) -> str:
        return "Registration is open; students may enroll or drop."


class InProgressState(CourseState):
    """Academic term is active.

    New regular enrollments are locked. Students may withdraw/drop.
    Assignments and grades may be recorded.
    """

    name: str = "IN_PROGRESS"
    can_enroll: bool = False
    can_drop: bool = True
    can_grade: bool = True
    can_modify_details: bool = False

    def enroll_student(self, course: "Course", student: "Student") -> bool:
        raise CourseStateError(
            f"Cannot enroll in '{course.course_id}': registration is closed because "
            "classes are already IN_PROGRESS."
        )

    def remove_student(self, course: "Course", student: "Student") -> bool:
        return course._do_remove(student)

    def calculate_grade(self, course: "Course", score: float) -> str:
        return course._do_calculate_grade(score)

    def advance(self, course: "Course") -> CourseState:
        next_state = CompletedState()
        course.set_state(next_state)
        return next_state

    def get_status_description(self) -> str:
        return "Classes in session; enrollment locked, grading active."


class CompletedState(CourseState):
    """Course term is concluded and archived.

    Grades are finalized. All mutations (enrollment, dropping, regrading)
    are strictly prohibited.
    """

    name: str = "COMPLETED"
    can_enroll: bool = False
    can_drop: bool = False
    can_grade: bool = False
    can_modify_details: bool = False

    def enroll_student(self, course: "Course", student: "Student") -> bool:
        raise CourseStateError(
            f"Cannot enroll in '{course.course_id}': course is COMPLETED and archived."
        )

    def remove_student(self, course: "Course", student: "Student") -> bool:
        raise CourseStateError(
            f"Cannot drop student from '{course.course_id}': course is COMPLETED and archived."
        )

    def calculate_grade(self, course: "Course", score: float) -> str:
        raise CourseStateError(
            f"Cannot calculate or update grades for '{course.course_id}': course is COMPLETED."
        )

    def advance(self, course: "Course") -> CourseState:
        raise CourseStateError(
            f"Course '{course.course_id}' is already in terminal COMPLETED state."
        )

    def get_status_description(self) -> str:
        return "Term completed; archived and read-only."
