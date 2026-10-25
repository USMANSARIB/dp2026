package com.course.model;

import java.util.List;

/**
 * Component interface in the Decorator Pattern.
 * Defines the common behavior for core courses and all dynamic course decorators.
 */
public interface CourseComponent {
    int getId();
    String getCode();
    String getTitle();
    String getInstructor();
    int getCredits();
    double getBaseFee();
    double getTotalFee();
    String getDay();
    String getStartTime();
    String getEndTime();
    String getScheduleSummary();
    List<String> getAddonFeatures();
    String getDescription();
    int getCapacity();
    int getEnrolledCount();
    
    /**
     * Serializes course component details into JSON format.
     */
    String toJson();
}
