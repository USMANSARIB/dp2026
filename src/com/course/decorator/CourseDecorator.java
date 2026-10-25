package com.course.decorator;

import com.course.model.Course;
import com.course.model.CourseComponent;
import java.util.List;

/**
 * Abstract Decorator class in the Decorator Pattern.
 * Implements the CourseComponent interface and maintains a reference to a wrapped CourseComponent.
 * Delegates default behavior to the wrapped component.
 */
public abstract class CourseDecorator implements CourseComponent {
    protected CourseComponent decoratedCourse;

    public CourseDecorator(CourseComponent decoratedCourse) {
        this.decoratedCourse = decoratedCourse;
    }

    @Override
    public int getId() { return decoratedCourse.getId(); }

    @Override
    public String getCode() { return decoratedCourse.getCode(); }

    @Override
    public String getTitle() { return decoratedCourse.getTitle(); }

    @Override
    public String getInstructor() { return decoratedCourse.getInstructor(); }

    @Override
    public int getCredits() { return decoratedCourse.getCredits(); }

    @Override
    public double getBaseFee() { return decoratedCourse.getBaseFee(); }

    @Override
    public double getTotalFee() { return decoratedCourse.getTotalFee(); }

    @Override
    public String getDay() { return decoratedCourse.getDay(); }

    @Override
    public String getStartTime() { return decoratedCourse.getStartTime(); }

    @Override
    public String getEndTime() { return decoratedCourse.getEndTime(); }

    @Override
    public String getScheduleSummary() { return decoratedCourse.getScheduleSummary(); }

    @Override
    public List<String> getAddonFeatures() { return decoratedCourse.getAddonFeatures(); }

    @Override
    public String getDescription() { return decoratedCourse.getDescription(); }

    @Override
    public int getCapacity() { return decoratedCourse.getCapacity(); }

    @Override
    public int getEnrolledCount() { return decoratedCourse.getEnrolledCount(); }

    @Override
    public String toJson() {
        StringBuilder addonsJson = new StringBuilder("[");
        List<String> addons = getAddonFeatures();
        for (int i = 0; i < addons.size(); i++) {
            addonsJson.append("\"").append(Course.escapeJson(addons.get(i))).append("\"");
            if (i < addons.size() - 1) addonsJson.append(",");
        }
        addonsJson.append("]");

        return "{"
                + "\"id\":" + getId() + ","
                + "\"code\":\"" + Course.escapeJson(getCode()) + "\","
                + "\"title\":\"" + Course.escapeJson(getTitle()) + "\","
                + "\"instructor\":\"" + Course.escapeJson(getInstructor()) + "\","
                + "\"credits\":" + getCredits() + ","
                + "\"baseFee\":" + String.format(java.util.Locale.US, "%.2f", getBaseFee()) + ","
                + "\"totalFee\":" + String.format(java.util.Locale.US, "%.2f", getTotalFee()) + ","
                + "\"day\":\"" + Course.escapeJson(getDay()) + "\","
                + "\"startTime\":\"" + Course.escapeJson(getStartTime()) + "\","
                + "\"endTime\":\"" + Course.escapeJson(getEndTime()) + "\","
                + "\"scheduleSummary\":\"" + Course.escapeJson(getScheduleSummary()) + "\","
                + "\"capacity\":" + getCapacity() + ","
                + "\"enrolledCount\":" + getEnrolledCount() + ","
                + "\"description\":\"" + Course.escapeJson(getDescription()) + "\","
                + "\"addons\":" + addonsJson.toString()
                + "}";
    }
}
