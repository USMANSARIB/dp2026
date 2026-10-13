# State Pattern

## 1. Intent

> **Allow an object to alter its behavior when its internal state changes. The object will appear to change its class.**
>
> — *Design Patterns: Elements of Reusable Object-Oriented Software* (GoF)

The State pattern is a **behavioural** design pattern that lets an object change its behavior when its internal state changes. It extracts state-specific behaviors into separate state classes and makes the original object delegate execution to an instance of one of these state classes.

---

## 2. Problem It Solves

In academic institutions, a course transitions through well-defined lifecycle phases across a semester:

```
[ DRAFT ] ──▶ [ OPEN_REGISTRATION ] ──▶ [ IN_PROGRESS ] ──▶ [ COMPLETED ]
```

Each phase imposes strict academic policies:

| Phase | Enroll Students? | Drop Students? | Grade / Assignments? | Modify Details? |
|-------|------------------|----------------|----------------------|-----------------|
| **DRAFT** | ❌ Prohibited | ❌ Prohibited | ❌ Prohibited | ✅ Allowed |
| **OPEN_REGISTRATION** | ✅ Allowed | ✅ Allowed | ❌ Prohibited | ❌ Locked |
| **IN_PROGRESS** | ❌ Closed | ✅ Allowed | ✅ Allowed | ❌ Locked |
| **COMPLETED** | ❌ Archived | ❌ Archived | ❌ Read-only | ❌ Archived |

**Without** the State pattern, methods become bloated with brittle conditional checks:

```python
# ❌ Spaghetti conditionals scattered across multiple methods
class Course:
    def enroll_student(self, student):
        if self.status == "DRAFT":
            raise ValueError("Draft course cannot accept students!")
        elif self.status == "IN_PROGRESS":
            raise ValueError("Enrollment closed for ongoing semester!")
        elif self.status == "COMPLETED":
            raise ValueError("Course is archived!")
        elif self.status == "OPEN_REGISTRATION":
            # Actual enrollment logic...
            pass
```

Problems:
- Adding or modifying a state requires modifying **every single method** (`enroll`, `drop`, `grade`, `advance`).
- Violates the **Open/Closed Principle** and **Single Responsibility Principle**.
- State transitions are scattered, prone to invalid state leaps.

---

## 3. Solution — Architecture

```
                    ┌────────────────────────────┐
                    │          Course            │  ← Context
                    │  ────────────────────────  │
                    │  - state: CourseState      │
                    │  + set_state(state)        │
                    │  + advance_state()         │
                    │  + enroll_student(student) │
                    │  + calculate_grade(score)  │
                    └─────────────┬──────────────┘
                                  │ delegates to current state
                                  ▼
                    ┌────────────────────────────┐
                    │        CourseState         │  ← State Interface (ABC)
                    │  ────────────────────────  │
                    │  + enroll_student(c, s)    │
                    │  + remove_student(c, s)    │
                    │  + calculate_grade(c, sc)  │
                    │  + advance(course)         │
                    └─────────────┬──────────────┘
                                  │
      ┌──────────────────┬────────┴─────────┬──────────────────┐
      ▼                  ▼                  ▼                  ▼
┌────────────┐  ┌──────────────────┐  ┌─────────────┐  ┌───────────────┐
│ DraftState │  │ OpenRegistration │  │ InProgress  │  │ Completed     │
│            │  │      State       │  │    State    │  │     State     │
└────────────┘  └──────────────────┘  └─────────────┘  └───────────────┘
      │ advance()        │ advance()        │ advance()        │ advance()
      └─────────────────▶└─────────────────▶└─────────────────▶❌ (Terminal)
```

---

## 4. Code Walkthrough

### 4.1 State Interface & Custom Exception

```python
# src/patterns/state.py
class CourseStateError(Exception):
    """Raised when an action is prohibited in the current lifecycle state."""

class CourseState(ABC):
    name: str = "ABSTRACT"
    can_enroll: bool = False
    can_drop: bool = False
    can_grade: bool = False

    @abstractmethod
    def enroll_student(self, course: "Course", student: "Student") -> bool: ...

    @abstractmethod
    def remove_student(self, course: "Course", student: "Student") -> bool: ...

    @abstractmethod
    def calculate_grade(self, course: "Course", score: float) -> str: ...

    @abstractmethod
    def advance(self, course: "Course") -> "CourseState": ...
```

### 4.2 Concrete Lifecycle States

#### `DraftState`
```python
class DraftState(CourseState):
    name: str = "DRAFT"
    can_enroll: bool = False

    def enroll_student(self, course: Course, student: Student) -> bool:
        raise CourseStateError(
            f"Cannot enroll in '{course.course_id}': course is currently in DRAFT state."
        )

    def advance(self, course: Course) -> CourseState:
        next_state = OpenRegistrationState()
        course.set_state(next_state)
        return next_state
```

#### `OpenRegistrationState`
```python
class OpenRegistrationState(CourseState):
    name: str = "OPEN_REGISTRATION"
    can_enroll: bool = True
    can_grade: bool = False

    def enroll_student(self, course: Course, student: Student) -> bool:
        return course._do_enroll(student)

    def calculate_grade(self, course: Course, score: float) -> str:
        raise CourseStateError(
            f"Cannot calculate grade for '{course.course_id}': registration is open "
            "but lectures have not commenced."
        )

    def advance(self, course: Course) -> CourseState:
        next_state = InProgressState()
        course.set_state(next_state)
        return next_state
```

#### `InProgressState` & `CompletedState`
- `InProgressState` locks new enrollments, permits drops/withdrawals, and enables grading via attached strategies.
- `CompletedState` is a terminal state that permanently disallows any mutations (enrollment, dropping, regrading).

### 4.3 Context Delegation in `Course`

```python
# src/domain/course.py
@dataclass
class Course(ABC):
    state: "CourseState | None" = field(default=None, repr=False)

    def enroll_student(self, student: Student) -> bool:
        if self.state is not None:
            return self.state.enroll_student(self, student)
        return self._do_enroll(student)

    def advance_state(self) -> CourseState:
        if self.state is None:
            raise ValueError(f"Course '{self.course_id}' has no state assigned.")
        return self.state.advance(self)
```

---

## 5. Lifecycle Transitions in Action

```python
course = CourseFactory.create_course(CourseType.LECTURE, "CS201", "Data Structures", 3)
course.set_state(DraftState())

# 1. Attempt enrollment in DRAFT -> Blocked
try:
    course.enroll_student(alice)
except CourseStateError as e:
    print(e)  # Cannot enroll in 'CS201': course is currently in DRAFT state.

# 2. Advance to OPEN_REGISTRATION -> Enrollment succeeds
course.advance_state()  # Now OpenRegistrationState
course.enroll_student(alice)  # True

# 3. Advance to IN_PROGRESS -> New enrollments blocked, grading enabled
course.advance_state()  # Now InProgressState
course.calculate_grade(92.0)  # "A"

# 4. Advance to COMPLETED -> Finalized and read-only
course.advance_state()  # Now CompletedState
```

---

## 6. Trade-Offs

| Pros | Cons |
|------|------|
| **Single Responsibility Principle**: Organizes the code related to particular states into separate classes | Introduces multiple state classes |
| **Open/Closed Principle**: Introduce new states without changing existing state classes or context | Can be overkill if a state machine has only 1-2 trivial states |
| Eliminates monolithic, error-prone `if/elif/else` conditional logic | States must coordinate transitions cleanly with the context |
| Clear validation and informative error messages | — |

---

## 7. Related Files

- [`src/patterns/state.py`](../src/patterns/state.py) — Full State pattern implementation
- [`src/domain/course.py`](../src/domain/course.py) — Course context integration
- [`src/services/course_manager.py`](../src/services/course_manager.py) — Service orchestration (`set_course_state()`, `advance_course_state()`)
- [`tests/test_patterns.py`](../tests/test_patterns.py) — `TestStatePattern` test suite
