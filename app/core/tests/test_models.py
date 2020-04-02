from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models
from unittest.mock import patch


def sample_user(email='test@test.com', password='Test123'):
    """Creates a sample user."""
    return get_user_model().objects.create_user(email, password)


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

    def test_tag_str(self):
        """Tests tag string representation."""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='top'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Tests ingredient string representation."""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Geléia de Mocotó'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Tests recipe string representation."""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='My recipe',
            time_minutes=5,
            price=5.00
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_filename_uuid(self, mock_uuid):
        """Tests that image is saved at correct location."""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'my-image.jpg')

        expected_path = f'uploads/recipe/{uuid}.jpg'

        self.assertEqual(file_path, expected_path)
