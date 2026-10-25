package com.course.service;

import com.course.decorator.CertificateDecorator;
import com.course.decorator.HonorsTrackDecorator;
import com.course.decorator.LabSessionDecorator;
import com.course.model.Course;
import com.course.model.CourseComponent;
import com.course.model.EnrolledCourse;
import com.course.observer.CourseObserver;
import com.course.observer.CourseSubject;
import com.course.observer.StudentNotificationObserver;
import com.course.observer.ScheduleSyncObserver;
import com.course.observer.AuditLoggerObserver;
import com.course.strategy.EarlyRegistrationStrategy;
import com.course.strategy.FinancialAidStrategy;
import com.course.strategy.MeritScholarshipStrategy;
import com.course.strategy.StandardBillingStrategy;
import com.course.strategy.TuitionBillingStrategy;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Central Service that manages Course Catalog, Wishlist, and Student Schedule.
 * Implements CourseSubject to broadcast lifecycle events to registered Observers.
 */
public class CourseManager implements CourseSubject {
    private final Map<Integer, Course> courseCatalog = new LinkedHashMap<>();
    private final Set<Integer> wishlist = new LinkedHashSet<>();
    private final Map<Integer, EnrolledCourse> studentSchedule = new LinkedHashMap<>();
    private final List<CourseObserver> observers = new ArrayList<>();

    private int nextCourseId = 1;

    // Direct access to observers for UI consumption
    private final StudentNotificationObserver notificationObserver = new StudentNotificationObserver();
    private final ScheduleSyncObserver scheduleSyncObserver = new ScheduleSyncObserver();
    private final AuditLoggerObserver auditLoggerObserver = new AuditLoggerObserver();

    public CourseManager() {
        // Automatically register core system observers
        registerObserver(notificationObserver);
        registerObserver(scheduleSyncObserver);
        registerObserver(auditLoggerObserver);

        // Seed initial course catalog
        seedInitialData();
    }

    // ================= Observer Subject Implementation =================

    @Override
    public synchronized void registerObserver(CourseObserver observer) {
        if (!observers.contains(observer)) {
            observers.add(observer);
        }
    }

    @Override
    public synchronized void removeObserver(CourseObserver observer) {
        observers.remove(observer);
    }

    @Override
    public synchronized void notifyObservers(String eventType, CourseComponent course, String details) {
        for (CourseObserver observer : observers) {
            try {
                observer.onCourseEvent(eventType, course, details);
            } catch (Exception e) {
                System.err.println("Error notifying observer: " + e.getMessage());
            }
        }
    }

    public StudentNotificationObserver getNotificationObserver() {
        return notificationObserver;
    }

    public ScheduleSyncObserver getScheduleSyncObserver() {
        return scheduleSyncObserver;
    }

    public AuditLoggerObserver getAuditLoggerObserver() {
        return auditLoggerObserver;
    }

    // ================= Course Catalog Management =================

    public synchronized Course addCourse(String code, String title, String instructor, int credits,
                                         double baseFee, String day, String startTime, String endTime,
                                         int capacity, String description) {
        int id = nextCourseId++;
        Course course = new Course(id, code, title, instructor, credits, baseFee, day,
                                   startTime, endTime, capacity, 0, description);
        courseCatalog.put(id, course);

        notifyObservers("COURSE_ADDED", course, "New course published: " + code + " - " + title);
        return course;
    }

    public synchronized boolean updateCourse(int id, String code, String title, String instructor,
                                             int credits, double baseFee, String day,
                                             String startTime, String endTime, int capacity,
                                             String description) {
        Course course = courseCatalog.get(id);
        if (course == null) return false;

        String oldSchedule = course.getScheduleSummary();

        course.setCode(code);
        course.setTitle(title);
        course.setInstructor(instructor);
        course.setCredits(credits);
        course.setBaseFee(baseFee);
        course.setDay(day);
        course.setStartTime(startTime);
        course.setEndTime(endTime);
        course.setCapacity(capacity);
        course.setDescription(description);

        String newSchedule = course.getScheduleSummary();
        String changeDetails = "Course updated: " + code + " (" + title + ")";
        if (!oldSchedule.equals(newSchedule)) {
            changeDetails += " [Schedule changed from: " + oldSchedule + " to: " + newSchedule + "]";
        }

        notifyObservers("COURSE_UPDATED", course, changeDetails);
        return true;
    }

    public synchronized boolean deleteCourse(int id) {
        Course course = courseCatalog.remove(id);
        if (course == null) return false;

        // Clean up from wishlist and student schedule
        wishlist.remove(id);
        studentSchedule.remove(id);

        notifyObservers("COURSE_DELETED", course, "Course " + course.getCode() + " was deleted from curriculum.");
        return true;
    }

    public synchronized Course getCourse(int id) {
        return courseCatalog.get(id);
    }

    public synchronized List<Course> getAllCourses() {
        return new ArrayList<>(courseCatalog.values());
    }

    // ================= Wishlist Management =================

    public synchronized boolean addToWishlist(int courseId) {
        Course course = courseCatalog.get(courseId);
        if (course == null) return false;

        if (wishlist.contains(courseId)) {
            return false; // already in wishlist
        }

        wishlist.add(courseId);
        notifyObservers("WISHLIST_ADDED", course, "Added to student wishlist: " + course.getCode());
        return true;
    }

    public synchronized boolean removeFromWishlist(int courseId) {
        Course course = courseCatalog.get(courseId);
        boolean removed = wishlist.remove(courseId);
        if (removed && course != null) {
            notifyObservers("WISHLIST_REMOVED", course, "Removed from wishlist: " + course.getCode());
        }
        return removed;
    }

    public synchronized List<Course> getWishlist() {
        List<Course> list = new ArrayList<>();
        for (Integer id : wishlist) {
            Course c = courseCatalog.get(id);
            if (c != null) {
                list.add(c);
            }
        }
        return list;
    }

    public synchronized boolean isWishlisted(int courseId) {
        return wishlist.contains(courseId);
    }

    // ================= Schedule & Enrollment (Decorator & Strategy Integration) =================

    /**
     * Enrolls a student into a course using dynamic decorators (Lab, Honors, Certificate)
     * and a selected TuitionBillingStrategy.
     */
    public synchronized String enrollCourse(int courseId, boolean addLab, boolean addHonors,
                                            boolean addCertificate, String strategyType) {
        Course baseCourse = courseCatalog.get(courseId);
        if (baseCourse == null) {
            return "Course not found.";
        }

        if (studentSchedule.containsKey(courseId)) {
            return "You are already enrolled in this course (" + baseCourse.getCode() + ").";
        }

        if (baseCourse.getEnrolledCount() >= baseCourse.getCapacity()) {
            notifyObservers("ENROLLMENT_FAILED", baseCourse, "Enrollment failed: Course is at full capacity (" + baseCourse.getCode() + ").");
            return "Course is at full capacity.";
        }

        // Validate time conflict with existing enrolled courses
        for (EnrolledCourse existing : studentSchedule.values()) {
            if (hasTimeConflict(baseCourse.getDay(), baseCourse.getStartTime(), baseCourse.getEndTime(),
                                existing.getCourse().getDay(), existing.getCourse().getStartTime(), existing.getCourse().getEndTime())) {
                String conflictMsg = "Time conflict detected with enrolled course: "
                        + existing.getCourse().getCode() + " (" + existing.getCourse().getScheduleSummary() + ").";
                notifyObservers("SCHEDULE_CONFLICT", baseCourse, conflictMsg);
                return conflictMsg;
            }
        }

        // 1. DECORATOR PATTERN: Dynamically decorate the base course with selected add-ons
        CourseComponent decorated = baseCourse;
        if (addLab) {
            decorated = new LabSessionDecorator(decorated);
        }
        if (addHonors) {
            decorated = new HonorsTrackDecorator(decorated);
        }
        if (addCertificate) {
            decorated = new CertificateDecorator(decorated);
        }

        // 2. STRATEGY PATTERN: Select and apply the tuition billing strategy
        TuitionBillingStrategy strategy;
        if ("merit".equalsIgnoreCase(strategyType)) {
            strategy = new MeritScholarshipStrategy();
        } else if ("financial_aid".equalsIgnoreCase(strategyType)) {
            strategy = new FinancialAidStrategy();
        } else if ("early_bird".equalsIgnoreCase(strategyType)) {
            strategy = new EarlyRegistrationStrategy();
        } else {
            strategy = new StandardBillingStrategy();
        }

        EnrolledCourse enrollment = new EnrolledCourse(decorated, strategy);
        studentSchedule.put(courseId, enrollment);
        baseCourse.incrementEnrolled();

        // Optional: remove from wishlist if enrolled
        wishlist.remove(courseId);

        String successMsg = "Successfully enrolled in " + baseCourse.getCode()
                + " [Plan: " + strategy.getPlanName()
                + ", Total: $" + String.format(java.util.Locale.US, "%.2f", enrollment.getFinalTuition()) + "]";
        notifyObservers("SCHEDULE_ENROLLED", decorated, successMsg);
        return null; // null means success
    }

    public synchronized boolean dropCourse(int courseId) {
        EnrolledCourse enrolled = studentSchedule.remove(courseId);
        if (enrolled == null) return false;

        Course baseCourse = courseCatalog.get(courseId);
        if (baseCourse != null) {
            baseCourse.decrementEnrolled();
            notifyObservers("SCHEDULE_DROPPED", enrolled.getCourse(), "Dropped course: " + baseCourse.getCode());
        }
        return true;
    }

    public synchronized List<EnrolledCourse> getSchedule() {
        return new ArrayList<>(studentSchedule.values());
    }

    public synchronized boolean isEnrolled(int courseId) {
        return studentSchedule.containsKey(courseId);
    }

    // ================= Timetable Conflict Detection Helper =================

    public static boolean hasTimeConflict(String day1, String start1, String end1,
                                          String day2, String start2, String end2) {
        if (!day1.equalsIgnoreCase(day2)) {
            return false; // different days, no conflict
        }

        int s1 = parseTimeToMinutes(start1);
        int e1 = parseTimeToMinutes(end1);
        int s2 = parseTimeToMinutes(start2);
        int e2 = parseTimeToMinutes(end2);

        // Conflict occurs if intervals overlap: max(s1, s2) < min(e1, e2)
        return Math.max(s1, s2) < Math.min(e1, e2);
    }

    private static int parseTimeToMinutes(String timeStr) {
        try {
            String[] parts = timeStr.trim().split(":");
            int hours = Integer.parseInt(parts[0].trim());
            int mins = Integer.parseInt(parts[1].trim());
            return hours * 60 + mins;
        } catch (Exception e) {
            return 0;
        }
    }

    // ================= Seed Sample Courses =================

    private void seedInitialData() {
        addCourse("CS101", "Introduction to Computer Science", "Dr. Alan Turing", 3,
                450.00, "Monday", "09:00", "10:30", 35,
                "Foundations of algorithmic problem-solving, structured programming, and core computing logic.");

        addCourse("CS201", "Data Structures & Algorithms", "Prof. Donald Knuth", 4,
                550.00, "Wednesday", "11:00", "12:30", 30,
                "Advanced data structures including trees, graphs, dynamic programming, and complexity analysis.");

        addCourse("MATH150", "Discrete Mathematics", "Dr. Ada Lovelace", 3,
                420.00, "Tuesday", "10:00", "11:30", 40,
                "Propositional logic, set theory, combinatorics, proof techniques, and graph models.");

        addCourse("PHYS101", "Applied Modern Physics", "Dr. Richard Feynman", 4,
                520.00, "Thursday", "13:00", "14:30", 25,
                "Mechanics, wave dynamics, thermodynamics, and experimental physical principles.");

        addCourse("DS310", "Machine Learning & Neural Networks", "Dr. Geoffrey Hinton", 3,
                600.00, "Friday", "14:00", "15:30", 28,
                "Supervised/unsupervised learning, gradient descent, backpropagation, and deep architectures.");

        addCourse("ART110", "Digital Design & Human Computer Interaction", "Prof. Don Norman", 3,
                380.00, "Monday", "13:00", "14:30", 30,
                "User interface paradigms, ergonomics, cognitive visual hierarchy, and modern design systems.");
    }
}
