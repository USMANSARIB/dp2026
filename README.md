# Student Course Management System — Design Patterns

A Python project demonstrating six classic **Gang of Four (GoF)** design patterns
through a realistic Student Course Management System, featuring a full **interactive terminal navigation menu**.

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

### 📖 Documentation & Walkthrough Guides

Each pattern and feature has a dedicated document explaining the theory, architecture, code walkthrough, step-by-step procedure, and trade-offs:

- [01 — Factory Method Pattern](docs/01_factory_method_pattern.md)
- [02 — Observer Pattern](docs/02_observer_pattern.md)
- [03 — Strategy Pattern](docs/03_strategy_pattern.md)
- [04 — Decorator Pattern](docs/04_decorator_pattern.md)
- [05 — Command Pattern](docs/05_command_pattern.md)
- [06 — State Pattern](docs/06_state_pattern.md)
- [07 — Terminal Navigation Guide (Step-by-Step Procedure)](docs/07_terminal_navigation_guide.md)

---

## 🖥️ Interactive Terminal Navigation Menu

Launch the terminal application to interactively showcase any feature on demand:

```bash
python src/main.py
```

```
╔══════════════════════════════════════════════════════════════════╗
║   STUDENT COURSE MANAGEMENT SYSTEM — Feature Navigation Menu   ║
╚══════════════════════════════════════════════════════════════════╝

  [1] Factory Method Pattern  — Dynamic Course Creation by Type
  [2] Observer Pattern        — Event Subscriptions & Broadcasts
  [3] Strategy Pattern        — Pluggable Runtime Grading Algorithms
  [4] Decorator Pattern       — Course Add-ons & Surcharge Stacking
  [5] Command Pattern         — Reversible Actions, Undo/Redo & Audit
  [6] State Pattern           — Academic Lifecycle & Access Control
  [7] System Status & Reports — Enrollment Summary & Audit Log
  [8] Full Guided Tour        — Walkthrough of All Patterns Step-by-Step
  [9] Run Test Suite          — Execute all 58 Automated Tests
  [0] Exit Application
```

### CLI Launch Modes

| Mode | Command | Description |
|------|---------|-------------|
| **Interactive Menu** | `python src/main.py` | Full interactive menu with on-demand navigation across all 6 patterns |
| **Guided Tour** | `python src/main.py --all` | Automated step-by-step walkthrough across all patterns with pauses |
| **In-Terminal Tests** | `python src/main.py --test` | Runs all 58 automated unit & integration tests directly |
| **Standard Unittest** | `python -m unittest discover -s tests -v` | Standard Python unittest runner |

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
│   ├── 06_state_pattern.md
│   └── 07_terminal_navigation_guide.md   # Step-by-step procedure manual
├── src/
│   ├── __init__.py
│   ├── main.py                           # Interactive CLI navigator & menu
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── student.py                    # Student entity (Observer)
│   │   └── course.py                     # Abstract Course base, CourseType & State hooks
│   ├── patterns/
│   │   ├── __init__.py
│   │   ├── factory.py                    # Factory Method pattern
│   │   ├── observer.py                   # Observer pattern
│   │   ├── strategy.py                   # Strategy pattern
│   │   ├── decorator.py                  # Decorator pattern
│   │   ├── command.py                    # Command pattern (Undo/Redo & Audit)
│   │   └── state.py                      # State pattern (Course lifecycle)
│   └── services/
│       ├── __init__.py
│       └── course_manager.py             # Service layer orchestrating all patterns
└── tests/
    ├── __init__.py
    └── test_patterns.py                  # 58 unit + integration tests
```

---

## Quick Start

### Prerequisites

- Python 3.10+ (uses `match`, `|` union types, modern type hints)

### Windows Console UTF-8 Setup (Recommended)

```powershell
$env:PYTHONIOENCODING="utf-8"
python src/main.py
```

### Run the Tests

```bash
python -m unittest discover -s tests -v
```

Expected output: **58 tests, all passing** in ~0.004s.

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
