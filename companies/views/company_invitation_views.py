from django.utils.translation import gettext as _
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from companies.choices import InvitationStatus
from companies.models import Company
from companies.models import CompanyInvitation
from companies.permissions import IsNotCompanyMember
from companies.permissions import IsNotCompanyOwner
from companies.permissions import IsObjectOwnerOrReadOnly
from companies.permissions import IsOwnerOrReadOnly
from companies.serializers import CompanyInvitationListSerializer
from companies.serializers import CompanyInvitationSerializer


class CompanyInvitationViewSet(viewsets.ModelViewSet):
    queryset = CompanyInvitation.objects.all()
    serializer_class = CompanyInvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        try:
            if self.action == "list":
                return CompanyInvitationListSerializer
            return CompanyInvitationSerializer
        except Exception as e:
            error_message = _("Failed to determine serializer: %s") % str(e)
            raise PermissionDenied(error_message) from e

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def received(self, request):
        invitations = CompanyInvitation.objects.filter(user=request.user)
        serializer = self.get_serializer(invitations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly])
    def sent(self, request, pk=None):
        company = self.get_object().company
        invitations = CompanyInvitation.objects.filter(company=company)
        serializer = self.get_serializer(invitations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly])
    def send_invitation(self, request):
        company_id = request.data.get("company_id")
        user_id = request.data.get("user_id")

        if not company_id or not user_id:
            return Response({"error": _("Company ID and User ID are required.")}, status=status.HTTP_400_BAD_REQUEST)

        company = Company.objects.get(pk=company_id, owner=request.user)

        if company.members.filter(pk=user_id).exists():
            return Response({"error": _("This user is already a member of the company.")},
                            status=status.HTTP_400_BAD_REQUEST)

        if CompanyInvitation.objects.filter(company=company, user_id=user_id,
                                            status=InvitationStatus.PENDING.name).exists():
            return Response({"error": _("An invitation is already pending for this user.")},
                            status=status.HTTP_400_BAD_REQUEST)

        CompanyInvitation.objects.create(company=company, user_id=user_id, status=InvitationStatus.PENDING.name)
        return Response({"status": _("Invitation sent successfully.")}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly])
    def revoke_invitation(self, request, pk=None):
        invitation = self.get_object()

        if invitation.status != InvitationStatus.PENDING.name:
            return Response({"error": _("Only pending invitations can be revoked.")},
                            status=status.HTTP_400_BAD_REQUEST)

        invitation.status = InvitationStatus.REVOKED.name
        invitation.save()

        return Response({"status": _("Invitation revoked successfully.")}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsNotCompanyMember,
                                                               IsNotCompanyOwner, IsObjectOwnerOrReadOnly])
    def accept(self, request, pk=None):
        invitation = self.get_object()

        if invitation.status != InvitationStatus.PENDING.name:
            return Response({"error": _("Only pending invitations can be accepted.")},
                            status=status.HTTP_400_BAD_REQUEST)
        print(request.user)
        print(":accept user124")
        invitation.company.members.add(request.user)
        invitation.status = InvitationStatus.ACCEPTED.name
        invitation.save()

        return Response({"status": _("Invitation accepted successfully.")}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsObjectOwnerOrReadOnly])
    def decline(self, request, pk=None):
        invitation = self.get_object()

        if invitation.status != InvitationStatus.PENDING.name:
            return Response({"error": _("Only pending invitations can be declined.")},
                            status=status.HTTP_400_BAD_REQUEST)

        invitation.status = InvitationStatus.DECLINED.name
        invitation.save()

        return Response({"status": _("Invitation declined successfully.")}, status=status.HTTP_200_OK)
