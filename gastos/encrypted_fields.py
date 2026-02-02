"""
Campos de modelo encriptados para datos sensibles
"""
from django.db import models
from encrypted_model_fields.fields import EncryptedCharField, EncryptedTextField, EncryptedDecimalField
from django.conf import settings


class EncryptedMoneyField(EncryptedDecimalField):
    """
    Campo encriptado para almacenar valores monetarios
    Usa EncryptedDecimalField de encrypted_model_fields
    """

    def __init__(self, *args, **kwargs):
        # Configurar valores por defecto para campos monetarios
        kwargs.setdefault('max_digits', 12)
        kwargs.setdefault('decimal_places', 2)
        super().__init__(*args, **kwargs)

    description = "Campo monetario encriptado"


class EncryptedAccountNumberField(EncryptedCharField):
    """
    Campo encriptado para números de cuenta bancaria
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 255)
        super().__init__(*args, **kwargs)

    description = "Número de cuenta bancaria encriptado"


class EncryptedEmailField(EncryptedCharField):
    """
    Campo encriptado para emails sensibles
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 254)
        super().__init__(*args, **kwargs)

    description = "Email encriptado"


class EncryptedPhoneField(EncryptedCharField):
    """
    Campo encriptado para números de teléfono
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 20)
        super().__init__(*args, **kwargs)

    description = "Teléfono encriptado"


# Nota: Para usar estos campos en los modelos:
#
# from gastos.encrypted_fields import EncryptedMoneyField, EncryptedAccountNumberField
#
# class Aportante(models.Model):
#     # Campo normal (no encriptado)
#     nombre = models.CharField(max_length=100)
#
#     # Campo encriptado
#     ingreso_mensual_encrypted = EncryptedMoneyField(
#         verbose_name="Ingreso Mensual (Encriptado)",
#         null=True,
#         blank=True
#     )
