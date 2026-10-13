"""
Unit tests for the Student Course Management System design patterns.

Tests cover:
    1. Factory Method  — correct course type creation
    2. Observer        — subscribe, notify, unsubscribe
    3. Strategy        — all grading algorithms
    4. Decorator       — stacking add-ons, fee accumulation
"""

from __future__ import annotations

import sys
import os
import unittest

# Ensure project root is on sys.path
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.domain.course import Course, CourseType
from src.domain.student import Student
from src.patterns.factory import (
    CourseFactory,
    LectureCourse,
    LabCourse,
    OnlineCourse,
    SeminarCourse,
)
from src.patterns.observer import CourseNotificationManager, EventType
from src.patterns.strategy import (
    StandardGradingStrategy,
    PassFailGradingStrategy,
    CurvedGradingStrategy,
    WeightedGradingStrategy,
)
from src.patterns.decorator import (
    HonorsDistinctionDecorator,
    LabAccessPassDecorator,
    TutoringSupportDecorator,
    CertificateDecorator,
)
from src.patterns.command import (
    Command,
    EnrollStudentCommand,
    DropStudentCommand,
    RecordGradeCommand,
    ChangeGradingStrategyCommand,
    CommandInvoker,
)
from src.patterns.state import (
    CourseState,
    DraftState,
    OpenRegistrationState,
    InProgressState,
    CompletedState,
    CourseStateError,
)
from src.services.course_manager import CourseManager


# ======================================================================
# 1. Factory Method Pattern Tests
# ======================================================================

class TestFactoryMethodPattern(unittest.TestCase):
    """Verify that the CourseFactory produces the correct concrete types."""

    def test_create_lecture_course(self) -> None:
        course = CourseFactory.create_course(
            CourseType.LECTURE, "CS101", "Intro to CS", 3
        )
        self.assertIsInstance(course, LectureCourse)
        self.assertEqual(course.course_id, "CS101")
        self.assertEqual(course.credits, 3)

    def test_create_lab_course(self) -> None:
        course = CourseFactory.create_course(
            CourseType.LAB, "CHEM201", "Organic Chem Lab", 2, max_students=20
        )
        self.assertIsInstance(course, LabCourse)
        self.assertEqual(course.max_students, 20)

    def test_create_online_course(self) -> None:
        course = CourseFactory.create_course(
            CourseType.ONLINE, "ENG102", "English Online", 3
        )
        self.assertIsInstance(course, OnlineCourse)

    def test_create_seminar_course(self) -> None:
        course = CourseFactory.create_course(
            CourseType.SEMINAR, "PHIL401", "AI Ethics", 3, max_students=15
        )
        self.assertIsInstance(course, SeminarCourse)
        self.assertEqual(course.max_students, 15)

    def test_invalid_course_type_raises(self) -> None:
        with self.assertRaises(ValueError):
            CourseFactory.create_course("invalid", "X", "X", 1)  # type: ignore[arg-type]

    def test_get_available_types(self) -> None:
        types = CourseFactory.get_available_types()
        self.assertEqual(len(types), 4)
        self.assertIn(CourseType.LECTURE, types)

    def test_description_not_empty(self) -> None:
        for ctype in CourseType:
            course = CourseFactory.create_course(ctype, "T1", "Test", 1)
            self.assertTrue(len(course.get_description()) > 0)

    def test_requirements_is_list(self) -> None:
        for ctype in CourseType:
            course = CourseFactory.create_course(ctype, "T1", "Test", 1)
            reqs = course.get_requirements()
            self.assertIsInstance(reqs, list)
            self.assertTrue(len(reqs) > 0)


# ======================================================================
# 2. Observer Pattern Tests
# ======================================================================

class TestObserverPattern(unittest.TestCase):
    """Verify subscription, notification, and unsubscription."""

    def setUp(self) -> None:
        self.mgr = CourseNotificationManager("CS101")
        self.student = Student("S001", "Alice", "alice@uni.edu")

    def test_subscribe_and_notify(self) -> None:
        self.mgr.subscribe(EventType.ANNOUNCEMENT, self.student)
        count = self.mgr.notify(EventType.ANNOUNCEMENT, "Hello!")
        self.assertEqual(count, 1)
        self.assertEqual(len(self.student.notifications), 1)
        self.assertIn("ANNOUNCEMENT", self.student.notifications[0])

    def test_unsubscribe(self) -> None:
        self.mgr.subscribe(EventType.ANNOUNCEMENT, self.student)
        self.mgr.unsubscribe(EventType.ANNOUNCEMENT, self.student)
        count = self.mgr.notify(EventType.ANNOUNCEMENT, "Nope")
        self.assertEqual(count, 0)
        self.assertEqual(len(self.student.notifications), 0)

    def test_subscribe_all(self) -> None:
        self.mgr.subscribe_all(self.student)
        for event in EventType:
            self.assertEqual(self.mgr.get_subscriber_count(event), 1)

    def test_unsubscribe_all(self) -> None:
        self.mgr.subscribe_all(self.student)
        self.mgr.unsubscribe_all(self.student)
        for event in EventType:
            self.assertEqual(self.mgr.get_subscriber_count(event), 0)

    def test_no_duplicate_subscription(self) -> None:
        self.mgr.subscribe(EventType.ANNOUNCEMENT, self.student)
        self.mgr.subscribe(EventType.ANNOUNCEMENT, self.student)
        self.assertEqual(self.mgr.get_subscriber_count(EventType.ANNOUNCEMENT), 1)

    def test_callable_listener(self) -> None:
        received: list[str] = []
        listener = lambda et, msg: received.append(msg)
        self.mgr.subscribe(EventType.GRADE_RELEASED, listener)
        self.mgr.notify(EventType.GRADE_RELEASED, "Grade A")
        self.assertEqual(len(received), 1)
        self.assertIn("Grade A", received[0])

    def test_multiple_observers(self) -> None:
        bob = Student("S002", "Bob", "bob@uni.edu")
        self.mgr.subscribe(EventType.ANNOUNCEMENT, self.student)
        self.mgr.subscribe(EventType.ANNOUNCEMENT, bob)
        count = self.mgr.notify(EventType.ANNOUNCEMENT, "Hi all!")
        self.assertEqual(count, 2)
        self.assertEqual(len(self.student.notifications), 1)
        self.assertEqual(len(bob.notifications), 1)

    def test_event_isolation(self) -> None:
        """Notifications for one event type don't leak to another."""
        self.mgr.subscribe(EventType.ANNOUNCEMENT, self.student)
        self.mgr.notify(EventType.GRADE_RELEASED, "Leaked?")
        self.assertEqual(len(self.student.notifications), 0)


# ======================================================================
# 3. Strategy Pattern Tests
# ======================================================================

class TestStrategyPattern(unittest.TestCase):
    """Verify all grading strategy algorithms."""

    def test_standard_grading(self) -> None:
        s = StandardGradingStrategy()
        self.assertEqual(s.calculate_grade(95), "A")
        self.assertEqual(s.calculate_grade(85), "B")
        self.assertEqual(s.calculate_grade(75), "C")
        self.assertEqual(s.calculate_grade(65), "D")
        self.assertEqual(s.calculate_grade(50), "F")

    def test_standard_boundary(self) -> None:
        s = StandardGradingStrategy()
        self.assertEqual(s.calculate_grade(90), "A")
        self.assertEqual(s.calculate_grade(89.9), "B")

    def test_pass_fail(self) -> None:
        s = PassFailGradingStrategy(pass_threshold=60)
        self.assertEqual(s.calculate_grade(60), "Pass")
        self.assertEqual(s.calculate_grade(59.9), "Fail")
        self.assertEqual(s.calculate_grade(100), "Pass")
        self.assertEqual(s.calculate_grade(0), "Fail")

    def test_curved_grading(self) -> None:
        s = CurvedGradingStrategy(curve_points=5)
        # 87 + 5 = 92 → A
        self.assertEqual(s.calculate_grade(87), "A")
        # 55 + 5 = 60 → D
        self.assertEqual(s.calculate_grade(55), "D")
        # Cap at 100: 98 + 5 = 100 → A
        self.assertEqual(s.calculate_grade(98), "A")

    def test_weighted_grading(self) -> None:
        s = WeightedGradingStrategy(
            weights={"hw": 0.3, "mid": 0.3, "final": 0.4}
        )
        scores = {"hw": 100, "mid": 80, "final": 70}
        # 30 + 24 + 28 = 82 → B
        self.assertEqual(s.calculate_weighted_grade(scores), "B")

    def test_weighted_score(self) -> None:
        s = WeightedGradingStrategy(
            weights={"hw": 0.5, "final": 0.5}
        )
        score = s.get_weighted_score({"hw": 100, "final": 60})
        self.assertAlmostEqual(score, 80.0)

    def test_weighted_missing_component_raises(self) -> None:
        s = WeightedGradingStrategy(
            weights={"hw": 0.5, "final": 0.5}
        )
        with self.assertRaises(ValueError):
            s.calculate_weighted_grade({"hw": 90})

    def test_strategy_name(self) -> None:
        for strategy_cls in [
            StandardGradingStrategy,
            PassFailGradingStrategy,
            CurvedGradingStrategy,
        ]:
            name = strategy_cls().get_strategy_name()
            self.assertIsInstance(name, str)
            self.assertTrue(len(name) > 0)

    def test_course_without_strategy_raises(self) -> None:
        course = CourseFactory.create_course(
            CourseType.LECTURE, "T1", "Test", 1
        )
        with self.assertRaises(ValueError):
            course.calculate_grade(90)


# ======================================================================
# 4. Decorator Pattern Tests
# ======================================================================

class TestDecoratorPattern(unittest.TestCase):
    """Verify decorator stacking, fee accumulation, and description."""

    def setUp(self) -> None:
        self.base = CourseFactory.create_course(
            CourseType.LECTURE, "CS101", "Intro to CS", 3,
            base_fee=500.0,
        )

    def test_honors_decorator(self) -> None:
        decorated = HonorsDistinctionDecorator(self.base)
        self.assertEqual(decorated.get_total_fee(), 650.0)
        self.assertIn("Honors", decorated.get_description())
        self.assertIn("Honors thesis", str(decorated.get_requirements()))

    def test_lab_access_decorator(self) -> None:
        decorated = LabAccessPassDecorator(self.base)
        self.assertEqual(decorated.get_total_fee(), 600.0)
        self.assertIn("Lab Access", decorated.get_description())

    def test_tutoring_decorator(self) -> None:
        decorated = TutoringSupportDecorator(self.base)
        self.assertEqual(decorated.get_total_fee(), 700.0)
        self.assertIn("Tutoring", decorated.get_description())

    def test_certificate_decorator(self) -> None:
        decorated = CertificateDecorator(self.base)
        self.assertEqual(decorated.get_total_fee(), 575.0)
        self.assertIn("Certificate", decorated.get_description())

    def test_stacking_all_decorators(self) -> None:
        """Stack all four decorators and verify cumulative fee."""
        course = self.base
        course = HonorsDistinctionDecorator(course)    # +150
        course = LabAccessPassDecorator(course)         # +100
        course = TutoringSupportDecorator(course)       # +200
        course = CertificateDecorator(course)           # + 75
        expected = 500 + 150 + 100 + 200 + 75           # 1025
        self.assertEqual(course.get_total_fee(), expected)

    def test_decorator_preserves_course_id(self) -> None:
        decorated = HonorsDistinctionDecorator(self.base)
        self.assertEqual(decorated.course_id, "CS101")
        self.assertEqual(decorated.title, "Intro to CS")
        self.assertEqual(decorated.credits, 3)

    def test_decorator_enrollment(self) -> None:
        """Enrollment via a decorated course still works."""
        decorated = HonorsDistinctionDecorator(self.base)
        student = Student("S001", "Alice", "alice@uni.edu")
        result = decorated.enroll_student(student)
        self.assertTrue(result)
        self.assertIn(student, decorated.enrolled_students)

    def test_decorator_grading_strategy(self) -> None:
        """Strategy can be set through a decorated course."""
        decorated = CertificateDecorator(self.base)
        decorated.set_grading_strategy(StandardGradingStrategy())
        grade = decorated.calculate_grade(92)
        self.assertEqual(grade, "A")

    def test_requirements_accumulate(self) -> None:
        """Each decorator adds requirements on top of previous ones."""
        base_count = len(self.base.get_requirements())
        d1 = HonorsDistinctionDecorator(self.base)
        self.assertGreater(len(d1.get_requirements()), base_count)
        d2 = LabAccessPassDecorator(d1)
        self.assertGreater(len(d2.get_requirements()), len(d1.get_requirements()))


# ======================================================================
# 5. Integration / CourseManager Tests
# ======================================================================

class TestCourseManagerIntegration(unittest.TestCase):
    """End-to-end tests using the CourseManager service."""

    def setUp(self) -> None:
        self.mgr = CourseManager()
        self.mgr.create_course(CourseType.LECTURE, "CS101", "Intro CS", 3)
        self.mgr.register_student("S001", "Alice", "alice@uni.edu")

    def test_enroll_and_notify(self) -> None:
        result = self.mgr.enroll_student("S001", "CS101")
        self.assertTrue(result)
        student = self.mgr.get_student("S001")
        # Should have received the enrollment notification
        self.assertTrue(len(student.notifications) > 0)

    def test_grade_release_flow(self) -> None:
        self.mgr.set_grading_strategy("CS101", StandardGradingStrategy())
        self.mgr.enroll_student("S001", "CS101")
        letter = self.mgr.release_grade("S001", "CS101", 88.0)
        self.assertEqual(letter, "B")
        student = self.mgr.get_student("S001")
        self.assertEqual(student.grades["CS101"], 88.0)

    def test_enrollment_report(self) -> None:
        self.mgr.enroll_student("S001", "CS101")
        report = self.mgr.get_enrollment_report()
        self.assertIn("CS101", report)
        self.assertIn("1/", report)

    def test_drop_student(self) -> None:
        self.mgr.enroll_student("S001", "CS101")
        result = self.mgr.drop_student("S001", "CS101")
        self.assertTrue(result)
        course = self.mgr.get_course("CS101")
        self.assertEqual(len(course.enrolled_students), 0)

    def test_manager_command_execution_and_undo(self) -> None:
        cmd = EnrollStudentCommand(self.mgr, "S001", "CS101")
        self.assertTrue(self.mgr.execute_command(cmd))
        course = self.mgr.get_course("CS101")
        self.assertEqual(len(course.enrolled_students), 1)

        self.assertTrue(self.mgr.undo())
        self.assertEqual(len(course.enrolled_students), 0)

        self.assertTrue(self.mgr.redo())
        self.assertEqual(len(course.enrolled_students), 1)

    def test_manager_state_advance_flow(self) -> None:
        self.mgr.set_course_state("CS101", DraftState())
        course = self.mgr.get_course("CS101")
        self.assertEqual(course.state.name, "DRAFT")

        new_state = self.mgr.advance_course_state("CS101")
        self.assertEqual(new_state.name, "OPEN_REGISTRATION")
        self.assertEqual(course.state.name, "OPEN_REGISTRATION")


# ======================================================================
# 6. Command Pattern Tests
# ======================================================================

class TestCommandPattern(unittest.TestCase):
    """Verify Command execution, undo/redo stacks, and audit logging."""

    def setUp(self) -> None:
        self.mgr = CourseManager()
        self.mgr.create_course(CourseType.LECTURE, "CS101", "Intro CS", 3)
        self.mgr.set_grading_strategy("CS101", StandardGradingStrategy())
        self.mgr.register_student("S001", "Alice", "alice@uni.edu")
        self.mgr.register_student("S002", "Bob", "bob@uni.edu")
        self.invoker = CommandInvoker()

    def test_enroll_command_execute_and_undo(self) -> None:
        cmd = EnrollStudentCommand(self.mgr, "S001", "CS101")
        self.assertTrue(self.invoker.execute_command(cmd))
        course = self.mgr.get_course("CS101")
        self.assertIn(self.mgr.get_student("S001"), course.enrolled_students)

        # Undo enrollment
        self.assertTrue(self.invoker.undo())
        self.assertNotIn(self.mgr.get_student("S001"), course.enrolled_students)

    def test_drop_command_execute_and_undo(self) -> None:
        self.mgr.enroll_student("S001", "CS101")
        course = self.mgr.get_course("CS101")
        self.assertEqual(len(course.enrolled_students), 1)

        cmd = DropStudentCommand(self.mgr, "S001", "CS101")
        self.assertTrue(self.invoker.execute_command(cmd))
        self.assertEqual(len(course.enrolled_students), 0)

        # Undo drop
        self.assertTrue(self.invoker.undo())
        self.assertEqual(len(course.enrolled_students), 1)

    def test_record_grade_command_undo_restores_previous_score(self) -> None:
        self.mgr.enroll_student("S001", "CS101")
        student = self.mgr.get_student("S001")
        student.record_grade("CS101", 75.0)

        cmd = RecordGradeCommand(self.mgr, "S001", "CS101", 95.0)
        self.assertTrue(self.invoker.execute_command(cmd))
        self.assertEqual(student.grades["CS101"], 95.0)

        # Undo should restore 75.0
        self.assertTrue(self.invoker.undo())
        self.assertEqual(student.grades["CS101"], 75.0)

    def test_record_grade_command_undo_removes_new_grade(self) -> None:
        self.mgr.enroll_student("S001", "CS101")
        student = self.mgr.get_student("S001")
        self.assertNotIn("CS101", student.grades)

        cmd = RecordGradeCommand(self.mgr, "S001", "CS101", 88.0)
        self.assertTrue(self.invoker.execute_command(cmd))
        self.assertEqual(student.grades["CS101"], 88.0)

        # Undo should remove the grade key
        self.assertTrue(self.invoker.undo())
        self.assertNotIn("CS101", student.grades)

    def test_redo_command(self) -> None:
        cmd = EnrollStudentCommand(self.mgr, "S001", "CS101")
        self.invoker.execute_command(cmd)
        self.invoker.undo()
        self.assertTrue(self.invoker.can_redo)

        self.assertTrue(self.invoker.redo())
        course = self.mgr.get_course("CS101")
        self.assertIn(self.mgr.get_student("S001"), course.enrolled_students)
        self.assertFalse(self.invoker.can_redo)

    def test_change_grading_strategy_command(self) -> None:
        curved = CurvedGradingStrategy(5.0)
        cmd = ChangeGradingStrategyCommand(self.mgr, "CS101", curved)
        self.assertTrue(self.invoker.execute_command(cmd))
        course = self.mgr.get_course("CS101")
        self.assertEqual(course.grading_strategy.get_strategy_name(), curved.get_strategy_name())

        # Undo restores Standard
        self.assertTrue(self.invoker.undo())
        self.assertIsInstance(course.grading_strategy, StandardGradingStrategy)

    def test_command_invoker_audit_log(self) -> None:
        cmd = EnrollStudentCommand(self.mgr, "S001", "CS101")
        self.invoker.execute_command(cmd)
        self.invoker.undo()
        self.invoker.redo()

        log = self.invoker.get_audit_log()
        self.assertEqual(len(log), 3)
        self.assertIn("EXECUTE", log[0])
        self.assertIn("UNDO", log[1])
        self.assertIn("REDO", log[2])

    def test_empty_invoker_cannot_undo_or_redo(self) -> None:
        self.assertFalse(self.invoker.can_undo)
        self.assertFalse(self.invoker.can_redo)
        self.assertFalse(self.invoker.undo())
        self.assertFalse(self.invoker.redo())

    def test_invalid_command_fails_gracefully(self) -> None:
        cmd = EnrollStudentCommand(self.mgr, "INVALID_ID", "CS101")
        self.assertFalse(self.invoker.execute_command(cmd))
        self.assertFalse(self.invoker.can_undo)


# ======================================================================
# 7. State Pattern Tests
# ======================================================================

class TestStatePattern(unittest.TestCase):
    """Verify CourseState lifecycle, permissions, and transitions."""

    def setUp(self) -> None:
        self.course = CourseFactory.create_course(
            CourseType.LECTURE, "CS201", "Data Structures", 3
        )
        self.course.set_grading_strategy(StandardGradingStrategy())
        self.student = Student("S001", "Alice", "alice@uni.edu")

    def test_draft_state_blocks_enrollment(self) -> None:
        self.course.set_state(DraftState())
        with self.assertRaises(CourseStateError):
            self.course.enroll_student(self.student)

    def test_draft_state_blocks_grading(self) -> None:
        self.course.set_state(DraftState())
        with self.assertRaises(CourseStateError):
            self.course.calculate_grade(85.0)

    def test_open_registration_allows_enrollment(self) -> None:
        self.course.set_state(OpenRegistrationState())
        result = self.course.enroll_student(self.student)
        self.assertTrue(result)
        self.assertIn(self.student, self.course.enrolled_students)

    def test_open_registration_blocks_grading(self) -> None:
        self.course.set_state(OpenRegistrationState())
        with self.assertRaises(CourseStateError):
            self.course.calculate_grade(85.0)

    def test_in_progress_blocks_enrollment(self) -> None:
        self.course.set_state(InProgressState())
        with self.assertRaises(CourseStateError):
            self.course.enroll_student(self.student)

    def test_in_progress_allows_grading_and_drop(self) -> None:
        # Pre-enroll in open state
        self.course.set_state(OpenRegistrationState())
        self.course.enroll_student(self.student)

        # Advance to InProgress
        self.course.advance_state()
        self.assertIsInstance(self.course.state, InProgressState)

        # Grade calculation allowed
        grade = self.course.calculate_grade(92.0)
        self.assertEqual(grade, "A")

        # Dropping allowed (withdrawal)
        dropped = self.course.remove_student(self.student)
        self.assertTrue(dropped)
        self.assertEqual(len(self.course.enrolled_students), 0)

    def test_full_lifecycle_advancement(self) -> None:
        self.course.set_state(DraftState())
        self.assertEqual(self.course.state.name, "DRAFT")

        s1 = self.course.advance_state()
        self.assertIsInstance(s1, OpenRegistrationState)
        self.assertEqual(self.course.state.name, "OPEN_REGISTRATION")

        s2 = self.course.advance_state()
        self.assertIsInstance(s2, InProgressState)
        self.assertEqual(self.course.state.name, "IN_PROGRESS")

        s3 = self.course.advance_state()
        self.assertIsInstance(s3, CompletedState)
        self.assertEqual(self.course.state.name, "COMPLETED")

        # Cannot advance beyond COMPLETED
        with self.assertRaises(CourseStateError):
            self.course.advance_state()

    def test_completed_state_blocks_all_mutations(self) -> None:
        self.course.set_state(CompletedState())

        with self.assertRaises(CourseStateError):
            self.course.enroll_student(self.student)

        with self.assertRaises(CourseStateError):
            self.course.remove_student(self.student)

        with self.assertRaises(CourseStateError):
            self.course.calculate_grade(90.0)

    def test_state_with_decorator(self) -> None:
        self.course.set_state(DraftState())
        decorated = HonorsDistinctionDecorator(self.course)

        # Decorated course forwards state and raises CourseStateError
        with self.assertRaises(CourseStateError):
            decorated.enroll_student(self.student)

        # Advancing through decorator
        new_state = decorated.advance_state()
        self.assertIsInstance(new_state, OpenRegistrationState)
        self.assertTrue(decorated.enroll_student(self.student))


if __name__ == "__main__":
    unittest.main(verbosity=2)
