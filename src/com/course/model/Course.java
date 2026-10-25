package com.course.model;

import java.util.ArrayList;
import java.util.List;

/**
 * Concrete Component in the Decorator Pattern.
 * Represents a base academic course with core attributes.
 */
public class Course implements CourseComponent {
    private int id;
    private String code;
    private String title;
    private String instructor;
    private int credits;
    private double baseFee;
    private String day;          // e.g., "Monday", "Wednesday", etc.
    private String startTime;    // e.g., "09:00"
    private String endTime;      // e.g., "10:30"
    private int capacity;
    private int enrolledCount;
    private String description;

    public Course(int id, String code, String title, String instructor, int credits,
                  double baseFee, String day, String startTime, String endTime,
                  int capacity, int enrolledCount, String description) {
        this.id = id;
        this.code = code;
        this.title = title;
        this.instructor = instructor;
        this.credits = credits;
        this.baseFee = baseFee;
        this.day = day;
        this.startTime = startTime;
        this.endTime = endTime;
        this.capacity = capacity;
        this.enrolledCount = enrolledCount;
        this.description = description;
    }

    @Override
    public int getId() { return id; }

    @Override
    public String getCode() { return code; }

    @Override
    public String getTitle() { return title; }

    @Override
    public String getInstructor() { return instructor; }

    @Override
    public int getCredits() { return credits; }

    @Override
    public double getBaseFee() { return baseFee; }

    @Override
    public double getTotalFee() { return baseFee; }

    @Override
    public String getDay() { return day; }

    @Override
    public String getStartTime() { return startTime; }

    @Override
    public String getEndTime() { return endTime; }

    @Override
    public String getScheduleSummary() {
        return day + " " + startTime + " - " + endTime;
    }

    @Override
    public List<String> getAddonFeatures() {
        return new ArrayList<>(); // Base course has no add-ons
    }

    @Override
    public String getDescription() { return description; }

    @Override
    public int getCapacity() { return capacity; }

    @Override
    public int getEnrolledCount() { return enrolledCount; }

    // Mutator methods for Course Updates
    public void setCode(String code) { this.code = code; }
    public void setTitle(String title) { this.title = title; }
    public void setInstructor(String instructor) { this.instructor = instructor; }
    public void setCredits(int credits) { this.credits = credits; }
    public void setBaseFee(double baseFee) { this.baseFee = baseFee; }
    public void setDay(String day) { this.day = day; }
    public void setStartTime(String startTime) { this.startTime = startTime; }
    public void setEndTime(String endTime) { this.endTime = endTime; }
    public void setCapacity(int capacity) { this.capacity = capacity; }
    public void setEnrolledCount(int enrolledCount) { this.enrolledCount = enrolledCount; }
    public void setDescription(String description) { this.description = description; }

    public void incrementEnrolled() {
        if (enrolledCount < capacity) {
            enrolledCount++;
        }
    }

    public void decrementEnrolled() {
        if (enrolledCount > 0) {
            enrolledCount--;
        }
    }

    @Override
    public String toJson() {
        return "{"
                + "\"id\":" + id + ","
                + "\"code\":\"" + escapeJson(code) + "\","
                + "\"title\":\"" + escapeJson(title) + "\","
                + "\"instructor\":\"" + escapeJson(instructor) + "\","
                + "\"credits\":" + credits + ","
                + "\"baseFee\":" + String.format(java.util.Locale.US, "%.2f", baseFee) + ","
                + "\"totalFee\":" + String.format(java.util.Locale.US, "%.2f", getTotalFee()) + ","
                + "\"day\":\"" + escapeJson(day) + "\","
                + "\"startTime\":\"" + escapeJson(startTime) + "\","
                + "\"endTime\":\"" + escapeJson(endTime) + "\","
                + "\"capacity\":" + capacity + ","
                + "\"enrolledCount\":" + enrolledCount + ","
                + "\"description\":\"" + escapeJson(description) + "\","
                + "\"addons\":[]"
                + "}";
    }

    public static String escapeJson(String s) {
        if (s == null) return "";
        StringBuilder sb = new StringBuilder();
        for (char c : s.toCharArray()) {
            switch (c) {
                case '"': sb.append("\\\""); break;
                case '\\': sb.append("\\\\"); break;
                case '\b': sb.append("\\b"); break;
                case '\f': sb.append("\\f"); break;
                case '\n': sb.append("\\n"); break;
                case '\r': sb.append("\\r"); break;
                case '\t': sb.append("\\t"); break;
                default:
                    if (c < ' ') {
                        sb.append(String.format("\\u%04x", (int) c));
                    } else {
                        sb.append(c);
                    }
            }
        }
        return sb.toString();
    }
}
