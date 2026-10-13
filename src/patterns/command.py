"""
Command Pattern — Reversible Course Operations & Transaction History.

This module demonstrates the **Command** behavioural design pattern.
Requests (such as enrolling a student, dropping a student, or recording a
grade) are encapsulated as standalone command objects with `execute()`,
`undo()`, and `redo()` capabilities.

Key participants:
    - **Command (ABC)**: Common interface declaring `execute()` and `undo()`.
    - **Concrete Commands**:
        - `EnrollStudentCommand`: Enrolls a student; rolls back on undo.
        - `DropStudentCommand`: Drops a student; re-enrolls on undo.
        - `RecordGradeCommand`: Records a numeric score; restores previous score on undo.
        - `ChangeGradingStrategyCommand`: Swaps grading strategy; restores previous on undo.
    - **Invoker (`CommandInvoker`)**: Executes commands, manages undo/redo stacks,
      and preserves an audit trail of transactions.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.patterns.strategy import GradingStrategy
    from src.services.course_manager import CourseManager


# ======================================================================
# Abstract Command
# ======================================================================

class Command(ABC):
    """Abstract base class for all reversible commands.

    Every concrete command encapsulates a receiver, arguments, and previous
    state needed to safely undo the operation.
    """

    def __init__(self) -> None:
        self.created_at: datetime = datetime.now()
        self.executed: bool = False

    @abstractmethod
    def execute(self) -> bool:
        """Execute the command.

        Returns:
            True if execution succeeded, False otherwise.
        """

    @abstractmethod
    def undo(self) -> bool:
        """Undo the effect of this command.

        Returns:
            True if undo succeeded, False otherwise.
        """

    def redo(self) -> bool:
        """Re-apply this command.

        Default implementation re-invokes `execute()`.
        """
        return self.execute()

    @abstractmethod
    def get_description(self) -> str:
        """Return a human-readable summary of this command."""

    def __str__(self) -> str:
        return self.get_description()


# ======================================================================
# Concrete Commands
# ======================================================================

class EnrollStudentCommand(Command):
    """Encapsulates enrolling a student in a course with undo support."""

    def __init__(
        self,
        manager: "CourseManager",
        student_id: str,
        course_id: str,
    ) -> None:
        super().__init__()
        self.manager = manager
        self.student_id = student_id
        self.course_id = course_id

    def execute(self) -> bool:
        success = self.manager.enroll_student(self.student_id, self.course_id)
        self.executed = success
        return success

    def undo(self) -> bool:
        if not self.executed:
            return False
        success = self.manager.drop_student(self.student_id, self.course_id)
        if success:
            self.executed = False
        return success

    def get_description(self) -> str:
        return f"Enroll student '{self.student_id}' in course '{self.course_id}'"


class DropStudentCommand(Command):
    """Encapsulates dropping a student from a course with undo support."""

    def __init__(
        self,
        manager: "CourseManager",
        student_id: str,
        course_id: str,
    ) -> None:
        super().__init__()
        self.manager = manager
        self.student_id = student_id
        self.course_id = course_id

    def execute(self) -> bool:
        success = self.manager.drop_student(self.student_id, self.course_id)
        self.executed = success
        return success

    def undo(self) -> bool:
        if not self.executed:
            return False
        success = self.manager.enroll_student(self.student_id, self.course_id)
        if success:
            self.executed = False
        return success

    def get_description(self) -> str:
        return f"Drop student '{self.student_id}' from course '{self.course_id}'"


class RecordGradeCommand(Command):
    """Encapsulates recording a student grade with rollback to previous score."""

    def __init__(
        self,
        manager: "CourseManager",
        student_id: str,
        course_id: str,
        score: float,
    ) -> None:
        super().__init__()
        self.manager = manager
        self.student_id = student_id
        self.course_id = course_id
        self.score = score
        self._previous_score: float | None = None
        self._had_previous_grade: bool = False

    def execute(self) -> bool:
        student = self.manager.get_student(self.student_id)
        course = self.manager.get_course(self.course_id)
        if student is None or course is None:
            return False

        # Capture previous score if any
        if self.course_id in student.grades:
            self._had_previous_grade = True
            self._previous_score = student.grades[self.course_id]
        else:
            self._had_previous_grade = False
            self._previous_score = None

        result = self.manager.release_grade(self.student_id, self.course_id, self.score)
        self.executed = result is not None
        return self.executed

    def undo(self) -> bool:
        if not self.executed:
            return False

        student = self.manager.get_student(self.student_id)
        if student is None:
            return False

        if self._had_previous_grade and self._previous_score is not None:
            # Restore previous grade
            self.manager.release_grade(
                self.student_id, self.course_id, self._previous_score
            )
        else:
            # Remove grade entry entirely
            student.grades.pop(self.course_id, None)

        self.executed = False
        return True

    def get_description(self) -> str:
        return (
            f"Record grade {self.score:.1f} for student '{self.student_id}' "
            f"in course '{self.course_id}'"
        )


class ChangeGradingStrategyCommand(Command):
    """Encapsulates swapping grading strategies with rollback support."""

    def __init__(
        self,
        manager: "CourseManager",
        course_id: str,
        new_strategy: "GradingStrategy",
    ) -> None:
        super().__init__()
        self.manager = manager
        self.course_id = course_id
        self.new_strategy = new_strategy
        self._previous_strategy: "GradingStrategy | None" = None

    def execute(self) -> bool:
        course = self.manager.get_course(self.course_id)
        if course is None:
            return False

        self._previous_strategy = course.grading_strategy
        success = self.manager.set_grading_strategy(self.course_id, self.new_strategy)
        self.executed = success
        return success

    def undo(self) -> bool:
        if not self.executed or self._previous_strategy is None:
            return False

        success = self.manager.set_grading_strategy(
            self.course_id, self._previous_strategy
        )
        if success:
            self.executed = False
        return success

    def get_description(self) -> str:
        return (
            f"Change grading strategy for course '{self.course_id}' "
            f"to '{self.new_strategy.get_strategy_name()}'"
        )


# ======================================================================
# Invoker / Transaction Manager
# ======================================================================

@dataclass
class CommandInvoker:
    """Invoker that executes commands and manages undo / redo history.

    Attributes:
        _undo_stack: Stack of executed commands eligible for undo.
        _redo_stack: Stack of undone commands eligible for redo.
        _audit_log: Chronological list of recorded execution events.
    """

    _undo_stack: list[Command] = field(default_factory=list, repr=False)
    _redo_stack: list[Command] = field(default_factory=list, repr=False)
    _audit_log: list[str] = field(default_factory=list, repr=False)

    def execute_command(self, command: Command) -> bool:
        """Execute a command, record it to undo stack, and clear redo stack."""
        success = command.execute()
        timestamp = datetime.now().strftime("%H:%M:%S")
        if success:
            self._undo_stack.append(command)
            self._redo_stack.clear()
            self._audit_log.append(f"[{timestamp}] EXECUTE: {command.get_description()}")
        else:
            self._audit_log.append(f"[{timestamp}] FAILED : {command.get_description()}")
        return success

    def undo(self) -> bool:
        """Undo the most recently executed command."""
        if not self._undo_stack:
            return False

        command = self._undo_stack.pop()
        success = command.undo()
        timestamp = datetime.now().strftime("%H:%M:%S")
        if success:
            self._redo_stack.append(command)
            self._audit_log.append(f"[{timestamp}] UNDO   : {command.get_description()}")
        else:
            self._audit_log.append(f"[{timestamp}] UNDO_FAIL: {command.get_description()}")
        return success

    def redo(self) -> bool:
        """Redo the most recently undone command."""
        if not self._redo_stack:
            return False

        command = self._redo_stack.pop()
        success = command.redo()
        timestamp = datetime.now().strftime("%H:%M:%S")
        if success:
            self._undo_stack.append(command)
            self._audit_log.append(f"[{timestamp}] REDO   : {command.get_description()}")
        else:
            self._audit_log.append(f"[{timestamp}] REDO_FAIL: {command.get_description()}")
        return success

    @property
    def can_undo(self) -> bool:
        """Whether there are actions that can be undone."""
        return len(self._undo_stack) > 0

    @property
    def can_redo(self) -> bool:
        """Whether there are actions that can be redone."""
        return len(self._redo_stack) > 0

    def get_audit_log(self) -> list[str]:
        """Return a copy of the chronological audit log."""
        return list(self._audit_log)

    def clear(self) -> None:
        """Clear all stacks and audit log."""
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._audit_log.clear()
