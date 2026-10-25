# Student Course Management Portal

A lightweight, robust Student Course Management System written in **Java** (with built-in HTTP server) featuring a clean, minimalist white web interface and implementations of three classic Gang of Four (GoF) design patterns:
- **Decorator Pattern**
- **Strategy Pattern**
- **Observer Pattern**

---

## ✨ Features

- **Course Catalog (CRUD)**: Browse, Add new course, Edit course details, and Delete course.
- **Course Wishlist**: 1-click bookmarking to save desired courses for future registration.
- **Weekly Schedule / Timetable**:
  - Interactive 5-day (Monday - Friday) class schedule grid.
  - Automatic time conflict detection (prevents overlapping classes).
  - Summary metrics: total enrolled courses, total credit hours, and total tuition.
  - Drop course functionality with automatic seat release.
- **Course Customization & Add-ons** (*Decorator Pattern*):
  - Hands-on Laboratory Practicum (+$150.00, dedicated workstation & lab hours).
  - Honors Research Track (+1 Credit, +$100.00, 1-on-1 faculty mentorship).
  - Verified Professional Certificate (+$75.00, proctored exam voucher & digital badge).
- **Tuition & Scholarship Plans** (*Strategy Pattern*):
  - Standard Student Plan (Regular university tuition).
  - Academic Merit Scholarship (30% tuition reduction).
  - Need-Based Financial Aid (50% tuition reduction).
  - Early Registration Incentive (15% tuition reduction).
- **Live Notifications & System Activity Feed** (*Observer Pattern*):
  - Real-time event broadcasting on course publishing, updates, enrollments, and time conflict warnings.

---

## 🚀 Quick Start

### 1. Prerequisites
- Java SE JDK 17+ (Java 21, 26 tested). Zero external JAR dependencies required!

### 2. Compile
```powershell
javac -d bin (Get-ChildItem -Path src -Filter *.java -Recurse | Select-Object -ExpandProperty FullName)
```

### 3. Run
```powershell
java -cp bin com.course.Main 8080
```

### 4. Open in Browser
Visit [http://localhost:8080](http://localhost:8080) to interact with the student portal.

---

## 📖 Design Patterns Documentation

A dedicated document is available in [DESIGN_PATTERNS.md](file:///c:/Users/ceusm/New%20folder%20%284%29/DESIGN_PATTERNS.md), detailing the problem statements, class diagrams, dynamic wrapping, algorithm swapping, and observer notification workflows.
