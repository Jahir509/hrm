"""
First-time setup endpoint.

`POST /api/v1/organizations/bootstrap/` is the only way to seed an HRM
deployment from a completely empty database. It is intentionally open
(no auth) — and intentionally one-shot. Once any `Organization` row
exists, the endpoint refuses with 409 Conflict.

A successful request:

1. Creates (or fetches) the `admin` Role.
2. Creates the first admin Employee with the supplied credentials.
3. Creates the primary Organization with `is_primary=True` and
   `created_by=<the new admin>`.
4. Returns a fresh JWT pair, ready for the frontend to drop into
   `localStorage` so the user lands logged-in on the dashboard.

Everything happens inside a single `transaction.atomic()` block, so a
failure on step 3 rolls back the Employee created on step 2.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Role
from accounts.rbac import rbac

from .models import Organization
from .serializers import OrganizationSerializer


Employee = get_user_model()

ADMIN_FIELDS = (
    'admin_username',
    'admin_email',
    'admin_password',
    'admin_first_name',
    'admin_last_name',
)


class _AdminAccountSerializer(serializers.Serializer):
    """Validates only the admin-account half of the bootstrap payload."""

    username   = serializers.CharField(max_length=150)
    email      = serializers.EmailField()
    password   = serializers.CharField(min_length=8, write_only=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name  = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def validate_username(self, value):
        if Employee.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('That username is already taken.')
        return value

    def validate_email(self, value):
        if Employee.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('That email is already registered.')
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value


def _issue_tokens(user):
    """Return a JWT pair with the extra claims our frontend reads."""
    refresh = RefreshToken.for_user(user)
    refresh['role']       = getattr(getattr(user, 'role', None), 'name', '') or ''
    refresh['given_name'] = user.first_name or user.username
    access = refresh.access_token
    access['role']       = refresh['role']
    access['given_name'] = refresh['given_name']
    return {'access': str(access), 'refresh': str(refresh)}


@rbac(['POST'], public=True)
def bootstrap_organization(request):
    # One-shot: refuse once the tenant has been set up.
    if Organization.objects.exists():
        return Response(
            {'detail': 'Organization bootstrap has already been completed.'},
            status=status.HTTP_409_CONFLICT,
        )

    data = request.data

    # Pull the admin fields out of the (otherwise flat) payload.
    admin_payload = {
        'username':   data.get('admin_username'),
        'email':      data.get('admin_email'),
        'password':   data.get('admin_password'),
        'first_name': data.get('admin_first_name', ''),
        'last_name':  data.get('admin_last_name', ''),
    }
    admin_serializer = _AdminAccountSerializer(data=admin_payload)
    admin_serializer.is_valid(raise_exception=True)

    # Build the org payload from the remaining keys. QueryDict is multi-valued,
    # so we have to copy it before mutating.
    org_data = data.copy() if hasattr(data, 'copy') else dict(data)
    for field in ADMIN_FIELDS:
        org_data.pop(field, None)
    org_data['is_primary'] = True

    with transaction.atomic():
        role, _ = Role.objects.get_or_create(name='admin')

        admin = Employee.objects.create(
            username=admin_serializer.validated_data['username'],
            email=admin_serializer.validated_data['email'],
            first_name=admin_serializer.validated_data.get('first_name', ''),
            last_name=admin_serializer.validated_data.get('last_name', ''),
            role=role,
            is_staff=True,
            is_superuser=True,
        )
        admin.set_password(admin_serializer.validated_data['password'])
        admin.save()

        # Mimic an authenticated request for the org serializer's `created_by` hook.
        request.user = admin

        org_serializer = OrganizationSerializer(data=org_data, context={'request': request})
        if not org_serializer.is_valid():
            # Forces the atomic block to roll back the Employee we just created.
            raise serializers.ValidationError(org_serializer.errors)
        org_serializer.save()

    return Response(
        {
            'organization': org_serializer.data,
            'admin': {
                'id':         admin.id,
                'username':   admin.username,
                'email':      admin.email,
                'first_name': admin.first_name,
                'last_name':  admin.last_name,
                'role':       role.name,
            },
            'tokens': _issue_tokens(admin),
        },
        status=status.HTTP_201_CREATED,
    )
