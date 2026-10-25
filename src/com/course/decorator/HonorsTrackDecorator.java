package com.course.decorator;

import com.course.model.CourseComponent;
import java.util.ArrayList;
import java.util.List;

/**
 * Concrete Decorator in the Decorator Pattern.
 * Dynamically decorates a course with an Honors Research Track.
 * Augments course credits (+1 honors credit) and adds specialized faculty mentorship.
 */
public class HonorsTrackDecorator extends CourseDecorator {
    private static final double HONORS_FEE = 100.00;
    private static final int BONUS_CREDIT = 1;

    public HonorsTrackDecorator(CourseComponent decoratedCourse) {
        super(decoratedCourse);
    }

    @Override
    public int getCredits() {
        return super.getCredits() + BONUS_CREDIT;
    }

    @Override
    public double getTotalFee() {
        return super.getTotalFee() + HONORS_FEE;
    }

    @Override
    public List<String> getAddonFeatures() {
        List<String> features = new ArrayList<>(super.getAddonFeatures());
        features.add("Honors Research Track (+1 Credit, +$100.00, 1-on-1 Faculty Mentorship)");
        return features;
    }
}
