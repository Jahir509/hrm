from functools import wraps
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status


def rbac(methods=None, roles=None, perm=None, public=False):
    """
    Single decorator replacing @api_view + @permission_classes + role/permission checks.

    Usage:
        @rbac(['GET', 'POST'])                    # login required
        @rbac(['GET'], public=True)               # no auth
        @rbac(['GET'], roles=['admin'])            # login + role
        @rbac(['GET'], perm='department.view')    # login + permission codename
    """
    if methods is None:
        methods = ['GET']

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not public:
                if not request.user or not request.user.is_authenticated:
                    return Response(
                        {'detail': 'Authentication credentials were not provided.'},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )

                if roles:
                    user_role = getattr(request.user, 'role', None)
                    if not user_role or user_role.name not in roles:
                        return Response(
                            {'detail': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN,
                        )

                if perm:
                    user_role = getattr(request.user, 'role', None)
                    if not user_role or not user_role.has_perm(perm):
                        return Response(
                            {'detail': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN,
                        )

            return view_func(request, *args, **kwargs)

        perms = [AllowAny] if public else [IsAuthenticated]
        return api_view(methods)(permission_classes(perms)(wrapper))

    return decorator
