
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from companies.choices import RequestStatus
from companies.models import Company
from companies.models import CompanyRequest

User = get_user_model()

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
        self.client.force_authenticate(user=None)


    def test_send_request(self):
        self.client.force_authenticate(user=self.another_user)
        url = reverse('company-requests-send-request')
        data = {'company_id': self.company.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        request_exists = CompanyRequest.objects.filter(company=self.company, user=self.another_user,
                                                       status=RequestStatus.PENDING.name).exists()
        self.assertTrue(request_exists)
        self.client.force_authenticate(user=None)

    def test_cancel_request_with_invalid_status(self):
        company_request = CompanyRequest.objects.create(
            company=self.company,
            user=self.another_user,
            status=RequestStatus.APPROVED.name
        )
        self.client.force_authenticate(user=self.another_user)
        url = reverse('company-requests-cancel', kwargs={'pk': company_request.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Only pending requests can be canceled.", response.data['error'])
        self.client.force_authenticate(user=None)

    def test_cancel_request(self):
        company_request = CompanyRequest.objects.create(company=self.company, user=self.another_user,
                                                        status=RequestStatus.PENDING.name)
        self.client.force_authenticate(user=self.another_user)
        url = reverse('company-requests-cancel', kwargs={'pk': company_request.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        company_request.refresh_from_db()
        self.assertEqual(company_request.status, RequestStatus.CANCELED.name)
        self.client.force_authenticate(user=None)
