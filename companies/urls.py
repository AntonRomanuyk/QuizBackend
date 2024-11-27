from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from companies.views import CompanyViewSet

router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')

urlpatterns = [
    path("", include(router.urls)),
]
