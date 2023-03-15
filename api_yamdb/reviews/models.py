from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from api_yamdb.settings import (
    USER_ROLE,
    MODERATOR_ROLE,
    ADMIN_ROLE,
    USERNAME_MAX_LENGTH,
    EMAIL_MAX_LENGTH
)

from .validators import validate_year, MultilineUsernameValidator


FIRST_NAME_MAX_LENGTH = 150
LAST_NAME_MAX_LENGTH = 150
STRING_REPRESENTATION_MAX_LENGTH = 20
GENRE_AND_CATEGORY_NAME_MAX_LENGTH = 256
GENRE_AND_CATEGORY_SLUG_MAX_LENGTH = 50
TITLE_NAME_MAX_LENGTH = 256
SCORE_MIN_VALUE = 1
SCORE_MAX_VALUE = 10


class User(AbstractUser):
    ROLE_CHOICES = (
        (USER_ROLE, USER_ROLE,),
        (MODERATOR_ROLE, MODERATOR_ROLE,),
        (ADMIN_ROLE, ADMIN_ROLE,),
    )
    username_validator = MultilineUsernameValidator()
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.TextField('Роль', choices=ROLE_CHOICES, default=USER_ROLE)
    email = models.EmailField(
        'email address',
        unique=True,
        max_length=EMAIL_MAX_LENGTH
    )
    first_name = models.CharField(
        'first name',
        max_length=FIRST_NAME_MAX_LENGTH,
        blank=True
    )
    last_name = models.CharField(
        'last name like in AbstractUser but another',
        max_length=LAST_NAME_MAX_LENGTH,
        blank=True
    )
    username = models.CharField(
        'username',
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        help_text='Letters, digits and @/./+/-/_ only.',
        validators=[username_validator],
        error_messages=dict(unique="A user with username already exists."),
    )

    class Meta:
        ordering = ('role',)

    @property
    def is_admin(self):
        return self.role == ADMIN_ROLE or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == MODERATOR_ROLE


class BaseModelWithNameAndTitleProperties(models.Model):
    field_name = None

    name = models.TextField(
        unique=True,
        max_length=GENRE_AND_CATEGORY_NAME_MAX_LENGTH,
        verbose_name=f'Название для поля {field_name}',
        help_text=f'Введите название для поля {field_name}'
    )
    slug = models.SlugField(
        unique=True,
        max_length=GENRE_AND_CATEGORY_SLUG_MAX_LENGTH,
        verbose_name=f'Slug для поля {field_name}',
        help_text=f'Введите slug для поля {field_name}'
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name[:STRING_REPRESENTATION_MAX_LENGTH]


class Genre(BaseModelWithNameAndTitleProperties):
    field_name = 'жанр'


class Category(BaseModelWithNameAndTitleProperties):
    field_name = 'категория'


class Title(models.Model):
    name = models.TextField(
        unique=True,
        max_length=TITLE_NAME_MAX_LENGTH,
        verbose_name='Название произведения',
        help_text='Введите название произведения'
    )
    year = models.PositiveIntegerField(
        validators=(
            validate_year,
        ),
        verbose_name='Год выпуска',
        help_text='Введите год выпуска произведения'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание произведения',
        help_text='Введите описание произведения'
    )
    category = models.ForeignKey(
        Category,
        null=True,
        verbose_name='Категория произведения',
        help_text='Введите категорию произведения',
        on_delete=models.SET_NULL,
        related_name='titles'
    )

    genre = models.ManyToManyField(
        Genre,
        through='TitleGenre',
        verbose_name='Жанр(ы) произведения',
        help_text='Введите жанр(ы) произведения'
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name[:STRING_REPRESENTATION_MAX_LENGTH]


class TitleGenre(models.Model):
    genre = models.ForeignKey(Genre, null=True, on_delete=models.SET_NULL)
    title = models.ForeignKey(Title, null=True, on_delete=models.SET_NULL)


class Review(models.Model):
    """Модель для отзывов пользователей на произведения."""
    title = models.ForeignKey(
        Title,
        verbose_name='Название произведения',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField(
        verbose_name='Текст отзыва',
        help_text='Введите текст отзыва на данное произведение'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор отзыва',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.IntegerField(
        verbose_name='Рейтинг',
        validators=[
            MaxValueValidator(
                SCORE_MAX_VALUE,
                'Увы, выше 10 оценку поставить нельзя'
            ),
            MinValueValidator(
                SCORE_MIN_VALUE,
                'Нельзя поставить оценку ниже 1'
            )
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления отзыва',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author',),
                name='unique_review'
            ),
        ]

    def __str__(self):
        return self.text[:STRING_REPRESENTATION_MAX_LENGTH]


class Comment(models.Model):
    """Модель для комментариев пользователей к отзывам."""
    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор комментария',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления комментария',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:STRING_REPRESENTATION_MAX_LENGTH]
