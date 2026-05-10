# Attendance App — Implementation Guide

## Overview

The `attendance` app tracks daily employee attendance. Employees check in and out themselves via dedicated endpoints. Admins and HR managers can create or edit records manually, view all employees' records, and filter by date range or status. A monthly summary endpoint powers dashboard badge-style counters.

---

## What Was Built

### 1. Model — `attendance/models.py`

Single model: **`AttendanceRecord`**

| Field        | Type          | Description                                             |
|--------------|---------------|---------------------------------------------------------|
| `employee`   | FK(Employee)  | The employee this record belongs to                     |
| `date`       | DateField     | The calendar date of attendance                         |
| `check_in`   | DateTimeField | Timestamp of check-in (nullable — admin may pre-create) |
| `check_out`  | DateTimeField | Timestamp of check-out (nullable until employee checks out) |
| `status`     | CharField     | One of: `present`, `absent`, `late`, `half_day`, `on_leave`, `holiday` |
| `notes`      | TextField     | Optional admin note                                     |
| `created_at` | DateTimeField | Auto-set on creation                                    |
| `updated_at` | DateTimeField | Auto-updated on every save                              |

**Constraints:**
- `unique_together = ('employee', 'date')` — one record per employee per day.
- Default ordering: newest date first.

**Computed property:**
- `work_hours` — decimal hours between `check_in` and `check_out`; `None` if either is missing.

---

### 2. Serializer — `attendance/serializers.py`

`AttendanceRecordSerializer`:

- `employee_name` — read-only `get_full_name()` display field.
- `work_hours` — read-only computed property exposed as a float.
- `created_at`, `updated_at` — read-only.
- Cross-field validation: rejects payloads where `check_out <= check_in`.

---

### 3. Filters — `attendance/filters.py`

`AttendanceFilter` (powered by `django-filters`):

| Param         | Filters on      | Example                      |
|---------------|-----------------|------------------------------|
| `status`      | status field    | `?status=late`               |
| `employee_id` | employee PK     | `?employee_id=5`             |
| `date_from`   | date ≥          | `?date_from=2026-05-01`      |
| `date_to`     | date ≤          | `?date_to=2026-05-31`        |

All filters can be combined: `?status=present&date_from=2026-05-01&date_to=2026-05-31`.

---

### 4. Views — `attendance/views.py`

All views use `@rbac` **without** `public=True` — authentication is enforced automatically by the decorator (401 if unauthenticated). Role-based branching inside views uses the `_is_admin()` helper which checks for `admin` or `hr_manager` roles.

| View                    | Auth / Role                      | Purpose                                                         |
|-------------------------|----------------------------------|-----------------------------------------------------------------|
| `attendance_list`       | Any authenticated (GET); admin/hr (POST) | GET: admin sees all records, employees see only their own. POST: admin/hr manually creates a record. |
| `attendance_detail`     | Any authenticated (GET); admin/hr (PUT/PATCH/DELETE) | GET: own record for employees, any for admin. Mutations restricted to admin/hr. |
| `my_attendance`         | Any authenticated                | Current user's own records with full filter support.            |
| `attendance_check_in`   | Any authenticated                | Creates today's record with `check_in = now`. Auto-detects `late` if after 09:30. |
| `attendance_check_out`  | Any authenticated                | Stamps `check_out = now` on today's record. Auto-downgrades to `half_day` if < 5 hours worked. |
| `attendance_summary`    | Any authenticated                | Month-level counts per status (defaults to current year/month). |

#### Auto-status logic in check-in / check-out

- **Check-in:** If local time is after **09:30**, status is set to `late`; otherwise `present`.
- **Check-out:** If total hours worked is **< 5**, status is downgraded to `half_day` (only when currently `present` or `late`).

---

### 5. URLs — `attendance/urls.py`

Mounted at `api/v1/`:

| Method      | Endpoint                          | View                    | Description                          |
|-------------|-----------------------------------|-------------------------|--------------------------------------|
| GET         | `/api/v1/attendance/`             | `attendance_list`       | List records (scoped by role)        |
| POST        | `/api/v1/attendance/`             | `attendance_list`       | Manually create a record (admin/hr)  |
| GET         | `/api/v1/attendance/my/`          | `my_attendance`         | My own records (filterable)          |
| POST        | `/api/v1/attendance/check-in/`    | `attendance_check_in`   | Mark today's check-in                |
| POST        | `/api/v1/attendance/check-out/`   | `attendance_check_out`  | Mark today's check-out               |
| GET         | `/api/v1/attendance/summary/`     | `attendance_summary`    | Monthly status counts                |
| GET         | `/api/v1/attendance/<pk>/`        | `attendance_detail`     | Fetch single record                  |
| PUT / PATCH | `/api/v1/attendance/<pk>/`        | `attendance_detail`     | Update a record (admin/hr)           |
| DELETE      | `/api/v1/attendance/<pk>/`        | `attendance_detail`     | Delete a record (admin/hr)           |

> **Note:** Named routes (`my/`, `check-in/`, `check-out/`, `summary/`) are declared before `<pk>/` to prevent Django from matching them as integer PKs.

---

### 6. Admin — `attendance/admin.py`

Registered with:
- List display: id, employee, date, status, check_in, check_out, work_hours
- Filters: status, date
- Search: employee username and full name
- Read-only: created_at, updated_at

---

### 7. Seed Data — `core/management/commands/seed.py`

Added 500 attendance records (20 employees × 25 working days ending 2026-05-09):

| Status     | Approx. share |
|------------|---------------|
| present    | ~60%          |
| late       | ~12%          |
| absent     | ~12%          |
| half_day   | ~8%           |
| on_leave   | ~8%           |

Status is distributed deterministically (not randomly) using `(emp_idx * 7 + day_idx) % 25` so the seed is reproducible. Present/late records have realistic check-in/check-out times; absent and on_leave records have no timestamps.

---

### 8. Config — `config/urls.py`

Uncommented the previously commented-out line:

```python
path('api/v1/', include('attendance.urls')),
```

---

## Example Usage

### Employee self check-in

```http
POST /api/v1/attendance/check-in/
Authorization: Bearer <token>

→ 200 OK  { "id": 1, "date": "2026-05-10", "status": "present", "check_in": "...", ... }
```

### Employee self check-out

```http
POST /api/v1/attendance/check-out/
Authorization: Bearer <token>

→ 200 OK  { ..., "check_out": "...", "work_hours": 8.5, "status": "present" }
```

### My monthly summary

```http
GET /api/v1/attendance/summary/?year=2026&month=5
Authorization: Bearer <token>

→ { "year": 2026, "month": 5, "total": 22, "present": 14, "late": 3, "absent": 2, "half_day": 2, "on_leave": 1, "holiday": 0 }
```

### Admin: list all attendance for a date range

```http
GET /api/v1/attendance/?date_from=2026-05-01&date_to=2026-05-10&status=absent
Authorization: Bearer <admin-token>
```

### Admin: manually create a record

```http
POST /api/v1/attendance/
Authorization: Bearer <admin-token>

{ "employee": 5, "date": "2026-05-10", "status": "holiday", "notes": "Eid holiday" }
```

---

## Pattern Consistency

Follows the same conventions used across the HRM codebase:

- `@rbac` without `public=True` — auth enforced by decorator, not inside view body
- `get_object_or_404` for safe lookups
- `django-filters` `FilterSet` in a dedicated `filters.py`
- DRF `Response` + `status` constants
- `select_related` and `update_fields` for query efficiency
- Function-based views only — no ViewSets or class-based views
