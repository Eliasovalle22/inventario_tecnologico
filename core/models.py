from django.db import models

class UpperCaseMixin:
    uppercase_exclude = []

    def save(self, *args, **kwargs):
        exclude = set(self.uppercase_exclude)
        for field in self._meta.get_fields():
            if field.name in exclude:
                continue
            # Solo convertir CharField y TextField (no URLField, EmailField, etc.)
            if type(field) in (models.CharField, models.TextField):
                value = getattr(self, field.name, None)
                if isinstance(value, str) and value:
                    setattr(self, field.name, value.upper())
        super().save(*args, **kwargs)
