"""
Validadores personalizados de contraseñas para mayor seguridad
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re


class PasswordStrengthValidator:
    """
    Validador que verifica que la contraseña tenga al menos:
    - 1 letra mayúscula
    - 1 letra minúscula
    - 1 número
    - 1 carácter especial
    """

    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("La contraseña debe contener al menos una letra mayúscula."),
                code='password_no_upper',
            )

        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("La contraseña debe contener al menos una letra minúscula."),
                code='password_no_lower',
            )

        if not re.search(r'\d', password):
            raise ValidationError(
                _("La contraseña debe contener al menos un número."),
                code='password_no_digit',
            )

        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;]', password):
            raise ValidationError(
                _("La contraseña debe contener al menos un carácter especial (!@#$%^&*, etc.)."),
                code='password_no_special',
            )

    def get_help_text(self):
        return _(
            "Tu contraseña debe contener al menos una mayúscula, una minúscula, "
            "un número y un carácter especial."
        )


class MinimumLengthValidator:
    """
    Validador que requiere una longitud mínima de 12 caracteres
    (más seguro que el default de 8)
    """

    def __init__(self, min_length=12):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("La contraseña debe tener al menos %(min_length)d caracteres."),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return _(
            "Tu contraseña debe tener al menos %(min_length)d caracteres."
            % {'min_length': self.min_length}
        )


class NoPersonalInfoValidator:
    """
    Validador que evita que la contraseña contenga información personal del usuario
    """

    def validate(self, password, user=None):
        if not user:
            return

        password_lower = password.lower()

        # Verificar username
        if user.username and len(user.username) >= 3:
            if user.username.lower() in password_lower:
                raise ValidationError(
                    _("La contraseña no puede contener tu nombre de usuario."),
                    code='password_has_username',
                )

        # Verificar first_name
        if user.first_name and len(user.first_name) >= 3:
            if user.first_name.lower() in password_lower:
                raise ValidationError(
                    _("La contraseña no puede contener tu nombre."),
                    code='password_has_first_name',
                )

        # Verificar last_name
        if user.last_name and len(user.last_name) >= 3:
            if user.last_name.lower() in password_lower:
                raise ValidationError(
                    _("La contraseña no puede contener tu apellido."),
                    code='password_has_last_name',
                )

        # Verificar email (parte antes del @)
        if user.email:
            email_prefix = user.email.split('@')[0].lower()
            if len(email_prefix) >= 3 and email_prefix in password_lower:
                raise ValidationError(
                    _("La contraseña no puede contener tu dirección de email."),
                    code='password_has_email',
                )

    def get_help_text(self):
        return _(
            "Tu contraseña no puede contener tu nombre, apellido, usuario o email."
        )


class NoCommonPatternsValidator:
    """
    Validador que evita patrones comunes débiles
    """

    COMMON_PATTERNS = [
        '123456', '654321', 'qwerty', 'asdfgh', 'password', 'contraseña',
        '111111', '000000', 'abc123', '123abc', 'admin', 'user',
        '12345678', '87654321', 'password1', 'password123',
    ]

    def validate(self, password, user=None):
        password_lower = password.lower()

        for pattern in self.COMMON_PATTERNS:
            if pattern in password_lower:
                raise ValidationError(
                    _("La contraseña contiene un patrón común muy débil. Por favor elige una contraseña más segura."),
                    code='password_common_pattern',
                )

    def get_help_text(self):
        return _(
            "Tu contraseña no puede contener patrones comunes como '123456', 'qwerty', 'password', etc."
        )


class NoRepeatingCharactersValidator:
    """
    Validador que evita caracteres repetidos consecutivamente
    """

    def __init__(self, max_repeating=3):
        self.max_repeating = max_repeating

    def validate(self, password, user=None):
        # Buscar caracteres repetidos consecutivamente
        for i in range(len(password) - self.max_repeating + 1):
            char = password[i]
            if all(password[j] == char for j in range(i, i + self.max_repeating)):
                raise ValidationError(
                    _("La contraseña no puede tener el mismo carácter repetido %(max)d o más veces consecutivas."),
                    code='password_repeating_chars',
                    params={'max': self.max_repeating},
                )

    def get_help_text(self):
        return _(
            "Tu contraseña no puede tener el mismo carácter repetido %(max)d o más veces consecutivas."
            % {'max': self.max_repeating}
        )
