package com.course.strategy;

/**
 * Concrete Strategy in the Strategy Pattern.
 * Applies an Academic Merit Scholarship discount (30% discount on tuition).
 */
public class MeritScholarshipStrategy implements TuitionBillingStrategy {
    private static final double DISCOUNT_RATE = 0.30;

    @Override
    public String getPlanName() {
        return "Academic Merit Scholarship";
    }

    @Override
    public double calculateTuition(double courseFee, int credits) {
        return courseFee * (1.0 - DISCOUNT_RATE);
    }

    @Override
    public double getDiscountRate() {
        return DISCOUNT_RATE;
    }

    @Override
    public String getDescription() {
        return "Dean's List / High Academic Achievement grant providing a 30% reduction on tuition.";
    }
}
