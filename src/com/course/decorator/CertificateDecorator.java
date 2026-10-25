package com.course.decorator;

import com.course.model.CourseComponent;
import java.util.ArrayList;
import java.util.List;

/**
 * Concrete Decorator in the Decorator Pattern.
 * Dynamically decorates a course with an Official Verified Certificate credential.
 * Adds proctored certification exam access and verifiable digital credential (+$75.00).
 */
public class CertificateDecorator extends CourseDecorator {
    private static final double CERTIFICATE_FEE = 75.00;

    public CertificateDecorator(CourseComponent decoratedCourse) {
        super(decoratedCourse);
    }

    @Override
    public double getTotalFee() {
        return super.getTotalFee() + CERTIFICATE_FEE;
    }

    @Override
    public List<String> getAddonFeatures() {
        List<String> features = new ArrayList<>(super.getAddonFeatures());
        features.add("Verified Professional Certificate (+$75.00, proctored exam voucher & digital badge)");
        return features;
    }
}
