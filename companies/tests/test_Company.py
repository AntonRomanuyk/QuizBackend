
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from companies.models import Company

User = get_user_model()

class CompanyViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.another_user = User.objects.create_user(username='anotheruser', password='password123')
        self.non_member_user = User.objects.create_user(username='nonmember1', password='pass1')
        self.company = Company.objects.create(name='Test Company', owner=self.user,
                                              description='description', is_visible=True)
        self.company.members.add(self.another_user)
        self.client = APIClient()



    def test_create_company(self):
        data = {
            'name': 'New Company'
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse('company-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client.force_authenticate(user=None)

    def test_get_company_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('company-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.client.force_authenticate(user=None)

    def test_view_company_members(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        url = reverse('company-members', kwargs={'pk': self.company.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn( self.another_user.username, response.data['members'])
        self.client.force_authenticate(user=None)

    def test_join_requests(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('company-join-requests', kwargs={'pk': self.company.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.force_authenticate(user=None)

    def test_remove_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('company-remove-user', kwargs={'pk': self.company.pk})
        response = self.client.post(url, {'user_id': self.another_user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.another_user, self.company.members.all())
        self.client.force_authenticate(user=None)

    def test_remove_non_member(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('company-remove-user', kwargs={'pk': self.company.pk})
        response = self.client.post(url, {'user_id': self.non_member_user.id})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.client.force_authenticate(user=None)

    def test_owner_leave_company(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('company-leave-company', kwargs={'pk': self.company.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=None)

    def test_leave_company(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.another_user)
        url = reverse('company-leave-company', kwargs={'pk': self.company.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.another_user, self.company.members.all())
        self.client.force_authenticate(user=None)