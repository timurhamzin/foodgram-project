from django import template

register = template.Library()


@register.filter
def user_title(user):
    return user.first_name or user.username
