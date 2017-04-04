# -*- coding: utf-8 -*-

import random
import re

chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'


def get_random_string(length=12, allowed_chars=chars):
    return ''.join(random.choice(allowed_chars) for _ in range(length))


def inflection(name):
    """Convert camelcase names into snakecase attributes.

    CreateUser == create_user
    """
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
