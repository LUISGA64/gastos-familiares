from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Permite acceder a items de un diccionario en templates"""
    if dictionary:
        return dictionary.get(key)
    return None

@register.filter
def abs_value(value):
    """Retorna el valor absoluto de un número"""
    try:
        return abs(value)
    except (TypeError, ValueError):
        return value
