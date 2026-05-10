from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, datetime

from accounts.models import Role, Permission, Employee
from core.models import Department
from leave.models import LeaveType, LeaveBalance, LeaveRequest, PublicHoliday
from events.models import Event, EventAttendee
from recruitment.models import JobPosting, Applicant, Application, Interview


def dt(y, mo, d, h=9, mi=0):
    """Return a timezone-aware datetime."""
    return timezone.make_aware(datetime(y, mo, d, h, mi))


class Command(BaseCommand):
    help = "Wipe and reseed the database with demo data (min 20 entries per model)"

    def handle(self, *args, **kwargs):

        # ── Clear ─────────────────────────────────────────────────────────────
        self.stdout.write("\n[0] Clearing existing data...")
        Interview.objects.all().delete()
        Application.objects.all().delete()
        Applicant.objects.all().delete()
        JobPosting.objects.all().delete()
        EventAttendee.objects.all().delete()
        Event.objects.all().delete()
        LeaveRequest.objects.all().delete()
        LeaveBalance.objects.all().delete()
        PublicHoliday.objects.all().delete()
        LeaveType.objects.all().delete()
        Employee.objects.filter(is_superuser=False).delete()
        Department.objects.all().delete()
        Role.objects.all().delete()
        Permission.objects.all().delete()

        # ── Permissions ───────────────────────────────────────────────────────
        self.stdout.write("[1] Creating permissions...")
        perm_map = {}
        for codename, desc in [
            ("department.view",   "View departments"),
            ("department.manage", "Create/edit/delete departments"),
            ("employee.view",     "View employees"),
            ("employee.manage",   "Create/edit/delete employees"),
            ("leave.view",        "View leave records"),
            ("leave.manage",      "Approve/reject leave"),
            ("leave.apply",       "Apply for leave"),
            ("event.manage",      "Create/edit/delete events"),
            ("recruitment.manage","Manage job postings and applications"),
        ]:
            p, _ = Permission.objects.get_or_create(codename=codename, defaults={"description": desc})
            perm_map[codename] = p

        # ── Roles ─────────────────────────────────────────────────────────────
        self.stdout.write("[2] Creating roles...")
        admin_role = Role.objects.create(name="admin")
        admin_role.permissions.set(perm_map.values())

        hr_role = Role.objects.create(name="hr_manager")
        hr_role.permissions.set([
            perm_map["employee.view"],   perm_map["employee.manage"],
            perm_map["leave.view"],      perm_map["leave.manage"],
            perm_map["department.view"], perm_map["event.manage"],
            perm_map["recruitment.manage"],
        ])

        employee_role = Role.objects.create(name="employee")
        employee_role.permissions.set([
            perm_map["leave.apply"], perm_map["leave.view"],
            perm_map["department.view"], perm_map["employee.view"],
        ])

        # ── Departments ───────────────────────────────────────────────────────
        self.stdout.write("[3] Creating departments...")
        dept_names = ["Engineering", "Human Resources", "Finance", "Marketing", "Operations"]
        depts = {n: Department.objects.create(name=n) for n in dept_names}

        # ── Employees (20) ────────────────────────────────────────────────────
        self.stdout.write("[4] Creating 20 employees...")
        #  username, first, last, department, role, email, joined, dob, phone
        users_data = [
            ("alice",   "Alice",   "Rahman",    "Human Resources", hr_role,       "alice@hrm.com",   date(2022, 1, 15),  date(1990, 3, 12), "01711-100001"),
            ("bob",     "Bob",     "Hossain",   "Engineering",     employee_role, "bob@hrm.com",     date(2022, 3, 1),   date(1992, 7, 5),  "01711-100002"),
            ("carol",   "Carol",   "Islam",     "Engineering",     employee_role, "carol@hrm.com",   date(2022, 5, 10),  date(1993, 11, 20),"01711-100003"),
            ("david",   "David",   "Chowdhury", "Finance",         employee_role, "david@hrm.com",   date(2022, 6, 20),  date(1988, 4, 8),  "01711-100004"),
            ("eve",     "Eve",     "Begum",     "Marketing",       employee_role, "eve@hrm.com",     date(2022, 8, 1),   date(1994, 9, 15), "01711-100005"),
            ("frank",   "Frank",   "Ahmed",     "Operations",      employee_role, "frank@hrm.com",   date(2022, 9, 15),  date(1991, 2, 28), "01711-100006"),
            ("grace",   "Grace",   "Khan",      "Engineering",     employee_role, "grace@hrm.com",   date(2022, 11, 1),  date(1995, 6, 10), "01711-100007"),
            ("henry",   "Henry",   "Miah",      "Finance",         employee_role, "henry@hrm.com",   date(2023, 1, 10),  date(1989, 12, 3), "01711-100008"),
            ("irene",   "Irene",   "Akter",     "Human Resources", hr_role,       "irene@hrm.com",   date(2023, 2, 20),  date(1987, 5, 22), "01711-100009"),
            ("john",    "John",    "Talukder",  "Operations",      employee_role, "john@hrm.com",    date(2023, 4, 5),   date(1990, 8, 17), "01711-100010"),
            ("karim",   "Karim",   "Uddin",     "Engineering",     employee_role, "karim@hrm.com",   date(2023, 5, 15),  date(1996, 1, 9),  "01711-100011"),
            ("layla",   "Layla",   "Sultana",   "Marketing",       employee_role, "layla@hrm.com",   date(2023, 6, 1),   date(1993, 10, 25),"01711-100012"),
            ("mehedi",  "Mehedi",  "Hasan",     "Engineering",     employee_role, "mehedi@hrm.com",  date(2023, 7, 10),  date(1991, 3, 14), "01711-100013"),
            ("nasrin",  "Nasrin",  "Parvin",    "Finance",         employee_role, "nasrin@hrm.com",  date(2023, 8, 20),  date(1992, 7, 30), "01711-100014"),
            ("omar",    "Omar",    "Faruk",     "Operations",      employee_role, "omar@hrm.com",    date(2023, 9, 1),   date(1988, 11, 11),"01711-100015"),
            ("priya",   "Priya",   "Das",       "Marketing",       employee_role, "priya@hrm.com",   date(2023, 10, 15), date(1994, 4, 2),  "01711-100016"),
            ("rafiq",   "Rafiq",   "Sarker",    "Engineering",     employee_role, "rafiq@hrm.com",   date(2023, 11, 1),  date(1990, 9, 19), "01711-100017"),
            ("sadia",   "Sadia",   "Khatun",    "Human Resources", employee_role, "sadia@hrm.com",   date(2024, 1, 10),  date(1995, 2, 7),  "01711-100018"),
            ("tanvir",  "Tanvir",  "Mahmud",    "Finance",         employee_role, "tanvir@hrm.com",  date(2024, 2, 20),  date(1989, 6, 26), "01711-100019"),
            ("usman",   "Usman",   "Gani",      "Operations",      admin_role,    "usman@hrm.com",   date(2024, 3, 1),   date(1985, 8, 13), "01711-100020"),
        ]

        employees = {}
        for username, first, last, dept_name, role, email, joined, dob, phone in users_data:
            emp = Employee.objects.create_user(
                username=username, email=email, password="password",
                first_name=first, last_name=last,
                department=depts[dept_name], role=role,
                date_joined_company=joined, date_of_birth=dob, phone=phone,
            )
            employees[username] = emp

        emp_list = list(employees.values())

        # ── Leave Types ───────────────────────────────────────────────────────
        self.stdout.write("[5] Creating leave types...")
        leave_types = {}
        for name, max_days, carry, carry_max, doc in [
            ("Annual Leave",    20, True,  5,  False),
            ("Sick Leave",      10, False, 0,  True),
            ("Casual Leave",    5,  False, 0,  False),
            ("Maternity Leave", 90, False, 0,  True),
        ]:
            leave_types[name] = LeaveType.objects.create(
                name=name, max_days_per_year=max_days,
                carry_forward=carry, carry_forward_max_days=carry_max,
                requires_document=doc, is_active=True,
            )

        # ── Leave Balances (20 employees × 4 types = 80) ──────────────────────
        self.stdout.write("[6] Creating leave balances (80 rows)...")
        for emp in emp_list:
            for lt in leave_types.values():
                LeaveBalance.objects.create(
                    employee=emp, leave_type=lt, year=2026,
                    allocated_days=lt.max_days_per_year,
                    used_days=0,
                    carried_forward_days=lt.carry_forward_max_days if lt.carry_forward else 0,
                )

        # ── Leave Requests (25) ───────────────────────────────────────────────
        self.stdout.write("[7] Creating leave requests (25 rows)...")
        reviewer = employees["alice"]
        al, sl, cl, ml = leave_types["Annual Leave"], leave_types["Sick Leave"], leave_types["Casual Leave"], leave_types["Maternity Leave"]

        leave_requests_data = [
            ("bob",    al, date(2026, 6, 1),  date(2026, 6, 5),   "approved",  "Family trip"),
            ("bob",    sl, date(2026, 3, 10), date(2026, 3, 11),  "approved",  "Fever"),
            ("carol",  cl, date(2026, 5, 20), date(2026, 5, 20),  "pending",   "Personal work"),
            ("david",  al, date(2026, 7, 14), date(2026, 7, 18),  "pending",   "Vacation"),
            ("eve",    sl, date(2026, 4, 2),  date(2026, 4, 3),   "rejected",  "No document provided"),
            ("frank",  cl, date(2026, 5, 5),  date(2026, 5, 5),   "cancelled", "Changed plans"),
            ("grace",  al, date(2026, 8, 1),  date(2026, 8, 10),  "approved",  "Annual holiday"),
            ("henry",  sl, date(2026, 2, 15), date(2026, 2, 16),  "approved",  "Medical checkup"),
            ("irene",  cl, date(2026, 5, 12), date(2026, 5, 12),  "pending",   "Bank errand"),
            ("john",   al, date(2026, 9, 1),  date(2026, 9, 3),   "pending",   "Travel"),
            ("karim",  sl, date(2026, 3, 5),  date(2026, 3, 7),   "approved",  "Injury"),
            ("layla",  al, date(2026, 6, 15), date(2026, 6, 20),  "approved",  "Eid holiday"),
            ("mehedi", cl, date(2026, 4, 28), date(2026, 4, 28),  "approved",  "Family function"),
            ("nasrin", ml, date(2026, 7, 1),  date(2026, 9, 28),  "approved",  "Maternity leave"),
            ("omar",   sl, date(2026, 5, 18), date(2026, 5, 19),  "pending",   "Flu"),
            ("priya",  al, date(2026, 10, 5), date(2026, 10, 10), "pending",   "Vacation"),
            ("rafiq",  cl, date(2026, 5, 25), date(2026, 5, 25),  "approved",  "Emergency"),
            ("sadia",  sl, date(2026, 4, 10), date(2026, 4, 11),  "rejected",  "No supporting doc"),
            ("tanvir", al, date(2026, 8, 20), date(2026, 8, 25),  "pending",   "Holiday travel"),
            ("usman",  cl, date(2026, 6, 3),  date(2026, 6, 3),   "approved",  "Personal"),
            ("bob",    al, date(2026, 11, 1), date(2026, 11, 5),  "pending",   "Year-end trip"),
            ("carol",  sl, date(2026, 2, 20), date(2026, 2, 21),  "approved",  "Cold"),
            ("david",  cl, date(2026, 3, 15), date(2026, 3, 15),  "cancelled", "Rescheduled"),
            ("grace",  sl, date(2026, 5, 8),  date(2026, 5, 8),   "pending",   "Headache"),
            ("henry",  al, date(2026, 12, 22),date(2026, 12, 31), "pending",   "Year-end leave"),
        ]

        for username, lt, start, end, req_status, reason in leave_requests_data:
            emp = employees[username]
            total = (end - start).days + 1
            LeaveRequest.objects.create(
                employee=emp, leave_type=lt,
                start_date=start, end_date=end, total_days=total,
                reason=reason, status=req_status,
                reviewed_by=reviewer if req_status in ("approved", "rejected") else None,
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

        # ── Public Holidays (12) ──────────────────────────────────────────────
        self.stdout.write("[8] Creating public holidays (12 rows)...")
        for name, day in [
            ("New Year's Day",          date(2026, 1, 1)),
            ("Shohid Dibosh",           date(2026, 2, 21)),
            ("Independence Day",        date(2026, 3, 26)),
            ("Bengali New Year",        date(2026, 4, 14)),
            ("May Day",                 date(2026, 5, 1)),
            ("Eid ul-Fitr (Day 1)",     date(2026, 4, 20)),
            ("Eid ul-Fitr (Day 2)",     date(2026, 4, 21)),
            ("Eid ul-Adha (Day 1)",     date(2026, 6, 27)),
            ("Eid ul-Adha (Day 2)",     date(2026, 6, 28)),
            ("National Mourning Day",   date(2026, 8, 15)),
            ("Durga Puja",              date(2026, 10, 2)),
            ("Victory Day",             date(2026, 12, 16)),
        ]:
            PublicHoliday.objects.create(name=name, date=day)

        # ── Events (20) ───────────────────────────────────────────────────────
        self.stdout.write("[9] Creating events (20 rows)...")
        hr_manager = employees["alice"]

        events_data = [
            # title, type, status, start, end, location, is_online, meeting_link, is_company_wide, dept_names
            ("Q1 All-Hands Meeting",         "meeting",     "published", dt(2026,1,15,10), dt(2026,1,15,12), "Auditorium A",      False, "",                           True,  []),
            ("Django REST Framework Training","training",   "published", dt(2026,2,5,9),   dt(2026,2,5,17),  "Training Room 2",   False, "",                           False, ["Engineering"]),
            ("Eid Celebration Party",        "celebration", "published", dt(2026,4,22,14), dt(2026,4,22,17), "Rooftop",           False, "",                           True,  []),
            ("Finance Budget Review",        "meeting",     "published", dt(2026,3,10,10), dt(2026,3,10,12), "Board Room",        False, "",                           False, ["Finance"]),
            ("New HR Policy Announcement",   "announcement","published", dt(2026,3,20,11), dt(2026,3,20,11,30), "Online",          True,  "https://meet.hrm.com/hr1",   True,  []),
            ("Engineering Sprint Planning",  "meeting",     "published", dt(2026,5,4,9),   dt(2026,5,4,10),  "",                  True,  "https://meet.hrm.com/eng1",  False, ["Engineering"]),
            ("Marketing Campaign Kickoff",   "meeting",     "published", dt(2026,5,12,10), dt(2026,5,12,11), "Marketing Conf Room",False,"",                           False, ["Marketing"]),
            ("Leadership Development Workshop","training",  "published", dt(2026,5,20,9),  dt(2026,5,20,17), "Training Room 1",   False, "",                           False, ["Human Resources","Engineering"]),
            ("Company Anniversary Gala",     "celebration", "published", dt(2026,6,1,18),  dt(2026,6,1,22),  "Grand Ballroom",    False, "",                           True,  []),
            ("Operations Process Review",    "meeting",     "published", dt(2026,6,10,9),  dt(2026,6,10,11), "Operations Hall",   False, "",                           False, ["Operations"]),
            ("Python Advanced Training",     "training",    "published", dt(2026,6,15,9),  dt(2026,6,16,17), "Training Room 2",   False, "",                           False, ["Engineering"]),
            ("Q2 Finance Close Meeting",     "meeting",     "published", dt(2026,7,3,10),  dt(2026,7,3,12),  "Board Room",        False, "",                           False, ["Finance"]),
            ("Mid-Year Performance Review",  "announcement","published", dt(2026,7,10,11), dt(2026,7,10,11,30),"Online",           True,  "https://meet.hrm.com/perf1", True,  []),
            ("Marketing Q3 Planning",        "meeting",     "published", dt(2026,7,20,10), dt(2026,7,20,12), "Marketing Conf Room",False,"",                           False, ["Marketing"]),
            ("Safety & Compliance Training", "training",    "published", dt(2026,8,5,9),   dt(2026,8,5,13),  "Training Room 1",   False, "",                           True,  []),
            ("Engineering Tech Talk",        "meeting",     "draft",     dt(2026,8,18,15), dt(2026,8,18,16), "",                  True,  "https://meet.hrm.com/tech1", False, ["Engineering"]),
            ("Employee Wellness Day",        "celebration", "published", dt(2026,9,5,10),  dt(2026,9,5,17),  "Company Garden",    False, "",                           True,  []),
            ("Recruitment Drive Briefing",   "meeting",     "published", dt(2026,9,15,10), dt(2026,9,15,11), "HR Conference Room",False,"",                           False, ["Human Resources"]),
            ("Year-End Strategy Meeting",    "meeting",     "draft",     dt(2026,12,1,9),  dt(2026,12,1,12), "Board Room",        False, "",                           True,  []),
            ("Christmas & New Year Party",   "celebration", "published", dt(2026,12,24,17),dt(2026,12,24,22),"Rooftop",           False, "",                           True,  []),
        ]

        event_objs = []
        for title, etype, estatus, start, end, location, is_online, link, company_wide, dept_names in events_data:
            ev = Event.objects.create(
                title=title, event_type=etype, status=estatus,
                start_datetime=start, end_datetime=end,
                location=location, is_online=is_online, meeting_link=link,
                is_company_wide=company_wide,
                created_by=hr_manager,
            )
            if dept_names:
                ev.departments.set([depts[d] for d in dept_names])
            event_objs.append(ev)

        # ── Event Attendees (40+) ─────────────────────────────────────────────
        self.stdout.write("[10] Creating event attendees (40+ rows)...")
        attendee_data = [
            # (event_index, username, rsvp)
            (0,  "bob",    "accepted"), (0,  "carol",  "accepted"), (0,  "david",  "accepted"),
            (0,  "frank",  "declined"), (0,  "karim",  "accepted"),
            (1,  "bob",    "accepted"), (1,  "carol",  "accepted"), (1,  "grace",  "accepted"),
            (1,  "karim",  "accepted"), (1,  "mehedi", "invited"),  (1,  "rafiq",  "accepted"),
            (2,  "bob",    "accepted"), (2,  "eve",    "accepted"), (2,  "layla",  "accepted"),
            (3,  "david",  "accepted"), (3,  "henry",  "accepted"), (3,  "nasrin", "accepted"),
            (4,  "alice",  "attended"), (4,  "irene",  "attended"), (4,  "sadia",  "attended"),
            (5,  "bob",    "accepted"), (5,  "carol",  "accepted"), (5,  "grace",  "invited"),
            (6,  "eve",    "accepted"), (6,  "layla",  "accepted"), (6,  "priya",  "invited"),
            (7,  "alice",  "accepted"), (7,  "irene",  "accepted"), (7,  "bob",    "invited"),
            (8,  "john",   "accepted"), (8,  "omar",   "accepted"), (8,  "frank",  "declined"),
            (9,  "frank",  "accepted"), (9,  "john",   "accepted"), (9,  "omar",   "invited"),
            (10, "bob",    "accepted"), (10, "carol",  "accepted"), (10, "rafiq",  "invited"),
            (11, "david",  "accepted"), (11, "henry",  "invited"),
            (12, "alice",  "attended"), (12, "usman",  "attended"),
            (14, "usman",  "accepted"), (14, "irene",  "accepted"),
            (16, "alice",  "accepted"), (16, "irene",  "accepted"), (16, "sadia",  "invited"),
        ]

        for event_idx, username, rsvp in attendee_data:
            EventAttendee.objects.get_or_create(
                event=event_objs[event_idx],
                employee=employees[username],
                defaults={"rsvp_status": rsvp, "responded_at": timezone.now() if rsvp != "invited" else None},
            )

        # ── Job Postings (20) ─────────────────────────────────────────────────
        self.stdout.write("[11] Creating job postings (20 rows)...")
        job_postings_data = [
            ("Senior Software Engineer",      "Engineering",     "We need an experienced Django developer.",      "5+ yrs Python, REST APIs",             3, "open",   date(2026, 6, 30)),
            ("Frontend Developer",            "Engineering",     "React developer for our HRM frontend.",         "3+ yrs React, TypeScript",             2, "open",   date(2026, 6, 30)),
            ("DevOps Engineer",               "Engineering",     "Maintain CI/CD and cloud infra.",               "AWS, Docker, Kubernetes",              1, "open",   date(2026, 7, 15)),
            ("HR Business Partner",           "Human Resources", "Strategic HR partner for departments.",         "5+ yrs HR experience",                 1, "open",   date(2026, 6, 15)),
            ("Recruitment Specialist",        "Human Resources", "Source and screen candidates.",                 "2+ yrs recruitment",                   2, "open",   date(2026, 6, 20)),
            ("Financial Analyst",             "Finance",         "Analyze budgets and financial reports.",        "CA/CPA, Excel, 3+ yrs exp",            1, "open",   date(2026, 6, 30)),
            ("Accounts Payable Officer",      "Finance",         "Manage vendor payments.",                       "2+ yrs accounting",                    1, "open",   date(2026, 7, 1)),
            ("Digital Marketing Manager",     "Marketing",       "Lead digital campaigns.",                       "SEO, SEM, social media, 4+ yrs",       1, "open",   date(2026, 6, 25)),
            ("Content Writer",               "Marketing",       "Write blogs and marketing copy.",               "Excellent English, 2+ yrs",            2, "open",   date(2026, 7, 10)),
            ("Operations Manager",           "Operations",      "Oversee daily operational activities.",         "5+ yrs ops management",                1, "open",   date(2026, 7, 31)),
            ("Logistics Coordinator",        "Operations",      "Coordinate supply chain and logistics.",        "3+ yrs logistics",                     2, "open",   date(2026, 7, 31)),
            ("QA Engineer",                  "Engineering",     "Test software quality and write test cases.",   "Selenium, Pytest, 3+ yrs",             1, "open",   date(2026, 8, 15)),
            ("Data Analyst",                 "Engineering",     "Analyze product and business data.",            "Python, SQL, Power BI",                1, "open",   date(2026, 8, 15)),
            ("Training & Development Officer","Human Resources","Design and deliver training programs.",          "Learning management, 3+ yrs",          1, "closed", date(2026, 4, 30)),
            ("Brand Manager",               "Marketing",       "Manage company brand identity.",                "Brand strategy, 4+ yrs",               1, "closed", date(2026, 4, 15)),
            ("Junior Accountant",           "Finance",         "Assist with bookkeeping and reports.",          "B.Com, 1+ yrs",                        2, "closed", date(2026, 3, 31)),
            ("Intern – Software",           "Engineering",     "6-month internship in backend development.",    "CS student, Python basics",            3, "closed", date(2026, 3, 15)),
            ("Supply Chain Analyst",        "Operations",      "Optimize supply chain processes.",              "Supply chain, analytics, 2+ yrs",      1, "draft",  date(2026, 9, 1)),
            ("SEO Specialist",              "Marketing",       "Drive organic growth.",                         "SEO tools, content, 2+ yrs",           1, "draft",  date(2026, 9, 15)),
            ("System Administrator",        "Engineering",     "Maintain IT infrastructure.",                   "Linux, networking, 3+ yrs",            1, "draft",  date(2026, 9, 30)),
        ]

        job_objs = []
        for title, dept_name, desc, reqs, vacancies, jstatus, deadline in job_postings_data:
            j = JobPosting.objects.create(
                title=title, department=depts[dept_name],
                description=desc, requirements=reqs, vacancies=vacancies,
                status=jstatus, deadline=deadline,
                created_by=employees["alice"],
            )
            job_objs.append(j)

        # ── Applicants (25) ───────────────────────────────────────────────────
        self.stdout.write("[12] Creating applicants (25 rows)...")
        applicants_data = [
            ("Arif",      "Hossain",   "arif.h@gmail.com",      "01811-200001"),
            ("Brishti",   "Alam",      "brishti.a@yahoo.com",   "01811-200002"),
            ("Cyrus",     "Patel",     "cyrus.p@gmail.com",     "01811-200003"),
            ("Dina",      "Karim",     "dina.k@outlook.com",    "01811-200004"),
            ("Enam",      "Choudhury", "enam.c@gmail.com",      "01811-200005"),
            ("Farida",    "Begum",     "farida.b@gmail.com",    "01811-200006"),
            ("Golam",     "Rabbani",   "golam.r@yahoo.com",     "01811-200007"),
            ("Halima",    "Siddiqua",  "halima.s@gmail.com",    "01811-200008"),
            ("Imran",     "Khan",      "imran.k@hotmail.com",   "01811-200009"),
            ("Jesmin",    "Akter",     "jesmin.a@gmail.com",    "01811-200010"),
            ("Kamrul",    "Islam",     "kamrul.i@gmail.com",    "01811-200011"),
            ("Lina",      "Moni",      "lina.m@gmail.com",      "01811-200012"),
            ("Mamun",     "Rashid",    "mamun.r@yahoo.com",     "01811-200013"),
            ("Nadia",     "Rahman",    "nadia.r@gmail.com",     "01811-200014"),
            ("Opu",       "Sarkar",    "opu.s@gmail.com",       "01811-200015"),
            ("Parvin",    "Sultana",   "parvin.s@outlook.com",  "01811-200016"),
            ("Quamrul",   "Hasan",     "quamrul.h@gmail.com",   "01811-200017"),
            ("Rina",      "Das",       "rina.d@gmail.com",      "01811-200018"),
            ("Sabbir",    "Ahmed",     "sabbir.a@gmail.com",    "01811-200019"),
            ("Tahmina",   "Khatun",    "tahmina.k@yahoo.com",   "01811-200020"),
            ("Ujjal",     "Biswas",    "ujjal.b@gmail.com",     "01811-200021"),
            ("Violet",    "Gomes",     "violet.g@gmail.com",    "01811-200022"),
            ("Wahid",     "Mia",       "wahid.m@hotmail.com",   "01811-200023"),
            ("Xena",      "Paul",      "xena.p@gmail.com",      "01811-200024"),
            ("Yusuf",     "Talukdar",  "yusuf.t@gmail.com",     "01811-200025"),
        ]

        applicant_objs = []
        for first, last, email, phone in applicants_data:
            a = Applicant.objects.create(first_name=first, last_name=last, email=email, phone=phone)
            applicant_objs.append(a)

        # ── Applications (25) ─────────────────────────────────────────────────
        self.stdout.write("[13] Creating applications (25 rows)...")
        # (applicant_index, job_index, status, cover_letter)
        applications_data = [
            (0,  0,  "interview",  "I have 6 years of Django experience."),
            (1,  1,  "screening",  "React is my primary skill."),
            (2,  2,  "offer",      "AWS certified with 4 years DevOps exp."),
            (3,  3,  "hired",      "HR partner with strategic background."),
            (4,  4,  "applied",    "Passionate about talent acquisition."),
            (5,  5,  "interview",  "CPA with 4 years in financial analysis."),
            (6,  6,  "screening",  "Accounts payable specialist."),
            (7,  7,  "offer",      "Led digital campaigns for 5 years."),
            (8,  8,  "applied",    "Content writer with SEO knowledge."),
            (9,  9,  "hired",      "Managed operations for a 200-person team."),
            (10, 10, "interview",  "Logistics coordinator at a 3PL company."),
            (11, 11, "screening",  "QA engineer, Selenium + Pytest expert."),
            (12, 12, "applied",    "Data analyst with Power BI dashboards."),
            (13, 13, "rejected",   "Interested in L&D role."),
            (14, 14, "rejected",   "Brand manager with FMCG background."),
            (15, 15, "hired",      "Junior accountant with 2 years exp."),
            (16, 16, "hired",      "CS final-year student, Python enthusiast."),
            (17, 0,  "applied",    "5 years Python, interested in senior role."),
            (18, 1,  "screening",  "Frontend dev, TypeScript + React Native."),
            (19, 2,  "interview",  "DevOps with GCP and Docker experience."),
            (20, 4,  "applied",    "Recruiter with startup background."),
            (21, 5,  "screening",  "Financial analyst, strong in modeling."),
            (22, 7,  "applied",    "Digital marketing with e-commerce focus."),
            (23, 9,  "screening",  "Operations background in manufacturing."),
            (24, 11, "applied",    "QA lead, automation testing specialist."),
        ]

        application_objs = []
        for app_i, job_i, app_status, cover in applications_data:
            ap = Application.objects.create(
                job_posting=job_objs[job_i],
                applicant=applicant_objs[app_i],
                status=app_status,
                cover_letter=cover,
            )
            application_objs.append(ap)

        # ── Interviews (20) ───────────────────────────────────────────────────
        self.stdout.write("[14] Creating interviews (20 rows)...")
        interviewer = employees["irene"]
        interview_data = [
            # (application_index, scheduled, mode, venue, result)
            (0,  dt(2026,4,10,10), "online",    "",                      "passed"),
            (1,  dt(2026,4,12,14), "online",    "",                      "pending"),
            (2,  dt(2026,3,20,10), "in_person", "HR Conference Room",    "passed"),
            (3,  dt(2026,3,5,11),  "in_person", "HR Conference Room",    "passed"),
            (5,  dt(2026,4,15,10), "online",    "",                      "passed"),
            (6,  dt(2026,4,18,15), "phone",     "",                      "pending"),
            (7,  dt(2026,3,28,10), "in_person", "Marketing Conf Room",   "passed"),
            (10, dt(2026,4,20,9),  "in_person", "Operations Hall",       "passed"),
            (11, dt(2026,4,22,14), "online",    "",                      "pending"),
            (13, dt(2026,3,10,11), "phone",     "",                      "failed"),
            (14, dt(2026,3,12,10), "in_person", "Marketing Conf Room",   "failed"),
            (15, dt(2026,2,20,10), "in_person", "Finance Conference Rm", "passed"),
            (16, dt(2026,2,25,14), "online",    "",                      "passed"),
            (17, dt(2026,5,5,10),  "online",    "",                      "pending"),
            (18, dt(2026,5,7,14),  "online",    "",                      "pending"),
            (19, dt(2026,4,28,10), "in_person", "Engineering Lab",       "passed"),
            (21, dt(2026,5,10,10), "phone",     "",                      "pending"),
            (22, dt(2026,5,12,14), "online",    "",                      "pending"),
            (23, dt(2026,5,8,9),   "in_person", "Operations Hall",       "pending"),
            (0,  dt(2026,5,1,10),  "in_person", "Engineering Lab",       "passed"),
        ]

        for app_i, sched, mode, venue, result in interview_data:
            Interview.objects.create(
                application=application_objs[app_i],
                interviewer=interviewer,
                scheduled_at=sched,
                mode=mode,
                venue=venue,
                result=result,
            )

        # ── Summary ───────────────────────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS(
            f"\n✓ Seed complete.\n"
            f"  Employees:       {Employee.objects.filter(is_superuser=False).count()}\n"
            f"  Departments:     {Department.objects.count()}\n"
            f"  Leave Types:     {LeaveType.objects.count()}\n"
            f"  Leave Balances:  {LeaveBalance.objects.count()}\n"
            f"  Leave Requests:  {LeaveRequest.objects.count()}\n"
            f"  Public Holidays: {PublicHoliday.objects.count()}\n"
            f"  Events:          {Event.objects.count()}\n"
            f"  Event Attendees: {EventAttendee.objects.count()}\n"
            f"  Job Postings:    {JobPosting.objects.count()}\n"
            f"  Applicants:      {Applicant.objects.count()}\n"
            f"  Applications:    {Application.objects.count()}\n"
            f"  Interviews:      {Interview.objects.count()}\n"
            f"\n  All passwords: password\n"
        ))
