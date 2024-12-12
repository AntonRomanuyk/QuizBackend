from django.utils.translation import gettext as _
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from companies.choices import RequestStatus
from companies.models import Company
from companies.models import CompanyRequest
from companies.permissions import IsNotCompanyMember
from companies.permissions import IsNotCompanyOwner
from companies.permissions import IsObjectOwnerOrReadOnly
from companies.permissions import IsOwnerOrReadOnly
from companies.serializers import CompanyRequestListSerializer
from companies.serializers import CompanyRequestSerializer


class CompanyRequestViewSet(viewsets.ModelViewSet):
    queryset = CompanyRequest.objects.all()
    serializer_class = CompanyRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]


    def get_serializer_class(self):
        try:
            if self.action == "list":
                return CompanyRequestListSerializer
            return CompanyRequestSerializer
        except Exception as e:
            error_message = _("Failed to determine serializer: %s") % str(e)
            raise PermissionDenied(error_message) from e

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_requests(self, request):
        requests = CompanyRequest.objects.filter(user=request.user)
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        company_request = self.get_object()

        if company_request.status != RequestStatus.PENDING.name:
            return Response({"error": _("This request is not pending.")}, status=status.HTTP_400_BAD_REQUEST)

        company_request.status = RequestStatus.APPROVED.name
        company_request.company.members.add(company_request.user)
        company_request.save()

        return Response({"status": _("The request has been approved.")}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        company_request = self.get_object()

        if company_request.status != RequestStatus.PENDING.name:
            return Response({"error": _("This request is not pending.")}, status=status.HTTP_400_BAD_REQUEST)

        company_request.status = RequestStatus.REJECTED.name
        company_request.save()

        return Response({"status": _("The request has been rejected.")}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated,
                                                                IsNotCompanyMember, IsNotCompanyOwner])
    def send_request(self, request):
        company_id = request.data.get("company_id")
        if not company_id:
            return Response({"error": _("Company ID is required.")}, status=status.HTTP_400_BAD_REQUEST)

        try:
            company = Company.objects.get(pk=company_id)
        except Company.DoesNotExist:
            return Response({"error": _("Company not found.")}, status=status.HTTP_404_NOT_FOUND)

        if CompanyRequest.objects.filter(company=company, user=request.user,
                                         status=RequestStatus.PENDING.name).exists():
            return Response({"error": _("You already have a pending request for this company.")},
                            status=status.HTTP_400_BAD_REQUEST)

        CompanyRequest.objects.create(company=company, user=request.user, status=RequestStatus.PENDING.name)
        return Response({"status": _("Request sent successfully.")}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsObjectOwnerOrReadOnly])
    def cancel(self, request, pk=None):

        company_request = self.get_object()

        if company_request.status != RequestStatus.PENDING.name:
            return Response({"error": _("Only pending requests can be canceled.")}, status=status.HTTP_400_BAD_REQUEST)

        company_request.status = RequestStatus.CANCELED.name
        company_request.save()

        return Response({"status": _("Request canceled successfully.")}, status=status.HTTP_200_OK)
