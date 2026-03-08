import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class UppercaseValidator:
    """Valida que la contraseña contenga al menos una letra mayúscula."""

    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _('La contraseña debe contener al menos una letra mayúscula (A-Z).'),
                code='password_no_upper',
            )

    def get_help_text(self):
        return _('Tu contraseña debe contener al menos una letra mayúscula (A-Z).')


class SpecialCharacterValidator:
    """Valida que la contraseña contenga al menos un carácter especial."""

    def validate(self, password, user=None):
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
            raise ValidationError(
                _('La contraseña debe contener al menos un carácter especial (!@#$%^&*...).'),
                code='password_no_special',
            )

    def get_help_text(self):
        return _('Tu contraseña debe contener al menos un carácter especial (!@#$%^&*...).')
