package com.course.strategy;

/**
 * Concrete Strategy in the Strategy Pattern.
 * Applies an Early Registration Incentive (15% reduction on tuition).
 */
public class EarlyRegistrationStrategy implements TuitionBillingStrategy {
    private static final double DISCOUNT_RATE = 0.15;

    @Override
    public String getPlanName() {
        return "Early Registration Incentive";
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
        return "Priority enrollment discount giving a 15% reduction for registering before the priority deadline.";
    }
}
