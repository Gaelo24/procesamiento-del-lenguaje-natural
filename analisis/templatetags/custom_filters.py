# en analisis/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiplica el valor por el argumento."""
    try:
        return value * arg
    except (ValueError, TypeError):
        return ''