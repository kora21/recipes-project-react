from django.contrib.auth import get_user_model
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Ingredient, IngredientRecipe, Recipe,
                            Subscriptions, Tag)
from rest_framework import serializers

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор для использования с моделью User."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        """Проверка подписки пользователей."""
        user = self.context.get('request').user

        return not (user.is_anonymous or (user == obj)) and \
            Subscriptions.objects.filter(user=user, author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """ Сериализатор создания пользователя. """

    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        ]


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class UserSubscribeSerializer(CustomUserSerializer):
    """Сериализатор вывода авторов на которых подписан текущий пользователь."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        read_only_fields = ('email', 'username')

    def get_is_subscribed(self, obj):
        """Проверка подписки пользователей."""
        request = self.context.get('request')
        return not (not request or request.user.is_anonymous) and \
            Subscriptions.objects.filter(user=self.context.get(
                                         'request').user, author=obj).exists()

    def get_recipes(self, obj):
        recipe_objects = obj.recipes.all()
        recipe_serializer = RecipeShortSerializer(
            recipe_objects,
            many=True)
        return recipe_serializer.data

    def get_recipes_count(self, obj):
        """Показывает общее количество рецептов у каждого автора."""
        return obj.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Tag"""
    class Meta:
        model = Tag
        fields = "__all__"
        read_only_fields = ("__all__",)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Ingredient"""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', )


class IngredientRecipeSerealizer(serializers.ModelSerializer):
    """Сериалайзер для модели Ингридиентов и Блюд"""
    id = serializers.IntegerField()
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецепта"""
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    name = serializers.CharField(required=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('tags', 'ingredients', 'author', 'id',
                  'name', 'image', 'text', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart')

    def get_ingredients(self, obj):
        """Получает список ингридиентов для рецепта"""
        ingredients = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientRecipeSerealizer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        """Проверка - находится ли рецепт в избранном."""
        user = self.context.get('request').user
        return not user.is_anonymous and Recipe.objects.filter(
            in_favorites__user=user, id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверка - находится ли рецепт в списке  покупок."""
        user = self.context.get('request').user
        return not user.is_anonymous and Recipe.objects.filter(
            in_shopping_cart__user=user, id=obj.id).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создание модели рецепта"""
    ingredients = IngredientRecipeSerealizer(many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    author = CustomUserSerializer(read_only=True,
                                  default=serializers.CurrentUserDefault(
                                  ))
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('tags', 'ingredients', 'author', 'id',
                  'name', 'image', 'text', 'cooking_time')

    @staticmethod
    def add_list_ingredients(ingredients, recipe):
        """Создание списка ингридиентов для рецепта."""
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient.get('amount'),
                recipe=recipe
            )

    @transaction.atomic
    def create(self, validated_data):
        """Создает рецепт"""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.add_list_ingredients(recipe=recipe,
                                  ingredients=ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновляет рецепт"""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.add_list_ingredients(recipe=instance,
                                  ingredients=ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance,
                                    context=context).data
