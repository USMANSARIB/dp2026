"""
Student Course Management System — Interactive CLI Demo.

Runs a guided demonstration of all four design patterns:
    1. Factory Method  — creating different course types
    2. Observer         — broadcasting notifications to students
    3. Strategy         — switching grading algorithms at runtime
    4. Decorator        — dynamically adding features to a course
"""

from __future__ import annotations

import sys
import os
import io

# Fix Windows console encoding for Unicode box-drawing characters
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace"
    )

# Ensure the project root is on sys.path so `src.*` imports resolve
# regardless of which directory the script is launched from.
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
from src.services.course_manager import CourseManager


# ── Helpers ─────────────────────────────────────────────────────────────

def banner(title: str) -> None:
    width = 64
    print()
    print("═" * width)
    print(f"  {title}")
    print("═" * width)


def section(title: str) -> None:
    print(f"\n── {title} {'─' * max(1, 50 - len(title))}")


def pause() -> None:
    print()
    input("  ▶ Press Enter to continue...")


# ── Demo Scenarios ──────────────────────────────────────────────────────

def demo_factory_method(mgr: CourseManager) -> None:
    """Demonstrate the Factory Method pattern."""
    banner("1. FACTORY METHOD PATTERN — Course Creation")

    print("\nAvailable course types:", CourseFactory.get_available_types())
    print()

    courses_spec = [
        (CourseType.LECTURE,  "CS101", "Intro to Computer Science",   3, 40, 600.0),
        (CourseType.LAB,      "CHEM201", "Organic Chemistry Lab",     2, 20, 750.0),
        (CourseType.ONLINE,   "ENG102", "English Composition Online", 3, 100, 400.0),
        (CourseType.SEMINAR,  "PHIL401", "Ethics in AI Seminar",      3, 15, 550.0),
    ]

    for ctype, cid, title, credits, cap, fee in courses_spec:
        course = mgr.create_course(ctype, cid, title, credits, cap, fee)
        print(f"  ✅ Created: {course}")
        print(f"     Type       : {type(course).__name__}")
        print(f"     Description: {course.get_description()}")
        print(f"     Requirements: {course.get_requirements()}")
        print()


def demo_observer(mgr: CourseManager) -> None:
    """Demonstrate the Observer pattern."""
    banner("2. OBSERVER PATTERN — Notification System")

    # Register students
    alice = mgr.register_student("S001", "Alice Johnson", "alice@uni.edu")
    bob   = mgr.register_student("S002", "Bob Williams", "bob@uni.edu")
    carol = mgr.register_student("S003", "Carol Martinez", "carol@uni.edu")

    print(f"\nRegistered students: {alice}, {bob}, {carol}")

    # Enroll students (auto-subscribes them to notifications)
    section("Enrolling students in CS101")
    for student_id in ["S001", "S002", "S003"]:
        mgr.enroll_student(student_id, "CS101")

    section("Enrolling Alice & Bob in CHEM201")
    mgr.enroll_student("S001", "CHEM201")
    mgr.enroll_student("S002", "CHEM201")

    # Post announcements
    section("Broadcasting announcements")
    notified = mgr.post_announcement("CS101", "Midterm exam is on Oct 15!")
    print(f"  📢 CS101 announcement sent to {notified} observers")

    notified = mgr.post_assignment("CS101", "Homework 3: Recursion")
    print(f"  📝 CS101 assignment notification sent to {notified} observers")

    notified = mgr.post_announcement("CHEM201", "Lab safety briefing on Monday")
    print(f"  📢 CHEM201 announcement sent to {notified} observers")

    # Show notifications received by each student
    section("Student notification inboxes")
    for sid in ["S001", "S002", "S003"]:
        student = mgr.get_student(sid)
        print(f"\n  📬 {student.name}'s notifications ({len(student.notifications)}):")
        for n in student.notifications:
            print(f"     • {n}")


def demo_strategy(mgr: CourseManager) -> None:
    """Demonstrate the Strategy pattern."""
    banner("3. STRATEGY PATTERN — Grading Algorithms")

    test_scores = [95.0, 82.0, 67.0, 55.0, 45.0]

    strategies = [
        StandardGradingStrategy(),
        PassFailGradingStrategy(pass_threshold=60.0),
        CurvedGradingStrategy(curve_points=7.0),
    ]

    for strategy in strategies:
        section(strategy.get_strategy_name())
        mgr.set_grading_strategy("CS101", strategy)
        for score in test_scores:
            grade = mgr.get_course("CS101").calculate_grade(score)
            print(f"    Score {score:5.1f} → {grade}")

    # Weighted grading demo
    section("Weighted Grading")
    weighted = WeightedGradingStrategy(
        weights={"homework": 0.30, "midterm": 0.30, "final": 0.40}
    )
    mgr.set_grading_strategy("CS101", weighted)
    sample_scores = {"homework": 95, "midterm": 78, "final": 70}
    raw = weighted.get_weighted_score(sample_scores)
    letter = weighted.calculate_weighted_grade(sample_scores)
    print(f"    Components: {sample_scores}")
    print(f"    Weights:    {weighted.weights}")
    print(f"    Weighted avg: {raw:.1f} → {letter}")

    # Grade release with notification
    section("Releasing grades (Observer + Strategy)")
    mgr.set_grading_strategy("CS101", StandardGradingStrategy())
    for sid, score in [("S001", 92.0), ("S002", 78.0), ("S003", 61.0)]:
        letter = mgr.release_grade(sid, "CS101", score)
        student = mgr.get_student(sid)
        print(f"  🎯 {student.name}: {score} → {letter}")


def demo_decorator(mgr: CourseManager) -> None:
    """Demonstrate the Decorator pattern."""
    banner("4. DECORATOR PATTERN — Course Add-Ons")

    course = mgr.get_course("CS101")
    section("Base course")
    print(f"  {course}")
    print(f"  Fee: ${course.get_total_fee():.2f}")
    print(f"  Requirements: {course.get_requirements()}")

    # Stack decorators one at a time
    section("Adding Honors Distinction")
    course = HonorsDistinctionDecorator(course)
    mgr.replace_course("CS101", course)
    print(f"  {course}")
    print(f"  Fee: ${course.get_total_fee():.2f}")
    print(f"  Requirements: {course.get_requirements()}")

    section("Adding Lab Access Pass")
    course = LabAccessPassDecorator(course)
    mgr.replace_course("CS101", course)
    print(f"  {course}")
    print(f"  Fee: ${course.get_total_fee():.2f}")

    section("Adding Tutoring Support")
    course = TutoringSupportDecorator(course)
    mgr.replace_course("CS101", course)
    print(f"  {course}")
    print(f"  Fee: ${course.get_total_fee():.2f}")

    section("Adding Certificate of Completion")
    course = CertificateDecorator(course)
    mgr.replace_course("CS101", course)
    print(f"  {course}")
    print(f"  Fee: ${course.get_total_fee():.2f}")
    print(f"  Description: {course.get_description()}")

    section("Fee breakdown")
    print(f"  Base fee:       $600.00")
    print(f"  + Honors:       $150.00")
    print(f"  + Lab Access:   $100.00")
    print(f"  + Tutoring:     $200.00")
    print(f"  + Certificate:  $ 75.00")
    print(f"  ────────────────────────")
    print(f"  Total:          ${course.get_total_fee():.2f}")

    section("All requirements (accumulated)")
    for req in course.get_requirements():
        print(f"    • {req}")


def demo_enrollment_report(mgr: CourseManager) -> None:
    """Print a final enrollment report."""
    banner("FINAL ENROLLMENT REPORT")
    print(mgr.get_enrollment_report())


# ── Main ────────────────────────────────────────────────────────────────

def main() -> None:
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║   STUDENT COURSE MANAGEMENT SYSTEM — Design Patterns Demo  ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    mgr = CourseManager()

    demo_factory_method(mgr)
    pause()

    demo_observer(mgr)
    pause()

    demo_strategy(mgr)
    pause()

    demo_decorator(mgr)
    pause()

    demo_enrollment_report(mgr)

    print("\n✅ All design pattern demonstrations complete!\n")


if __name__ == "__main__":
    main()
