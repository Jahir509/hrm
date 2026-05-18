from django.db import models
from django.conf import settings


class Organization(models.Model):
    TYPE_PRIVATE     = 'private'
    TYPE_PUBLIC      = 'public'
    TYPE_NONPROFIT   = 'nonprofit'
    TYPE_GOVERNMENT  = 'government'
    TYPE_PARTNERSHIP = 'partnership'
    TYPE_SOLE        = 'sole_proprietorship'

    TYPE_CHOICES = [
        (TYPE_PRIVATE,     'Private Limited'),
        (TYPE_PUBLIC,      'Public Limited'),
        (TYPE_NONPROFIT,   'Non-Profit'),
        (TYPE_GOVERNMENT,  'Government'),
        (TYPE_PARTNERSHIP, 'Partnership'),
        (TYPE_SOLE,        'Sole Proprietorship'),
    ]

    SIZE_MICRO  = 'micro'        # 1-9
    SIZE_SMALL  = 'small'        # 10-49
    SIZE_MEDIUM = 'medium'       # 50-249
    SIZE_LARGE  = 'large'        # 250-999
    SIZE_ENTERPRISE = 'enterprise'  # 1000+

    SIZE_CHOICES = [
        (SIZE_MICRO,      'Micro (1-9)'),
        (SIZE_SMALL,      'Small (10-49)'),
        (SIZE_MEDIUM,     'Medium (50-249)'),
        (SIZE_LARGE,      'Large (250-999)'),
        (SIZE_ENTERPRISE, 'Enterprise (1000+)'),
    ]

    STATUS_ACTIVE    = 'active'
    STATUS_INACTIVE  = 'inactive'
    STATUS_SUSPENDED = 'suspended'

    STATUS_CHOICES = [
        (STATUS_ACTIVE,    'Active'),
        (STATUS_INACTIVE,  'Inactive'),
        (STATUS_SUSPENDED, 'Suspended'),
    ]

    # Identity
    name                = models.CharField(max_length=255, unique=True)
    legal_name          = models.CharField(max_length=255, blank=True)
    short_name          = models.CharField(max_length=50, blank=True)
    slug                = models.SlugField(max_length=120, unique=True)
    registration_number = models.CharField(max_length=100, blank=True)
    tax_id              = models.CharField(max_length=100, blank=True)
    industry            = models.CharField(max_length=100, blank=True)
    organization_type   = models.CharField(max_length=30, choices=TYPE_CHOICES, default=TYPE_PRIVATE)
    size                = models.CharField(max_length=20, choices=SIZE_CHOICES, default=SIZE_SMALL)
    founded_date        = models.DateField(null=True, blank=True)

    # Branding
    logo            = models.ImageField(upload_to='organization/logos/', null=True, blank=True)
    favicon         = models.ImageField(upload_to='organization/favicons/', null=True, blank=True)
    primary_color   = models.CharField(max_length=7, blank=True, help_text='Hex code e.g. #1A73E8')
    secondary_color = models.CharField(max_length=7, blank=True)

    # Contact
    email   = models.EmailField(blank=True)
    phone   = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True)

    # Headquarters address
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city          = models.CharField(max_length=100, blank=True)
    state         = models.CharField(max_length=100, blank=True)
    country       = models.CharField(max_length=100, blank=True)
    postal_code   = models.CharField(max_length=20, blank=True)

    # About
    description = models.TextField(blank=True)
    mission     = models.TextField(blank=True)
    vision      = models.TextField(blank=True)

    # Operational defaults
    currency           = models.CharField(max_length=3, default='USD', help_text='ISO 4217 code')
    timezone           = models.CharField(max_length=64, default='Asia/Dhaka')
    fiscal_year_start  = models.CharField(max_length=5, default='01-01', help_text='MM-DD')
    weekly_working_days = models.PositiveSmallIntegerField(default=5)
    weekly_working_hours = models.DecimalField(max_digits=4, decimal_places=2, default=40)

    # People
    ceo = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='led_organizations',
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='owned_organizations',
    )

    # Status
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    is_primary = models.BooleanField(default=False, help_text='The tenant organization for this deployment')

    # Audit
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='organizations_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Branch(models.Model):
    TYPE_HEADQUARTERS = 'headquarters'
    TYPE_REGIONAL     = 'regional'
    TYPE_BRANCH       = 'branch'
    TYPE_REMOTE       = 'remote'
    TYPE_FACTORY      = 'factory'
    TYPE_WAREHOUSE    = 'warehouse'

    TYPE_CHOICES = [
        (TYPE_HEADQUARTERS, 'Headquarters'),
        (TYPE_REGIONAL,     'Regional Office'),
        (TYPE_BRANCH,       'Branch Office'),
        (TYPE_REMOTE,       'Remote'),
        (TYPE_FACTORY,      'Factory'),
        (TYPE_WAREHOUSE,    'Warehouse'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='branches',
    )
    name        = models.CharField(max_length=255)
    code        = models.CharField(max_length=20, blank=True)
    branch_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_BRANCH)

    email   = models.EmailField(blank=True)
    phone   = models.CharField(max_length=30, blank=True)

    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city          = models.CharField(max_length=100, blank=True)
    state         = models.CharField(max_length=100, blank=True)
    country       = models.CharField(max_length=100, blank=True)
    postal_code   = models.CharField(max_length=20, blank=True)
    timezone      = models.CharField(max_length=64, blank=True)

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='managed_branches',
    )
    opened_on = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['organization', 'name']
        unique_together = ('organization', 'code')

    def __str__(self):
        return f'{self.name} ({self.organization.name})'


class Holiday(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='holidays',
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='holidays',
        help_text='Leave blank for org-wide holiday',
    )
    name        = models.CharField(max_length=150)
    date        = models.DateField()
    is_recurring = models.BooleanField(default=False, help_text='Repeats every year on the same MM-DD')
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date']
        unique_together = ('organization', 'branch', 'date', 'name')

    def __str__(self):
        return f'{self.name} ({self.date})'


class WorkSchedule(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='work_schedules',
    )
    name       = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time   = models.TimeField()
    break_minutes = models.PositiveIntegerField(default=60)

    works_monday    = models.BooleanField(default=True)
    works_tuesday   = models.BooleanField(default=True)
    works_wednesday = models.BooleanField(default=True)
    works_thursday  = models.BooleanField(default=True)
    works_friday    = models.BooleanField(default=True)
    works_saturday  = models.BooleanField(default=False)
    works_sunday    = models.BooleanField(default=False)

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['organization', 'name']
        unique_together = ('organization', 'name')

    def __str__(self):
        return f'{self.name} ({self.organization.name})'


class OrganizationDocument(models.Model):
    TYPE_POLICY     = 'policy'
    TYPE_HANDBOOK   = 'handbook'
    TYPE_CONTRACT   = 'contract'
    TYPE_LICENSE    = 'license'
    TYPE_CERTIFICATE = 'certificate'
    TYPE_OTHER      = 'other'

    TYPE_CHOICES = [
        (TYPE_POLICY,      'Policy'),
        (TYPE_HANDBOOK,    'Handbook'),
        (TYPE_CONTRACT,    'Contract'),
        (TYPE_LICENSE,     'License'),
        (TYPE_CERTIFICATE, 'Certificate'),
        (TYPE_OTHER,       'Other'),
    ]

    organization  = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='documents',
    )
    title         = models.CharField(max_length=255)
    document_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_OTHER)
    file          = models.FileField(upload_to='organization/documents/')
    description   = models.TextField(blank=True)
    effective_date = models.DateField(null=True, blank=True)
    expiry_date    = models.DateField(null=True, blank=True)

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='organization_documents',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} [{self.document_type}]'


class SocialLink(models.Model):
    PLATFORM_CHOICES = [
        ('linkedin',  'LinkedIn'),
        ('twitter',   'Twitter / X'),
        ('facebook',  'Facebook'),
        ('instagram', 'Instagram'),
        ('youtube',   'YouTube'),
        ('github',    'GitHub'),
        ('other',     'Other'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='social_links',
    )
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    url      = models.URLField()

    class Meta:
        unique_together = ('organization', 'platform')

    def __str__(self):
        return f'{self.organization.name} - {self.platform}'
