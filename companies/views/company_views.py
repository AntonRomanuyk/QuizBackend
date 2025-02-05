from django.utils.translation import gettext as _
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from companies.filters import CompanyFilter
from companies.models import Company
from companies.permissions import IsCompanyMember
from companies.permissions import IsOwnerOrReadOnly
from companies.serializers import CompanyListSerializer
from companies.serializers import CompanyRequestListSerializer
from companies.serializers import CompanySerializer
from quiz_users.serializers import CompanyUserSerializer

# Create your views here.



class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filterset_class = CompanyFilter

    def get_queryset(self):
        try:
            if self.action in ['list', 'retrieve']:
                return self.queryset.filter(is_visible=True)
            return self.queryset
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

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def perform_create(self, serializer):
        try:
            serializer.save(owner=self.request.user)
        except Exception as e:
            error_message = _("Failed to create company: %s") % str(e)
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def members(self, request, pk=None):
        company = self.get_object()
        members = company.members.all()
        return Response({'members': [member.username for member in members]})

    @action(detail=True, methods=['get'])
    def join_requests(self, request, pk=None):
        company = self.get_object()
        join_requests = company.requests_company.all()
        serializer = CompanyRequestListSerializer(join_requests, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def remove_user(self, request, pk=None):
        company = self.get_object()
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": _("User ID is required.")}, status=status.HTTP_400_BAD_REQUEST)

        if not company.members.filter(pk=user_id).exists():
            return Response({"error": _("User is not a member of this company.")}, status=status.HTTP_404_NOT_FOUND)

        user = company.members.get(pk=user_id)

        if user == company.owner:
            return Response({"error": _("You cannot remove the owner from the company.")},
                            status=status.HTTP_400_BAD_REQUEST)

        company.members.remove(user)

        return Response({"status": _(f"User {user.username} has been removed from the company.")},
                        status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated, IsCompanyMember],
    )
    def leave_company(self, request, pk=None):
        company = self.get_object()
        if request.user == company.owner:
            return Response({"error": _("You cannot remove the owner from the company.")},
                            status=status.HTTP_403_FORBIDDEN)
        company.members.remove(request.user)
        response = {"status": _("You have left the company.")}

        return Response(response, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def appoint_admin(self, request, pk=None):
        company = self.get_object()
        user_id = request.data.get('user_id')

        try:
            user = company.members.get(id=user_id)
        except company.members.model.DoesNotExist:
            return Response({"error": _("User not in company members.")}, status=status.HTTP_400_BAD_REQUEST)

        company.admins.add(user)
        return Response({"message": _(f"{user.username} is now an admin.")}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def remove_admin(self, request, pk=None):
        company = self.get_object()
        user_id = request.data.get('user_id')

        try:
            user = company.admins.get(id=user_id)
        except company.admins.model.DoesNotExist:
            return Response({"error": _("User is not an admin.")}, status=status.HTTP_400_BAD_REQUEST)

        company.admins.remove(user)
        return Response({"message": _(f"{user.username} is no longer an admin.")}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def list_admins(self, request, pk=None):
        company = self.get_object()
        admins = company.admins.only('id', 'username')
        serializer = CompanyUserSerializer(admins, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
