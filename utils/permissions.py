ADMIN_ROLES = ('admin', 'hr_manager')


def is_admin(user):
    """Return True if the user has admin or hr_manager role."""
    role = getattr(user, 'role', None)
    return bool(role and role.name in ADMIN_ROLES)


def has_role(user, *roles):
    """Return True if the user's role matches any of the given role names."""
    role = getattr(user, 'role', None)
    return bool(role and role.name in roles)
