from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta

from accounts.models import Role, Permission, Employee
from core.models import Department
from leave.models import LeaveType, LeaveBalance, LeaveRequest, PublicHoliday


class Command(BaseCommand):
    help = "Seed the database with demo data"

    def handle(self, *args, **kwargs):
        self.stdout.write("\n[1] Clearing existing seed data...")
        LeaveRequest.objects.all().delete()
        LeaveBalance.objects.all().delete()
        PublicHoliday.objects.all().delete()
        LeaveType.objects.all().delete()
        Employee.objects.filter(is_superuser=False).delete()
        Department.objects.all().delete()
        Role.objects.all().delete()
        Permission.objects.all().delete()

        # ── Permissions ───────────────────────────────────────────────────────
        self.stdout.write("[2] Creating permissions...")
        perm_map = {}
        for codename, desc in [
            ("department.view",   "View departments"),
            ("department.manage", "Create/edit/delete departments"),
            ("employee.view",     "View employees"),
            ("employee.manage",   "Create/edit/delete employees"),
            ("leave.view",        "View leave records"),
            ("leave.manage",      "Approve/reject leave"),
            ("leave.apply",       "Apply for leave"),
        ]:
            p, _ = Permission.objects.get_or_create(codename=codename, defaults={"description": desc})
            perm_map[codename] = p

        # ── Roles ─────────────────────────────────────────────────────────────
        self.stdout.write("[3] Creating roles...")
        admin_role = Role.objects.create(name="admin")
        admin_role.permissions.set(perm_map.values())

        hr_role = Role.objects.create(name="hr_manager")
        hr_role.permissions.set([
            perm_map["employee.view"], perm_map["employee.manage"],
            perm_map["leave.view"],    perm_map["leave.manage"],
            perm_map["department.view"],
        ])

        employee_role = Role.objects.create(name="employee")
        employee_role.permissions.set([
            perm_map["leave.apply"], perm_map["leave.view"],
            perm_map["department.view"], perm_map["employee.view"],
        ])

        # ── Departments ───────────────────────────────────────────────────────
        self.stdout.write("[4] Creating departments...")
        depts = {
            name: Department.objects.create(name=name)
            for name in ["Engineering", "Human Resources", "Finance", "Marketing", "Operations"]
        }

        # ── Employees ─────────────────────────────────────────────────────────
        self.stdout.write("[5] Creating employees...")
        users_data = [
            ("alice", "Alice", "Rahman",    "Human Resources", hr_role,       "alice@hrm.com"),
            ("bob",   "Bob",   "Hossain",   "Engineering",     employee_role, "bob@hrm.com"),
            ("carol", "Carol", "Islam",     "Engineering",     employee_role, "carol@hrm.com"),
            ("david", "David", "Chowdhury", "Finance",         employee_role, "david@hrm.com"),
            ("eve",   "Eve",   "Begum",     "Marketing",       employee_role, "eve@hrm.com"),
            ("frank", "Frank", "Ahmed",     "Operations",      employee_role, "frank@hrm.com"),
            ("grace", "Grace", "Khan",      "Engineering",     employee_role, "grace@hrm.com"),
            ("henry", "Henry", "Miah",      "Finance",         employee_role, "henry@hrm.com"),
            ("irene", "Irene", "Akter",     "Marketing",       hr_role,       "irene@hrm.com"),
            ("john",  "John",  "Talukder",  "Operations",      employee_role, "john@hrm.com"),
        ]

        employees = {}
        for i, (username, first, last, dept_name, role, email) in enumerate(users_data):
            emp = Employee.objects.create_user(
                username=username,
                email=email,
                password="password",
                first_name=first,
                last_name=last,
                department=depts[dept_name],
                role=role,
                date_joined_company=date(2023, 1, 1) + timedelta(days=i * 30),
            )
            employees[username] = emp

        # ── Leave Types ───────────────────────────────────────────────────────
        self.stdout.write("[6] Creating leave types...")
        leave_types = {}
        for name, max_days, carry, carry_max, doc in [
            ("Annual Leave",    20, True,  5,  False),
            ("Sick Leave",      10, False, 0,  True),
            ("Casual Leave",    5,  False, 0,  False),
            ("Maternity Leave", 90, False, 0,  True),
        ]:
            leave_types[name] = LeaveType.objects.create(
                name=name,
                max_days_per_year=max_days,
                carry_forward=carry,
                carry_forward_max_days=carry_max,
                requires_document=doc,
                is_active=True,
            )

        # ── Leave Balances ────────────────────────────────────────────────────
        self.stdout.write("[7] Creating leave balances...")
        for emp in employees.values():
            for lt in leave_types.values():
                LeaveBalance.objects.create(
                    employee=emp,
                    leave_type=lt,
                    year=2026,
                    allocated_days=lt.max_days_per_year,
                    used_days=0,
                    carried_forward_days=lt.carry_forward_max_days if lt.carry_forward else 0,
                )

        # ── Leave Requests ────────────────────────────────────────────────────
        self.stdout.write("[8] Creating leave requests...")
        hr_reviewer = employees["alice"]
        requests_data = [
            ("bob",   "Annual Leave", date(2026, 6, 1),  date(2026, 6, 5),  "approved", "Family trip"),
            ("bob",   "Sick Leave",   date(2026, 3, 10), date(2026, 3, 11), "approved", "Fever"),
            ("carol", "Casual Leave", date(2026, 5, 20), date(2026, 5, 20), "pending",  "Personal work"),
            ("david", "Annual Leave", date(2026, 7, 14), date(2026, 7, 18), "pending",  "Vacation"),
            ("eve",   "Sick Leave",   date(2026, 4, 2),  date(2026, 4, 3),  "rejected", "No document"),
            ("frank", "Casual Leave", date(2026, 5, 5),  date(2026, 5, 5),  "cancelled","Changed plans"),
            ("grace", "Annual Leave", date(2026, 8, 1),  date(2026, 8, 10), "approved", "Annual leave"),
            ("henry", "Sick Leave",   date(2026, 2, 15), date(2026, 2, 16), "approved", "Medical"),
            ("irene", "Casual Leave", date(2026, 5, 12), date(2026, 5, 12), "pending",  "Errand"),
            ("john",  "Annual Leave", date(2026, 9, 1),  date(2026, 9, 3),  "pending",  "Travel"),
        ]

        for username, lt_name, start, end, req_status, reason in requests_data:
            emp = employees[username]
            lt  = leave_types[lt_name]
            total = (end - start).days + 1

            LeaveRequest.objects.create(
                employee=emp,
                leave_type=lt,
                start_date=start,
                end_date=end,
                total_days=total,
                reason=reason,
                status=req_status,
                reviewed_by=hr_reviewer if req_status in ("approved", "rejected") else None,
                review_note="Approved." if req_status == "approved" else ("Insufficient documentation." if req_status == "rejected" else ""),
                reviewed_at=timezone.now() if req_status in ("approved", "rejected") else None,
            )

            if req_status == "approved":
                try:
                    bal = LeaveBalance.objects.get(employee=emp, leave_type=lt, year=start.year)
                    bal.used_days += total
                    bal.save()
                except LeaveBalance.DoesNotExist:
                    pass

        # ── Public Holidays ───────────────────────────────────────────────────
        self.stdout.write("[9] Creating public holidays...")
        for name, day in [
            ("New Year's Day",   date(2026, 1,  1)),
            ("Independence Day", date(2026, 3, 26)),
            ("Bengali New Year", date(2026, 4, 14)),
            ("Eid ul-Fitr",      date(2026, 4, 20)),
            ("Eid ul-Adha",      date(2026, 6, 27)),
            ("Victory Day",      date(2026, 12, 16)),
        ]:
            PublicHoliday.objects.create(name=name, date=day)

        self.stdout.write(self.style.SUCCESS(
            f"\n✓ Seed complete.\n"
            f"  Employees:      {Employee.objects.filter(is_superuser=False).count()}\n"
            f"  Departments:    {Department.objects.count()}\n"
            f"  Leave Types:    {LeaveType.objects.count()}\n"
            f"  Leave Requests: {LeaveRequest.objects.count()}\n"
            f"  Public Holidays:{PublicHoliday.objects.count()}\n"
            f"\n  All passwords: password\n"
        ))
