from django import template
from django.contrib.auth import get_user_model

User = get_user_model()

register = template.Library()


@register.simple_tag
def is_follow(followee, follower):
    if not isinstance(followee, User) or not isinstance(follower, User):
        return False

    return followee.is_follow(follower)
