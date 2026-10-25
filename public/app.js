/**
 * Student Course Management Portal
 * Frontend Client Application
 */

const API_BASE = '';

// Application State
let courses = [];
let schedule = [];
let wishlist = [];
let strategies = [];
let currentEnrollCourse = null;

// DOM Elements
const navTabs = document.querySelectorAll('.nav-tab');
const tabContents = document.querySelectorAll('.tab-content');
const courseGrid = document.getElementById('course-grid');
const wishlistGrid = document.getElementById('wishlist-grid');
const enrolledList = document.getElementById('enrolled-list');
const timetableGrid = document.getElementById('timetable-grid');
const activityFeed = document.getElementById('activity-feed');

const scheduleCountBadge = document.getElementById('schedule-count');
const wishlistCountBadge = document.getElementById('wishlist-count');
const alertCountBadge = document.getElementById('alert-count');

const metricCourses = document.getElementById('metric-courses');
const metricCredits = document.getElementById('metric-credits');
const metricTuition = document.getElementById('metric-tuition');

const catalogSearch = document.getElementById('catalog-search');
const catalogDayFilter = document.getElementById('catalog-day-filter');

// Modals
const modalEnroll = document.getElementById('modal-enroll');
const modalCourseForm = document.getElementById('modal-course-form');
const btnOpenAddModal = document.getElementById('btn-open-add-modal');
const btnCloseEnrollModal = document.getElementById('btn-close-enroll-modal');
const btnCancelEnroll = document.getElementById('btn-cancel-enroll');
const btnCloseCourseModal = document.getElementById('btn-close-course-modal');
const btnCancelCourseForm = document.getElementById('btn-cancel-course-form');

// Forms
const formEnroll = document.getElementById('form-enroll');
const formCourseEdit = document.getElementById('form-course-edit');

// Calculation Breakdown Elements
const enrollAddLab = document.getElementById('enroll-add-lab');
const enrollAddHonors = document.getElementById('enroll-add-honors');
const enrollAddCert = document.getElementById('enroll-add-cert');
const enrollStrategySelect = document.getElementById('enroll-strategy-select');
const planDescriptionHint = document.getElementById('plan-description-hint');

const calcBaseFee = document.getElementById('calc-base-fee');
const calcAddonFee = document.getElementById('calc-addon-fee');
const calcCredits = document.getElementById('calc-credits');
const calcDiscountAmount = document.getElementById('calc-discount-amount');
const calcFinalTotal = document.getElementById('calc-final-total');

// ================= Initialization =================
document.addEventListener('DOMContentLoaded', () => {
    setupTabNavigation();
    setupEventListeners();
    loadAllData();

    // Auto-refresh notifications every 8 seconds
    setInterval(loadNotifications, 8000);
});

// ================= Tab Navigation =================
function setupTabNavigation() {
    navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tab;
            navTabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            const targetContent = document.getElementById(`tab-${target}`);
            if (targetContent) {
                targetContent.classList.add('active');
            }

            if (target === 'schedule') renderScheduleView();
            if (target === 'wishlist') renderWishlistView();
            if (target === 'activity') loadNotifications();
        });
    });
}

// ================= Event Listeners =================
function setupEventListeners() {
    // Search & Filters
    catalogSearch.addEventListener('input', renderCourseCatalog);
    catalogDayFilter.addEventListener('change', renderCourseCatalog);

    // Add Course Modal Triggers
    btnOpenAddModal.addEventListener('click', () => openCourseModal(null));
    btnCloseCourseModal.addEventListener('click', closeCourseModal);
    btnCancelCourseForm.addEventListener('click', closeCourseModal);

    // Enroll Modal Triggers
    btnCloseEnrollModal.addEventListener('click', closeEnrollModal);
    btnCancelEnroll.addEventListener('click', closeEnrollModal);

    // Live Tuition Calculation on Add-ons / Strategy Change
    [enrollAddLab, enrollAddHonors, enrollAddCert, enrollStrategySelect].forEach(el => {
        el.addEventListener('change', updateEnrollCostPreview);
    });

    // Form Submissions
    formEnroll.addEventListener('submit', handleEnrollSubmit);
    formCourseEdit.addEventListener('submit', handleCourseFormSubmit);

    // Refresh Activity
    const refreshBtn = document.getElementById('btn-refresh-activity');
    if (refreshBtn) refreshBtn.addEventListener('click', loadNotifications);
}

// ================= API Data Fetching =================
async function loadAllData() {
    await Promise.all([
        loadCourses(),
        loadSchedule(),
        loadWishlist(),
        loadStrategies(),
        loadNotifications()
    ]);
}

async function loadCourses() {
    try {
        const res = await fetch(`${API_BASE}/api/courses`);
        courses = await res.json();
        renderCourseCatalog();
    } catch (e) {
        showToast('Error loading courses from server.', 'error');
    }
}

async function loadSchedule() {
    try {
        const res = await fetch(`${API_BASE}/api/schedule`);
        schedule = await res.json();
        scheduleCountBadge.textContent = schedule.length;
        renderScheduleView();
    } catch (e) {
        console.error(e);
    }
}

async function loadWishlist() {
    try {
        const res = await fetch(`${API_BASE}/api/wishlist`);
        wishlist = await res.json();
        wishlistCountBadge.textContent = wishlist.length;
    } catch (e) {
        console.error(e);
    }
}

async function loadStrategies() {
    try {
        const res = await fetch(`${API_BASE}/api/strategies`);
        strategies = await res.json();
    } catch (e) {
        console.error(e);
    }
}

async function loadNotifications() {
    try {
        const res = await fetch(`${API_BASE}/api/notifications`);
        const alerts = await res.json();
        alertCountBadge.textContent = alerts.length;
        renderActivityFeed(alerts);
    } catch (e) {
        console.error(e);
    }
}

// ================= Render Views =================

function renderCourseCatalog() {
    const query = catalogSearch.value.toLowerCase().trim();
    const dayFilter = catalogDayFilter.value;

    const filtered = courses.filter(c => {
        const matchesQuery = c.code.toLowerCase().includes(query) ||
            c.title.toLowerCase().includes(query) ||
            c.instructor.toLowerCase().includes(query);
        const matchesDay = !dayFilter || c.day === dayFilter;
        return matchesQuery && matchesDay;
    });

    courseGrid.innerHTML = '';

    if (filtered.length === 0) {
        courseGrid.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🔍</div>
                <p>No courses match your search criteria.</p>
            </div>
        `;
        return;
    }

    filtered.forEach(course => {
        const isWish = course.isWishlisted;
        const isEnr = course.isEnrolled;
        const capPct = Math.min(100, Math.round((course.enrolledCount / course.capacity) * 100));
        let capBarClass = '';
        if (capPct >= 100) capBarClass = 'full';
        else if (capPct >= 80) capBarClass = 'almost-full';

        const card = document.createElement('div');
        card.className = 'course-card';
        card.innerHTML = `
            <div>
                <div class="course-card-top">
                    <span class="course-code-badge">${escapeHtml(course.code)}</span>
                    <div class="course-actions-quick">
                        <button class="btn-icon ${isWish ? 'wishlisted' : ''}" title="${isWish ? 'Remove from Wishlist' : 'Add to Wishlist'}" onclick="toggleWishlist(${course.id}, ${isWish})">
                            ${isWish ? '★' : '☆'}
                        </button>
                        <button class="btn-icon" title="Edit Course" onclick="openCourseModal(${course.id})">
                            ✏️
                        </button>
                        <button class="btn-icon" title="Delete Course" onclick="deleteCourse(${course.id})">
                            🗑️
                        </button>
                    </div>
                </div>

                <h3 class="course-title">${escapeHtml(course.title)}</h3>
                <p class="course-instructor">Instructor: <strong>${escapeHtml(course.instructor)}</strong></p>
                <p class="course-description">${escapeHtml(course.description || 'No syllabus provided.')}</p>

                <div class="course-meta-tags">
                    <span class="meta-tag">📅 ${escapeHtml(course.day)}</span>
                    <span class="meta-tag">⏰ ${escapeHtml(course.startTime)} - ${escapeHtml(course.endTime)}</span>
                    <span class="meta-tag">🎖️ ${course.credits} Credits</span>
                </div>

                <div class="capacity-wrapper">
                    <div class="capacity-info">
                        <span>Class Enrollment</span>
                        <span><strong>${course.enrolledCount}</strong> / ${course.capacity} seats</span>
                    </div>
                    <div class="capacity-track">
                        <div class="capacity-bar ${capBarClass}" style="width: ${capPct}%"></div>
                    </div>
                </div>
            </div>

            <div class="course-card-bottom">
                <div class="course-fee">
                    <span class="fee-label">Tuition Fee</span>
                    <span class="fee-value">$${course.baseFee.toFixed(2)}</span>
                </div>
                ${isEnr ? `
                    <span class="enrolled-badge">✓ Enrolled</span>
                ` : `
                    <button class="btn btn-primary btn-sm" ${course.enrolledCount >= course.capacity ? 'disabled' : ''} onclick="openEnrollModal(${course.id})">
                        ${course.enrolledCount >= course.capacity ? 'Class Full' : 'Enroll Now'}
                    </button>
                `}
            </div>
        `;
        courseGrid.appendChild(card);
    });
}

function renderScheduleView() {
    let totalCredits = 0;
    let totalTuition = 0;

    // Days structure for weekly timetable
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    const timetableSlots = {
        Monday: [],
        Tuesday: [],
        Wednesday: [],
        Thursday: [],
        Friday: []
    };

    enrolledList.innerHTML = '';

    if (schedule.length === 0) {
        enrolledList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🗓️</div>
                <p>You have not enrolled in any courses yet.</p>
                <p style="font-size: 0.8rem; margin-top: 0.4rem;">Browse the catalog to add classes to your schedule.</p>
            </div>
        `;
    }

    schedule.forEach(item => {
        totalCredits += item.credits;
        totalTuition += item.finalTuition;

        if (timetableSlots[item.day]) {
            timetableSlots[item.day].push(item);
        }

        const row = document.createElement('div');
        row.className = 'enrolled-card';
        row.innerHTML = `
            <div class="enrolled-info">
                <div class="enrolled-title-row">
                    <span class="enrolled-code">${escapeHtml(item.code)}</span>
                    <span class="enrolled-title">${escapeHtml(item.title)}</span>
                </div>
                <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.2rem;">
                    👨‍🏫 ${escapeHtml(item.instructor)} &nbsp;|&nbsp; 📅 ${escapeHtml(item.scheduleSummary)} &nbsp;|&nbsp; 🎖️ ${item.credits} Credits
                </div>
                ${item.addons && item.addons.length > 0 ? `
                    <div class="enrolled-addons">
                        ${item.addons.map(addon => `<span class="addon-badge">✨ ${escapeHtml(addon)}</span>`).join('')}
                    </div>
                ` : ''}
            </div>
            <div class="enrolled-pricing-side">
                <div class="enrolled-cost-group">
                    <div class="enrolled-cost">$${item.finalTuition.toFixed(2)}</div>
                    <div class="enrolled-plan-label">${escapeHtml(item.billingPlan)}</div>
                </div>
                <button class="btn btn-danger btn-sm" onclick="dropCourse(${item.courseId})">Drop Class</button>
            </div>
        `;
        enrolledList.appendChild(row);
    });

    // Update Summary Metrics
    metricCourses.textContent = schedule.length;
    metricCredits.textContent = totalCredits;
    metricTuition.textContent = `$${totalTuition.toFixed(2)}`;

    // Render Weekly Timetable Columns
    timetableGrid.innerHTML = '';
    days.forEach(day => {
        const col = document.createElement('div');
        col.className = 'day-column';
        col.innerHTML = `<div class="day-header">${day}</div>`;

        const dayCourses = timetableSlots[day] || [];
        if (dayCourses.length === 0) {
            col.innerHTML += `<div class="day-empty">No classes</div>`;
        } else {
            dayCourses.sort((a, b) => a.startTime.localeCompare(b.startTime));
            dayCourses.forEach(c => {
                col.innerHTML += `
                    <div class="timetable-slot-card">
                        <div class="slot-code">${escapeHtml(c.code)}</div>
                        <div class="slot-title">${escapeHtml(c.title)}</div>
                        <div class="slot-time">⏰ ${escapeHtml(c.startTime)} - ${escapeHtml(c.endTime)}</div>
                    </div>
                `;
            });
        }
        timetableGrid.appendChild(col);
    });
}

function renderWishlistView() {
    wishlistGrid.innerHTML = '';

    if (wishlist.length === 0) {
        wishlistGrid.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⭐</div>
                <p>Your wishlist is currently empty.</p>
                <p style="font-size: 0.8rem; margin-top: 0.4rem;">Click the star icon on any course card to bookmark it here.</p>
            </div>
        `;
        return;
    }

    wishlist.forEach(course => {
        const isEnr = schedule.some(s => s.courseId === course.id);
        const card = document.createElement('div');
        card.className = 'course-card';
        card.innerHTML = `
            <div>
                <div class="course-card-top">
                    <span class="course-code-badge">${escapeHtml(course.code)}</span>
                    <button class="btn-icon wishlisted" title="Remove from Wishlist" onclick="toggleWishlist(${course.id}, true)">
                        ★
                    </button>
                </div>
                <h3 class="course-title">${escapeHtml(course.title)}</h3>
                <p class="course-instructor">Instructor: <strong>${escapeHtml(course.instructor)}</strong></p>
                <p class="course-description">${escapeHtml(course.description || 'No description.')}</p>
                <div class="course-meta-tags">
                    <span class="meta-tag">📅 ${escapeHtml(course.day)}</span>
                    <span class="meta-tag">⏰ ${escapeHtml(course.startTime)} - ${escapeHtml(course.endTime)}</span>
                    <span class="meta-tag">🎖️ ${course.credits} Credits</span>
                </div>
            </div>
            <div class="course-card-bottom">
                <div class="course-fee">
                    <span class="fee-label">Tuition Fee</span>
                    <span class="fee-value">$${course.baseFee.toFixed(2)}</span>
                </div>
                ${isEnr ? `
                    <span class="enrolled-badge">✓ Enrolled</span>
                ` : `
                    <button class="btn btn-primary btn-sm" onclick="openEnrollModal(${course.id})">Enroll Now</button>
                `}
            </div>
        `;
        wishlistGrid.appendChild(card);
    });
}

function renderActivityFeed(alerts) {
    activityFeed.innerHTML = '';
    if (!alerts || alerts.length === 0) {
        activityFeed.innerHTML = `<div class="empty-state"><p>No system activity recorded yet.</p></div>`;
        return;
    }

    alerts.forEach(item => {
        const div = document.createElement('div');
        div.className = `activity-item ${item.level || 'info'}`;
        div.innerHTML = `
            <div>
                <span style="font-weight: 700; font-size: 0.8rem; margin-right: 0.5rem; text-transform: uppercase;">[${escapeHtml(item.eventType)}]</span>
                <span class="activity-text">${escapeHtml(item.message)}</span>
            </div>
            <div class="activity-meta">${escapeHtml(item.timestamp)}</div>
        `;
        activityFeed.appendChild(div);
    });
}

// ================= Wishlist Toggle =================
async function toggleWishlist(courseId, isCurrentlyWishlisted) {
    try {
        const method = isCurrentlyWishlisted ? 'DELETE' : 'POST';
        const res = await fetch(`${API_BASE}/api/wishlist?id=${courseId}`, { method });
        if (res.ok) {
            showToast(isCurrentlyWishlisted ? 'Removed from wishlist.' : 'Added to wishlist.', 'success');
            await Promise.all([loadCourses(), loadWishlist(), loadNotifications()]);
        }
    } catch (e) {
        showToast('Failed to update wishlist.', 'error');
    }
}

// ================= Drop Course =================
async function dropCourse(courseId) {
    if (!confirm('Are you sure you want to drop this course from your schedule?')) return;

    try {
        const res = await fetch(`${API_BASE}/api/schedule?id=${courseId}`, { method: 'DELETE' });
        if (res.ok) {
            showToast('Course dropped from schedule.', 'success');
            await Promise.all([loadCourses(), loadSchedule(), loadNotifications()]);
        } else {
            const err = await res.json();
            showToast(err.error || 'Failed to drop course.', 'error');
        }
    } catch (e) {
        showToast('Network error while dropping course.', 'error');
    }
}

// ================= Delete Course =================
async function deleteCourse(courseId) {
    if (!confirm('Delete this course from the university curriculum?')) return;

    try {
        const res = await fetch(`${API_BASE}/api/courses?id=${courseId}`, { method: 'DELETE' });
        if (res.ok) {
            showToast('Course successfully deleted.', 'success');
            await Promise.all([loadCourses(), loadSchedule(), loadWishlist(), loadNotifications()]);
        } else {
            const err = await res.json();
            showToast(err.error || 'Failed to delete course.', 'error');
        }
    } catch (e) {
        showToast('Error deleting course.', 'error');
    }
}

// ================= Enrollment Modal & Live Cost Calculator =================

function openEnrollModal(courseId) {
    currentEnrollCourse = courses.find(c => c.id === courseId);
    if (!currentEnrollCourse) return;

    document.getElementById('enroll-course-id').value = currentEnrollCourse.id;
    document.getElementById('enroll-modal-title').textContent = `Enroll in ${currentEnrollCourse.code}`;
    document.getElementById('enroll-modal-subtitle').textContent = `${currentEnrollCourse.title} — ${currentEnrollCourse.instructor} (${currentEnrollCourse.day} ${currentEnrollCourse.startTime}-${currentEnrollCourse.endTime})`;

    // Reset options
    enrollAddLab.checked = false;
    enrollAddHonors.checked = false;
    enrollAddCert.checked = false;
    enrollStrategySelect.value = 'standard';

    updateEnrollCostPreview();
    modalEnroll.classList.add('open');
}

function closeEnrollModal() {
    modalEnroll.classList.remove('open');
    currentEnrollCourse = null;
}

function updateEnrollCostPreview() {
    if (!currentEnrollCourse) return;

    const baseFee = currentEnrollCourse.baseFee;
    let addonFee = 0;
    let extraCredits = 0;

    if (enrollAddLab.checked) addonFee += 150.00;
    if (enrollAddHonors.checked) {
        addonFee += 100.00;
        extraCredits += 1;
    }
    if (enrollAddCert.checked) addonFee += 75.00;

    const subtotal = baseFee + addonFee;
    const selectedPlanKey = enrollStrategySelect.value;
    const planObj = strategies.find(s => s.key === selectedPlanKey) || { discount: 0, desc: '' };

    planDescriptionHint.textContent = planObj.desc || '';

    const discountRate = planObj.discount || 0;
    const discountAmount = subtotal * discountRate;
    const finalTotal = subtotal - discountAmount;

    calcBaseFee.textContent = `$${baseFee.toFixed(2)}`;
    calcAddonFee.textContent = `+$${addonFee.toFixed(2)}`;
    calcCredits.textContent = `${currentEnrollCourse.credits + extraCredits} Credits`;
    calcDiscountAmount.textContent = `-$${discountAmount.toFixed(2)} (${Math.round(discountRate * 100)}%)`;
    calcFinalTotal.textContent = `$${finalTotal.toFixed(2)}`;
}

async function handleEnrollSubmit(e) {
    e.preventDefault();
    if (!currentEnrollCourse) return;

    const payload = {
        courseId: currentEnrollCourse.id,
        addLab: enrollAddLab.checked,
        addHonors: enrollAddHonors.checked,
        addCertificate: enrollAddCert.checked,
        strategy: enrollStrategySelect.value
    };

    try {
        const res = await fetch(`${API_BASE}/api/enroll`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (res.ok) {
            showToast('Enrollment confirmed!', 'success');
            closeEnrollModal();
            await Promise.all([loadCourses(), loadSchedule(), loadWishlist(), loadNotifications()]);

            // Switch to schedule tab so user sees their new enrolled class
            const scheduleTab = document.querySelector('[data-tab="schedule"]');
            if (scheduleTab) scheduleTab.click();
        } else {
            showToast(data.error || 'Enrollment failed.', 'error');
        }
    } catch (err) {
        showToast('Network error during enrollment.', 'error');
    }
}

// ================= Add / Edit Course Modal =================

function openCourseModal(courseId) {
    const modalTitle = document.getElementById('course-form-modal-title');
    const formId = document.getElementById('course-form-id');

    if (courseId) {
        const c = courses.find(item => item.id === courseId);
        if (!c) return;

        modalTitle.textContent = `Edit Course (${c.code})`;
        formId.value = c.id;
        document.getElementById('course-code').value = c.code;
        document.getElementById('course-title').value = c.title;
        document.getElementById('course-instructor').value = c.instructor;
        document.getElementById('course-credits').value = c.credits;
        document.getElementById('course-fee').value = c.baseFee;
        document.getElementById('course-day').value = c.day;
        document.getElementById('course-start').value = c.startTime;
        document.getElementById('course-end').value = c.endTime;
        document.getElementById('course-capacity').value = c.capacity;
        document.getElementById('course-desc').value = c.description || '';
    } else {
        modalTitle.textContent = 'Create New Course';
        formCourseEdit.reset();
        formId.value = '';
    }

    modalCourseForm.classList.add('open');
}

function closeCourseModal() {
    modalCourseForm.classList.remove('open');
    formCourseEdit.reset();
}

async function handleCourseFormSubmit(e) {
    e.preventDefault();
    const id = document.getElementById('course-form-id').value;

    const payload = {
        id: id || undefined,
        code: document.getElementById('course-code').value.trim(),
        title: document.getElementById('course-title').value.trim(),
        instructor: document.getElementById('course-instructor').value.trim(),
        credits: parseInt(document.getElementById('course-credits').value, 10),
        baseFee: parseFloat(document.getElementById('course-fee').value),
        day: document.getElementById('course-day').value,
        startTime: document.getElementById('course-start').value,
        endTime: document.getElementById('course-end').value,
        capacity: parseInt(document.getElementById('course-capacity').value, 10),
        description: document.getElementById('course-desc').value.trim()
    };

    const isEdit = Boolean(id);
    const method = isEdit ? 'PUT' : 'POST';

    try {
        const res = await fetch(`${API_BASE}/api/courses`, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            showToast(isEdit ? 'Course details updated.' : 'New course published!', 'success');
            closeCourseModal();
            await Promise.all([loadCourses(), loadSchedule(), loadNotifications()]);
        } else {
            const err = await res.json();
            showToast(err.error || 'Failed to save course.', 'error');
        }
    } catch (err) {
        showToast('Network error while saving course.', 'error');
    }
}

// ================= Utilities =================

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type === 'error' ? 'toast-error' : type === 'success' ? 'toast-success' : ''}`;
    toast.innerHTML = `<span>${escapeHtml(message)}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 250);
    }, 4000);
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
