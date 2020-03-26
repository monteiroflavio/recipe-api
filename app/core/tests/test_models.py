from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Tests creating a new user with email is successful."""
        email = 'test@test.com'
        password = 'Testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Tests that the email for a new user is normalized."""
        email = 'test@TEST.COM'
        user = get_user_model().objects.create_user(email)

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Tests creating user with no email raises error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None)

    def test_create_new_super_user(self):
        """Tests creating a new super user"""
        user = get_user_model().objects.create_superuser(
            'test@test.com',
            'Test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
