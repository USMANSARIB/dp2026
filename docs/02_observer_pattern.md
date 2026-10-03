# Observer Pattern

## 1. Intent

> **Define a one-to-many dependency between objects so that when one object changes state, all its dependents are notified and updated automatically.**
>
> — *Design Patterns: Elements of Reusable Object-Oriented Software* (GoF)

The Observer pattern is a **behavioural** design pattern that establishes a publish-subscribe relationship. A *subject* (publisher) maintains a list of *observers* (subscribers) and notifies them automatically whenever an event of interest occurs.

---

## 2. Problem It Solves

In the Student Course Management System, courses generate many types of events:

- 📢 **Announcements** (exam schedule changes, reminders)
- 📝 **New assignments** posted
- 🎯 **Grades released**
- 📅 **Schedule changes**
- 👥 **Enrollment updates**

**Without** the Observer pattern:

```python
# ❌ The course must know exactly who to notify and how
class Course:
    def post_announcement(self, msg):
        for student in self.students:
            send_email(student.email, msg)       # Email?
            send_sms(student.phone, msg)          # SMS?
            update_dashboard(student.id, msg)     # Dashboard?
            notify_admin(msg)                     # Admin too?
```

Problems:
- The course class is **tightly coupled** to notification delivery mechanisms.
- Adding a new notification channel requires modifying the `Course` class.
- Different observers may want **different event types** — the course shouldn't decide this.

---

## 3. Solution — Architecture

```
                    ┌──────────────────────────────────┐
                    │   CourseNotificationManager       │  ← Subject
                    │  ──────────────────────────────── │
                    │  - _listeners: {EventType: [...]} │
                    │  + subscribe(event, observer)     │
                    │  + unsubscribe(event, observer)   │
                    │  + notify(event, message)         │
                    └─────────┬────────────────────────┘
                              │  notifies
              ┌───────────────┼──────────────────┐
              ▼               ▼                  ▼
        ┌──────────┐   ┌──────────┐    ┌─────────────────┐
        │ Student   │   │ Student  │    │ Callable/Lambda │  ← Observers
        │ .update() │   │ .update()│    │ (event, msg)    │
        └──────────┘   └──────────┘    └─────────────────┘
```

Observers subscribe to **specific event types** via `EventType` enum values. When the subject fires `notify(event_type, message)`, only observers registered for that event type receive the callback.

---

## 4. Code Walkthrough

### 4.1 Event Types

```python
# src/patterns/observer.py

class EventType(Enum):
    ANNOUNCEMENT      = "ANNOUNCEMENT"
    ASSIGNMENT_POSTED = "ASSIGNMENT_POSTED"
    GRADE_RELEASED    = "GRADE_RELEASED"
    SCHEDULE_CHANGE   = "SCHEDULE_CHANGE"
    ENROLLMENT_UPDATE = "ENROLLMENT_UPDATE"
```

### 4.2 The Observer — `Student.update()`

The `Student` class acts as a **concrete observer** by implementing an `update()` method:

```python
# src/domain/student.py

@dataclass
class Student:
    student_id: str
    name: str
    email: str
    notifications: list[str] = field(default_factory=list)

    def update(self, event_type: EventType, message: str) -> None:
        """Called by the subject when an event occurs."""
        formatted = f"[{event_type.value}] {message}"
        self.notifications.append(formatted)
```

### 4.3 The Subject — `CourseNotificationManager`

```python
# src/patterns/observer.py

class CourseNotificationManager:
    def __init__(self, course_id: str) -> None:
        self.course_id = course_id
        self._listeners: dict[EventType, list] = {
            event: [] for event in EventType
        }

    def subscribe(self, event_type: EventType, observer) -> None:
        if observer not in self._listeners[event_type]:
            self._listeners[event_type].append(observer)

    def unsubscribe(self, event_type: EventType, observer) -> None:
        try:
            self._listeners[event_type].remove(observer)
        except ValueError:
            pass

    def notify(self, event_type: EventType, message: str) -> int:
        full_message = f"[Course {self.course_id}] {message}"
        count = 0
        for observer in self._listeners[event_type]:
            if callable(getattr(observer, "update", None)):
                observer.update(event_type, full_message)
            elif callable(observer):
                observer(event_type, full_message)
            count += 1
        return count
```

### 4.4 Usage Example

```python
manager = CourseNotificationManager("CS101")

alice = Student("S001", "Alice", "alice@uni.edu")
bob   = Student("S002", "Bob",   "bob@uni.edu")

# Subscribe to specific events
manager.subscribe(EventType.ANNOUNCEMENT, alice)
manager.subscribe(EventType.ANNOUNCEMENT, bob)
manager.subscribe(EventType.GRADE_RELEASED, alice)

# Broadcast
manager.notify(EventType.ANNOUNCEMENT, "Midterm on Oct 15!")
# → Both Alice and Bob receive this

manager.notify(EventType.GRADE_RELEASED, "Grades posted for HW3")
# → Only Alice receives this (Bob is not subscribed to GRADE_RELEASED)

print(alice.notifications)
# ['[ANNOUNCEMENT] [Course CS101] Midterm on Oct 15!',
#  '[GRADE_RELEASED] [Course CS101] Grades posted for HW3']
print(bob.notifications)
# ['[ANNOUNCEMENT] [Course CS101] Midterm on Oct 15!']
```

---

## 5. Key Design Decisions

### Event-Type Filtering
Unlike simple Observer implementations that broadcast *all* events to *all* observers, our design filters by `EventType`. A student subscribed only to `GRADE_RELEASED` will never receive `ANNOUNCEMENT` notifications. This prevents notification fatigue.

### Dual Observer Support
The `notify()` method supports both:
- **Object observers** with an `update(event_type, message)` method (e.g., `Student`).
- **Callable observers** — plain functions or lambdas — for quick ad-hoc listeners (e.g., logging).

```python
# Lambda as an observer
manager.subscribe(
    EventType.ANNOUNCEMENT,
    lambda et, msg: print(f"LOG: {msg}")
)
```

### Auto-Subscription on Enrollment
When the `CourseManager` enrolls a student, it automatically calls `subscribe_all()` to wire the student up for every event type. When the student drops the course, `unsubscribe_all()` cleanly removes them.

---

## 6. Trade-Offs

| Pros | Cons |
|------|------|
| Loose coupling between subject and observers | Observers are notified in insertion order (no priority) |
| Easy to add new observers without modifying subject | Memory leaks if observers are never unsubscribed |
| Supports selective subscription by event type | Debugging notification chains can be complex |
| Works with both objects and plain callables | — |

---

## 7. Related Files

- [`src/domain/student.py`](../src/domain/student.py) — `Student.update()` concrete observer
- [`src/patterns/observer.py`](../src/patterns/observer.py) — Full subject/observer implementation
- [`src/services/course_manager.py`](../src/services/course_manager.py) — Auto-subscription on enrollment
- [`tests/test_patterns.py`](../tests/test_patterns.py) — `TestObserverPattern` test class
