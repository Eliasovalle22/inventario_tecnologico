from django import forms
from .models import Activo
from catalogos.models import Categoria, Marca, Ubicacion, Estado
from django.contrib.auth.models import User

class ActivoForm(forms.ModelForm):
    class Meta:
        model = Activo
        fields = '__all__'
        exclude = ['creado_por', 'fecha_creacion', 'fecha_actualizacion']
        widgets = {
            'fecha_compra': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'especificaciones': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Ingrese especificaciones: procesador, RAM, disco, etc.'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar los campos
        self.fields['codigo'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ej: ACT-001'})
        self.fields['tipo'].widget.attrs.update({'class': 'form-select'})
        self.fields['serial'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Número de serie'})
        self.fields['modelo'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Modelo del equipo'})
        self.fields['valor_compra'].widget.attrs.update({'class': 'form-control', 'placeholder': '0.00'})
        self.fields['garantia_meses'].widget.attrs.update({'class': 'form-control', 'min': 0})
        self.fields['proveedor'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nombre del proveedor'})
        self.fields['factura'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Número de factura'})
        
        # Para campos ForeignKey, asegurar que tengan las opciones correctas
        self.fields['categoria'].queryset = Categoria.objects.all().order_by('nombre')
        self.fields['categoria'].widget.attrs.update({'class': 'form-select'})
        
        self.fields['marca'].queryset = Marca.objects.all().order_by('nombre')
        self.fields['marca'].widget.attrs.update({'class': 'form-select'})
        
        self.fields['estado'].queryset = Estado.objects.all().order_by('nombre')
        self.fields['estado'].widget.attrs.update({'class': 'form-select'})
        
        self.fields['ubicacion'].queryset = Ubicacion.objects.all().order_by('nombre')
        self.fields['ubicacion'].widget.attrs.update({'class': 'form-select'})
        
        self.fields['responsable'].queryset = User.objects.filter(is_active=True).order_by('username')
        self.fields['responsable'].widget.attrs.update({'class': 'form-select'})
        self.fields['responsable'].required = False
        
        # Hacer algunos campos opcionales
        self.fields['serial'].required = False
        self.fields['valor_compra'].required = False
        self.fields['proveedor'].required = False
        self.fields['factura'].required = False