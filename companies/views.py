from django.utils.translation import gettext as _
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from companies.models import Company
from companies.serializers import CompanyListSerializer
from companies.serializers import CompanySerializer


# Create your views here.
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    permission_classes = [permissions.IsAuthenticated]

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

    def perform_update(self, serializer):
        try:
            if self.get_object().owner != self.request.user:
                error_message = _("You can only edit your own companies.")
                raise PermissionDenied(error_message)
            serializer.save()
        except PermissionDenied as e:
            raise e
        except Exception as e:
            error_message = _("Failed to update company: %s") % str(e)
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self, instance):
        try:
            if instance.owner != self.request.user:
                error_message = _("You can only delete your own companies.")
                raise PermissionDenied(error_message)
            instance.delete()
        except PermissionDenied as e:
            raise e
        except Exception as e:
            error_message = _("Failed to delete company: %s") % str(e)
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)
