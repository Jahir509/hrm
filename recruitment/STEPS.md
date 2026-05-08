# Recruitment App — Build Steps

## What was built

Full recruitment module for the HRM system. All endpoints are public (`public=True` via `@rbac`).

---

## Step 1 — Models (`models.py`)

Four models added:

| Model | Key fields |
|---|---|
| `JobPosting` | title, department (FK), description, requirements, vacancies, status (draft/open/closed), deadline, created_by (FK Employee) |
| `Applicant` | first_name, last_name, email (unique), phone, resume (FileField) |
| `Application` | job_posting (FK), applicant (FK), status (applied→screening→interview→offer→hired/rejected), cover_letter, notes. Unique together: (job_posting, applicant) |
| `Interview` | application (FK), interviewer (FK Employee), scheduled_at, mode (online/in_person/phone), venue, notes, result (pending/passed/failed) |

---

## Step 2 — Serializers (`serializers.py`)

- `JobPostingSerializer` — includes `application_count` (SerializerMethodField), `department_name`, `created_by_name`
- `ApplicantSerializer` — standard
- `ApplicationSerializer` — includes `interview_count`; validates job must be `open` to accept new applications
- `ApplicationAdvanceSerializer` — action serializer for the advance endpoint (status + optional notes)
- `InterviewSerializer` — includes `applicant_name`, `job_title`, `interviewer_name`

---

## Step 3 — Filters (`filters.py`)

| FilterSet | Fields |
|---|---|
| `JobPostingFilter` | status, department, deadline (lte) |
| `ApplicationFilter` | status, job_posting, applicant |
| `InterviewFilter` | result, mode, interviewer, application |

---

## Step 4 — Views (`views.py`)

All views use `@rbac(..., public=True)` — no authentication required.

| View | Methods | Description |
|---|---|---|
| `job_posting_list` | GET, POST | List / create job postings |
| `job_posting_detail` | GET, PUT, PATCH, DELETE | Retrieve / update / delete |
| `job_posting_close` | POST | Set status to `closed` |
| `applicant_list` | GET, POST | List / create applicants |
| `applicant_detail` | GET, PUT, PATCH, DELETE | Retrieve / update / delete |
| `application_list` | GET, POST | List / create applications |
| `application_detail` | GET, PUT, PATCH, DELETE | Retrieve / update / delete |
| `application_advance` | POST | Move application to next stage |
| `interview_list` | GET, POST | List / create interviews |
| `interview_detail` | GET, PUT, PATCH, DELETE | Retrieve / update / delete |

---

## Step 5 — URLs (`urls.py`)

```
GET  POST        /api/v1/jobs/
GET  PUT  PATCH  DELETE   /api/v1/jobs/<pk>/
POST             /api/v1/jobs/<pk>/close/

GET  POST        /api/v1/applicants/
GET  PUT  PATCH  DELETE   /api/v1/applicants/<pk>/

GET  POST        /api/v1/applications/
GET  PUT  PATCH  DELETE   /api/v1/applications/<pk>/
POST             /api/v1/applications/<pk>/advance/

GET  POST        /api/v1/interviews/
GET  PUT  PATCH  DELETE   /api/v1/interviews/<pk>/
```

---

## Step 6 — Registered in `config/urls.py`

```python
path('api/v1/', include('recruitment.urls')),
```

---

## Step 7 — Admin (`admin.py`)

All four models registered with `@admin.register`. List displays and filters configured for each.

---

## Step 8 — Migration

```bash
python manage.py makemigrations recruitment
python manage.py migrate recruitment
```

Migration file: `migrations/0001_initial.py`

---

## Application status flow

```
applied → screening → interview → offer → hired
                                        ↘ rejected (from any stage via /advance/)
```

Advancing is done via `POST /api/v1/applications/<pk>/advance/`:
```json
{ "status": "screening", "notes": "optional" }
```

Closing a job posting: `POST /api/v1/jobs/<pk>/close/`
