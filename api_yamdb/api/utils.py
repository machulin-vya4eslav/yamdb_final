from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from reviews.models import User


def send_confirmation_code(user, email):
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        'yamdb registration',
        f'your confirmation code is {confirmation_code}',
        'yamdb@yandex.ru',
        (email,)
    )


def validate_token_for_user(confirmation_code, username):
    user = get_object_or_404(User, username=username)
    if not default_token_generator.check_token(user, confirmation_code):
        raise ValidationError(detail='confirmation_code not valid')
