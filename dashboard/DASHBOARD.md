# Dashboard App — Backend

A single read-only Django app that aggregates rollups from every other HRM
module into one JSON payload tuned for the frontend dashboard. The app owns
no models of its own — it only queries existing data.

---

## Files

```
dashboard/
├── __init__.py
├── apps.py            # DashboardConfig
├── migrations/        # empty (no models)
├── urls.py            # /api/v1/dashboard/
├── views.py           # dashboard_overview
└── DASHBOARD.md       # this file
```

Wired into the project in two places:

- [config/settings.py](../config/settings.py) — added `'dashboard'` to `INSTALLED_APPS`.
- [config/urls.py](../config/urls.py) — added `path('api/v1/', include('dashboard.urls'))`.

---

## Endpoint

| Method | Path                  | Auth                    | Description                       |
| ------ | --------------------- | ----------------------- | --------------------------------- |
| GET    | `/api/v1/dashboard/`  | Authenticated (`@rbac`) | Aggregated rollup for the caller. |

Decorator: `@rbac(['GET'])` — login required, no role restriction. Internally
the view branches on `utils.permissions.is_admin(user)`:

- **admin / hr_manager** — sees organization-wide rollups.
- **regular employee** — sees their own scope where applicable (attendance,
  leave requests, sprint tasks, notifications).

Other modules (employees, recruitment, events, public holidays) are always
organization-wide.

---

## Response shape

```jsonc
{
  "as_of": "2026-05-18T05:41:07.084Z",
  "is_admin": true,

  "employee": {
    "total": 42,
    "active": 38,
    "inactive": 4,
    "by_department": [
      { "department__name": "Engineering", "value": 14 },
      { "department__name": "HR", "value": 5 }
    ]
  },

  "attendance": {
    "today": true,
    "today_status": "present",
    "presentDays": 14,
    "totalDays": 18,
    "leaveDays": 2,
    "ratio": 77.78,
    "breakdown": { "present": 12, "late": 2, "absent": 1, "half_day": 1, "on_leave": 2, "holiday": 0 }
  },

  "leaveApplications": {
    "total": 28, "applied": 4, "pending": 3,
    "approved": 18, "rejected": 5, "cancelled": 2,
    "breakdown": { "pending": 3, "approved": 18, "rejected": 5, "cancelled": 2 }
  },

  "jobs": { "total": 8, "active": 5, "closed": 2, "draft": 1 },

  "candidates": {
    "total": 45, "active": 33, "hired": 6, "rejected": 6,
    "breakdown": { "applied": 12, "screening": 10, "interview": 8, "offer": 3, "hired": 6, "rejected": 6 }
  },

  "jobApplications": {
    "total": 45,
    "recentApplied": [
      { "applicationId": 12, "jobTitle": "Backend Engineer",
        "candidateName": "Alice Doe", "project": "interview",
        "applied_at": "2026-05-12T10:14:00Z" }
    ]
  },

  "officeEvents": {
    "total": 4,
    "upcoming": [
      { "eventId": 7, "title": "All-hands", "eventDate": "2026-05-21T15:00:00Z",
        "event_type": "meeting", "location": "Main Hall" }
    ]
  },

  "sprints": {
    "total": 6, "active": 2, "completed": 3,
    "tasks": { "total": 48, "breakdown": { "todo": 14, "in_progress": 12, "in_review": 6, "done": 16 } }
  },

  "notices": {
    "total": 22, "unread": 5,
    "recent": [
      { "id": 91, "title": "Leave Approved", "notification_type": "leave",
        "created_at": "2026-05-17T09:22:00Z", "is_read": false }
    ]
  },

  "upcomingInterviews": [
    { "interviewId": 4, "candidateName": "Alice Doe", "jobTitle": "Backend Engineer",
      "scheduledAt": "2026-05-19T14:00:00Z", "mode": "online", "result": "pending" }
  ],

  "publicHolidays": [ { "name": "Labour Day", "date": "2026-05-01" } ],

  "trends": {
    "months": ["2025-12", "2026-01", "2026-02", "2026-03", "2026-04", "2026-05"],
    "applications": [3, 5, 8, 6, 10, 13],
    "leave_requests": [2, 4, 6, 3, 5, 4]
  }
}
```

---

## What's pulled from where

| Block               | Source models                                      | Filter scope                            |
| ------------------- | -------------------------------------------------- | --------------------------------------- |
| `employee`          | `accounts.Employee`                                | Org-wide                                |
| `attendance`        | `attendance.AttendanceRecord` (current month)      | Admin: all · Employee: self             |
| `leaveApplications` | `leave.LeaveRequest`                               | Admin: all · Employee: self             |
| `jobs`              | `recruitment.JobPosting`                           | Org-wide                                |
| `candidates`        | `recruitment.Application` (status breakdown)       | Org-wide                                |
| `jobApplications`   | `recruitment.Application` (5 most recent)          | Org-wide                                |
| `officeEvents`      | `events.Event` (published, upcoming)               | Org-wide                                |
| `sprints` / `tasks` | `sprint.Sprint`, `sprint.Task`                     | Admin: all tasks · Employee: assigned   |
| `notices`           | `notifications.Notification`                       | Per user                                |
| `upcomingInterviews`| `recruitment.Interview`                            | Org-wide                                |
| `publicHolidays`    | `leave.PublicHoliday` (next 5)                     | Org-wide                                |
| `trends`            | `recruitment.Application`, `leave.LeaveRequest`    | Last 6 calendar months                  |

---

## Helpers (`views.py`)

- `_month_bounds(reference=None)` — returns `(today, first_of_month, first_of_next_month)`.
- `_last_n_months(n=6)` — list of `(year, month)` tuples in chronological order.
- `_month_range(year, month)` — timezone-aware `[start, end)` datetime window.
- `_monthly_counts(qs, datetime_field, months)` — portable per-month `Count()`
  rollup (loops per month so it works on SQLite as well as Postgres without
  raw SQL / `Trunc` adapters).

---

## RBAC choices

We deliberately use plain `@rbac(['GET'])` rather than `roles=['admin', 'hr_manager']`
on the whole view. Branching on `is_admin(user)` inside the view lets us:

1. Serve a single endpoint for both roles — the frontend doesn't fork code paths.
2. Quietly downgrade the scope (employee sees only their own attendance/leave/tasks)
   instead of returning 403, which the dashboard would render as an error.

If you want to lock down dashboard access by role in the future, swap to
`@rbac(['GET'], roles=['admin', 'hr_manager'])` and the rest of the file is
unchanged.

---

## Running locally

No migration needed (no models). After pulling:

```bash
python manage.py check     # confirms the new app loads
python manage.py runserver
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/dashboard/
```

---

## Adding a new module to the rollup

1. Import its models at the top of `views.py`.
2. Build a `_block` dict with the counts / breakdowns you want.
3. Add it to the final `Response({...})`.
4. Mirror the new key in the frontend's `DashboardOverview` TS interface
   (`src/services/dashboard.service.ts`) and render it in
   `dashboard.component.html`.
