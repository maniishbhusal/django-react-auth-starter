"""URL overrides that replace djoser.urls + djoser.urls.jwt with throttled views."""

from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenVerifyView

from .djoser_views import (
    ThrottledTokenObtainPairView,
    ThrottledTokenRefreshView,
    ThrottledUserViewSet,
)

router = DefaultRouter()
router.register("users", ThrottledUserViewSet)

urlpatterns = [
    path("jwt/create/", ThrottledTokenObtainPairView.as_view(), name="jwt-create"),
    path("jwt/refresh/", ThrottledTokenRefreshView.as_view(), name="jwt-refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="jwt-verify"),
    *router.urls,
]
