
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from companies.choices import InvitationStatus
from companies.models import Company
from companies.models import CompanyInvitation

User = get_user_model()

class CompanyInvitationViewSetTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='pass')
        self.member = User.objects.create_user(username='member', password='pass')
        self.non_member = User.objects.create_user(username='non_member', password='pass')

        self.company = Company.objects.create(name='Test Company', owner=self.user,
                                              description='description', is_visible=True)
        self.company.members.add(self.member)

        self.client = APIClient()

    def test_received_invitations(self):
        self.client.force_authenticate(user=self.member)
        url = reverse('company-invitations-received')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.force_authenticate(user=None)

    def test_sent_invitations(self):
        invitation = CompanyInvitation.objects.create(
            company=self.company,
            user=self.non_member,
            status=InvitationStatus.PENDING.name
        )
        self.client.force_authenticate(user=self.user)
        url = reverse('company-invitations-sent', kwargs={'pk': self.company.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(invitation.id, [inv['id'] for inv in response.data])

    def test_send_invitation(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('company-invitations-send-invitation')
        data = {'company_id': self.company.id, 'user_id': self.non_member.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        invitation_exists = CompanyInvitation.objects.filter(company=self.company, user=self.non_member).exists()
        self.assertTrue(invitation_exists)
        self.client.force_authenticate(user=None)

    def test_send_invitation_to_member(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('company-invitations-send-invitation')
        data = {'company_id': self.company.id, 'user_id': self.member.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This user is already a member of the company", response.data['error'])
        self.client.force_authenticate(user=None)


    def test_accept_invitation(self):
        invitation = CompanyInvitation.objects.create(
            company=self.company,
            user=self.non_member,
            status=InvitationStatus.PENDING.name
        )
        self.client.force_authenticate(user=self.non_member)
        url = reverse('company-invitations-accept', kwargs={'pk': invitation.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, InvitationStatus.ACCEPTED.name)
        self.client.force_authenticate(user=None)

    def test_accept_non_pending_invitation(self):
        invitation = CompanyInvitation.objects.create(
            company=self.company,
            user=self.non_member,
            status=InvitationStatus.ACCEPTED.name
        )
        self.client.force_authenticate(user=self.non_member)
        url = reverse('company-invitations-accept', kwargs={'pk': invitation.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.client.force_authenticate(user=None)

    def test_decline_non_pending_invitation(self):
        invitation = CompanyInvitation.objects.create(
            company=self.company,
            user=self.non_member,
            status=InvitationStatus.REVOKED.name
        )
        self.client.force_authenticate(user=self.non_member)
        url = reverse('company-invitations-decline', kwargs={'pk': invitation.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.client.force_authenticate(user=None)

    def test_revoke_invitation_not_owner(self):
        invitation = CompanyInvitation.objects.create(
            company=self.company,
            user=self.non_member,
            status=InvitationStatus.PENDING.name
        )
        self.client.force_authenticate(user=self.non_member)
        url = reverse('company-invitations-revoke-invitation', kwargs={'pk': invitation.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=None)

    def test_revoke_pending_invitation(self):
        invitation = CompanyInvitation.objects.create(
            company=self.company,
            user=self.non_member,
            status=InvitationStatus.PENDING.name
        )
        self.client.force_authenticate(user=self.user)
        url = reverse('company-invitations-revoke-invitation', kwargs={'pk': invitation.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, InvitationStatus.REVOKED.name)
        self.client.force_authenticate(user=None)

    def test_revoke_non_pending_invitation(self):
        invitation = CompanyInvitation.objects.create(
            company=self.company,
            user=self.non_member,
            status=InvitationStatus.ACCEPTED.name
        )
        self.client.force_authenticate(user=self.user)
        url = reverse('company-invitations-revoke-invitation', kwargs={'pk': invitation.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.client.force_authenticate(user=None)

    def test_decline_invitation(self):
        invitation = CompanyInvitation.objects.create(
            company=self.company,
            user=self.non_member,
            status=InvitationStatus.PENDING.name
        )
        self.client.force_authenticate(user=self.non_member)
        url = reverse('company-invitations-decline', kwargs={'pk': invitation.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, InvitationStatus.DECLINED.name)
        self.client.force_authenticate(user=None)
