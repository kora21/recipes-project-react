from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Foodgram модель пользователя."""

    email = models.EmailField(
        verbose_name="Адрес электронной почты",
        max_length=254,
        unique=True
    )
    username = models.CharField(
        verbose_name="Уникальный юзернейм",
        max_length=56,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=154,
        blank=True
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=154,
        blank=True
    )
    password = models.CharField(
        verbose_name=("Пароль"),
        max_length=150,
        null=True
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

    def __str__(self) -> str:
        return f"{self.username}: {self.email}"


class Subscriptions(models.Model):
    """Подписки пользователей друг на друга."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriber",
        verbose_name="Автор рецепта",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribing",
        verbose_name="Подписчик на автора",
    )
    date_added = models.DateTimeField(
        verbose_name="Дата создания подписки",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self) -> str:
        return f"{self.user.username} -> {self.author.username}"
