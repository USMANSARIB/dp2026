package com.course.observer;

import com.course.model.CourseComponent;

/**
 * Observer interface in the Observer Pattern.
 * Subscribed observers receive notifications when course lifecycle events occur.
 */
public interface CourseObserver {
    /**
     * Called whenever a course is added, updated, deleted, wishlisted, or enrolled.
     * @param eventType the type of event (e.g. COURSE_ADDED, COURSE_UPDATED, COURSE_DELETED, WISHLIST_UPDATED, SCHEDULE_ENROLLED)
     * @param course the course component involved in the event
     * @param details descriptive contextual message about the change
     */
    void onCourseEvent(String eventType, CourseComponent course, String details);
}
