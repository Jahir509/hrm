# Notifications App — Implementation Guide

## Overview

The `notifications` app provides an in-app notification system for the HRM platform. Admins or HR managers can push notifications to any employee, and employees can view, filter, and mark their own notifications as read.

---

## What Was Built

### 1. Model — `notifications/models.py`

A single `Notification` model with the following fields:

| Field               | Type         | Description                                      |
|---------------------|--------------|--------------------------------------------------|
| `recipient`         | FK(Employee) | The employee who receives this notification      |
| `title`             | CharField    | Short heading of the notification                |
| `message`           | TextField    | Full notification body                           |
| `notification_type` | CharField    | Category: `leave`, `attendance`, `payroll`, `performance`, `recruitment`, `training`, `system` |
| `is_read`           | BooleanField | Whether the recipient has read it (default: False) |
| `read_at`           | DateTimeField| Timestamp when it was marked read (nullable)     |
| `created_at`        | DateTimeField| Auto-set on creation                             |

Default ordering: newest first (`-created_at`).

---

### 2. Serializer — `notifications/serializers.py`

`NotificationSerializer` serializes all fields. Key design decisions:

- `recipient_name` — read-only computed field (`get_full_name`) for display.
- `is_read`, `read_at`, `created_at` — **read-only** (cannot be set via POST; changed only through dedicated endpoints).
- Validates that `title` and `message` are not blank strings.

---

### 3. Filters — `notifications/filters.py`

`NotificationFilter` (powered by `django-filters`) supports these query params:

| Param               | Filters on           | Example                        |
|---------------------|----------------------|--------------------------------|
| `is_read`           | read/unread          | `?is_read=false`               |
| `notification_type` | category             | `?notification_type=leave`     |
| `created_after`     | date range (start)   | `?created_after=2026-05-01`    |
| `created_before`    | date range (end)     | `?created_before=2026-05-10`   |

---

### 4. Views — `notifications/views.py`

All views use `@rbac` **without** `public=True`, so the decorator enforces authentication automatically — unauthenticated requests receive a `401` before the view body runs. No manual auth helper needed. POST (create) additionally checks that the caller's role is `admin` or `hr_manager` inline, since GET and POST share one decorator.

| View function              | Auth / Role                  | Purpose                                              |
|----------------------------|------------------------------|------------------------------------------------------|
| `notification_list`        | Any authenticated user (GET); `admin`/`hr_manager` (POST) | GET: current user's notifications (filtered). POST: create a notification for a given recipient. |
| `notification_detail`      | GET: fetch one notification. DELETE: delete it. Both scoped to `recipient=request.user`. |
| `notification_mark_read`   | POST: mark a single notification as read; sets `read_at` timestamp. |
| `notification_mark_all_read` | POST: bulk-mark all unread notifications of current user as read. |
| `notification_unread_count` | GET: returns `{"unread_count": N}` — useful for badge counters in frontends. |

---

### 5. URLs — `notifications/urls.py`

Mounted at `api/v1/`:

| Method | Endpoint                                  | View                        | Description                        |
|--------|-------------------------------------------|-----------------------------|------------------------------------|
| GET    | `/api/v1/notifications/`                  | `notification_list`         | List current user's notifications  |
| POST   | `/api/v1/notifications/`                  | `notification_list`         | Create a notification              |
| GET    | `/api/v1/notifications/unread-count/`     | `notification_unread_count` | Get unread badge count             |
| POST   | `/api/v1/notifications/mark-all-read/`    | `notification_mark_all_read`| Mark all unread as read            |
| GET    | `/api/v1/notifications/<pk>/`             | `notification_detail`       | Fetch single notification          |
| DELETE | `/api/v1/notifications/<pk>/`             | `notification_detail`       | Delete a notification              |
| POST   | `/api/v1/notifications/<pk>/mark-read/`   | `notification_mark_read`    | Mark one notification as read      |

> **Note:** `unread-count/` and `mark-all-read/` are declared before `<pk>/` in `urls.py` so Django does not interpret them as integer primary keys.

---

### 6. Admin — `notifications/admin.py`

Registered with list display, filters by type and read status, and search by recipient username, title, or message body. `created_at` and `read_at` are read-only in the admin form.

---

### 7. Config — `config/urls.py`

Uncommented the previously commented-out line:

```python
path('api/v1/', include('notifications.urls')),
```

---

## Migration

After creating the model, run:

```bash
python manage.py makemigrations notifications
python manage.py migrate
```

---

## Example Usage

### Create a notification (admin/HR)

```http
POST /api/v1/notifications/
Authorization: Bearer <token>

{
  "recipient": 3,
  "title": "Leave Approved",
  "message": "Your annual leave request for May 15–17 has been approved.",
  "notification_type": "leave"
}
```

### Get my notifications

```http
GET /api/v1/notifications/?is_read=false&notification_type=leave
Authorization: Bearer <token>
```

### Mark one as read

```http
POST /api/v1/notifications/12/mark-read/
Authorization: Bearer <token>
```

### Get unread count (for a badge)

```http
GET /api/v1/notifications/unread-count/
Authorization: Bearer <token>

→ { "unread_count": 5 }
```

---

## Pattern Consistency

This app follows the same conventions used throughout the HRM codebase:

- `@rbac` decorator from `accounts/rbac.py` instead of `@api_view` + `@permission_classes`
- `get_object_or_404` for safe lookups
- `django-filters` `FilterSet` in a dedicated `filters.py`
- DRF `Response` + `status` constants
- `select_related` / `update_fields` for query efficiency
- No ViewSets or class-based views — consistent with all other apps
