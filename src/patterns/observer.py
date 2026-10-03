"""
Observer Pattern — Course Notification System.

This module demonstrates the **Observer** behavioural design pattern.
A `CourseNotificationManager` (the *subject*) maintains a list of
observers — `Student` objects and arbitrary callback listeners — and
broadcasts notifications when events like announcements, assignment
postings, or grade releases occur.

Key participants:
    - **Subject**: `CourseNotificationManager`
    - **Observer**: `Student` (via its `update()` method)
    - **Events**: `EventType` enum
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from src.domain.student import Student


class EventType(Enum):
    """Categories of events a course can publish."""

    ANNOUNCEMENT = "ANNOUNCEMENT"
    ASSIGNMENT_POSTED = "ASSIGNMENT_POSTED"
    GRADE_RELEASED = "GRADE_RELEASED"
    SCHEDULE_CHANGE = "SCHEDULE_CHANGE"
    ENROLLMENT_UPDATE = "ENROLLMENT_UPDATE"


# Type alias for a generic listener callback
Listener = Callable[[EventType, str], None]


class CourseNotificationManager:
    """Subject that manages subscriptions and broadcasts events.

    Observers subscribe to specific `EventType` values.  When `notify()`
    is called, only observers registered for that event type are alerted.

    Usage::

        manager = CourseNotificationManager("CS101")

        # Students as observers
        manager.subscribe(EventType.ANNOUNCEMENT, student_alice)
        manager.subscribe(EventType.GRADE_RELEASED, student_bob)

        # Generic callable listener
        manager.subscribe(EventType.ANNOUNCEMENT, lambda et, msg: print(msg))

        manager.notify(EventType.ANNOUNCEMENT, "Midterm moved to next week!")
    """

    def __init__(self, course_id: str) -> None:
        self.course_id = course_id
        # event_type → list of (Student | Listener)
        self._listeners: dict[EventType, list[Student | Listener]] = {
            event: [] for event in EventType
        }

    # ------------------------------------------------------------------
    # Subscription management
    # ------------------------------------------------------------------
    def subscribe(
        self,
        event_type: EventType,
        observer: Student | Listener,
    ) -> None:
        """Register an observer for a particular event type.

        Args:
            event_type: The event category to listen to.
            observer: A `Student` instance or any callable matching
                      ``(EventType, str) -> None``.
        """
        if observer not in self._listeners[event_type]:
            self._listeners[event_type].append(observer)

    def unsubscribe(
        self,
        event_type: EventType,
        observer: Student | Listener,
    ) -> None:
        """Remove an observer from a particular event type."""
        try:
            self._listeners[event_type].remove(observer)
        except ValueError:
            pass  # observer was not subscribed — silently ignore

    def subscribe_all(self, observer: Student | Listener) -> None:
        """Subscribe an observer to *every* event type at once."""
        for event_type in EventType:
            self.subscribe(event_type, observer)

    def unsubscribe_all(self, observer: Student | Listener) -> None:
        """Remove an observer from *every* event type at once."""
        for event_type in EventType:
            self.unsubscribe(event_type, observer)

    # ------------------------------------------------------------------
    # Broadcasting
    # ------------------------------------------------------------------
    def notify(self, event_type: EventType, message: str) -> int:
        """Broadcast a message to all observers of the given event type.

        Args:
            event_type: The category of the event.
            message: The human-readable notification content.

        Returns:
            The number of observers that were notified.
        """
        full_message = f"[Course {self.course_id}] {message}"
        count = 0
        for observer in self._listeners[event_type]:
            if callable(getattr(observer, "update", None)):
                observer.update(event_type, full_message)  # type: ignore[union-attr]
            elif callable(observer):
                observer(event_type, full_message)
            count += 1
        return count

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------
    def get_subscriber_count(self, event_type: EventType) -> int:
        """Return the number of observers for a given event type."""
        return len(self._listeners[event_type])

    def get_all_subscribers(self) -> dict[EventType, int]:
        """Return a mapping of event types to their subscriber counts."""
        return {et: len(subs) for et, subs in self._listeners.items()}
