# Sprint App — Implementation Guide

## Overview

The `sprint` app brings lightweight project/sprint management into the HRM platform. It tracks time-boxed sprints and the tasks inside them. Admins and HR managers control sprint lifecycle (planning → active → completed). Any authenticated employee can create tasks, move them across status columns, and view their own assigned work.

---

## What Was Built

### 1. Models — `sprint/models.py`

#### `Sprint`

| Field        | Type          | Description                                         |
|--------------|---------------|-----------------------------------------------------|
| `name`       | CharField     | Sprint name (e.g. "Sprint 4 — Attendance")          |
| `goal`       | TextField     | What this sprint aims to achieve (optional)         |
| `start_date` | DateField     | Sprint start                                        |
| `end_date`   | DateField     | Sprint end                                          |
| `status`     | CharField     | `planning`, `active`, `completed`, `cancelled`      |
| `created_by` | FK(Employee)  | Who created the sprint                              |
| `created_at` | DateTimeField | Auto-set                                            |
| `updated_at` | DateTimeField | Auto-updated                                        |

#### `Task`

| Field          | Type          | Description                                           |
|----------------|---------------|-------------------------------------------------------|
| `sprint`       | FK(Sprint)    | Sprint this task belongs to                           |
| `title`        | CharField     | Task title                                            |
| `description`  | TextField     | Optional longer description                           |
| `assigned_to`  | FK(Employee)  | Who is responsible (nullable)                         |
| `created_by`   | FK(Employee)  | Who created the task                                  |
| `status`       | CharField     | `todo`, `in_progress`, `in_review`, `done`            |
| `priority`     | CharField     | `low`, `medium`, `high`, `critical`                   |
| `story_points` | PositiveInt   | Effort estimate (optional)                            |
| `due_date`     | DateField     | Must not exceed `sprint.end_date` (validated)         |
| `created_at`   | DateTimeField | Auto-set                                              |
| `updated_at`   | DateTimeField | Auto-updated                                          |

Default ordering: priority descending, then status, then created_at.

---

### 2. Serializers — `sprint/serializers.py`

#### `SprintSerializer`
- `created_by_name` — read-only `get_full_name()` of creator.
- `task_count` — read-only count of related tasks via `tasks.count`.
- `created_by` — read-only; auto-set to `request.user` in `create()`.
- Cross-field validation: `end_date` must be after `start_date`.

#### `TaskSerializer`
- `assigned_to_name`, `created_by_name`, `sprint_name` — read-only display fields.
- `created_by` — read-only; auto-set to `request.user` in `create()`.
- `validate_title` — rejects blank titles.
- Cross-field validation: `due_date` must not exceed `sprint.end_date`.

#### `TaskStatusSerializer`
- Minimal serializer used only by the `task_move` endpoint — accepts a single `status` choice field.

---

### 3. Filters — `sprint/filters.py`

#### `SprintFilter`

| Param          | Filters on         | Example                        |
|----------------|--------------------|--------------------------------|
| `status`       | sprint status      | `?status=active`               |
| `start_after`  | start_date ≥       | `?start_after=2026-04-01`      |
| `start_before` | start_date ≤       | `?start_before=2026-04-30`     |

#### `TaskFilter`

| Param         | Filters on     | Example                    |
|---------------|----------------|----------------------------|
| `sprint`      | sprint PK      | `?sprint=3`                |
| `status`      | task status    | `?status=in_progress`      |
| `priority`    | priority level | `?priority=critical`       |
| `assigned_to` | employee PK    | `?assigned_to=5`           |

---

### 4. Views — `sprint/views.py`

All views use `@rbac` without `public=True`. Role checks use the shared `_is_admin()` helper (`admin` or `hr_manager`).

| View              | Auth / Role                        | Purpose                                                      |
|-------------------|------------------------------------|--------------------------------------------------------------|
| `sprint_list`     | Any (GET); admin/hr (POST)         | List all sprints (filtered). Create a sprint.                |
| `sprint_detail`   | Any (GET); admin/hr (PUT/PATCH/DELETE) | Fetch, update, or delete a sprint.                       |
| `sprint_activate` | admin/hr only                      | Move sprint from `planning` → `active`. Blocks if another sprint is already active. |
| `sprint_complete` | admin/hr only                      | Move sprint from `active` → `completed`.                     |
| `sprint_tasks`    | Any authenticated                  | All tasks belonging to a specific sprint (filterable).       |
| `task_list`       | Any authenticated (GET + POST)     | List all tasks (filtered). Any employee can create a task.   |
| `task_detail`     | Any (GET/PUT/PATCH); admin/hr (DELETE) | Fetch or edit a task. Only admin/hr can delete.          |
| `task_move`       | Any authenticated                  | Change a task's `status` only (kanban-style column move).    |
| `my_tasks`        | Any authenticated                  | Current user's assigned tasks (filterable).                  |

#### Sprint lifecycle rules
- Only one sprint may be `active` at a time — `sprint_activate` enforces this.
- `planning` → `active` → `completed` is the only forward path.
- `sprint_activate` rejects anything not in `planning`.
- `sprint_complete` rejects anything not in `active`.

---

### 5. URLs — `sprint/urls.py`

Mounted at `api/v1/`:

| Method          | Endpoint                              | View              | Description                        |
|-----------------|---------------------------------------|-------------------|------------------------------------|
| GET             | `/api/v1/sprints/`                    | `sprint_list`     | List sprints                       |
| POST            | `/api/v1/sprints/`                    | `sprint_list`     | Create sprint (admin/hr)           |
| GET             | `/api/v1/sprints/<pk>/`               | `sprint_detail`   | Fetch sprint                       |
| PUT / PATCH     | `/api/v1/sprints/<pk>/`               | `sprint_detail`   | Update sprint (admin/hr)           |
| DELETE          | `/api/v1/sprints/<pk>/`               | `sprint_detail`   | Delete sprint (admin/hr)           |
| POST            | `/api/v1/sprints/<pk>/activate/`      | `sprint_activate` | Activate sprint (admin/hr)         |
| POST            | `/api/v1/sprints/<pk>/complete/`      | `sprint_complete` | Complete sprint (admin/hr)         |
| GET             | `/api/v1/sprints/<pk>/tasks/`         | `sprint_tasks`    | Tasks in a sprint                  |
| GET             | `/api/v1/tasks/`                      | `task_list`       | List all tasks                     |
| POST            | `/api/v1/tasks/`                      | `task_list`       | Create a task                      |
| GET             | `/api/v1/tasks/my/`                   | `my_tasks`        | My assigned tasks                  |
| GET             | `/api/v1/tasks/<pk>/`                 | `task_detail`     | Fetch task                         |
| PUT / PATCH     | `/api/v1/tasks/<pk>/`                 | `task_detail`     | Update task                        |
| DELETE          | `/api/v1/tasks/<pk>/`                 | `task_detail`     | Delete task (admin/hr)             |
| POST            | `/api/v1/tasks/<pk>/move/`            | `task_move`       | Move task to a new status column   |

---

### 6. Seed Data — `core/management/commands/seed.py`

5 sprints representing a realistic development timeline, each with 5 tasks (25 total):

| Sprint | Status    | Period              |
|--------|-----------|---------------------|
| Sprint 1 — Foundation  | completed | Jan 2026 |
| Sprint 2 — Auth & RBAC | completed | Feb 2026 |
| Sprint 3 — Leave       | completed | Mar 2026 |
| Sprint 4 — Attendance  | active    | Apr 2026 |
| Sprint 5 — Payroll     | planning  | May 2026 |

Tasks are assigned to the engineering team (`bob`, `carol`, `grace`, `karim`, `mehedi`, `rafiq`) with realistic statuses — earlier sprints are all `done`, the active sprint has a mix of `done`, `in_review`, `in_progress`, and `todo`.

---

## Example Usage

### Create a sprint (admin/hr)

```http
POST /api/v1/sprints/
Authorization: Bearer <admin-token>

{
  "name": "Sprint 6 — Performance",
  "goal": "Build performance review module.",
  "start_date": "2026-06-01",
  "end_date": "2026-06-19"
}
```

### Activate a sprint

```http
POST /api/v1/sprints/5/activate/
Authorization: Bearer <admin-token>
```

### Create a task

```http
POST /api/v1/tasks/
Authorization: Bearer <token>

{
  "sprint": 4,
  "title": "Write attendance API tests",
  "assigned_to": 2,
  "priority": "high",
  "story_points": 3,
  "due_date": "2026-04-22"
}
```

### Move a task to in_review (kanban move)

```http
POST /api/v1/tasks/18/move/
Authorization: Bearer <token>

{ "status": "in_review" }
```

### My assigned tasks filtered by sprint

```http
GET /api/v1/tasks/my/?sprint=4&status=in_progress
Authorization: Bearer <token>
```
