package com.course.decorator;

import com.course.model.CourseComponent;
import java.util.ArrayList;
import java.util.List;

/**
 * Concrete Decorator in the Decorator Pattern.
 * Dynamically decorates a course with a hands-on Laboratory Session.
 * Adds lab equipment fee (+$150.00) and lab session hours.
 */
public class LabSessionDecorator extends CourseDecorator {
    private static final double LAB_FEE = 150.00;

    public LabSessionDecorator(CourseComponent decoratedCourse) {
        super(decoratedCourse);
    }

    @Override
    public double getTotalFee() {
        return super.getTotalFee() + LAB_FEE;
    }

    @Override
    public String getScheduleSummary() {
        return super.getScheduleSummary() + " [Includes 2hr Lab Session]";
    }

    @Override
    public List<String> getAddonFeatures() {
        List<String> features = new ArrayList<>(super.getAddonFeatures());
        features.add("Hands-on Laboratory Session (+$150.00, dedicated workstation & equipment)");
        return features;
    }
}
