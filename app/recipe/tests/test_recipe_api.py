from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPE_URLS = reverse('recipe:recipe-list')


def sample_tag(user, name='sample tag'):
    """Creates and returns a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='sample ingredient'):
    """Creates and returns a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def generate_recipe_detail_url(recipe_id):
    """Generates recipe detail url for given id."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_recipe(user, **params):
    """Creates and return a sample recipe"""
    defaults = {
        'title': 'sample recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeAPITest(TestCase):
    """Tests unauthenticated recipe APIs."""

    def setUp(self):
        self.client = APIClient()

    def test_authentication_required(self):
        """Tests that authentication is required."""
        res = self.client.get(RECIPE_URLS)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITest(TestCase):
    """Tests authenticated recipe APIs."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'Test123'
        )
        self.client.force_authenticate(self.user)

    def test_retrive_recipes(self):
        """Tests retrieving a list of recipes."""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URLS)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Tests retrieving recipes for user."""
        user2 = get_user_model().objects.create_user(
            'other@test.com',
            'Test123'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URLS)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Tests viewing a recipe detail."""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))
        url = generate_recipe_detail_url(recipe.id)

        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
