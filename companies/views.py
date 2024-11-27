from django.utils.translation import gettext as _
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from companies.models import Company
from companies.permissions import IsOwnerOrReadOnly
from companies.serializers import CompanyListSerializer
from companies.serializers import CompanySerializer

# Create your views here.



class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        try:
            if self.action in ['list', 'retrieve']:
                return self.queryset.filter(is_visible=True)
            return self.queryset.filter(owner=self.request.user)
        except Exception as e:
            error_message = _("Failed to retrieve the company list: %s") % str(e)
            raise PermissionDenied(error_message) from e

    def get_serializer_class(self):
        try:
            if self.action == "list":
                return CompanyListSerializer
            return CompanySerializer
        except Exception as e:
            error_message = _("Failed to determine serializer: %s") % str(e)
            raise PermissionDenied(error_message) from e

    def perform_create(self, serializer):
        try:
            serializer.save(owner=self.request.user)
        except Exception as e:
            error_message = _("Failed to create company: %s") % str(e)
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)
