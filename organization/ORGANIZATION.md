# Organization App — Implementation Guide

## Overview

The `organization` app centralizes everything an HR system needs to describe and manage the company itself. It models the company entity, its physical/regional offices, holidays, working schedules, official documents, and social media presence. Admins and HR managers control all writes; any authenticated user can read.

---

## What Was Built

### 1. Models — `organization/models.py`

#### `Organization`

The top-level company record. Supports multi-organization deployments via the `is_primary` flag.

##### Identity

| Field                 | Type      | Description                                                |
|-----------------------|-----------|------------------------------------------------------------|
| `name`                | CharField | Display name. Unique.                                      |
| `legal_name`          | CharField | Full legal/registered name.                                |
| `short_name`          | CharField | Abbreviation or acronym.                                   |
| `slug`                | SlugField | URL-safe identifier. Unique.                               |
| `registration_number` | CharField | Company / business registration number.                    |
| `tax_id`              | CharField | TIN / VAT / EIN number.                                    |
| `industry`            | CharField | Industry sector (e.g. "Software", "Manufacturing").        |
| `organization_type`   | CharField | `private`, `public`, `nonprofit`, `government`, `partnership`, `sole_proprietorship`. |
| `size`                | CharField | `micro` (1-9), `small` (10-49), `medium` (50-249), `large` (250-999), `enterprise` (1000+). |
| `founded_date`        | DateField | When the company was founded.                              |

##### Branding

| Field             | Type           | Description                              |
|-------------------|----------------|------------------------------------------|
| `logo`            | ImageField     | Uploaded to `media/organization/logos/`. |
| `favicon`         | ImageField     | Uploaded to `media/organization/favicons/`. |
| `primary_color`   | CharField (#hex) | Brand primary color (validated).       |
| `secondary_color` | CharField (#hex) | Brand secondary color.                 |

##### Contact

| Field     | Type      | Description       |
|-----------|-----------|-------------------|
| `email`   | EmailField | Main contact.    |
| `phone`   | CharField | Main phone line.  |
| `website` | URLField  | Public website.   |

##### Headquarters address

| Field           | Type      | Description                |
|-----------------|-----------|----------------------------|
| `address_line1` | CharField | Street line 1.             |
| `address_line2` | CharField | Street line 2.             |
| `city`          | CharField | City.                      |
| `state`         | CharField | State / province / region. |
| `country`       | CharField | Country.                   |
| `postal_code`   | CharField | ZIP / postal code.         |

##### About

| Field         | Type      | Description                       |
|---------------|-----------|-----------------------------------|
| `description` | TextField | Long-form "About us" text.        |
| `mission`     | TextField | Mission statement.                |
| `vision`      | TextField | Vision statement.                 |

##### Operational defaults

| Field                  | Type           | Default     | Description                                      |
|------------------------|----------------|-------------|--------------------------------------------------|
| `currency`             | CharField(3)   | `USD`       | ISO 4217 currency code (used for payroll).       |
| `timezone`             | CharField      | `Asia/Dhaka`| Default tz when a branch doesn't override.       |
| `fiscal_year_start`    | CharField(5)   | `01-01`     | `MM-DD` — when the fiscal year begins.           |
| `weekly_working_days`  | PositiveSmallInt | `5`       | Default working days per week.                   |
| `weekly_working_hours` | Decimal(4,2)   | `40.00`     | Default working hours per week.                  |

##### People

| Field   | Type           | Description                          |
|---------|----------------|--------------------------------------|
| `ceo`   | FK(Employee)   | Current CEO. Nullable.               |
| `owner` | FK(Employee)   | Owner / primary contact. Nullable.   |

##### Status

| Field        | Type      | Description                                                                       |
|--------------|-----------|-----------------------------------------------------------------------------------|
| `status`     | CharField | `active`, `inactive`, `suspended`.                                                |
| `is_primary` | Boolean   | Marks the tenant organization for this deployment. Only one org may have it true. |

##### Audit

| Field        | Type           | Description       |
|--------------|----------------|-------------------|
| `created_by` | FK(Employee)   | Who created it.   |
| `created_at` | DateTimeField  | Auto-set.         |
| `updated_at` | DateTimeField  | Auto-updated.     |

---

#### `Branch`

A physical or logical office under an `Organization`.

| Field           | Type           | Description                                                       |
|-----------------|----------------|-------------------------------------------------------------------|
| `organization`  | FK(Organization) | Parent organization.                                            |
| `name`          | CharField      | Branch name.                                                      |
| `code`          | CharField      | Short code (e.g. `DHK-01`). Unique per organization.              |
| `branch_type`   | CharField      | `headquarters`, `regional`, `branch`, `remote`, `factory`, `warehouse`. |
| `email`         | EmailField     | Branch email.                                                     |
| `phone`         | CharField      | Branch phone.                                                     |
| `address_line1` | CharField      | Street line 1.                                                    |
| `address_line2` | CharField      | Street line 2.                                                    |
| `city`          | CharField      | City.                                                             |
| `state`         | CharField      | State / region.                                                   |
| `country`       | CharField      | Country.                                                          |
| `postal_code`   | CharField      | ZIP / postal code.                                                |
| `timezone`      | CharField      | Branch-specific timezone. Falls back to organization timezone.    |
| `manager`       | FK(Employee)   | Branch manager. Nullable.                                         |
| `opened_on`     | DateField      | When the branch opened.                                           |
| `is_active`     | Boolean        | Mark branches as closed without deleting them.                    |
| `created_at`    | DateTimeField  | Auto-set.                                                         |
| `updated_at`    | DateTimeField  | Auto-updated.                                                     |

Unique constraint: `(organization, code)`.

---

#### `Holiday`

Org-wide or branch-scoped holidays. Used by attendance/leave to identify non-working days.

| Field          | Type           | Description                                                      |
|----------------|----------------|------------------------------------------------------------------|
| `organization` | FK(Organization) | Owner organization.                                            |
| `branch`       | FK(Branch)     | Optional. Leave blank for an org-wide holiday.                   |
| `name`         | CharField      | E.g. "Independence Day".                                         |
| `date`         | DateField      | The holiday date.                                                |
| `is_recurring` | Boolean        | If true, repeats every year on the same MM-DD.                   |
| `description`  | TextField      | Optional notes.                                                  |
| `created_at`   | DateTimeField  | Auto-set.                                                        |
| `updated_at`   | DateTimeField  | Auto-updated.                                                    |

Unique constraint: `(organization, branch, date, name)`.

---

#### `WorkSchedule`

Reusable working-hours template that can be assigned to teams or branches.

| Field             | Type           | Description                                            |
|-------------------|----------------|--------------------------------------------------------|
| `organization`    | FK(Organization) | Owner organization.                                  |
| `name`            | CharField      | Schedule name (e.g. "Standard 9-5"). Unique per org.   |
| `start_time`      | TimeField      | Daily start time.                                      |
| `end_time`        | TimeField      | Daily end time. Must be after `start_time` (validated).|
| `break_minutes`   | PositiveInt    | Daily break length in minutes. Default `60`.           |
| `works_monday`    | Boolean        | Working day flag.                                      |
| `works_tuesday`   | Boolean        | Working day flag.                                      |
| `works_wednesday` | Boolean        | Working day flag.                                      |
| `works_thursday`  | Boolean        | Working day flag.                                      |
| `works_friday`    | Boolean        | Working day flag.                                      |
| `works_saturday`  | Boolean        | Working day flag. Default `False`.                     |
| `works_sunday`    | Boolean        | Working day flag. Default `False`.                     |
| `is_default`      | Boolean        | Marks the default schedule for the organization.       |
| `created_at`      | DateTimeField  | Auto-set.                                              |
| `updated_at`      | DateTimeField  | Auto-updated.                                          |

---

#### `OrganizationDocument`

Official files attached to the organization — policies, handbooks, contracts, licenses, certificates.

| Field            | Type           | Description                                              |
|------------------|----------------|----------------------------------------------------------|
| `organization`   | FK(Organization) | Owner organization.                                    |
| `title`          | CharField      | Document title.                                          |
| `document_type`  | CharField      | `policy`, `handbook`, `contract`, `license`, `certificate`, `other`. |
| `file`           | FileField      | Uploaded to `media/organization/documents/`.             |
| `description`    | TextField      | Optional summary.                                        |
| `effective_date` | DateField      | Date the document takes effect.                          |
| `expiry_date`    | DateField      | Date the document expires.                               |
| `uploaded_by`    | FK(Employee)   | Auto-set to the uploading user.                          |
| `created_at`     | DateTimeField  | Auto-set.                                                |
| `updated_at`     | DateTimeField  | Auto-updated.                                            |

---

#### `SocialLink`

Public social media presence for an organization.

| Field          | Type           | Description                                                            |
|----------------|----------------|------------------------------------------------------------------------|
| `organization` | FK(Organization) | Owner organization.                                                  |
| `platform`     | CharField      | `linkedin`, `twitter`, `facebook`, `instagram`, `youtube`, `github`, `other`. |
| `url`          | URLField       | The profile URL.                                                       |

Unique constraint: `(organization, platform)`.

---

### 2. Serializers — `organization/serializers.py`

#### `OrganizationSerializer`
- Read-only display fields: `ceo_name`, `owner_name`, `branch_count`, `social_links` (nested).
- `validate_primary_color` — rejects values not starting with `#`.
- Cross-field validation: only one `Organization` may have `is_primary=True`.
- `created_by` auto-set to `request.user`.

#### `BranchSerializer`
- Read-only display fields: `organization_name`, `manager_name`.

#### `HolidaySerializer`
- Read-only display fields: `organization_name`, `branch_name`.
- Cross-field validation: if `branch` is given, it must belong to the chosen `organization`.

#### `WorkScheduleSerializer`
- Read-only display field: `organization_name`.
- Cross-field validation: `end_time` must be after `start_time`.

#### `OrganizationDocumentSerializer`
- Read-only display fields: `organization_name`, `uploaded_by_name`.
- `uploaded_by` auto-set to `request.user`.

#### `SocialLinkSerializer`
- Plain ModelSerializer.

---

### 3. Filters — `organization/filters.py`

#### `OrganizationFilter`

| Param               | Filters on        | Example                          |
|---------------------|-------------------|----------------------------------|
| `name`              | name (icontains)  | `?name=acme`                     |
| `organization_type` | exact match       | `?organization_type=private`     |
| `size`              | exact match       | `?size=medium`                   |
| `status`            | exact match       | `?status=active`                 |
| `industry`          | exact match       | `?industry=Software`             |
| `country`           | iexact            | `?country=Bangladesh`            |

#### `BranchFilter`

| Param          | Filters on        | Example                |
|----------------|-------------------|------------------------|
| `organization` | organization PK   | `?organization=1`      |
| `branch_type`  | type              | `?branch_type=regional`|
| `is_active`    | active flag       | `?is_active=true`      |
| `city`         | exact             | `?city=Dhaka`          |
| `country`      | exact             | `?country=Bangladesh`  |
| `name`         | name (icontains)  | `?name=hq`             |

#### `HolidayFilter`

| Param          | Filters on   | Example                     |
|----------------|--------------|-----------------------------|
| `organization` | org PK       | `?organization=1`           |
| `branch`       | branch PK    | `?branch=2`                 |
| `is_recurring` | recurring    | `?is_recurring=true`        |
| `date_after`   | date ≥       | `?date_after=2026-01-01`    |
| `date_before`  | date ≤       | `?date_before=2026-12-31`   |

#### `WorkScheduleFilter`

| Param          | Filters on   | Example              |
|----------------|--------------|----------------------|
| `organization` | org PK       | `?organization=1`    |
| `is_default`   | default flag | `?is_default=true`   |

#### `OrganizationDocumentFilter`

| Param           | Filters on    | Example                  |
|-----------------|---------------|--------------------------|
| `organization`  | org PK        | `?organization=1`        |
| `document_type` | type          | `?document_type=policy`  |

---

### 4. Views — `organization/views.py`

All views use `@rbac` (login required). Writes (`POST`, `PUT`, `PATCH`, `DELETE`) require `is_admin` (`admin` or `hr_manager` role); reads only require authentication.

| View                     | Auth / Role                              | Purpose                                              |
|--------------------------|------------------------------------------|------------------------------------------------------|
| `organization_list`      | Any (GET); admin/hr (POST)               | List & create organizations.                         |
| `organization_detail`    | Any (GET); admin/hr (PUT/PATCH/DELETE)   | Fetch / update / delete a single organization.       |
| `primary_organization`   | Any authenticated                        | Returns the org with `is_primary=True`.              |
| `organization_branches`  | Any authenticated                        | All branches for a specific organization.            |
| `branch_list`            | Any (GET); admin/hr (POST)               | List & create branches.                              |
| `branch_detail`          | Any (GET); admin/hr (PUT/PATCH/DELETE)   | Fetch / update / delete a branch.                    |
| `holiday_list`           | Any (GET); admin/hr (POST)               | List & create holidays.                              |
| `holiday_detail`         | Any (GET); admin/hr (PUT/PATCH/DELETE)   | Fetch / update / delete a holiday.                   |
| `work_schedule_list`     | Any (GET); admin/hr (POST)               | List & create work schedules.                        |
| `work_schedule_detail`   | Any (GET); admin/hr (PUT/PATCH/DELETE)   | Fetch / update / delete a schedule.                  |
| `document_list`          | Any (GET); admin/hr (POST)               | List & upload organization documents.                |
| `document_detail`        | Any (GET); admin/hr (PUT/PATCH/DELETE)   | Fetch / update / delete a document.                  |
| `social_link_list`       | Any (GET); admin/hr (POST)               | List & create social links.                          |
| `social_link_detail`     | Any (GET); admin/hr (PUT/PATCH/DELETE)   | Fetch / update / delete a social link.               |

---

### 5. URLs — `organization/urls.py`

Mounted at `api/v1/`:

| Method        | Endpoint                                              | View                     |
|---------------|-------------------------------------------------------|--------------------------|
| GET           | `/api/v1/organizations/`                              | `organization_list`      |
| POST          | `/api/v1/organizations/`                              | `organization_list`      |
| GET           | `/api/v1/organizations/primary/`                      | `primary_organization`   |
| GET           | `/api/v1/organizations/<pk>/`                         | `organization_detail`    |
| PUT / PATCH   | `/api/v1/organizations/<pk>/`                         | `organization_detail`    |
| DELETE        | `/api/v1/organizations/<pk>/`                         | `organization_detail`    |
| GET           | `/api/v1/organizations/<pk>/branches/`                | `organization_branches`  |
| GET           | `/api/v1/branches/`                                   | `branch_list`            |
| POST          | `/api/v1/branches/`                                   | `branch_list`            |
| GET           | `/api/v1/branches/<pk>/`                              | `branch_detail`          |
| PUT / PATCH   | `/api/v1/branches/<pk>/`                              | `branch_detail`          |
| DELETE        | `/api/v1/branches/<pk>/`                              | `branch_detail`          |
| GET           | `/api/v1/holidays/`                                   | `holiday_list`           |
| POST          | `/api/v1/holidays/`                                   | `holiday_list`           |
| GET           | `/api/v1/holidays/<pk>/`                              | `holiday_detail`         |
| PUT / PATCH   | `/api/v1/holidays/<pk>/`                              | `holiday_detail`         |
| DELETE        | `/api/v1/holidays/<pk>/`                              | `holiday_detail`         |
| GET           | `/api/v1/work-schedules/`                             | `work_schedule_list`     |
| POST          | `/api/v1/work-schedules/`                             | `work_schedule_list`     |
| GET           | `/api/v1/work-schedules/<pk>/`                        | `work_schedule_detail`   |
| PUT / PATCH   | `/api/v1/work-schedules/<pk>/`                        | `work_schedule_detail`   |
| DELETE        | `/api/v1/work-schedules/<pk>/`                        | `work_schedule_detail`   |
| GET           | `/api/v1/organization-documents/`                     | `document_list`          |
| POST          | `/api/v1/organization-documents/`                     | `document_list`          |
| GET           | `/api/v1/organization-documents/<pk>/`                | `document_detail`        |
| PUT / PATCH   | `/api/v1/organization-documents/<pk>/`                | `document_detail`        |
| DELETE        | `/api/v1/organization-documents/<pk>/`                | `document_detail`        |
| GET           | `/api/v1/organization-social-links/`                  | `social_link_list`       |
| POST          | `/api/v1/organization-social-links/`                  | `social_link_list`       |
| GET           | `/api/v1/organization-social-links/<pk>/`             | `social_link_detail`     |
| PUT / PATCH   | `/api/v1/organization-social-links/<pk>/`             | `social_link_detail`     |
| DELETE        | `/api/v1/organization-social-links/<pk>/`             | `social_link_detail`     |

---

### 6. Admin — `organization/admin.py`

All six models are registered. `OrganizationAdmin` uses two inlines so an admin can edit branches and social links inline with the organization. Slug is auto-prepopulated from `name`.

---

## Example Usage

### Create an organization (admin/hr)

```http
POST /api/v1/organizations/
Authorization: Bearer <admin-token>

{
  "name": "Acme Corp",
  "legal_name": "Acme Corporation Ltd.",
  "slug": "acme-corp",
  "registration_number": "REG-2020-12345",
  "tax_id": "TIN-9876543",
  "industry": "Software",
  "organization_type": "private",
  "size": "medium",
  "founded_date": "2015-06-01",
  "email": "info@acme.example",
  "phone": "+880-1700-000000",
  "website": "https://acme.example",
  "address_line1": "House 12, Road 4",
  "city": "Dhaka",
  "country": "Bangladesh",
  "postal_code": "1212",
  "currency": "BDT",
  "timezone": "Asia/Dhaka",
  "primary_color": "#1A73E8",
  "is_primary": true
}
```

### Add a branch

```http
POST /api/v1/branches/
Authorization: Bearer <admin-token>

{
  "organization": 1,
  "name": "Chattogram Office",
  "code": "CTG-01",
  "branch_type": "regional",
  "city": "Chattogram",
  "country": "Bangladesh",
  "manager": 7,
  "opened_on": "2022-03-15"
}
```

### Add a recurring holiday

```http
POST /api/v1/holidays/
Authorization: Bearer <admin-token>

{
  "organization": 1,
  "name": "Independence Day",
  "date": "2026-03-26",
  "is_recurring": true
}
```

### Define a work schedule

```http
POST /api/v1/work-schedules/
Authorization: Bearer <admin-token>

{
  "organization": 1,
  "name": "Standard 9-5",
  "start_time": "09:00",
  "end_time": "17:00",
  "break_minutes": 60,
  "works_monday": true,
  "works_tuesday": true,
  "works_wednesday": true,
  "works_thursday": true,
  "works_friday": true,
  "is_default": true
}
```

### Upload an organization document

```http
POST /api/v1/organization-documents/
Authorization: Bearer <admin-token>
Content-Type: multipart/form-data

organization=1
title=Employee Handbook 2026
document_type=handbook
file=@handbook.pdf
effective_date=2026-01-01
```

### Get the primary organization

```http
GET /api/v1/organizations/primary/
Authorization: Bearer <token>
```

### List active branches in Bangladesh

```http
GET /api/v1/branches/?country=Bangladesh&is_active=true
Authorization: Bearer <token>
```
