# Design Patterns in Student Course Management System

This document provides an in-depth architectural explanation of how the **Decorator**, **Strategy**, and **Observer** design patterns are implemented in Java for the Student Course Management System.

---

## 1. Architectural Overview

The system manages university courses (creation, update, deletion), student wishlists, active weekly timetables, conflict detection, and tuition billing. 

```
                                 +-----------------------+
                                 |  Web Browser Client   |
                                 | (Clean White Minimal) |
                                 +-----------+-----------+
                                             | HTTP / JSON
                                             v
                                 +-----------------------+
                                 |   SimpleHttpServer    |
                                 | (Java SE com.sun.net) |
                                 +-----------+-----------+
                                             |
                                             v
+-----------------------------------------------------------------------------------------+
|                                    CourseManager                                        |
|  (Central Service & CourseSubject orchestrating Catalog, Schedule, and Wishlist)       |
+--------------------------------------------+--------------------------------------------+
       |                                     |                                     |
       v                                     v                                     v
+-------------------+              +-------------------+                 +-------------------+
| DECORATOR PATTERN |              | STRATEGY PATTERN  |                 | OBSERVER PATTERN  |
| Course Add-ons &  |              | Tuition Billing   |                 | Real-time Alerts  |
| Dynamic Options   |              | & Scholarships    |                 | & Audit Tracking  |
+-------------------+              +-------------------+                 +-------------------+
```

### Clean Domain Abstraction (Frontend vs Backend Separation)
As per software engineering best practices, design patterns are strictly internal structural and behavioral solutions in the **backend**. The user-facing frontend utilizes intuitive domain terminology:
- **Decorator Pattern** $\rightarrow$ Presented as *"Course Add-ons & Practicum Options"* (Lab Sessions, Honors Track, Verified Certificates).
- **Strategy Pattern** $\rightarrow$ Presented as *"Tuition & Scholarship Plans"* (Standard Student, Academic Merit, Need-Based Aid, Early Bird).
- **Observer Pattern** $\rightarrow$ Presented as *"Live Alerts & System Activity Feed"* (Timetable synchronization, conflict warnings, administrative audits).

---

## 2. Decorator Design Pattern (Structural)

### 2.1 The Problem
Academic courses often offer elective add-ons such as:
1. Laboratory practicum sessions ($+\$150$, $+2$ practical hours).
2. Honors research tracks ($+\$100$, $+1$ bonus academic credit, faculty mentorship).
3. Verified industry certificates ($+\$75$, proctored exam voucher).

If inheritance were used to support every combination, a **combinatorial class explosion** would occur:
- `CourseWithLab`
- `CourseWithHonors`
- `CourseWithCertificate`
- `CourseWithLabAndHonors`
- `CourseWithLabAndCertificate`
- `CourseWithLabHonorsAndCertificate` ($2^N$ subclasses for $N$ options).

### 2.2 The Solution
The **Decorator Pattern** allows features to be attached dynamically to a base course at runtime by wrapping it within decorator objects that conform to the same interface (`CourseComponent`).

### 2.3 Class Structure

```
                         <<interface>>
                        CourseComponent
              +----------------------------------+
              | +getId(): int                    |
              | +getCode(): String               |
              | +getTitle(): String              |
              | +getCredits(): int               |
              | +getBaseFee(): double            |
              | +getTotalFee(): double           |
              | +getScheduleSummary(): String    |
              | +getAddonFeatures(): List<String>|
              +----------------------------------+
                               ^
                               |
            +------------------+------------------+
            |                                     |
    +---------------+                   +--------------------+
    |    Course     |                   |  CourseDecorator   | (abstract)
    |  (Component)  |                   +--------------------+
    +---------------+                   | -decoratedCourse   |
                                        +--------------------+
                                                  ^
                                                  |
                     +----------------------------+----------------------------+
                     |                            |                            |
          +---------------------+      +---------------------+      +---------------------+
          | LabSessionDecorator |      | HonorsTrackDecorator|      |CertificateDecorator |
          +---------------------+      +---------------------+      +---------------------+
          | +getTotalFee()      |      | +getCredits()       |      | +getTotalFee()      |
          | +getScheduleSummary()      | +getTotalFee()      |      | +getAddonFeatures() |
          +---------------------+      +---------------------+      +---------------------+
```

### 2.4 Implementation Details

- **`CourseComponent.java`**: The common interface defining methods for course metadata, credit hours, fee calculations, and schedule information.
- **`Course.java`**: Concrete component storing core course data (e.g. `CS101`, 3 credits, $\$450.00$ base fee).
- **`CourseDecorator.java`**: Abstract decorator that implements `CourseComponent` and holds a reference to `decoratedCourse`. By default, it delegates all method calls to the wrapped instance.
- **`LabSessionDecorator.java`**: Overrides `getTotalFee()` by adding $\$150.00$ and overrides `getScheduleSummary()` to append laboratory hours.
- **`HonorsTrackDecorator.java`**: Overrides `getCredits()` by adding $+1$ credit and `getTotalFee()` by adding $\$100.00$.
- **`CertificateDecorator.java`**: Overrides `getTotalFee()` by adding $\$75.00$ and appends verified certification details.

### 2.5 Dynamic Composition in Code
When a student enrolls, the decorators wrap the course dynamically:

```java
CourseComponent course = baseCourse;

if (addLab) {
    course = new LabSessionDecorator(course);
}
if (addHonors) {
    course = new HonorsTrackDecorator(course);
}
if (addCertificate) {
    course = new CertificateDecorator(course);
}

// course.getCredits() -> dynamically computes credits (e.g. 3 + 1 = 4)
// course.getTotalFee() -> dynamically aggregates fees ($450 + $150 + $100 = $700)
```

---

## 3. Strategy Design Pattern (Behavioral)

### 3.1 The Problem
Tuition calculation varies across different student tiers and financial aid categories:
- Regular standard tuition ($100\%$).
- Academic Merit Scholarship ($30\%$ discount).
- Need-Based Financial Aid Grant ($50\%$ discount).
- Early Registration Incentive ($15\%$ discount).

Hardcoding nested conditional branches (`if/else` or `switch`) inside the enrollment calculation violates the **Open/Closed Principle** (OCP) and makes adding new scholarships or changing rates error-prone.

### 3.2 The Solution
The **Strategy Pattern** defines a family of tuition billing algorithms, encapsulates each one inside a separate class, and makes them interchangeable at runtime.

### 3.3 Class Structure

```
                                <<interface>>
                            TuitionBillingStrategy
                +--------------------------------------------+
                | +getPlanName(): String                     |
                | +calculateTuition(fee: double, cr: int): db|
                | +getDiscountRate(): double                 |
                | +getDescription(): String                  |
                +--------------------------------------------+
                                       ^
         +--------------------+--------+--------+--------------------+
         |                    |                 |                    |
+-----------------+  +-----------------+  +----------------+  +---------------------+
| StandardBilling |  |MeritScholarship |  |  FinancialAid  |  |  EarlyRegistration  |
|    Strategy     |  |    Strategy     |  |    Strategy    |  |       Strategy      |
+-----------------+  +-----------------+  +----------------+  +---------------------+
| rate = 0.0      |  | rate = 0.30     |  | rate = 0.50    |  | rate = 0.15         |
+-----------------+  +-----------------+  +----------------+  +---------------------+
```

### 3.4 Implementation Details

- **`TuitionBillingStrategy.java`**: Strategy interface declaring `calculateTuition(double courseFee, int credits)`.
- **`StandardBillingStrategy.java`**: `return courseFee;`
- **`MeritScholarshipStrategy.java`**: `return courseFee * 0.70;` (30% reduction).
- **`FinancialAidStrategy.java`**: `return courseFee * 0.50;` (50% reduction).
- **`EarlyRegistrationStrategy.java`**: `return courseFee * 0.85;` (15% reduction).

### 3.5 Runtime Execution in Code

```java
TuitionBillingStrategy strategy;
switch (strategyType) {
    case "merit": strategy = new MeritScholarshipStrategy(); break;
    case "financial_aid": strategy = new FinancialAidStrategy(); break;
    case "early_bird": strategy = new EarlyRegistrationStrategy(); break;
    default: strategy = new StandardBillingStrategy(); break;
}

// Total fee calculated after decorators have been applied:
double finalPayable = strategy.calculateTuition(decoratedCourse.getTotalFee(), decoratedCourse.getCredits());
```

---

## 4. Observer Design Pattern (Behavioral)

### 4.1 The Problem
When course operations occur (such as adding a course, modifying lecture times, dropping a class, or detecting schedule overlaps), multiple distinct system components must respond:
1. The **Student Notification Center** must display real-time user-facing alerts.
2. The **Schedule Synchronization Engine** must check for timetable conflicts and update calendar slots.
3. The **Administrative Audit Logger** must record immutable audit logs with timestamps.

Coupling all of these responsibilities directly into `CourseManager` violates the **Single Responsibility Principle** (SRP).

### 4.2 The Solution
The **Observer Pattern** establishes a one-to-many dependency between an observable subject (`CourseSubject`) and observer objects (`CourseObserver`). When an event occurs, all registered observers are notified automatically without the subject knowing their concrete implementations.

### 4.3 Class Structure

```
        <<interface>>                                      <<interface>>
        CourseSubject                                      CourseObserver
+-----------------------------+               +--------------------------------------+
| +registerObserver(o)        |               | +onCourseEvent(type, course, details)|
| +removeObserver(o)          |               +--------------------------------------+
| +notifyObservers(...)       |                                  ^
+-----------------------------+                                  |
               ^                               +-----------------+-----------------+
               |                               |                 |                 |
     +-------------------+            +-----------------+ +---------------+ +---------------+
     |   CourseManager   |<>--------->|   StudentNotif  | | ScheduleSync  | |  AuditLogger  |
     | (ConcreteSubject) |            |     Observer    | |   Observer    | |   Observer    |
     +-------------------+            +-----------------+ +---------------+ +---------------+
```

### 4.4 Implementation Details

- **`CourseObserver.java`**: Interface specifying `onCourseEvent(String eventType, CourseComponent course, String details)`.
- **`CourseSubject.java`**: Interface for registering, deregistering, and notifying observers.
- **`CourseManager.java`**: The concrete subject maintaining a thread-safe list of `CourseObserver` instances.
- **`StudentNotificationObserver.java`**: Maintains a chronological buffer of user alerts (e.g. `COURSE_ADDED`, `SCHEDULE_ENROLLED`, `SCHEDULE_CONFLICT`).
- **`ScheduleSyncObserver.java`**: Listens for course updates (`COURSE_UPDATED`) or deletions (`COURSE_DELETED`) to monitor timetable integrity.
- **`AuditLoggerObserver.java`**: Records administrative audit entries with ISO timestamps.

### 4.5 Event Dispatch Workflow in Code

```java
// Inside CourseManager:
public void notifyObservers(String eventType, CourseComponent course, String details) {
    for (CourseObserver observer : observers) {
        observer.onCourseEvent(eventType, course, details);
    }
}

// Triggered during enrollment:
notifyObservers("SCHEDULE_ENROLLED", decoratedCourse, 
    "Enrolled in " + decoratedCourse.getCode() + " with " + strategy.getPlanName());

// Triggered when a time conflict is detected:
notifyObservers("SCHEDULE_CONFLICT", conflictingCourse, 
    "Time conflict detected with enrolled course: " + existingCourse.getCode());
```

---

## 5. Pattern Synergy: A Complete Enrollment Lifecycle

When a student enrolls in a course through the portal:

```
1. Client sends POST /api/enroll:
   { courseId: 1, addLab: true, addHonors: true, addCert: false, strategy: "merit" }
        |
        v
2. CourseManager retrieves base Course:
   BaseCourse ("CS101", 3 credits, $450 baseFee)
        |
        v
3. DECORATOR PATTERN dynamically wraps the base course:
   CourseComponent decorated = new HonorsTrackDecorator(new LabSessionDecorator(baseCourse));
   -> Credits = 3 + 1 = 4 credits
   -> Total Fee = $450 + $150 (Lab) + $100 (Honors) = $700.00
        |
        v
4. STRATEGY PATTERN calculates tuition:
   TuitionBillingStrategy strategy = new MeritScholarshipStrategy();
   -> Final Payable = $700.00 * (1.0 - 0.30) = $490.00
        |
        v
5. OBSERVER PATTERN notifies registered listeners:
   CourseManager.notifyObservers("SCHEDULE_ENROLLED", decorated, "Enrolled in CS101...");
   -> StudentNotificationObserver adds alert to notification tray
   -> ScheduleSyncObserver records timetable block
   -> AuditLoggerObserver appends to system audit log
        |
        v
6. HTTP 200 OK returned to frontend with updated state
```

---

## 6. How to Run the Application

### Prerequisites
- Java Development Kit (JDK 17 or higher, including JDK 21 / 26).

### 1. Compile
From the workspace root directory, run:
```powershell
javac -d bin (Get-ChildItem -Path src -Filter *.java -Recurse | Select-Object -ExpandProperty FullName)
```

### 2. Run
```powershell
java -cp bin com.course.Main 8080
```

### 3. Open in Browser
Navigate to:
```
http://localhost:8080
```
