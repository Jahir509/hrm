# Events App

Manages company events, attendee tracking, RSVP, and per-employee calendar views.

---

## Files

### `models.py`
Defines the two database tables.

| Model | Purpose |
|---|---|
| `Event` | A company event (meeting, training, celebration, etc.) with type, status, datetime range, location, online flag, department targeting, and company-wide flag. |
| `EventAttendee` | Join table between `Event` and `Employee` with RSVP status (`invited / accepted / declined / attended`), `responded_at`, and an optional note. Unique per `(event, employee)`. |

**Event fields of note:**
- `event_type` — `meeting`, `training`, `celebration`, `announcement`, `other`
- `status` — `draft` (hidden from calendar), `published`, `cancelled`
- `departments` (M2M → `core.Department`) — target specific departments; leave empty if `is_company_wide=True`
- `is_company_wide` — surfaces the event in every employee's calendar regardless of department

---

### `serializers.py`
| Serializer | Used for |
|---|---|
| `EventSerializer` | Full event CRUD. Auto-sets `created_by` from `request.user` on create. Exposes `attendee_count` and `department_names` as read-only computed fields. |
| `EventAttendeeSerializer` | Attendee list / detail. Exposes `employee_name` and `event_title`. |
| `RSVPSerializer` | Accepts `rsvp_status` (`accepted` / `declined`) and optional `note` for the RSVP endpoint. |

---

### `filters.py`
| FilterSet | Filterable fields |
|---|---|
| `EventFilter` | `event_type`, `status`, `is_company_wide`, `department` (by id), `created_by` (by id), `start_from` (date ≥), `start_until` (date ≤) |
| `EventAttendeeFilter` | `event` (by id), `employee` (by id), `rsvp_status` |

---

### `views.py`
All views use the `@rbac` decorator (login required by default).

| View function | Methods | Description |
|---|---|---|
| `event_list` | GET, POST | List all events (filterable) / create a new event |
| `event_detail` | GET, PUT, PATCH, DELETE | Retrieve / update / delete a single event |
| `event_attendee_list` | GET, POST | List attendees for an event / add an attendee |
| `event_attendee_detail` | GET, PATCH, DELETE | Retrieve / update RSVP / remove an attendee |
| `event_rsvp` | POST | Current user accepts or declines an event (upserts an `EventAttendee` row) |
| `my_events` | GET | All `EventAttendee` rows for the current user |
| `my_calendar` | GET | Published events visible to the current user for a given month |

**`my_calendar` visibility rule:** an event appears if it is `published` **and** (`is_company_wide=True` OR the event targets the user's department OR the user is in the attendee list).

**`my_calendar` response shape:**
```json
{
  "year": 2026,
  "month": 5,
  "month_name": "May",
  "total_days": 31,
  "events": [ ...flat list of EventSerializer objects... ],
  "by_date": {
    "8":  [ ...events whose span includes the 8th... ],
    "15": [ ...events whose span includes the 15th... ]
  }
}
```
Query params: `?year=2026&month=5` (both default to the current date).

---

### `urls.py`
All paths are mounted under `api/v1/` in `config/urls.py`.

| URL | View |
|---|---|
| `events/` | `event_list` |
| `events/<pk>/` | `event_detail` |
| `events/<pk>/attendees/` | `event_attendee_list` |
| `events/<pk>/attendees/<att_pk>/` | `event_attendee_detail` |
| `events/<pk>/rsvp/` | `event_rsvp` |
| `my-events/` | `my_events` |
| `my-calendar/` | `my_calendar` |

---

## Getting started

```bash
python manage.py makemigrations events
python manage.py migrate
```
