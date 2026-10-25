package com.course.strategy;

/**
 * Strategy interface in the Strategy Pattern.
 * Defines the contract for interchangeable tuition billing and discount calculation algorithms.
 */
public interface TuitionBillingStrategy {
    /**
     * Gets the user-friendly name of the billing plan.
     */
    String getPlanName();

    /**
     * Calculates the final payable tuition based on the course fee and credit hours.
     * @param courseFee total fee after decorators are applied
     * @param credits course credit hours
     * @return final calculated tuition
     */
    double calculateTuition(double courseFee, int credits);

    /**
     * Discount percentage applied (e.g., 0.30 for 30%).
     */
    double getDiscountRate();

    /**
     * Description explaining the eligibility/benefits of this billing strategy.
     */
    String getDescription();
}
