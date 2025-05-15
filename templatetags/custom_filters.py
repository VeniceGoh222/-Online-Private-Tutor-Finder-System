from django import template

register = template.Library()

@register.filter
def div(value, arg):
    try:
        value = float(value)
        arg = float(arg)
        if arg:
            return value / arg
        return 0
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def sub(value, arg):
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name='get')
def get_item(dictionary, key):
    """Get an item from a dictionary using bracket notation."""
    if not dictionary:
        return []
    return dictionary.get(key, [])
