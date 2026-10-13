"""
Student Course Management System — Interactive CLI & Feature Navigation.

Provides an interactive terminal menu and guided demonstration of all six
classic Gang of Four (GoF) design patterns:
    1. Factory Method  — dynamic creation of course types without concrete coupling
    2. Observer         — broadcast notifications to students on course events
    3. Strategy         — pluggable runtime grading algorithms
    4. Decorator        — dynamically stacking features and tuition fees
    5. Command          — reversible registrar transactions with undo/redo & audit log
    6. State            — course lifecycle state machine & access enforcement
    7. System Reports   — real-time enrollment summary & transaction audit trail
    8. Guided Tour      — sequential walkthrough of all patterns step-by-step
    9. Test Suite       — in-terminal runner for all 58 automated tests
"""

from __future__ import annotations

import io
import os
import sys
import unittest

# Fix Windows console encoding for Unicode box-drawing characters
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace"
    )

# Ensure the project root is on sys.path so `src.*` imports resolve
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.domain.course import CourseType
from src.patterns.factory import CourseFactory
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
    EnrollStudentCommand,
    DropStudentCommand,
    RecordGradeCommand,
    ChangeGradingStrategyCommand,
    CommandInvoker,
)
from src.patterns.state import (
    DraftState,
    OpenRegistrationState,
    InProgressState,
    CompletedState,
    CourseStateError,
)
from src.services.course_manager import CourseManager


# ── UI Helpers ──────────────────────────────────────────────────────────

def banner(title: str) -> None:
    """Print a decorative section header banner."""
    width = 66
    print()
    print("═" * width)
    print(f"  {title}")
    print("═" * width)


def section(title: str) -> None:
    """Print a sub-section divider."""
    print(f"\n── {title} {'─' * max(1, 52 - len(title))}")


def pause() -> None:
    """Wait for user acknowledgment, handling non-interactive environments."""
    print()
    try:
        input("  ▶ Press Enter to continue...")
    except (EOFError, KeyboardInterrupt):
        pass


def ensure_baseline_data(mgr: CourseManager) -> None:
    """Ensure standard courses and students exist for isolated menu navigation."""
    if "CS101" not in mgr.courses:
        mgr.create_course(
            CourseType.LECTURE, "CS101", "Intro to Computer Science", 3, 40, 600.0
        )
    if "CHEM201" not in mgr.courses:
        mgr.create_course(
            CourseType.LAB, "CHEM201", "Organic Chemistry Lab", 2, 20, 750.0
        )
    if "ENG102" not in mgr.courses:
        mgr.create_course(
            CourseType.ONLINE, "ENG102", "English Composition Online", 3, 100, 400.0
        )
    if "PHIL401" not in mgr.courses:
        mgr.create_course(
            CourseType.SEMINAR, "PHIL401", "Ethics in AI Seminar", 3, 15, 550.0
        )

    if "S001" not in mgr.students:
        mgr.register_student("S001", "Alice Johnson", "alice@uni.edu")
    if "S002" not in mgr.students:
        mgr.register_student("S002", "Bob Williams", "bob@uni.edu")
    if "S003" not in mgr.students:
        mgr.register_student("S003", "Carol Martinez", "carol@uni.edu")


# ── Demo Scenarios ──────────────────────────────────────────────────────

def demo_factory_method(mgr: CourseManager) -> None:
    """Feature 1: Factory Method Pattern — Course Creation."""
    banner("1. FACTORY METHOD PATTERN — Course Creation")

    print("\nRegistered Course Delivery Types in Factory Registry:")
    for ctype in CourseFactory.get_available_types():
        print(f"  • {ctype.name:<8} (key: '{ctype.value}')")

    courses_spec = [
        (CourseType.LECTURE,  "CS101",   "Intro to Computer Science",   3, 40, 600.0),
        (CourseType.LAB,      "CHEM201", "Organic Chemistry Lab",       2, 20, 750.0),
        (CourseType.ONLINE,   "ENG102",  "English Composition Online",  3, 100, 400.0),
        (CourseType.SEMINAR,  "PHIL401", "Ethics in AI Seminar",        3, 15, 550.0),
    ]

    section("Step 1.1: Instantiating concrete courses via CourseFactory")
    for ctype, cid, title, credits, cap, fee in courses_spec:
        course = mgr.create_course(ctype, cid, title, credits, cap, fee)
        print(f"  ✅ Created: {course}")
        print(f"     Subclass    : {type(course).__name__}")
        print(f"     Description : {course.get_description()}")
        print(f"     Requirements: {course.get_requirements()}")
        print()

    section("Step 1.2: Client decoupling & validation")
    print("  Factory encapsulates concrete constructors and enforces registered types.")


def demo_observer(mgr: CourseManager) -> None:
    """Feature 2: Observer Pattern — Course Notification System."""
    banner("2. OBSERVER PATTERN — Notification System")

    ensure_baseline_data(mgr)
    alice = mgr.get_student("S001")
    bob   = mgr.get_student("S002")
    carol = mgr.get_student("S003")

    section("Step 2.1: Enrolling students & auto-subscribing to course events")
    for sid in ["S001", "S002", "S003"]:
        mgr.enroll_student(sid, "CS101")
        print(f"  ✅ Enrolled {mgr.get_student(sid).name} into CS101")

    mgr.enroll_student("S001", "CHEM201")
    mgr.enroll_student("S002", "CHEM201")
    print(f"  ✅ Enrolled Alice & Bob into CHEM201")

    section("Step 2.2: Broadcasting announcements & assignments")
    n1 = mgr.post_announcement("CS101", "Midterm exam is on Oct 15 in Hall B!")
    print(f"  📢 CS101 announcement sent to {n1} subscribed observers")

    n2 = mgr.post_assignment("CS101", "Homework 3: Binary Trees and Recursion")
    print(f"  📝 CS101 assignment notification sent to {n2} subscribed observers")

    n3 = mgr.post_announcement("CHEM201", "Mandatory lab safety briefing on Monday")
    print(f"  📢 CHEM201 announcement sent to {n3} subscribed observers")

    section("Step 2.3: Student notification inbox inspection")
    for sid in ["S001", "S002", "S003"]:
        student = mgr.get_student(sid)
        print(f"\n  📬 {student.name}'s inbox ({len(student.notifications)} messages):")
        for msg in student.notifications[-3:]:  # Show recent 3
            print(f"     • {msg}")


def demo_strategy(mgr: CourseManager) -> None:
    """Feature 3: Strategy Pattern — Pluggable Grading Algorithms."""
    banner("3. STRATEGY PATTERN — Runtime Grading Algorithms")

    ensure_baseline_data(mgr)
    test_scores = [95.0, 82.0, 67.0, 55.0, 45.0]

    strategies = [
        StandardGradingStrategy(),
        PassFailGradingStrategy(pass_threshold=60.0),
        CurvedGradingStrategy(curve_points=7.0),
    ]

    section("Step 3.1: Evaluating scores across different grading policies")
    for strategy in strategies:
        mgr.set_grading_strategy("CS101", strategy)
        print(f"\n  Active Strategy: {strategy.get_strategy_name()}")
        for score in test_scores:
            grade = mgr.get_course("CS101").calculate_grade(score)
            print(f"    Raw Score {score:5.1f} → Letter Grade: {grade}")

    section("Step 3.2: Multi-component Weighted Grading Strategy")
    weighted = WeightedGradingStrategy(
        weights={"homework": 0.30, "midterm": 0.30, "final": 0.40}
    )
    mgr.set_grading_strategy("CS101", weighted)
    sample_scores = {"homework": 95, "midterm": 78, "final": 70}
    raw = weighted.get_weighted_score(sample_scores)
    letter = weighted.calculate_weighted_grade(sample_scores)
    print(f"    Grading Components: {sample_scores}")
    print(f"    Component Weights : {weighted.weights}")
    print(f"    Composite Average : {raw:.1f}% → Letter Grade: {letter}")

    section("Step 3.3: Grade release with Observer integration")
    mgr.set_grading_strategy("CS101", StandardGradingStrategy())
    for sid, score in [("S001", 92.0), ("S002", 78.0), ("S003", 61.0)]:
        letter = mgr.release_grade(sid, "CS101", score)
        student = mgr.get_student(sid)
        print(f"  🎯 {student.name:<16}: Score {score:.1f} → Grade {letter}")


def demo_decorator(mgr: CourseManager) -> None:
    """Feature 4: Decorator Pattern — Dynamic Course Add-ons & Fee Stacking."""
    banner("4. DECORATOR PATTERN — Course Add-On Features")

    ensure_baseline_data(mgr)
    # Start with fresh base course for clean demonstration
    base_course = CourseFactory.create_course(
        CourseType.LECTURE, "CS101", "Intro to Computer Science", 3, 40, 600.0
    )
    mgr.replace_course("CS101", base_course)

    section("Step 4.1: Inspecting base course")
    print(f"  Course       : {base_course}")
    print(f"  Base Tuition : ${base_course.get_total_fee():.2f}")
    print(f"  Requirements : {base_course.get_requirements()}")

    section("Step 4.2: Stacking decorators progressively")
    # 1. Honors
    course = HonorsDistinctionDecorator(base_course)
    mgr.replace_course("CS101", course)
    print(f"  + Added Honors Distinction  -> Total: ${course.get_total_fee():.2f}")

    # 2. Lab Access
    course = LabAccessPassDecorator(course)
    mgr.replace_course("CS101", course)
    print(f"  + Added 24/7 Lab Access Pass -> Total: ${course.get_total_fee():.2f}")

    # 3. Tutoring Support
    course = TutoringSupportDecorator(course)
    mgr.replace_course("CS101", course)
    print(f"  + Added Tutoring Support     -> Total: ${course.get_total_fee():.2f}")

    # 4. Certificate
    course = CertificateDecorator(course)
    mgr.replace_course("CS101", course)
    print(f"  + Added Final Certificate    -> Total: ${course.get_total_fee():.2f}")

    section("Step 4.3: Itemized tuition breakdown")
    print(f"  Base fee:       $600.00")
    print(f"  + Honors:       $150.00")
    print(f"  + Lab Access:   $100.00")
    print(f"  + Tutoring:     $200.00")
    print(f"  + Certificate:  $ 75.00")
    print(f"  ────────────────────────")
    print(f"  Total Tuition:  ${course.get_total_fee():.2f}")

    section("Step 4.4: Accumulated requirements from all decorators")
    for req in course.get_requirements():
        print(f"    • {req}")


def demo_command(mgr: CourseManager) -> None:
    """Feature 5: Command Pattern — Reversible Transactions, Undo/Redo & Audit Trail."""
    banner("5. COMMAND PATTERN — Transactions, Undo/Redo & Audit Trail")

    ensure_baseline_data(mgr)
    david = mgr.get_student("S004")
    if david is None:
        david = mgr.register_student("S004", "David Kim", "david@uni.edu")
    print(f"\nStudent Profile: {david}")

    section("Step 5.1: Executing enrollment transaction via Command")
    enroll_cmd = EnrollStudentCommand(mgr, "S004", "CHEM201")
    mgr.execute_command(enroll_cmd)
    print(f"  ✅ Executed: {enroll_cmd}")
    chem = mgr.get_course("CHEM201")
    print(f"     CHEM201 Roster: {[s.name for s in chem.enrolled_students]}")

    section("Step 5.2: Undoing enrollment (Rollback transaction)")
    mgr.undo()
    print("  ↩️ Undo applied!")
    print(f"     CHEM201 Roster after rollback: {[s.name for s in chem.enrolled_students]}")

    section("Step 5.3: Redoing enrollment (Roll-forward transaction)")
    mgr.redo()
    print("  ↪️ Redo applied!")
    print(f"     CHEM201 Roster after re-apply: {[s.name for s in chem.enrolled_students]}")

    section("Step 5.4: Grade updates with previous score restoration")
    mgr.set_grading_strategy("CHEM201", StandardGradingStrategy())

    # Initial Grade
    grade_cmd1 = RecordGradeCommand(mgr, "S004", "CHEM201", 78.0)
    mgr.execute_command(grade_cmd1)
    print(f"  📝 Initial score recorded: {david.name} = {david.grades.get('CHEM201')} (C)")

    # Typo Update
    grade_cmd2 = RecordGradeCommand(mgr, "S004", "CHEM201", 96.0)
    mgr.execute_command(grade_cmd2)
    print(f"  📝 Accidental score typo : {david.name} = {david.grades.get('CHEM201')} (A)")

    # Undo Typo
    mgr.undo()
    print(f"  ↩️ Undo rollback applied : {david.name} restored to = {david.grades.get('CHEM201')} (C)")

    section("Step 5.5: Chronological Transaction Audit Trail")
    for log_entry in mgr.get_audit_log():
        print(f"    {log_entry}")


def demo_state(mgr: CourseManager) -> None:
    """Feature 6: State Pattern — Course Lifecycle Management."""
    banner("6. STATE PATTERN — Academic Course Lifecycle")

    ensure_baseline_data(mgr)
    math = mgr.get_course("MATH201")
    if math is None:
        math = mgr.create_course(
            CourseType.LECTURE, "MATH201", "Linear Algebra", 3, max_students=30, base_fee=550.0
        )
    math.set_grading_strategy(StandardGradingStrategy())

    alice = mgr.get_student("S001")
    bob = mgr.get_student("S002")

    # Phase 1: DRAFT
    mgr.set_course_state("MATH201", DraftState())
    section(f"Phase 1: [{math.state.name}] — {math.state.get_status_description()}")
    print("  Action: Attempting to enroll Alice in DRAFT course...")
    try:
        math.enroll_student(alice)
    except CourseStateError as e:
        print(f"  ⛔ Access Blocked: {e}")

    # Phase 2: OPEN_REGISTRATION
    mgr.advance_course_state("MATH201")
    section(f"Phase 2: [{math.state.name}] — {math.state.get_status_description()}")
    enrolled = math.enroll_student(alice)
    print(f"  ✅ Enrollment Accepted: Alice is enrolled = {enrolled}")
    print("  Action: Attempting to release final grades before lectures commence...")
    try:
        math.calculate_grade(95.0)
    except CourseStateError as e:
        print(f"  ⛔ Access Blocked: {e}")

    # Phase 3: IN_PROGRESS
    mgr.advance_course_state("MATH201")
    section(f"Phase 3: [{math.state.name}] — {math.state.get_status_description()}")
    print("  Action: Attempting new student enrollment during ongoing semester...")
    try:
        math.enroll_student(bob)
    except CourseStateError as e:
        print(f"  ⛔ Access Blocked: {e}")
    grade = math.calculate_grade(92.0)
    print(f"  🎯 Grading Active: Alice's numeric score 92.0 evaluated → Grade {grade}")

    # Phase 4: COMPLETED
    mgr.advance_course_state("MATH201")
    section(f"Phase 4: [{math.state.name}] — {math.state.get_status_description()}")
    print("  Action: Attempting new enrollment in archived course...")
    try:
        math.enroll_student(bob)
    except CourseStateError as e:
        print(f"  ⛔ Access Blocked: {e}")

    print("  Action: Attempting grade modification on completed course record...")
    try:
        math.calculate_grade(80.0)
    except CourseStateError as e:
        print(f"  ⛔ Access Blocked: {e}")


def demo_system_reports(mgr: CourseManager) -> None:
    """Feature 7: System Status & Audit Reports."""
    banner("7. SYSTEM STATUS & AUDIT REPORTS")
    ensure_baseline_data(mgr)

    section("Active Course Enrollment Report")
    print(mgr.get_enrollment_report())

    section("Registrar Transaction Audit Trail")
    log = mgr.get_audit_log()
    if not log:
        print("  (No transactions recorded yet in this session.)")
    else:
        for entry in log:
            print(f"    {entry}")


def demo_run_test_suite() -> None:
    """Feature 9: Execute all 58 automated tests directly from terminal."""
    banner("AUTOMATED TEST SUITE (58 Tests)")
    loader = unittest.TestLoader()
    suite = loader.discover("tests")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        print(f"\n✅ All {result.testsRun} tests passed successfully!")
    else:
        print(f"\n❌ Failures: {len(result.failures)}, Errors: {len(result.errors)}")


def run_all_step_by_step(mgr: CourseManager) -> None:
    """Feature 8: Run the complete guided tour through all six patterns."""
    demo_factory_method(mgr)
    pause()

    demo_observer(mgr)
    pause()

    demo_strategy(mgr)
    pause()

    demo_decorator(mgr)
    pause()

    demo_command(mgr)
    pause()

    demo_state(mgr)
    pause()

    demo_system_reports(mgr)


# ── Interactive Navigation Menu ─────────────────────────────────────────

def print_navigation_menu() -> None:
    """Print the main terminal navigation menu."""
    print("\n" + "═" * 66)
    print("  STUDENT COURSE MANAGEMENT SYSTEM — Feature Navigation Menu")
    print("═" * 66)
    print("  [1] Factory Method Pattern  — Dynamic Course Creation by Type")
    print("  [2] Observer Pattern        — Event Subscriptions & Broadcasts")
    print("  [3] Strategy Pattern        — Pluggable Runtime Grading Algorithms")
    print("  [4] Decorator Pattern       — Course Add-ons & Surcharge Stacking")
    print("  [5] Command Pattern         — Reversible Actions, Undo/Redo & Audit")
    print("  [6] State Pattern           — Academic Lifecycle & Access Control")
    print("  [7] System Status & Reports — Enrollment Summary & Audit Log")
    print("  [8] Full Guided Tour        — Walkthrough of All Patterns Step-by-Step")
    print("  [9] Run Test Suite          — Execute all 58 Automated Tests")
    print("  [0] Exit Application")
    print("═" * 66)


def interactive_navigation(mgr: CourseManager) -> None:
    """Main interactive terminal loop allowing users to navigate any feature."""
    while True:
        print_navigation_menu()
        try:
            choice = input("  ▶ Select an option (0-9): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  Exiting navigation. Goodbye!")
            break

        if choice == "1":
            demo_factory_method(mgr)
            pause()
        elif choice == "2":
            demo_observer(mgr)
            pause()
        elif choice == "3":
            demo_strategy(mgr)
            pause()
        elif choice == "4":
            demo_decorator(mgr)
            pause()
        elif choice == "5":
            demo_command(mgr)
            pause()
        elif choice == "6":
            demo_state(mgr)
            pause()
        elif choice == "7":
            demo_system_reports(mgr)
            pause()
        elif choice == "8":
            run_all_step_by_step(mgr)
            pause()
        elif choice == "9":
            demo_run_test_suite()
            pause()
        elif choice == "0":
            print("\n  👋 Exited Student Course Management System. Goodbye!\n")
            break
        else:
            print(f"\n  ⚠️ Invalid option '{choice}'. Please enter a number from 0 to 9.")


# ── Entry Point ─────────────────────────────────────────────────────────

def main() -> None:
    """Application entry point supporting interactive menu and batch modes."""
    # Check flags
    if "--test" in sys.argv:
        demo_run_test_suite()
        return

    is_batch = "--all" in sys.argv or "-a" in sys.argv

    mgr = CourseManager()

    if is_batch:
        print()
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║   STUDENT COURSE MANAGEMENT SYSTEM — Automated Guided Tour ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        run_all_step_by_step(mgr)
        print("\n✅ All design pattern demonstrations complete!\n")
    else:
        print()
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║   STUDENT COURSE MANAGEMENT SYSTEM — Terminal Navigation   ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        interactive_navigation(mgr)


if __name__ == "__main__":
    main()
