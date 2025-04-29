from django import forms
from .models import Equipo, CambioParte

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = '__all__'
        widgets = {
            'fecha_compra': forms.DateInput(attrs={'type': 'date'}),
            'fecha_instalacion': forms.DateInput(attrs={'type': 'date'}),
        }

class CambioParteForm(forms.ModelForm):
    class Meta:
        model = CambioParte
        fields = '__all__'
        widgets = {
            'fecha_cambio': forms.DateInput(attrs={'type': 'date'}),
        }
