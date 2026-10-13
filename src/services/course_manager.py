"""
Course Manager Service — Orchestration Layer.

Brings together all six design patterns into a cohesive service
that client code (e.g. the CLI in `main.py`) interacts with:
    1. Factory Method — create courses by type
    2. Observer       — broadcast notifications on course events
    3. Strategy       — swap grading algorithms at runtime
    4. Decorator      — wrap courses with add-on features and fees
    5. Command        — execute reversible operations with undo/redo & audit log
    6. State          — track and enforce course lifecycle phases
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.course import Course, CourseType
from src.domain.student import Student
from src.patterns.command import Command, CommandInvoker
from src.patterns.factory import CourseFactory
from src.patterns.observer import CourseNotificationManager, EventType
from src.patterns.state import CourseState
from src.patterns.strategy import GradingStrategy


@dataclass
class CourseManager:
    """High-level service for managing courses and students.

    Internally orchestrates:
        - **Factory Method** to create courses.
        - **Observer** to broadcast notifications.
        - **Strategy** to compute grades.
        - **Decorator** applied by wrapping courses.
        - **Command** to execute reversible actions with audit history.
        - **State** to govern course lifecycle transitions and permissions.

    Attributes:
        courses: Registry of course_id → Course.
        students: Registry of student_id → Student.
        notifiers: Registry of course_id → CourseNotificationManager.
        invoker: Invoker managing command execution, undo, redo, and audit trail.
    """

    courses: dict[str, Course] = field(default_factory=dict)
    students: dict[str, Student] = field(default_factory=dict)
    notifiers: dict[str, CourseNotificationManager] = field(default_factory=dict)
    invoker: CommandInvoker = field(default_factory=CommandInvoker)

    # ------------------------------------------------------------------
    # Course management  (Factory Pattern)
    # ------------------------------------------------------------------
    def create_course(
        self,
        course_type: CourseType,
        course_id: str,
        title: str,
        credits: int,
        max_students: int = 30,
        base_fee: float = 500.0,
    ) -> Course:
        """Create a course using the Factory Method and register it."""
        course = CourseFactory.create_course(
            course_type=course_type,
            course_id=course_id,
            title=title,
            credits=credits,
            max_students=max_students,
            base_fee=base_fee,
        )
        self.courses[course_id] = course
        self.notifiers[course_id] = CourseNotificationManager(course_id)
        return course

    def replace_course(self, course_id: str, course: Course) -> None:
        """Replace a registered course (e.g. after decorating it)."""
        self.courses[course_id] = course

    def get_course(self, course_id: str) -> Course | None:
        return self.courses.get(course_id)

    # ------------------------------------------------------------------
    # Student management
    # ------------------------------------------------------------------
    def register_student(
        self,
        student_id: str,
        name: str,
        email: str,
    ) -> Student:
        """Register a new student in the system."""
        student = Student(student_id=student_id, name=name, email=email)
        self.students[student_id] = student
        return student

    def get_student(self, student_id: str) -> Student | None:
        return self.students.get(student_id)

    # ------------------------------------------------------------------
    # Enrollment  (Observer subscription is wired automatically)
    # ------------------------------------------------------------------
    def enroll_student(self, student_id: str, course_id: str) -> bool:
        """Enroll a student in a course and subscribe to all notifications.

        Returns:
            True if enrollment succeeded, False otherwise.
        """
        student = self.students.get(student_id)
        course = self.courses.get(course_id)
        if student is None or course is None:
            return False

        if not course.enroll_student(student):
            return False

        # Auto-subscribe the student to every event type (Observer)
        notifier = self.notifiers[course_id]
        notifier.subscribe_all(student)

        # Broadcast enrollment event
        notifier.notify(
            EventType.ENROLLMENT_UPDATE,
            f"{student.name} has enrolled in {course.title}.",
        )
        return True

    def drop_student(self, student_id: str, course_id: str) -> bool:
        """Remove a student from a course and unsubscribe from events."""
        student = self.students.get(student_id)
        course = self.courses.get(course_id)
        if student is None or course is None:
            return False

        if not course.remove_student(student):
            return False

        notifier = self.notifiers[course_id]
        notifier.notify(
            EventType.ENROLLMENT_UPDATE,
            f"{student.name} has dropped {course.title}.",
        )
        notifier.unsubscribe_all(student)
        return True

    # ------------------------------------------------------------------
    # Notifications  (Observer Pattern)
    # ------------------------------------------------------------------
    def post_announcement(self, course_id: str, message: str) -> int:
        """Broadcast an announcement to all enrolled students.

        Returns:
            Number of students notified.
        """
        notifier = self.notifiers.get(course_id)
        if notifier is None:
            return 0
        return notifier.notify(EventType.ANNOUNCEMENT, message)

    def post_assignment(self, course_id: str, assignment_name: str) -> int:
        """Notify students of a new assignment."""
        notifier = self.notifiers.get(course_id)
        if notifier is None:
            return 0
        return notifier.notify(
            EventType.ASSIGNMENT_POSTED,
            f"New assignment posted: '{assignment_name}'",
        )

    def release_grade(
        self,
        student_id: str,
        course_id: str,
        score: float,
    ) -> str | None:
        """Record a score, compute the letter grade, and notify the student.

        Returns:
            The computed letter grade, or None if inputs are invalid.
        """
        student = self.students.get(student_id)
        course = self.courses.get(course_id)
        if student is None or course is None:
            return None

        student.record_grade(course_id, score)
        letter = course.calculate_grade(score)

        notifier = self.notifiers.get(course_id)
        if notifier:
            notifier.notify(
                EventType.GRADE_RELEASED,
                f"Grade released for {student.name}: {score:.1f} → {letter}",
            )
        return letter

    # ------------------------------------------------------------------
    # Grading  (Strategy Pattern)
    # ------------------------------------------------------------------
    def set_grading_strategy(
        self,
        course_id: str,
        strategy: GradingStrategy,
    ) -> bool:
        """Attach a grading strategy to a course at runtime."""
        course = self.courses.get(course_id)
        if course is None:
            return False
        course.set_grading_strategy(strategy)
        return True

    # ------------------------------------------------------------------
    # Command Pattern (Transactions & Undo/Redo)
    # ------------------------------------------------------------------
    def execute_command(self, command: Command) -> bool:
        """Execute a reversible command via the internal invoker."""
        return self.invoker.execute_command(command)

    def undo(self) -> bool:
        """Undo the last executed transaction."""
        return self.invoker.undo()

    def redo(self) -> bool:
        """Redo the last undone transaction."""
        return self.invoker.redo()

    def get_audit_log(self) -> list[str]:
        """Retrieve chronological history of executed/undone transactions."""
        return self.invoker.get_audit_log()

    # ------------------------------------------------------------------
    # State Pattern (Course Lifecycle Management)
    # ------------------------------------------------------------------
    def set_course_state(self, course_id: str, state: CourseState) -> bool:
        """Set the lifecycle state of a registered course and notify observers."""
        course = self.courses.get(course_id)
        if course is None:
            return False

        course.set_state(state)
        notifier = self.notifiers.get(course_id)
        if notifier:
            notifier.notify(
                EventType.STATE_CHANGED,
                f"Course {course.title} transitioned to state: {state.name}",
            )
        return True

    def advance_course_state(self, course_id: str) -> CourseState | None:
        """Advance the course to its next lifecycle state and notify observers."""
        course = self.courses.get(course_id)
        if course is None:
            return None

        new_state = course.advance_state()
        notifier = self.notifiers.get(course_id)
        if notifier:
            notifier.notify(
                EventType.STATE_CHANGED,
                f"Course {course.title} advanced to state: {new_state.name}",
            )
        return new_state

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------
    def get_enrollment_report(self) -> str:
        """Generate a summary of all courses and their enrollment counts."""
        lines: list[str] = ["=" * 60, "ENROLLMENT REPORT", "=" * 60]
        for cid, course in self.courses.items():
            enrolled = len(course.enrolled_students)
            lines.append(
                f"  {cid}: {course.title} — "
                f"{enrolled}/{course.max_students} students, "
                f"${course.get_total_fee():.2f}"
            )
        lines.append("=" * 60)
        return "\n".join(lines)
