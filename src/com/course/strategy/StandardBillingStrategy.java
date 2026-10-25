package com.course.strategy;

/**
 * Concrete Strategy in the Strategy Pattern.
 * Regular tuition plan with standard university rates (no discounts).
 */
public class StandardBillingStrategy implements TuitionBillingStrategy {
    @Override
    public String getPlanName() {
        return "Standard Student Plan";
    }

    @Override
    public double calculateTuition(double courseFee, int credits) {
        return courseFee;
    }

    @Override
    public double getDiscountRate() {
        return 0.0;
    }

    @Override
    public String getDescription() {
        return "Standard baseline university tuition rate with no special discounts applied.";
    }
}
