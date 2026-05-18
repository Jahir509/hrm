from django.contrib import admin
from .models import (
    Organization,
    Branch,
    Holiday,
    WorkSchedule,
    OrganizationDocument,
    SocialLink,
)


class BranchInline(admin.TabularInline):
    model = Branch
    extra = 0
    fields = ('name', 'code', 'branch_type', 'city', 'country', 'is_active')


class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 0


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display  = ('id', 'name', 'organization_type', 'size', 'status', 'country', 'is_primary')
    list_filter   = ('organization_type', 'size', 'status', 'is_primary', 'country')
    search_fields = ('name', 'legal_name', 'registration_number', 'tax_id', 'email')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    inlines = [SocialLinkInline, BranchInline]


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display  = ('id', 'name', 'organization', 'branch_type', 'city', 'country', 'is_active')
    list_filter   = ('branch_type', 'is_active', 'country')
    search_fields = ('name', 'code', 'city')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display  = ('id', 'name', 'date', 'organization', 'branch', 'is_recurring')
    list_filter   = ('is_recurring', 'organization')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    list_display  = ('id', 'name', 'organization', 'start_time', 'end_time', 'is_default')
    list_filter   = ('is_default', 'organization')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(OrganizationDocument)
class OrganizationDocumentAdmin(admin.ModelAdmin):
    list_display  = ('id', 'title', 'organization', 'document_type', 'effective_date', 'expiry_date')
    list_filter   = ('document_type', 'organization')
    search_fields = ('title', 'description')
    readonly_fields = ('uploaded_by', 'created_at', 'updated_at')


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display  = ('id', 'organization', 'platform', 'url')
    list_filter   = ('platform',)
