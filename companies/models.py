from django.conf import settings
from django.db import models

from companies.choices import InvitationStatus
from companies.choices import RequestStatus
from core.models import TimeStampedModel


# Create your models here.
class Company(TimeStampedModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='companies_owner'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_visible = models.BooleanField(default=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="companies_members",
    )

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name

class CompanyInvitation(TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="invitations_company")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="invitations_user")
    status = models.CharField(max_length=20, choices=[(tag.name, tag.value) for tag in InvitationStatus],
                              default=InvitationStatus.PENDING.name)

    class Meta:
        verbose_name = "Company Invitation"
        verbose_name_plural = "Company Invitations"

class CompanyRequest(TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="requests_company")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="requests_user")
    status = models.CharField(max_length=20, choices=[(tag.name, tag.value) for tag in RequestStatus],
                              default=RequestStatus.PENDING.name)

    class Meta:
        verbose_name = "Company Request"
        verbose_name_plural = "Company Requests"

