import datetime
import re

from django.core import validators
from django.utils.deconstruct import deconstructible
from rest_framework import serializers


def validate_year(value):
    current_year = datetime.date.today().year
    if value > current_year:
        raise serializers.ValidationError(
            f'Год издания не может быть больше текущего {current_year}'
        )
    return value


@deconstructible
class MultilineUsernameValidator(validators.RegexValidator):
    regex = r'^[\w.@+-]+\Z'
    message = (
        'Enter a valid username. This value may contain only letters, '
        'numbers, and @/./+/-/_ characters.'
    )
    flags = re.ASCII


def validate_username(username):
    MultilineUsernameValidator()(username)
    if username == 'me':
        raise serializers.ValidationError(detail='invalid username')
    return username
