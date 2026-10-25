package com.course.observer;

import com.course.model.Course;
import com.course.model.CourseComponent;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.List;

/**
 * Concrete Observer in the Observer Pattern.
 * Dispatches live notification alerts for the student whenever course information changes,
 * capacity updates occur, or enrollment actions take place.
 */
public class StudentNotificationObserver implements CourseObserver {
    public static class NotificationItem {
        private final int id;
        private final String timestamp;
        private final String eventType;
        private final String courseCode;
        private final String message;
        private final String level; // "info", "success", "warning"

        public NotificationItem(int id, String timestamp, String eventType, String courseCode, String message, String level) {
            this.id = id;
            this.timestamp = timestamp;
            this.eventType = eventType;
            this.courseCode = courseCode;
            this.message = message;
            this.level = level;
        }

        public String toJson() {
            return "{"
                    + "\"id\":" + id + ","
                    + "\"timestamp\":\"" + Course.escapeJson(timestamp) + "\","
                    + "\"eventType\":\"" + Course.escapeJson(eventType) + "\","
                    + "\"courseCode\":\"" + Course.escapeJson(courseCode) + "\","
                    + "\"message\":\"" + Course.escapeJson(message) + "\","
                    + "\"level\":\"" + Course.escapeJson(level) + "\""
                    + "}";
        }
    }

    private final List<NotificationItem> notifications = Collections.synchronizedList(new ArrayList<>());
    private int nextId = 1;
    private final SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");

    @Override
    public void onCourseEvent(String eventType, CourseComponent course, String details) {
        String timestamp = dateFormat.format(new Date());
        String code = (course != null) ? course.getCode() : "GENERAL";
        String level = "info";

        if (eventType.contains("ERROR") || eventType.contains("CONFLICT")) {
            level = "warning";
        } else if (eventType.contains("ENROLLED") || eventType.contains("ADDED")) {
            level = "success";
        }

        NotificationItem item = new NotificationItem(nextId++, timestamp, eventType, code, details, level);
        notifications.add(0, item); // latest first

        // Keep buffer manageable
        if (notifications.size() > 50) {
            notifications.remove(notifications.size() - 1);
        }
    }

    public List<NotificationItem> getNotifications() {
        return new ArrayList<>(notifications);
    }

    public void clear() {
        notifications.clear();
    }
}
