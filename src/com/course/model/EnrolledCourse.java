package com.course.model;

import com.course.strategy.TuitionBillingStrategy;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;

/**
 * Represents an enrolled course in the student's personal schedule.
 * Integrates:
 * 1. Decorator Pattern: The course field is a decorated CourseComponent (e.g. Lab, Honors, Certificate).
 * 2. Strategy Pattern: The tuition is calculated using a chosen TuitionBillingStrategy.
 */
public class EnrolledCourse {
    private final CourseComponent course;
    private final TuitionBillingStrategy billingStrategy;
    private final double finalTuition;
    private final String enrolledAt;

    public EnrolledCourse(CourseComponent course, TuitionBillingStrategy billingStrategy) {
        this.course = course;
        this.billingStrategy = billingStrategy;
        this.finalTuition = billingStrategy.calculateTuition(course.getTotalFee(), course.getCredits());
        this.enrolledAt = new SimpleDateFormat("yyyy-MM-dd HH:mm").format(new Date());
    }

    public CourseComponent getCourse() {
        return course;
    }

    public TuitionBillingStrategy getBillingStrategy() {
        return billingStrategy;
    }

    public double getFinalTuition() {
        return finalTuition;
    }

    public String getEnrolledAt() {
        return enrolledAt;
    }

    public String toJson() {
        StringBuilder addonsJson = new StringBuilder("[");
        List<String> addons = course.getAddonFeatures();
        for (int i = 0; i < addons.size(); i++) {
            addonsJson.append("\"").append(Course.escapeJson(addons.get(i))).append("\"");
            if (i < addons.size() - 1) addonsJson.append(",");
        }
        addonsJson.append("]");

        return "{"
                + "\"courseId\":" + course.getId() + ","
                + "\"code\":\"" + Course.escapeJson(course.getCode()) + "\","
                + "\"title\":\"" + Course.escapeJson(course.getTitle()) + "\","
                + "\"instructor\":\"" + Course.escapeJson(course.getInstructor()) + "\","
                + "\"credits\":" + course.getCredits() + ","
                + "\"baseFee\":" + String.format(java.util.Locale.US, "%.2f", course.getBaseFee()) + ","
                + "\"totalFee\":" + String.format(java.util.Locale.US, "%.2f", course.getTotalFee()) + ","
                + "\"finalTuition\":" + String.format(java.util.Locale.US, "%.2f", finalTuition) + ","
                + "\"billingPlan\":\"" + Course.escapeJson(billingStrategy.getPlanName()) + "\","
                + "\"discountRate\":" + billingStrategy.getDiscountRate() + ","
                + "\"day\":\"" + Course.escapeJson(course.getDay()) + "\","
                + "\"startTime\":\"" + Course.escapeJson(course.getStartTime()) + "\","
                + "\"endTime\":\"" + Course.escapeJson(course.getEndTime()) + "\","
                + "\"scheduleSummary\":\"" + Course.escapeJson(course.getScheduleSummary()) + "\","
                + "\"enrolledAt\":\"" + Course.escapeJson(enrolledAt) + "\","
                + "\"addons\":" + addonsJson.toString()
                + "}";
    }
}
