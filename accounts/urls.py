from django.urls import path
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from . import views


class HrmTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that injects extra claims the frontend reads
    (role, given_name) into both the access and refresh tokens. The plain
    `TokenObtainPairSerializer` only includes `user_id`, so without this
    override the frontend's role-based gating (e.g. who can approve
    leaves) always sees an empty role and locks out legitimate approvers.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = getattr(getattr(user, 'role', None), 'name', '') or ''
        token['given_name'] = user.first_name or user.username
        return token


class HrmTokenObtainPairView(TokenObtainPairView):
    serializer_class = HrmTokenObtainPairSerializer


urlpatterns = [
    path('token/',           HrmTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/',   TokenRefreshView.as_view(),       name='token_refresh'),
    path('token/verify/',    TokenVerifyView.as_view(),        name='token_verify'),
    path('me/',              views.me,                         name='auth-me'),
    # path('register/',        RegisterView.as_view(),           name='register'),
    # path('change-password/', ChangePasswordView.as_view(),     name='change_password'),
    # path('logout/',          LogoutView.as_view(),             name='logout'),
]