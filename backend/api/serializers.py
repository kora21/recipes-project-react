from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag
from users.models import Subscriptions

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для использования с моделью User."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "password",
        )
        read_only_fields = ("is_subscribed",)

    def get_is_subscribed(self, obj):
        """Проверка подписки пользователей."""
        user = self.context.get("request").user
        if user.is_anonymous or (user == obj):
            return False
        return Subscriptions.objects.filter(user=user, author=obj).exists()

    def create(self, validated_data):
        """Создаёт нового пользователя с запрошенными полями."""
        user = User(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class UserSubscribeSerializer(UserSerializer):
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

    def get_is_subscribed(*args) -> bool:
        """Проверка подписки пользователей."""
        return True

    def get_recipes_count(self, obj):
        """Показывает общее количество рецептов у каждого автора."""
        return obj.recipes.count()

    def get_recipes(self, obj):
        from .serializers import RecipeShortSerializer
        recipe_objects = obj.recipes.all()
        recipe_serializer = RecipeShortSerializer(
            recipe_objects,
            many=True)
        return recipe_serializer.data


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
        fields = "__all__"
        read_only_fields = ("__all__",)


class IngredientRecipeSerealizer(serializers.ModelSerializer):
    """Сериалайзер для модели Ингридиентов и Блюд"""
    id = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецепта"""
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerealizer(many=True)
    # name = serializers.CharField(required=True)
    image = Base64ImageField()
    # text = serializers.CharField(required=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('tags', 'ingredients', 'author', 'id',
                  'name', 'image', 'text', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        """Проверка - находится ли рецепт в избранном."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(in_favorites__user=user,
                                     id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверка - находится ли рецепт в списке  покупок."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(in_shopping_cart__user=user,
                                     id=obj.id).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создание модели рецепта"""
    ingredients = IngredientRecipeSerealizer(many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    author = UserSerializer(read_only=True,
                            default=serializers.CurrentUserDefault(
                            ))
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('tags', 'ingredients', 'author', 'id',
                  'name', 'image', 'text', 'cooking_time')

    def add_list_ingredients(self, ingredients, recipe):
        """Создание списка ингридиентов для рецепта."""
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient.get('amount'),
                recipe=recipe
            )

    def create(self, validated_data):
        """Создает рецепт"""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.add_list_ingredients(recipe=recipe,
                                  ingredients=ingredients)
        return recipe

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
