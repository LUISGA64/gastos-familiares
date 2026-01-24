from django import template
from decimal import Decimal

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


@register.filter
def formato_moneda(valor):
    """Formatea un valor monetario con separadores de miles y signo de pesos"""
    try:
        # Convertir a float si es Decimal
        if isinstance(valor, Decimal):
            valor = float(valor)

        # Formatear con separadores de miles
        if valor >= 0:
            return "${:,.0f}".format(valor).replace(",", ".")
        else:
            return "-${:,.0f}".format(abs(valor)).replace(",", ".")
    except (TypeError, ValueError):
        return "$0"


@register.filter
def formato_moneda_privado(valor, ocultar=False):
    """Formatea un valor monetario pero lo oculta si la privacidad está activa"""
    if ocultar:
        return "****"
    return formato_moneda(valor)


@register.simple_tag
def mostrar_valor(valor, usuario):
    """Muestra el valor monetario o **** según las preferencias del usuario"""
    try:
        # Obtener preferencias del usuario
        if hasattr(usuario, 'preferencias') and usuario.preferencias.ocultar_valores_monetarios:
            return "****"
        return formato_moneda(valor)
    except:
        return formato_moneda(valor)



