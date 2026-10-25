package com.course.observer;

import com.course.model.CourseComponent;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Concrete Observer in the Observer Pattern.
 * Synchronizes and monitors student schedule consistency.
 * Automatically triggers validation alerts when an enrolled course's time or day changes,
 * or when a course is removed by department administrators.
 */
public class ScheduleSyncObserver implements CourseObserver {
    private final List<String> scheduleAlerts = Collections.synchronizedList(new ArrayList<>());

    @Override
    public void onCourseEvent(String eventType, CourseComponent course, String details) {
        if ("COURSE_UPDATED".equals(eventType) && course != null) {
            scheduleAlerts.add(0, "[Timetable Sync] Course " + course.getCode() + " updated schedule to: " + course.getScheduleSummary());
        } else if ("COURSE_DELETED".equals(eventType) && course != null) {
            scheduleAlerts.add(0, "[Timetable Warning] Course " + course.getCode() + " was deleted from department catalog.");
        }
        if (scheduleAlerts.size() > 20) {
            scheduleAlerts.remove(scheduleAlerts.size() - 1);
        }
    }

    public List<String> getScheduleAlerts() {
        return new ArrayList<>(scheduleAlerts);
    }
}
