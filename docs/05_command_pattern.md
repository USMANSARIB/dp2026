# Command Pattern

## 1. Intent

> **Encapsulate a request as an object, thereby letting you parameterize clients with different requests, queue or log requests, and support undoable operations.**
>
> — *Design Patterns: Elements of Reusable Object-Oriented Software* (GoF)

The Command pattern is a **behavioural** design pattern that turns a request into a standalone object that contains all information about the request. This transformation lets you pass requests as arguments, delay or queue a request's execution, maintain execution history, and support reversible operations (**Undo / Redo**).

---

## 2. Problem It Solves

In the Student Course Management System, critical registrar operations are performed daily:

- 🎓 **Enrolling** a student in a course
- ❌ **Dropping** a student from a course
- 🎯 **Recording or modifying** a student's grade
- ⚙️ **Changing grading policies** on an active course

**Without** the Command pattern, operations are executed directly and destructively:

```python
# ❌ Direct execution — irreversible, no history, no rollback
def change_grade(student, course_id, new_score):
    student.grades[course_id] = new_score  # Old score is lost forever!
```

Problems:
- **No Undo/Redo**: If an instructor accidentally inputs `58.0` instead of `85.0`, or a student drops a class by mistake during add/drop week, there is no way to automatically revert to the previous state.
- **No Audit Trail**: The system has no centralized log recording who performed what action, when, and whether it succeeded.
- **Tight Coupling**: UI or API controllers must know the exact details of receivers and execution logic rather than executing standardized command objects.

---

## 3. Solution — Architecture

```
┌─────────────────────────────────┐
│         CommandInvoker          │  ← Invoker
│  ─────────────────────────────  │
│  - _undo_stack: list[Command]   │
│  - _redo_stack: list[Command]   │
│  - _audit_log:  list[str]       │
│  + execute_command(cmd)         │
│  + undo()                       │
│  + redo()                       │
└────────────────┬────────────────┘
                 │ executes / manages
                 ▼
        ┌──────────────────┐
        │     Command      │  ← Command Interface (ABC)
        │  ──────────────  │
        │  + execute()     │
        │  + undo()        │
        │  + redo()        │
        └────────┬─────────┘
                 │
   ┌─────────────┼───────────────┬────────────────────────────┐
   ▼             ▼               ▼                            ▼
EnrollStudent  DropStudent   RecordGrade            ChangeGradingStrategy
   Command       Command       Command                     Command
   │             │               │                            │
   └─────────────┴───────┬───────┴────────────────────────────┘
                         │ delegates to
                         ▼
           ┌────────────────────────────┐
           │ CourseManager / Course /   │  ← Receivers
           │ Student                    │
           └────────────────────────────┘
```

---

## 4. Code Walkthrough

### 4.1 Abstract Command Interface

```python
# src/patterns/command.py
class Command(ABC):
    def __init__(self) -> None:
        self.created_at: datetime = datetime.now()
        self.executed: bool = False

    @abstractmethod
    def execute(self) -> bool:
        """Execute the command."""

    @abstractmethod
    def undo(self) -> bool:
        """Undo the effect of this command."""

    def redo(self) -> bool:
        """Re-apply this command."""
        return self.execute()

    @abstractmethod
    def get_description(self) -> str:
        """Human-readable summary."""
```

### 4.2 Concrete Commands

#### `EnrollStudentCommand` & `DropStudentCommand`

Symmetric commands where `undo()` delegates to the inverse operation:

```python
class EnrollStudentCommand(Command):
    def __init__(self, manager: CourseManager, student_id: str, course_id: str) -> None:
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
```

#### `RecordGradeCommand` (State-Preserving Undo)

Captures previous score prior to modification so that rolling back restores the exact pre-existing grade:

```python
class RecordGradeCommand(Command):
    def __init__(self, manager: CourseManager, student_id: str, course_id: str, score: float) -> None:
        super().__init__()
        self.manager = manager
        self.student_id = student_id
        self.course_id = course_id
        self.score = score
        self._previous_score: float | None = None
        self._had_previous_grade: bool = False

    def execute(self) -> bool:
        student = self.manager.get_student(self.student_id)
        if not student:
            return False
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
        if self._had_previous_grade and self._previous_score is not None:
            self.manager.release_grade(self.student_id, self.course_id, self._previous_score)
        else:
            student.grades.pop(self.course_id, None)
        self.executed = False
        return True
```

### 4.3 The Invoker (`CommandInvoker`)

The invoker manages execution, the undo stack, the redo stack, and an immutable audit log:

```python
@dataclass
class CommandInvoker:
    _undo_stack: list[Command] = field(default_factory=list)
    _redo_stack: list[Command] = field(default_factory=list)
    _audit_log: list[str] = field(default_factory=list)

    def execute_command(self, command: Command) -> bool:
        success = command.execute()
        if success:
            self._undo_stack.append(command)
            self._redo_stack.clear()
            self._audit_log.append(f"EXECUTE: {command.get_description()}")
        return success

    def undo(self) -> bool:
        if not self._undo_stack:
            return False
        cmd = self._undo_stack.pop()
        success = cmd.undo()
        if success:
            self._redo_stack.append(cmd)
            self._audit_log.append(f"UNDO: {cmd.get_description()}")
        return success

    def redo(self) -> bool:
        if not self._redo_stack:
            return False
        cmd = self._redo_stack.pop()
        success = cmd.redo()
        if success:
            self._undo_stack.append(cmd)
            self._audit_log.append(f"REDO: {cmd.get_description()}")
        return success
```

---

## 5. Client Usage & Audit Trail

```python
invoker = CommandInvoker()

# 1. Enroll Alice
cmd1 = EnrollStudentCommand(mgr, "S001", "CS101")
invoker.execute_command(cmd1)

# 2. Record Grade
cmd2 = RecordGradeCommand(mgr, "S001", "CS101", 95.0)
invoker.execute_command(cmd2)

# 3. Undo grade recording
invoker.undo()  # S001's grade is removed or restored

# 4. Redo grade recording
invoker.redo()  # 95.0 is reapplied

# 5. Check audit trail
for entry in invoker.get_audit_log():
    print(entry)
```

Output:
```
[14:02:10] EXECUTE: Enroll student 'S001' in course 'CS101'
[14:02:11] EXECUTE: Record grade 95.0 for student 'S001' in course 'CS101'
[14:02:15] UNDO   : Record grade 95.0 for student 'S001' in course 'CS101'
[14:02:17] REDO   : Record grade 95.0 for student 'S001' in course 'CS101'
```

---

## 6. Trade-Offs

| Pros | Cons |
|------|------|
| **Single Responsibility Principle**: Decouples classes invoking operations from classes performing them | Increases class count (each action requires a class) |
| **Open/Closed Principle**: Add new reversible commands without breaking existing code | Slightly higher memory footprint storing previous states |
| **Undo / Redo**: Built-in support for rollback and roll-forward | Commands with side effects (external emails) need careful undo handling |
| **Audit Log**: Transparent record of all system operations | — |

---

## 7. Related Files

- [`src/patterns/command.py`](../src/patterns/command.py) — Full Command pattern implementation
- [`src/services/course_manager.py`](../src/services/course_manager.py) — Service integration via `execute_command()`, `undo()`, `redo()`
- [`tests/test_patterns.py`](../tests/test_patterns.py) — `TestCommandPattern` test suite
