from django.test import TestCase

from .models import User


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")

    def test_user_creation(self):
        self.assertEqual(self.user.username, "testuser")

    def test_user_update(self):
        self.user.username = "updateduser"
        self.user.save()
        self.assertEqual(self.user.username, "updateduser")

    def test_user_deletion(self):
        self.user.delete()
        self.assertFalse(User.objects.filter(username="testuser").exists())
