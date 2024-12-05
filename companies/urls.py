from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from companies.company_invitation_views import CompanyInvitationViewSet
from companies.company_request_views import CompanyRequestViewSet
from companies.views import CompanyViewSet

router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'invitations', CompanyInvitationViewSet, basename='company-invitations')
router.register(r'requests', CompanyRequestViewSet, basename='company-requests')

urlpatterns = [
    path("", include(router.urls)),
]
