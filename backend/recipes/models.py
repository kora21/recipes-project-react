from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Теги для рецептов"""
    name = models.CharField(max_length=64, verbose_name="Тэг", unique=True)
    colour = models.CharField(
        verbose_name="Цвет",
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name="Слаг тэга",
        max_length=256,
        unique=True,
    )

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингридиенты для рецепта"""
    name = models.CharField(
        verbose_name="Ингридиент",
        max_length=256,
    )
    measurement_unit = models.CharField(
        verbose_name="Единицы измерения",
        max_length=24,
    )

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецепта"""
    name = models.CharField(verbose_name="Название блюда", max_length=256)
    text = models.TextField(
        verbose_name="Описание блюда",
        max_length=256
    )
    author = models.ForeignKey(
        User,
        related_name="recipes",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Автор рецепта"
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="Тег"
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientRecipe",
        related_name='recipes',
        verbose_name="Ингредиенты блюда"
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
        editable=False,
    )
    image = models.ImageField(
        verbose_name="Изображение блюда",
        upload_to="recipe/",
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        default=0,
        validators=[
            MinValueValidator(1, message='Минимальное значение 1!')])

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-pub_date",)

    def __str__(self) -> str:
        return f"{self.name}. Автор: {self.author.username}"


class IngredientRecipe(models.Model):
    """Количество ингридиентов в блюде."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredient",
        verbose_name="В каких рецептах"
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipe",
        verbose_name="Связанные ингредиенты"
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество",
        default=0,
        validators=[
            MinValueValidator(1, message='Минимальное количество 1!')]
    )

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Количество ингридиентов"
        ordering = ("recipe",)

    def __str__(self):
        return f"{self.amount} {self.ingredient}"


class Favorite(models.Model):
    """Избранные рецепты."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="in_favorites",
        verbose_name="Избранные рецепты",
    )
    date_added = models.DateTimeField(
        verbose_name="Дата добавления", auto_now_add=True, editable=False
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"

    def __str__(self) -> str:
        return f"{self.user} -> {self.recipe}"


class Shopping_cart(models.Model):
    """Рецепты в корзине покупок."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="in_shopping_cart",
        verbose_name="Рецепты в списке покупок",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="in_shopping_cart",
        verbose_name="Владелец списка покупок",
    )
    date_added = models.DateTimeField(
        verbose_name="Дата добавления", auto_now_add=True, editable=False
    )

    class Meta:
        verbose_name = "Рецепт в списке покупок"
        verbose_name_plural = "Рецепты в списке покупок"

    def __str__(self) -> str:
        return f"{self.user} -> {self.recipe}"
