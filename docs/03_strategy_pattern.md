# Strategy Pattern

## 1. Intent

> **Define a family of algorithms, encapsulate each one, and make them interchangeable.** Strategy lets the algorithm vary independently from the clients that use it.
>
> — *Design Patterns: Elements of Reusable Object-Oriented Software* (GoF)

The Strategy pattern is a **behavioural** design pattern that extracts a set of interchangeable algorithms into their own classes behind a common interface. The *context* (in our case, a `Course`) holds a reference to one strategy at a time and delegates the work to it — and can swap the strategy at runtime.

---

## 2. Problem It Solves

Different courses may require different grading policies:

| Course | Grading Style | Logic |
|--------|--------------|-------|
| CS101 (Lecture) | Standard A-F | ≥90→A, ≥80→B, ≥70→C, ≥60→D, else F |
| CHEM201 (Lab) | Pass/Fail | ≥60→Pass, else Fail |
| ENG102 (Online) | Curved | Add N bonus points, then grade on standard scale |
| PHIL401 (Seminar) | Weighted | Combine homework (30%), midterm (30%), final (40%) |

**Without** the Strategy pattern:

```python
# ❌ Monolithic grading inside Course
class Course:
    def calculate_grade(self, score, mode="standard"):
        if mode == "standard":
            if score >= 90: return "A"
            elif score >= 80: return "B"
            # ...
        elif mode == "pass_fail":
            return "Pass" if score >= 60 else "Fail"
        elif mode == "curved":
            score += self.curve_points
            # ... repeat standard logic
        elif mode == "weighted":
            # ... completely different signature
```

Problems:
- **Single Responsibility violation** — the `Course` class owns N unrelated algorithms.
- Adding a new grading scheme means modifying the method — violates **Open/Closed Principle**.
- Unit-testing each algorithm independently is difficult.

---

## 3. Solution — Architecture

```
┌────────────────────┐          ┌──────────────────────────┐
│      Course        │          │    GradingStrategy (ABC)  │
│  ─────────────     │ uses     │  ──────────────────────── │
│  grading_strategy ─┼─────────▶│  + calculate_grade(score) │
│  calculate_grade() │          │  + get_strategy_name()    │
└────────────────────┘          └────────────┬─────────────┘
                                             │ implements
                         ┌───────────┬───────┼───────┬────────────┐
                         ▼           ▼       ▼       ▼            
                    Standard     PassFail  Curved  Weighted
                    Grading      Grading   Grading  Grading
                    Strategy     Strategy  Strategy Strategy
```

The `Course` class simply delegates:

```python
def calculate_grade(self, score: float) -> str:
    return self.grading_strategy.calculate_grade(score)
```

---

## 4. Code Walkthrough

### 4.1 Abstract Strategy

```python
# src/patterns/strategy.py

class GradingStrategy(ABC):
    @abstractmethod
    def calculate_grade(self, score: float) -> str:
        """Convert a numeric score (0-100) to a letter grade."""

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Return a human-readable name for this strategy."""
```

### 4.2 Concrete Strategies

#### StandardGradingStrategy

```python
class StandardGradingStrategy(GradingStrategy):
    def __init__(self, a_threshold=90, b_threshold=80, 
                 c_threshold=70, d_threshold=60):
        self._thresholds = [
            (a_threshold, "A"), (b_threshold, "B"),
            (c_threshold, "C"), (d_threshold, "D"),
        ]

    def calculate_grade(self, score: float) -> str:
        for threshold, grade in self._thresholds:
            if score >= threshold:
                return grade
        return "F"

    def get_strategy_name(self) -> str:
        return "Standard Grading (A-F)"
```

#### PassFailGradingStrategy

```python
class PassFailGradingStrategy(GradingStrategy):
    def __init__(self, pass_threshold: float = 60.0):
        self._pass_threshold = pass_threshold

    def calculate_grade(self, score: float) -> str:
        return "Pass" if score >= self._pass_threshold else "Fail"
```

#### CurvedGradingStrategy

```python
class CurvedGradingStrategy(GradingStrategy):
    def __init__(self, curve_points: float = 5.0):
        self._curve_points = curve_points
        self._standard = StandardGradingStrategy()

    def calculate_grade(self, score: float) -> str:
        curved_score = min(score + self._curve_points, 100.0)
        return self._standard.calculate_grade(curved_score)
```

> **Note:** `CurvedGradingStrategy` internally delegates to `StandardGradingStrategy` after applying the boost — this is *composition over inheritance* in action.

#### WeightedGradingStrategy

```python
@dataclass
class WeightedGradingStrategy(GradingStrategy):
    weights: dict[str, float] = field(default_factory=lambda: {
        "homework": 0.3, "midterm": 0.3, "final": 0.4,
    })

    def calculate_weighted_grade(self, scores: dict[str, float]) -> str:
        weighted_sum = sum(
            scores[comp] * weight
            for comp, weight in self.weights.items()
        )
        return self._standard.calculate_grade(weighted_sum)
```

### 4.3 Runtime Swapping

```python
course = CourseFactory.create_course(CourseType.LECTURE, "CS101", "Intro CS", 3)

# Start with standard grading
course.set_grading_strategy(StandardGradingStrategy())
print(course.calculate_grade(85))  # → "B"

# Switch to pass/fail mid-semester
course.set_grading_strategy(PassFailGradingStrategy(pass_threshold=50))
print(course.calculate_grade(85))  # → "Pass"

# Apply a generous curve
course.set_grading_strategy(CurvedGradingStrategy(curve_points=10))
print(course.calculate_grade(82))  # → 92 → "A"
```

---

## 5. Key Design Decisions

### Configurable Thresholds
Each strategy accepts customisation via its constructor. The `StandardGradingStrategy` allows redefining A/B/C/D thresholds; the `PassFailGradingStrategy` allows setting the pass threshold; the `CurvedGradingStrategy` accepts the number of bonus points.

### Composition Inside Strategies
`CurvedGradingStrategy` and `WeightedGradingStrategy` internally reuse `StandardGradingStrategy` by composition. This avoids code duplication and ensures consistent grade-letter mapping.

### Safety — No Strategy = Error
If a course's grading strategy is `None` and `calculate_grade()` is called, a `ValueError` is raised with a clear message. This prevents silent failures.

---

## 6. Trade-Offs

| Pros | Cons |
|------|------|
| Each algorithm is independently testable | More classes to manage |
| Easy to add new strategies without touching existing code | Client must know which strategy to set |
| Strategies can be swapped at runtime | Slight indirection overhead |
| Eliminates conditional logic in the context class | — |

---

## 7. Related Files

- [`src/domain/course.py`](../src/domain/course.py) — `Course.calculate_grade()` context method
- [`src/patterns/strategy.py`](../src/patterns/strategy.py) — All grading strategy implementations
- [`src/services/course_manager.py`](../src/services/course_manager.py) — `set_grading_strategy()` service method
- [`tests/test_patterns.py`](../tests/test_patterns.py) — `TestStrategyPattern` test class
