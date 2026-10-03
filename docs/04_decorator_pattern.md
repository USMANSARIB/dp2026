# Decorator Pattern

## 1. Intent

> **Attach additional responsibilities to an object dynamically.** Decorators provide a flexible alternative to subclassing for extending functionality.
>
> — *Design Patterns: Elements of Reusable Object-Oriented Software* (GoF)

The Decorator pattern is a **structural** design pattern that wraps an existing object with a new object that adds behaviour — all while preserving the original object's interface. Decorators can be *stacked* (composed), allowing combinatorial feature extension without creating an exponential number of subclasses.

---

## 2. Problem It Solves

Courses can optionally include add-on features:

| Add-On | Description | Extra Fee |
|--------|-------------|-----------|
| Honors Distinction | Requires an honors thesis; marks the transcript | +$150 |
| Lab Access Pass | 24/7 lab access with safety training | +$100 |
| Tutoring Support | Weekly 1-on-1 tutoring sessions | +$200 |
| Certificate | Official certificate of completion | +$75 |

A student might want *any combination* of these add-ons on *any course type*. If we used subclassing:

```
Course
├── LectureCourse
│   ├── LectureCourseWithHonors
│   ├── LectureCourseWithLabAccess
│   ├── LectureCourseWithHonorsAndLabAccess
│   ├── LectureCourseWithHonorsAndTutoring
│   └── ... (16 combinations just for Lecture!)
├── LabCourse
│   ├── ... (another 16)
└── ... (64 total subclasses!)
```

This is called **subclass explosion** — and it's unmanageable.

---

## 3. Solution — Architecture

```
                      ┌───────────────┐
                      │    Course     │  ← Component interface
                      │    (ABC)      │
                      └───────┬───────┘
                              │
              ┌───────────────┼───────────────────┐
              ▼               ▼                   ▼
        ┌───────────┐  ┌──────────────┐    ┌──────────────┐
        │ Lecture    │  │ CourseDecorator│   │ Lab          │
        │ Course    │  │ (wraps Course)│   │ Course       │
        └───────────┘  └──────┬───────┘   └──────────────┘
                              │ extends
              ┌───────┬───────┼───────┬────────┐
              ▼       ▼       ▼       ▼
          Honors   LabAccess Tutoring Certificate
          Decorator Decorator Decorator Decorator
```

Each decorator:
1. **Wraps** a `Course` instance (the "component").
2. **Forwards** all interface calls to the wrapped course.
3. **Adds** its own behaviour (description text, requirements, fees).

Because every decorator *is* a `Course`, decorators can wrap other decorators — enabling stacking.

---

## 4. Code Walkthrough

### 4.1 Base Decorator

```python
# src/patterns/decorator.py

class CourseDecorator(Course):
    """Abstract decorator that wraps a Course and delegates all calls."""

    def __init__(self, wrapped_course: Course) -> None:
        self._wrapped = wrapped_course

    # Delegate all dataclass properties to the wrapped course
    @property
    def course_id(self) -> str:
        return self._wrapped.course_id

    @property
    def title(self) -> str:
        return self._wrapped.title

    # ... (credits, max_students, base_fee, enrolled_students, etc.)

    # Default forwarding
    def get_description(self) -> str:
        return self._wrapped.get_description()

    def get_requirements(self) -> list[str]:
        return list(self._wrapped.get_requirements())

    def get_total_fee(self) -> float:
        return self._wrapped.get_total_fee()
```

### 4.2 Concrete Decorators

#### HonorsDistinctionDecorator

```python
class HonorsDistinctionDecorator(CourseDecorator):
    SURCHARGE = 150.0

    def get_description(self) -> str:
        return self._wrapped.get_description() + " [Honors Section]"

    def get_requirements(self) -> list[str]:
        reqs = list(self._wrapped.get_requirements())
        reqs.extend([
            "Honors thesis proposal",
            "Additional scholarly reading list",
        ])
        return reqs

    def get_total_fee(self) -> float:
        return self._wrapped.get_total_fee() + self.SURCHARGE
```

#### CertificateDecorator

```python
class CertificateDecorator(CourseDecorator):
    SURCHARGE = 75.0

    def get_description(self) -> str:
        return self._wrapped.get_description() + " + Certificate of Completion"

    def get_requirements(self) -> list[str]:
        reqs = list(self._wrapped.get_requirements())
        reqs.append("Maintain minimum 70% overall grade for certificate eligibility")
        return reqs

    def get_total_fee(self) -> float:
        return self._wrapped.get_total_fee() + self.SURCHARGE
```

*(Similar for `LabAccessPassDecorator` and `TutoringSupportDecorator`.)*

### 4.3 Stacking Decorators

```python
# Start with a base lecture course ($500)
course = CourseFactory.create_course(CourseType.LECTURE, "CS101", "Intro CS", 3)
print(course.get_total_fee())  # → $500.00

# Add Honors Distinction (+$150)
course = HonorsDistinctionDecorator(course)
print(course.get_total_fee())  # → $650.00

# Add Lab Access (+$100)
course = LabAccessPassDecorator(course)
print(course.get_total_fee())  # → $750.00

# Add Tutoring (+$200)
course = TutoringSupportDecorator(course)
print(course.get_total_fee())  # → $950.00

# Add Certificate (+$75)
course = CertificateDecorator(course)
print(course.get_total_fee())  # → $1,025.00

# Description accumulates too
print(course.get_description())
# → '...' is a traditional lecture course ...
#   [Honors Section] + 24/7 Lab Access + Personal Tutoring
#   + Certificate of Completion
```

**Fee breakdown:**

```
  Base fee:       $500.00
  + Honors:       $150.00
  + Lab Access:   $100.00
  + Tutoring:     $200.00
  + Certificate:  $ 75.00
  ────────────────────────
  Total:        $1,025.00
```

### 4.4 Transparent Interface

Because every decorator *is* a `Course`, all existing operations work seamlessly:

```python
# Enrollment works through decorators
course.enroll_student(alice)

# Grading works through decorators
course.set_grading_strategy(StandardGradingStrategy())
grade = course.calculate_grade(92)  # → "A"
```

---

## 5. Key Design Decisions

### Property Delegation
Since `Course` is a `@dataclass` with fields like `course_id`, `title`, etc., the `CourseDecorator` cannot simply inherit these as regular attributes. Instead, it exposes them as `@property` descriptors that delegate reads and writes to the wrapped course. This ensures that modifying an attribute through a decorator updates the original underlying course.

### Immutable Requirements Copying
`get_requirements()` returns `list(self._wrapped.get_requirements())` — a **copy** — before extending. This prevents decorators from mutating the wrapped course's original requirements list.

### Surcharge as Class Constant
Each decorator defines its fee as a class-level `SURCHARGE` constant. This makes fees easy to discover, document, and test, and allows subclasses to override the amount if needed.

---

## 6. Trade-Offs

| Pros | Cons |
|------|------|
| Avoids subclass explosion (4 decorators vs. 64 subclasses) | Many small objects in the wrapping chain |
| Features can be combined in any order at runtime | Hard to remove a specific decorator from the middle |
| Follows the Open/Closed Principle | `isinstance()` checks may not work as expected |
| Each decorator is independently testable | Debugging nested decorators can be complex |

---

## 7. Related Files

- [`src/domain/course.py`](../src/domain/course.py) — `Course.get_total_fee()` base implementation
- [`src/patterns/decorator.py`](../src/patterns/decorator.py) — All decorator implementations
- [`src/services/course_manager.py`](../src/services/course_manager.py) — `replace_course()` for decorated courses
- [`tests/test_patterns.py`](../tests/test_patterns.py) — `TestDecoratorPattern` test class
