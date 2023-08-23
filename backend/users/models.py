from django.contrib.auth.models import AbstractUser
from django.db import models
from users.consts import MAX_LEN_FIELD, MAX_LEN_USERS


class User(AbstractUser):
    """Foodgram модель пользователя."""

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=MAX_LEN_FIELD,
        unique=True
    )
    username = models.CharField(
        verbose_name='Уникальный юзернейм',
        max_length=MAX_LEN_USERS,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_LEN_USERS,
        blank=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_LEN_USERS,
        blank=True
    )
    password = models.CharField(
        verbose_name=('Пароль'),
        max_length=MAX_LEN_FIELD,
        null=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id']

    def __str__(self):
        return self.username
