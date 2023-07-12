import os

from django import template

register = template.Library()

@register.filter
def basename(value):
    return os.path.basename(value.file.name)

@register.filter
def replace_spaces(value):
    return value.replace(" ", "")


@register.filter
def update_variable(new_value):
    return new_value