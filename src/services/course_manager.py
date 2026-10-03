"""
Course Manager Service — Orchestration Layer.

Brings together all four design patterns into a cohesive service
that client code (e.g. the CLI in `main.py`) interacts with.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.course import Course, CourseType
from src.domain.student import Student
from src.patterns.factory import CourseFactory
from src.patterns.observer import CourseNotificationManager, EventType
from src.patterns.strategy import GradingStrategy


@dataclass
class CourseManager:
    """High-level service for managing courses and students.

    Internally uses:
        - **Factory Method** to create courses.
        - **Observer** to broadcast notifications.
        - **Strategy** to compute grades.
        - **Decorator** is applied externally by wrapping courses.

    Attributes:
        courses: Registry of course_id → Course.
        students: Registry of student_id → Student.
        notifiers: Registry of course_id → CourseNotificationManager.
    """

    courses: dict[str, Course] = field(default_factory=dict)
    students: dict[str, Student] = field(default_factory=dict)
    notifiers: dict[str, CourseNotificationManager] = field(default_factory=dict)

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
