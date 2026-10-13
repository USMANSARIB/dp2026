# Student Course Management System — Design Patterns

A Python project demonstrating six classic **Gang of Four (GoF)** design patterns
through a realistic Student Course Management System.

---

## Design Patterns Used

| # | Pattern | Category | Module | Purpose |
|---|---------|----------|--------|---------|
| 1 | **Factory Method** | Creational | [`factory.py`](src/patterns/factory.py) | Create different course types (`Lecture`, `Lab`, `Online`, `Seminar`) without coupling to concrete classes |
| 2 | **Observer** | Behavioural | [`observer.py`](src/patterns/observer.py) | Broadcast notifications (announcements, grades, assignments, state changes) to enrolled students |
| 3 | **Strategy** | Behavioural | [`strategy.py`](src/patterns/strategy.py) | Swap grading algorithms at runtime (`Standard`, `PassFail`, `Curved`, `Weighted`) |
| 4 | **Decorator** | Structural | [`decorator.py`](src/patterns/decorator.py) | Dynamically add features (`Honors`, `Lab Access`, `Tutoring`, `Certificate`) to any course |
| 5 | **Command** | Behavioural | [`command.py`](src/patterns/command.py) | Encapsulate operations (`Enroll`, `Drop`, `RecordGrade`, `ChangeStrategy`) with Undo / Redo & Audit Trail |
| 6 | **State** | Behavioural | [`state.py`](src/patterns/state.py) | Govern course lifecycle phases (`Draft`, `OpenRegistration`, `InProgress`, `Completed`) & enforce transition rules |

### 📖 Pattern Documentation

Each pattern has a dedicated document explaining the theory, architecture, code walkthrough, and trade-offs:

- [01 — Factory Method Pattern](docs/01_factory_method_pattern.md)
- [02 — Observer Pattern](docs/02_observer_pattern.md)
- [03 — Strategy Pattern](docs/03_strategy_pattern.md)
- [04 — Decorator Pattern](docs/04_decorator_pattern.md)
- [05 — Command Pattern](docs/05_command_pattern.md)
- [06 — State Pattern](docs/06_state_pattern.md)

---

## Project Structure

```
dp/
├── README.md
├── docs/
│   ├── 01_factory_method_pattern.md
│   ├── 02_observer_pattern.md
│   ├── 03_strategy_pattern.md
│   ├── 04_decorator_pattern.md
│   ├── 05_command_pattern.md
│   └── 06_state_pattern.md
├── src/
│   ├── __init__.py
│   ├── main.py                      # Interactive CLI demo
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── student.py               # Student entity (Observer)
│   │   └── course.py                # Abstract Course base, CourseType & State hooks
│   ├── patterns/
│   │   ├── __init__.py
│   │   ├── factory.py               # Factory Method pattern
│   │   ├── observer.py              # Observer pattern
│   │   ├── strategy.py              # Strategy pattern
│   │   ├── decorator.py             # Decorator pattern
│   │   ├── command.py               # Command pattern (Undo/Redo & Audit)
│   │   └── state.py                 # State pattern (Course lifecycle)
│   └── services/
│       ├── __init__.py
│       └── course_manager.py        # Service layer orchestrating all patterns
└── tests/
    ├── __init__.py
    └── test_patterns.py             # 58 unit + integration tests
```

---

## Quick Start

### Prerequisites

- Python 3.10+ (uses `match`, `|` union types, modern type hints)

### Run the Interactive Demo

```bash
python src/main.py
```

This walks you through all six patterns step by step with real course management scenarios.

### Run the Tests

```bash
python -m unittest discover -s tests -v
```

Expected output: **58 tests, all passing**.

---

## How the Patterns Work Together

```
┌─────────────────────────────────────────────────────────────┐
│                     CourseManager                            │
│                  (Service / Façade)                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. FACTORY METHOD creates courses ──────────────────────┐  │
│                                                          │  │
│  2. OBSERVER notifies enrolled students ◄────────────────┤  │
│                                                          │  │
│  3. STRATEGY computes grades with pluggable algorithms ◄─┤  │
│                                                          │  │
│  4. DECORATOR adds optional features to courses ◄────────┤  │
│                                                          │  │
│  5. COMMAND executes operations with Undo / Redo ◄───────┤  │
│                                                          │  │
│  6. STATE enforces course lifecycle rules & transitions ◄┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

The `CourseManager` service orchestrates all six patterns:

1. **Factory Method** — `create_course()` uses `CourseFactory` to produce the right concrete course type.
2. **Observer** — Enrolling a student auto-subscribes them; `post_announcement()`, `release_grade()`, and state changes broadcast to observers.
3. **Strategy** — `set_grading_strategy()` attaches a grading algorithm; `release_grade()` delegates to it.
4. **Decorator** — After creation, courses can be wrapped with add-ons via `replace_course()`.
5. **Command** — `execute_command()` executes operations with an undo/redo stack and an audit log (`undo()`, `redo()`).
6. **State** — `set_course_state()` and `advance_course_state()` govern course phases (`Draft` → `Open Registration` → `In Progress` → `Completed`).

---

## License

This project is for educational purposes.
