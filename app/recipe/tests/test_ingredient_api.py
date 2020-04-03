from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient, Recipe
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientAPITest(TestCase):
    """Tests public available ingredients APIs."""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Tests login is required to access the endpoint."""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITest(TestCase):
    """Tests private ingredients APIs."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'Test123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        """Tests retrieving a list of ingredients."""

        Ingredient.objects.create(user=self.user, name='abóbra')
        Ingredient.objects.create(user=self.user, name='tangerina')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Tests listing ingredients for authenticated user only."""

        user2 = get_user_model().objects.create_user(
            'other@test.com',
            'Test321'
        )

        Ingredient.objects.create(user=user2, name='cabotiá')
        ingredient = Ingredient.objects.create(user=self.user, name='limão')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        """Tests creating a new ingredient."""
        payload = {'name': 'cenoura'}
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Tests creating invalid ingredient."""
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """Tests filtering ingredients assigned to recipes."""
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='ingredient 1'
        )
        ingredient2 = Ingredient.objects.create(
            user=self.user,
            name='ingredient 2'
        )
        recipe = Recipe.objects.create(
            user=self.user,
            title='recipe 1',
            time_minutes=1,
            price=1.00
        )
        recipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredients_assigned_unique(self):
        """Tests retrieving one instance of ingredient when its assigned to \
            more than one recipe."""
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='ingredient 1'
        )
        Ingredient.objects.create(
            user=self.user,
            name='ingredient 2'
        )
        recipe1 = Recipe.objects.create(
            user=self.user,
            title='recipe 1',
            time_minutes=1,
            price=1.00
        )
        recipe1.ingredients.add(ingredient)
        recipe2 = Recipe.objects.create(
            user=self.user,
            title='recipe 2',
            time_minutes=1,
            price=1.00
        )
        recipe2.ingredients.add(ingredient)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
