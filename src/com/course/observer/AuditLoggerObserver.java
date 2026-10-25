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
 * Maintains an immutable audit trail of administrative operations for auditing and record-keeping.
 */
public class AuditLoggerObserver implements CourseObserver {
    public static class AuditEntry {
        private final String timestamp;
        private final String eventType;
        private final String courseCode;
        private final String details;

        public AuditEntry(String timestamp, String eventType, String courseCode, String details) {
            this.timestamp = timestamp;
            this.eventType = eventType;
            this.courseCode = courseCode;
            this.details = details;
        }

        public String toJson() {
            return "{"
                    + "\"timestamp\":\"" + Course.escapeJson(timestamp) + "\","
                    + "\"eventType\":\"" + Course.escapeJson(eventType) + "\","
                    + "\"courseCode\":\"" + Course.escapeJson(courseCode) + "\","
                    + "\"details\":\"" + Course.escapeJson(details) + "\""
                    + "}";
        }
    }

    private final List<AuditEntry> auditLog = Collections.synchronizedList(new ArrayList<>());
    private final SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");

    @Override
    public void onCourseEvent(String eventType, CourseComponent course, String details) {
        String ts = dateFormat.format(new Date());
        String code = (course != null) ? course.getCode() : "SYSTEM";
        auditLog.add(0, new AuditEntry(ts, eventType, code, details));
        if (auditLog.size() > 100) {
            auditLog.remove(auditLog.size() - 1);
        }
    }

    public List<AuditEntry> getAuditLog() {
        return new ArrayList<>(auditLog);
    }
}
