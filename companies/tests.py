from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from companies.choices import InvitationStatus
from companies.choices import RequestStatus
from companies.models import Company
from companies.models import CompanyInvitation
from companies.models import CompanyRequest

User = get_user_model()


class CompanyViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_authenticate(user=self.user)

        self.another_user = User.objects.create_user(username='anotheruser', password='password123')

        self.company = Company.objects.create(name='Test Company', owner=self.user)
        self.company.members.add(self.user)

    def test_create_company(self):
        data = {
            'name': 'New Company'
        }
        response = self.client.post(reverse('company-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_company_list(self):
        response = self.client.get(reverse('company-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_view_company_members(self):
        url = reverse('company-members', kwargs={'pk': self.company.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('testuser', response.data['members'])

    def test_remove_user_from_company(self):
        self.company.members.add(self.another_user)
        url = reverse('company-remove-user', kwargs={'pk': self.company.pk})
        response = self.client.post(url, {'user_id': self.another_user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.another_user, self.company.members.all())


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

    def test_send_invitation(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('company-invitations-send-invitation')
        data = {'company_id': self.company.id, 'user_id': self.non_member.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        invitation_exists = CompanyInvitation.objects.filter(company=self.company, user=self.non_member).exists()
        self.assertTrue(invitation_exists)

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




class CompanyRequestViewSetTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='pass')
        self.another_user = User.objects.create_user(username='requester', password='pass')

        self.company = Company.objects.create(name='Test Company', owner=self.user,
                                              description='description', is_visible=True)
        self.client = APIClient()

    def test_my_requests(self):
        CompanyRequest.objects.create(company=self.company, user=self.another_user, status=RequestStatus.PENDING.name)
        self.client.force_authenticate(user=self.another_user)
        url = reverse('company-requests-my-requests')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_send_request(self):
        self.client.force_authenticate(user=self.another_user)
        url = reverse('company-requests-send-request')
        data = {'company_id': self.company.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        request_exists = CompanyRequest.objects.filter(company=self.company, user=self.another_user,
                                                       status=RequestStatus.PENDING.name).exists()
        self.assertTrue(request_exists)





    def test_cancel_request(self):
        company_request = CompanyRequest.objects.create(company=self.company, user=self.another_user,
                                                        status=RequestStatus.PENDING.name)
        self.client.force_authenticate(user=self.another_user)
        url = reverse('company-requests-cancel', kwargs={'pk': company_request.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        company_request.refresh_from_db()
        self.assertEqual(company_request.status, RequestStatus.CANCELED.name)
