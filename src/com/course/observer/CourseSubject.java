package com.course.observer;

import com.course.model.CourseComponent;

/**
 * Subject interface in the Observer Pattern.
 * Manages subscription, unsubscription, and event broadcasting to registered observers.
 */
public interface CourseSubject {
    void registerObserver(CourseObserver observer);
    void removeObserver(CourseObserver observer);
    void notifyObservers(String eventType, CourseComponent course, String details);
}
