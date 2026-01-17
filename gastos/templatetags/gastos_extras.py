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

@register.filter
def get_requisito_tipo_display(logro):
    """Retorna el texto legible del tipo de requisito"""
    tipos_display = {
        'dias_consecutivos': 'días consecutivos',
        'monto_ahorrado_mes': 'de ahorro mensual',
        'ahorro_acumulado': 'de ahorro total',
        'gastos_registrados': 'gastos registrados',
        'visitas_dashboard': 'visitas al dashboard',
        'meses_cumplidos': 'meses cumpliendo presupuesto',
    }
    return tipos_display.get(logro.requisito_tipo, logro.requisito_tipo)

