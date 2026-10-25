package com.course.strategy;

/**
 * Concrete Strategy in the Strategy Pattern.
 * Applies a Need-Based Financial Aid grant (50% reduction on tuition).
 */
public class FinancialAidStrategy implements TuitionBillingStrategy {
    private static final double DISCOUNT_RATE = 0.50;

    @Override
    public String getPlanName() {
        return "Need-Based Financial Aid";
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
        return "University student endowment grant providing a 50% reduction on tuition for eligible students.";
    }
}
