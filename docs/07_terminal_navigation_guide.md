# Terminal Navigation & Feature Showcase Guide

A complete, step-by-step procedural manual for navigating and demonstrating all features of the **Student Course Management System** directly from the terminal.

---

## 1. Overview & Launch Modes

The system provides an interactive CLI feature navigator that lets you explore every design pattern individually, run real-time system status reports, take a guided tour, or execute the automated test suite.

### How to Launch

```bash
# 1. Interactive Feature Navigation Menu (Default)
python src/main.py

# 2. Automated Guided Tour (Non-interactive / CI)
python src/main.py --all

# 3. Built-in Test Suite Runner (58 Tests)
python src/main.py --test
```

> [!TIP]
> On Windows PowerShell, ensure UTF-8 encoding is enabled for box-drawing characters:
> ```powershell
> $env:PYTHONIOENCODING="utf-8"
> python src/main.py
> ```

---

## 2. Terminal Navigation Menu Map

When launched in interactive mode, the terminal displays the master navigation menu:

```
╔══════════════════════════════════════════════════════════════════╗
║   STUDENT COURSE MANAGEMENT SYSTEM — Terminal Navigation Menu   ║
╚══════════════════════════════════════════════════════════════════╝

  [1] Factory Method Pattern  — Dynamic Course Creation by Type
  [2] Observer Pattern        — Event Subscriptions & Broadcasts
  [3] Strategy Pattern        — Pluggable Runtime Grading Algorithms
  [4] Decorator Pattern       — Course Add-ons & Surcharge Stacking
  [5] Command Pattern         — Reversible Actions, Undo/Redo & Audit
  [6] State Pattern           — Academic Lifecycle & Access Control
  [7] System Status & Reports — Enrollment Summary & Audit Log
  [8] Full Guided Tour        — Walkthrough of All Patterns Step-by-Step
  [9] Run Test Suite          — Execute all 58 Automated Tests
  [0] Exit Application
```

---

## 3. Step-by-Step Feature Procedures

### Feature [1]: Factory Method Pattern — Course Creation
**Goal**: Demonstrate polymorphic instantiation without coupling client code to concrete classes.

#### Procedure:
1. At the prompt `▶ Select an option (0-9):`, enter `1` and press `Enter`.
2. **Step 1.1 — Factory Registry Inspection**:
   - The terminal prints all registered delivery types (`LECTURE`, `LAB`, `ONLINE`, `SEMINAR`).
3. **Step 1.2 — Dynamic Instantiation**:
   - `CourseFactory.create_course()` creates 4 distinct course instances (`CS101`, `CHEM201`, `ENG102`, `PHIL401`).
   - The terminal displays the assigned subclass, title, credit hours, capacity, tuition fee, and custom resource requirements.
4. Press `Enter` to return to the main navigation menu.

#### Sample Terminal Output:
```
  ✅ Created: CHEM201: Organic Chemistry Lab (2 credits, $750.00)
     Subclass    : LabCourse
     Description : 'Organic Chemistry Lab' is a hands-on laboratory course...
     Requirements: ['Lab equipment and safety gear', 'Lab manual', 'PPE']
```

---

### Feature [2]: Observer Pattern — Notifications & Subscriptions
**Goal**: Demonstrate 1-to-many event broadcasting where enrolled students automatically receive updates.

#### Procedure:
1. Enter `2` and press `Enter`.
2. **Step 2.1 — Enrollment & Auto-Subscription**:
   - Students Alice, Bob, and Carol are enrolled in `CS101` and `CHEM201`.
   - The system automatically registers their `update()` callback to the course's `CourseNotificationManager`.
3. **Step 2.2 — Event Broadcasting**:
   - The system publishes `ANNOUNCEMENT` and `ASSIGNMENT_POSTED` events.
   - The terminal shows subscriber counts for each broadcast.
4. **Step 2.3 — Inbox Inspection**:
   - The terminal displays each student's personal message inbox, proving event isolation across courses.
5. Press `Enter` to return to the main menu.

#### Sample Terminal Output:
```
  📢 CS101 announcement sent to 3 subscribed observers
  📝 CS101 assignment notification sent to 3 subscribed observers

  📬 Alice Johnson's inbox (8 messages):
     • [ENROLLMENT_UPDATE] [Course CS101] Alice Johnson has enrolled...
     • [ANNOUNCEMENT] [Course CS101] Midterm exam is on Oct 15 in Hall B!
```

---

### Feature [3]: Strategy Pattern — Pluggable Grading
**Goal**: Demonstrate runtime algorithm swapping without modifying course classes.

#### Procedure:
1. Enter `3` and press `Enter`.
2. **Step 3.1 — Algorithm Swapping**:
   - A standard set of scores (`95.0`, `82.0`, `67.0`, `55.0`, `45.0`) is evaluated across 3 interchangeable strategies:
     - `StandardGradingStrategy`: Letter grades A-F by fixed score cutoffs.
     - `PassFailGradingStrategy`: Binary threshold (`>= 60.0`).
     - `CurvedGradingStrategy`: Applies point curve (`+7.0` pts) before mapping.
3. **Step 3.2 — Multi-Component Weighted Grading**:
   - Evaluates composite grades from homework (30%), midterm (30%), and final (40%).
4. **Step 3.3 — Grade Release with Observer Integration**:
   - Releases computed letter grades and alerts students via notifications.
5. Press `Enter` to return to the main menu.

#### Sample Terminal Output:
```
  Active Strategy: Curved Grading (+7.0 pts)
    Raw Score  95.0 → Letter Grade: A
    Raw Score  82.0 → Letter Grade: B
    Raw Score  67.0 → Letter Grade: C

  Composite Average : 79.9% → Letter Grade: C
```

---

### Feature [4]: Decorator Pattern — Add-on Features & Fee Stacking
**Goal**: Dynamically extend course capabilities and calculate cumulative tuition without class explosion.

#### Procedure:
1. Enter `4` and press `Enter`.
2. **Step 4.1 — Base Course**:
   - Inspects `CS101` base tuition ($600.00).
3. **Step 4.2 — Progressive Stacking**:
   - Wraps `CS101` with `HonorsDistinctionDecorator` (+$150.00 → $750.00).
   - Wraps with `LabAccessPassDecorator` (+$100.00 → $850.00).
   - Wraps with `TutoringSupportDecorator` (+$200.00 → $1050.00).
   - Wraps with `CertificateDecorator` (+$75.00 → $1125.00).
4. **Step 4.3 & 4.4 — Breakdown & Requirements**:
   - Displays itemized financial ledger and accumulated prerequisite list.
5. Press `Enter` to return to the main menu.

#### Sample Terminal Output:
```
  Base fee:       $600.00
  + Honors:       $150.00
  + Lab Access:   $100.00
  + Tutoring:     $200.00
  + Certificate:  $ 75.00
  ────────────────────────
  Total Tuition:  $1125.00
```

---

### Feature [5]: Command Pattern — Transactions, Undo/Redo & Audit Trail
**Goal**: Encapsulate operations as objects to provide atomic execution, undo, redo, and audit logging.

#### Procedure:
1. Enter `5` and press `Enter`.
2. **Step 5.1 — Command Execution**:
   - Executes `EnrollStudentCommand` for David Kim in `CHEM201`.
   - Verifies David is in the course roster.
3. **Step 5.2 — Rollback (Undo)**:
   - Invokes `mgr.undo()`.
   - Verifies David is removed from the roster.
4. **Step 5.3 — Roll-Forward (Redo)**:
   - Invokes `mgr.redo()`.
   - Verifies David is restored to the roster.
5. **Step 5.4 — Grade Typo Correction**:
   - Records grade `78.0` (C), then an accidental update `96.0` (A).
   - Invokes `mgr.undo()` to restore the original `78.0` (C).
6. **Step 5.5 — Audit Trail**:
   - Displays chronological, timestamped ledger of all executed, undone, and redone transactions.
7. Press `Enter` to return to the main menu.

#### Sample Terminal Output:
```
  ✅ Executed: Enroll student 'S004' in course 'CHEM201'
  ↩️ Undo applied! Roster after rollback: ['Alice Johnson', 'Bob Williams']
  ↪️ Redo applied! Roster after re-apply: ['Alice Johnson', 'Bob Williams', 'David Kim']

  Transaction Audit Trail:
    [18:10:02] EXECUTE: Enroll student 'S004' in course 'CHEM201'
    [18:10:02] UNDO   : Enroll student 'S004' in course 'CHEM201'
    [18:10:02] REDO   : Enroll student 'S004' in course 'CHEM201'
```

---

### Feature [6]: State Pattern — Course Lifecycle State Machine
**Goal**: Enforce academic permissions across course phases via discrete state classes.

#### Procedure:
1. Enter `6` and press `Enter`.
2. **Phase 1: DRAFT**:
   - Syllabus under construction.
   - Terminal attempts enrollment: blocked with `CourseStateError`.
3. **Phase 2: OPEN_REGISTRATION**:
   - Course advanced.
   - Enrollment succeeds.
   - Grading attempt blocked (classes have not started).
4. **Phase 3: IN_PROGRESS**:
   - Semester in session.
   - New student enrollment blocked (registration closed).
   - Grade calculation enabled.
5. **Phase 4: COMPLETED**:
   - Semester ended.
   - All mutations (enrollment, dropping, regrading) are permanently blocked.
6. Press `Enter` to return to the main menu.

#### Sample Terminal Output:
```
  Phase 1: [DRAFT] — Drafting curriculum; not open for enrollment or grading.
  ⛔ Access Blocked: Cannot enroll in 'MATH201': course is currently in DRAFT state.

  Phase 2: [OPEN_REGISTRATION] — Registration is open; students may enroll or drop.
  ✅ Enrollment Accepted: Alice is enrolled = True

  Phase 3: [IN_PROGRESS] — Classes in session; enrollment locked, grading active.
  🎯 Grading Active: Alice's numeric score 92.0 evaluated → Grade A

  Phase 4: [COMPLETED] — Term completed; archived and read-only.
  ⛔ Access Blocked: Cannot enroll in 'MATH201': course is COMPLETED and archived.
```

---

### Feature [7]: System Status & Audit Reports
**Goal**: View aggregate enrollment and financial statistics across all active courses, plus the global audit log.

#### Procedure:
1. Enter `7` and press `Enter`.
2. Displays formatted enrollment table with current roster count, capacity cap, and total fee per course.
3. Displays the full session transaction log.
4. Press `Enter` to return to the main menu.

---

### Feature [8]: Full Guided Tour
**Goal**: Run all 6 patterns sequentially with interactive pauses, ideal for end-to-end demonstrations or evaluator walkthroughs.

#### Procedure:
1. Enter `8` and press `Enter`.
2. The terminal guides you through Features 1 → 2 → 3 → 4 → 5 → 6 → 7 in chronological sequence.
3. At each checkpoint, press `Enter` to advance to the next pattern.

---

### Feature [9]: Automated Test Suite (58 Tests)
**Goal**: Run unit and integration tests directly inside the application.

#### Procedure:
1. Enter `9` and press `Enter`.
2. The test runner executes all 58 tests across all pattern suites:
   - `TestFactoryMethodPattern`
   - `TestObserverPattern`
   - `TestStrategyPattern`
   - `TestDecoratorPattern`
   - `TestCommandPattern`
   - `TestStatePattern`
   - `TestCourseManagerIntegration`
3. Confirms `Ran 58 tests ... OK`.
4. Press `Enter` to return to the main menu.

---

### Feature [0]: Exit Application
**Goal**: Cleanly shut down the application.

#### Procedure:
1. Enter `0` and press `Enter`.
2. The terminal displays a closing greeting and returns to the system shell.

---

## 4. State Persistence Across Selections

When navigating the interactive menu:
- The `CourseManager` service instance **persists throughout your session**.
- Actions performed in one feature (e.g., enrolling students via Feature 5, or setting course state in Feature 6) are reflected in Feature 7 (System Status Report).
- The baseline helper automatically initializes necessary prerequisites so **any menu option can be launched in any arbitrary order** without errors.
