from django.core.validators import validate_email
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import AccessToken
from api_yamdb.settings import EMAIL_MAX_LENGTH, USERNAME_MAX_LENGTH
from reviews.models import Title, Genre, Category, Comment, Review
from reviews.validators import (
    validate_year, validate_username, MultilineUsernameValidator
)
from reviews.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )

    def validate_username(self, username):
        MultilineUsernameValidator()(username)
        if username == 'me':
            raise ValidationError(detail='invalid username')
        return username


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(
        validators=(
            validate_email,
        ),
        max_length=EMAIL_MAX_LENGTH,
    )
    username = serializers.CharField(
        required=True,
        max_length=USERNAME_MAX_LENGTH,
        validators=(
            validate_username,
        )
    )

    class Meta:
        fields = ('username', 'email',)


class UserMeSerializer(UserSerializer):

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=USERNAME_MAX_LENGTH,
        validators=(
            validate_username,
        )
    )
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        fields = ('token',)
        read_only_fields = ('user', 'confirmation_code',)

    def get_token(self):
        return AccessToken.for_user(get_object_or_404(User, self.username))


class NameAndSlugFieldsBaseSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        lookup_field = 'slug'


class CategorySerializer(NameAndSlugFieldsBaseSerializer):

    class Meta(NameAndSlugFieldsBaseSerializer.Meta):
        model = Category


class GenreSerializer(NameAndSlugFieldsBaseSerializer):

    class Meta(NameAndSlugFieldsBaseSerializer.Meta):
        model = Genre


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )
    year = serializers.IntegerField(validators=(validate_year, ))

    class Meta:
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')
        model = Title


class TitleReadSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
        read_only_fields = fields
        model = Title


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
        read_only_fields = ('review',)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = ('id', 'title', 'text', 'author', 'score', 'pub_date')
        model = Review
        read_only_fields = ('title',)

    def validate(self, attrs):
        request = self.context['request']
        if request.method == 'POST':
            title_id = self.context['view'].kwargs.get('title_id')
            title = get_object_or_404(Title, id=title_id)
            review = title.reviews.filter(author=request.user)
            if review.exists():
                raise ValidationError(
                    'Нельзя оставлять отзыв на одно и то же произведение!')
        return attrs
