from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag, Recipe
from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class PublicTagsAPITest(TestCase):
    """Tests the public available tag APIs."""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Tests tjat login is required for listing tags."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITest(TestCase):
    """Tests authorized user tag APIs."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'Test123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Tests retrieving tags."""
        Tag.objects.create(user=self.user, name='pocoyo')
        Tag.objects.create(user=self.user, name='top')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Tests that tags listed is limited to authenticated user."""
        user2 = get_user_model().objects.create_user(
            'other@test.com',
            'Test321'
        )

        Tag.objects.create(user=user2, name='pocoyo')
        Tag.objects.create(user=self.user, name='top')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], 'top')

    def test_create_tag_succesful(self):
        """Tests creating a new tag."""
        payload = {'name': 'test tag'}

        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user, name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_invalid_tag(self):
        """Tests creating a invalid tag."""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        """Tests filtering tags assigned to recipes."""
        tag1 = Tag.objects.create(user=self.user, name='tag 1')
        tag2 = Tag.objects.create(user=self.user, name='tag 2')
        recipe = Recipe.objects.create(
            user=self.user,
            title='recipe 1',
            time_minutes=1,
            price=1.00
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        """Tests retrieving one instance of tag when its assigned to \
            more than one recipe."""
        tag = Tag.objects.create(user=self.user, name='tag 1')
        Tag.objects.create(user=self.user, name='tag 2')
        recipe1 = Recipe.objects.create(
            user=self.user,
            title='recipe 1',
            time_minutes=1,
            price=1.00
        )
        recipe1.tags.add(tag)
        recipe2 = Recipe.objects.create(
            user=self.user,
            title='recipe 2',
            time_minutes=1,
            price=1.00
        )
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
