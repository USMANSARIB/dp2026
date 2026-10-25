# Student Course Management Portal — Demonstration Guide

This guide walks you through verifying and demonstrating every feature of the **Student Course Management System**, showcasing the **Decorator**, **Strategy**, and **Observer** design patterns in action both through the **Web UI** and via **Terminal / API calls**.

> **Note on Server Port:**  
> If you saw `Failed to start server: Address already in use: bind`, it means the server is **already running** on port 8080! You can directly open **[http://localhost:8080](http://localhost:8080)** in your browser.  
> If you ever need to restart or run on an alternate port, you can specify a port like:  
> `java -cp bin com.course.Main 8081`

---

## 🧭 Demonstration Overview

```
+---------------------------------------------------------------------------------------------------------+
|                                  STUDENT COURSE PORTAL DEMO FLOW                                        |
+---------------------------------------------------------------------------------------------------------+
|  1. Explore Catalog      -> Search & Day filter, inspect pre-seeded courses & capacity bars             |
|  2. Add & Edit Courses   -> Publish CS305 / Modify room, capacity & syllabus                             |
|  3. Course Wishlist      -> Bookmark classes with 1-click star toggle                                    |
|  4. DECORATOR PATTERN    -> Dynamic Course Add-ons (Lab Practicum, Honors Track, Verified Certificate)   |
|  5. STRATEGY PATTERN     -> Tuition Discount Plans (Standard, Merit Scholar 30%, Need-Based Aid 50%)    |
|  6. Timetable View       -> Visual Monday-Friday calendar blocks & credit load metrics                   |
|  7. Conflict Detection   -> Automatic rejection of overlapping class schedules                          |
|  8. OBSERVER PATTERN     -> Real-time Activity Tray & Administrative Audit Trail                         |
+---------------------------------------------------------------------------------------------------------+
```

---

## Part 1: Interactive Web UI Demonstration

Open **[http://localhost:8080](http://localhost:8080)** in your web browser.

### Scenario 1: Exploring Catalog & Filtering
1. **Catalog View**: Observe the pre-seeded university courses (`CS101`, `CS201`, `MATH150`, `PHYS101`, `DS310`, `ART110`).
2. **Search**: Type `Data` in the search bar. Notice that only `CS201 Data Structures & Algorithms` is instantly displayed.
3. **Day Filter**: Select `Monday` from the dropdown. The catalog updates to show only Monday courses (`CS101`, `ART110`). Reset back to `All Days`.

---

### Scenario 2: Adding a New Course to Curriculum
1. Click the black **`+ Add Course`** button in the top navigation bar.
2. Fill in the modal form:
   - **Course Code**: `CS305`
   - **Course Title**: `Cloud Computing & Microservices`
   - **Instructor**: `Dr. Werner Vogels`
   - **Credits**: `3`
   - **Base Fee ($)**: `500`
   - **Lecture Day**: `Tuesday`
   - **Start Time**: `14:00`
   - **End Time**: `15:30`
   - **Capacity**: `30`
   - **Description**: `Architecting distributed cloud systems and microservices.`
3. Click **`Save Course`**.
4. **Result**: A success toast appears, and `CS305` is immediately visible in the catalog with 0/30 seats filled.

---

### Scenario 3: Course Wishlist (Bookmarking)
1. On the card for **`CS201` (Data Structures & Algorithms)**, click the **`☆`** (star) icon in the top right.
2. The star turns yellow (`★`).
3. Click on the **`⭐ Wishlist`** tab in the navigation bar.
4. **Result**: `CS201` appears in your saved wishlist, ready for one-click enrollment whenever registration opens.

---

### Scenario 4: The Decorator Pattern (Customizing Course Add-ons)
*The Decorator Pattern dynamically augments credits, fees, and schedule hours without subclass explosion.*

1. In the Catalog tab, find **`CS101` (Introduction to Computer Science)** ($450 base fee, 3 credits).
2. Click the **`Enroll Now`** button. The enrollment customization modal opens.
3. **Observe the Live Calculation Breakdown Card**:
   - Initial State: Base Course Tuition = `$450.00`, Credits = `3 Credits`, Total = `$450.00`.
4. **Check `🔬 Hands-on Laboratory Practicum`**:
   - Notice the decorator dynamically increases the add-on fee: `+$150.00`.
   - Subtotal becomes `$600.00`.
5. **Check `🎖️ Honors Research Track`**:
   - Notice the decorator dynamically increases credits from `3` to `4 Credits`!
   - Adds `+$100.00` honors stipend.
6. **Check `📜 Verified Professional Certificate`**:
   - Notice the decorator adds `+$75.00` for credential exam access.
   - Total Course Fee after decorators: `$450 + $150 + $100 + $75 = $775.00`.

---

### Scenario 5: The Strategy Pattern (Tuition & Scholarship Plans)
*The Strategy Pattern intercepts the decorated fee and applies the selected billing algorithm at runtime.*

1. In the same Enrollment Modal, look at the **`Tuition & Scholarship Plan`** dropdown.
2. Select **`Academic Merit Scholarship`**:
   - Notice the green discount line dynamically updates: `-$232.50 (30%)`.
   - **Total Payable Tuition**: `$542.50`.
3. Switch the plan to **`Need-Based Financial Aid`**:
   - Discount updates to: `-$387.50 (50%)`.
   - **Total Payable Tuition**: `$387.50`.
4. Switch to **`Early Registration Incentive`**:
   - Discount updates to: `-$116.25 (15%)`.
   - **Total Payable Tuition**: `$658.75`.
5. Keep **`Academic Merit Scholarship`** selected, and click **`Confirm Enrollment`**.
6. **Result**:
   - Success toast appears: *"Enrollment confirmed!"*
   - The UI automatically switches to the **`🗓️ My Schedule`** tab.

---

### Scenario 6: Schedule & Weekly Timetable Visualization
1. In the **`🗓️ My Schedule`** tab:
   - Notice the top summary metrics have updated:
     - **Enrolled Courses**: `1`
     - **Credit Hours**: `4` (base 3 + 1 honors bonus credit)
     - **Total Tuition**: `$542.50`
2. **Weekly Timetable Grid**:
   - Under the **`MONDAY`** column, `CS101` appears from `09:00 - 10:30`.
3. **Enrolled Course Details Card**:
   - Displays instructor, schedule summary: `"Monday 09:00 - 10:30 [Includes 2hr Lab Session]"`.
   - Applied add-on badges:
     - `✨ Hands-on Laboratory Session (+$150.00...)`
     - `✨ Honors Research Track (+1 Credit, +$100.00...)`
     - `✨ Verified Professional Certificate (+$75.00...)`
   - Billing plan badge: `Academic Merit Scholarship`.

---

### Scenario 7: Schedule Conflict Detection
*The system prevents overlapping class times on the same day.*

1. Go back to the **`📚 Catalog`** tab.
2. Click **`+ Add Course`** and create a conflicting course:
   - **Code**: `CS190`
   - **Title**: `Computer Architecture Seminar`
   - **Instructor**: `Dr. Turing`
   - **Credits**: `2`
   - **Base Fee**: `300`
   - **Day**: `Monday` *(Same day as CS101)*
   - **Start Time**: `09:30` *(Overlaps with CS101's 09:00-10:30 window)*
   - **End Time**: `11:00`
   - **Capacity**: `25`
   - Click **`Save Course`**.
3. Now attempt to enroll in `CS190`: click **`Enroll Now`** $\rightarrow$ click **`Confirm Enrollment`**.
4. **Result**:
   - A red error alert appears:
     > ⚠️ *"Time conflict detected with enrolled course: CS101 (Monday 09:00 - 10:30 [Includes 2hr Lab Session])."*
   - Enrollment is safely rejected.

---

### Scenario 8: The Observer Pattern (Live Alerts & Audit Log)
1. Click on the **`🔔 Activity`** tab in the top navigation bar.
2. Observe the chronological feed of real-time events dispatched by the `CourseSubject`:
   - `[SCHEDULE_CONFLICT]` — Warning log of the rejected conflict attempt.
   - `[COURSE_ADDED]` — Log of `CS190` created.
   - `[SCHEDULE_ENROLLED]` — Confirmation of `CS101` enrolled with Academic Merit Scholarship.
   - `[WISHLIST_ADDED]` — Confirmation of `CS201` bookmarked.
   - `[COURSE_ADDED]` — Initial system publication logs.

---

### Scenario 9: Updating an Existing Course & Observer Propagation
1. Go to **`📚 Catalog`**.
2. On **`MATH150`**, click the **`✏️`** (Edit) icon.
3. Change the instructor to `Prof. Carl Friedrich Gauss` and capacity to `45`.
4. Click **`Save Course`**.
5. Check the **`🔔 Activity`** tab: the `[COURSE_UPDATED]` event is logged with the new details.

---

### Scenario 10: Dropping a Course & Releasing Capacity
1. Go to **`🗓️ My Schedule`**.
2. Click the red **`Drop Class`** button next to `CS101`.
3. Confirm the prompt.
4. **Result**:
   - Metrics reset (Enrolled: `0`, Credits: `0`, Tuition: `$0.00`).
   - Timetable slot is cleared.
   - Course capacity in the catalog drops from 1 back to 0.
   - The Observer logs `[SCHEDULE_DROPPED]` in the activity feed.

---

## Part 2: Terminal / Headless Demonstration (cURL / PowerShell)

For automated or terminal evaluation, all features can be demonstrated via HTTP requests.

### 1. Retrieve Course Catalog
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/api/courses" -Method Get | Format-Table id, code, title, day, startTime, endTime, baseFee
```

### 2. Enroll Course with Decorators & Strategy
```powershell
# Enrolls in course 2 (CS201), with Lab (Decorator) + Merit Scholarship (Strategy):
$body = '{"courseId":2,"addLab":true,"addHonors":false,"addCertificate":false,"strategy":"merit"}'
Invoke-RestMethod -Uri "http://localhost:8080/api/enroll" -Method Post -ContentType "application/json" -Body $body
```

### 3. Verify Enrolled Schedule
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/api/schedule" -Method Get | Format-List
```

### 4. Inspect Live Observer Activity Feed
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/api/notifications" -Method Get | Select-Object -First 5 | Format-Table timestamp, eventType, courseCode, message
```

---

## Summary of Design Pattern Verifications

| Requirement | Code Verification | User-Facing Feature |
| :--- | :--- | :--- |
| **Decorator Pattern** | `LabSessionDecorator`, `HonorsTrackDecorator`, `CertificateDecorator` wrapping `CourseComponent`. | Dynamic add-on checkboxes (Lab, Honors credit, Certificate voucher) calculating fees & credits. |
| **Strategy Pattern** | `StandardBillingStrategy`, `MeritScholarshipStrategy`, `FinancialAidStrategy`, `EarlyRegistrationStrategy`. | Tuition plan selector dynamically altering payable tuition (Standard, 30% merit, 50% aid, 15% early bird). |
| **Observer Pattern** | `CourseSubject` notifying `StudentNotificationObserver`, `ScheduleSyncObserver`, and `AuditLoggerObserver`. | Activity feed, real-time alert toasts, timetable conflict warnings, and audit records. |
| **Course CRUD** | Add, Update, Delete in `CourseManager.java`. | `+ Add Course` modal, edit modal, delete button, live catalog updates. |
| **Wishlist** | Dedicated Set management in `CourseManager.java`. | Star toggle icon on cards and dedicated Wishlist view tab. |
| **Schedule / Timetable**| Conflict detection algorithm & timetable data in `CourseManager.java`. | 5-Day Monday–Friday timetable, enrolled courses list, total credit/tuition metric counters. |
