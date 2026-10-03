# Factory Method Pattern

## 1. Intent

> **Define an interface for creating an object, but let subclasses decide which class to instantiate.** Factory Method lets a class defer instantiation to subclasses.
>
> — *Design Patterns: Elements of Reusable Object-Oriented Software* (GoF)

The Factory Method pattern is a **creational** design pattern that provides a way to create objects without specifying their exact concrete class. Instead of calling a constructor directly, client code asks a *factory* to produce the desired object, using a descriptive key (like an enum value) rather than the class name.

---

## 2. Problem It Solves

In the Student Course Management System, we have **four distinct course types**:

| Type      | Class          | Description                    |
|-----------|----------------|--------------------------------|
| LECTURE   | `LectureCourse`  | Traditional classroom course  |
| LAB       | `LabCourse`       | Hands-on laboratory course    |
| ONLINE    | `OnlineCourse`    | Asynchronous/synchronous web  |
| SEMINAR   | `SeminarCourse`   | Small-group discussion format |

**Without** the Factory Method, client code would look like this:

```python
# ❌ Tight coupling — client must know every concrete class
if course_type == "lecture":
    course = LectureCourse(course_id, title, credits, ...)
elif course_type == "lab":
    course = LabCourse(course_id, title, credits, ...)
elif course_type == "online":
    course = OnlineCourse(course_id, title, credits, ...)
# ... and so on for every new type
```

Problems:
- Every time a new course type is added, **every client** that creates courses must be modified.
- The client is **tightly coupled** to concrete implementations.
- Violates the **Open/Closed Principle** (open for extension, closed for modification).

---

## 3. Solution — Architecture

```
┌──────────────────────────┐
│      CourseFactory        │  ← Creator (static factory method)
│  ─────────────────────── │
│  + create_course(type,   │
│      id, title, ...)     │───────────────┐
│  + get_available_types() │               │
└──────────────────────────┘               ▼
                                    ┌─────────────┐
                                    │   Course     │  ← Abstract Product
                                    │  (ABC)       │
                                    └──────┬──────┘
                           ┌───────┬───────┼───────┬────────┐
                           ▼       ▼       ▼       ▼        
                      Lecture   Lab    Online   Seminar     ← Concrete Products
                      Course   Course  Course   Course
```

The `CourseFactory` consults an internal **registry** (a dictionary mapping `CourseType` → class) to instantiate the right concrete product.

---

## 4. Code Walkthrough

### 4.1 Abstract Product — `Course` (base class)

```python
# src/domain/course.py
class CourseType(Enum):
    LECTURE = "lecture"
    LAB     = "lab"
    ONLINE  = "online"
    SEMINAR = "seminar"

@dataclass
class Course(ABC):
    course_id: str
    title: str
    credits: int
    max_students: int = 30
    base_fee: float = 500.0

    @abstractmethod
    def get_description(self) -> str: ...

    @abstractmethod
    def get_requirements(self) -> list[str]: ...
```

### 4.2 Concrete Products

Each subclass implements `get_description()` and `get_requirements()` with behaviour specific to its delivery format:

```python
# src/patterns/factory.py

@dataclass
class LectureCourse(Course):
    def get_description(self) -> str:
        return (
            f"'{self.title}' is a traditional lecture course held in a "
            f"classroom setting with up to {self.max_students} students."
        )

    def get_requirements(self) -> list[str]:
        return [
            "Classroom with projector",
            "Textbook (required)",
            "Notebook for in-class exercises",
        ]

@dataclass
class LabCourse(Course):
    def get_description(self) -> str:
        return (
            f"'{self.title}' is a hands-on laboratory course where students "
            f"work on practical experiments and projects."
        )

    def get_requirements(self) -> list[str]:
        return [
            "Lab equipment and safety gear",
            "Lab manual",
            "Personal protective equipment (PPE)",
            "Pre-lab report templates",
        ]
```

*(Similar for `OnlineCourse` and `SeminarCourse`.)*

### 4.3 The Factory (Creator)

```python
# Registry mapping CourseType → concrete class
_COURSE_REGISTRY: dict[CourseType, type[Course]] = {
    CourseType.LECTURE:  LectureCourse,
    CourseType.LAB:     LabCourse,
    CourseType.ONLINE:  OnlineCourse,
    CourseType.SEMINAR: SeminarCourse,
}

class CourseFactory:
    @staticmethod
    def create_course(
        course_type: CourseType,
        course_id: str,
        title: str,
        credits: int,
        max_students: int = 30,
        base_fee: float = 500.0,
    ) -> Course:
        course_class = _COURSE_REGISTRY.get(course_type)
        if course_class is None:
            raise ValueError(f"Unknown course type: {course_type!r}")
        return course_class(
            course_id=course_id,
            title=title,
            credits=credits,
            max_students=max_students,
            base_fee=base_fee,
        )
```

### 4.4 Client Code

```python
# Clean — no knowledge of concrete classes needed
course = CourseFactory.create_course(
    course_type=CourseType.LAB,
    course_id="CHEM301",
    title="Organic Chemistry Lab",
    credits=2,
    max_students=20,
    base_fee=750.00,
)
print(course.get_description())
# → 'Organic Chemistry Lab' is a hands-on laboratory course ...
```

---

## 5. Adding a New Course Type

To add a new course type (say `WORKSHOP`), you only need to:

1. Add `WORKSHOP = "workshop"` to the `CourseType` enum.
2. Create a `WorkshopCourse(Course)` dataclass.
3. Add one line to `_COURSE_REGISTRY`.

**No existing client code changes.** This is the power of the Factory Method.

---

## 6. Trade-Offs

| Pros | Cons |
|------|------|
| Decouples creation from usage | Adds an extra layer of abstraction |
| Supports the Open/Closed Principle | Registry must be kept in sync with enum |
| Centralises creation logic | Overkill for systems with a single type |
| Easy to unit-test with mock factories | — |

---

## 7. Related Files

- [`src/domain/course.py`](../src/domain/course.py) — Abstract `Course` base & `CourseType` enum
- [`src/patterns/factory.py`](../src/patterns/factory.py) — Full factory implementation
- [`tests/test_patterns.py`](../tests/test_patterns.py) — `TestFactoryMethodPattern` test class
