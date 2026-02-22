from django import forms
from .models import Asignacion
from inventario.models import Activo
from django.contrib.auth.models import User
from django.utils import timezone

class AsignacionForm(forms.ModelForm):
    class Meta:
        model = Asignacion
        fields = ['activo', 'usuario_asignado', 'fecha_estimada_devolucion', 'motivo', 'observaciones', 'evidencias']
        widgets = {
            'fecha_estimada_devolucion': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'motivo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Trabajo remoto, etc.'}),
            'observaciones': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'evidencias': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://drive.google.com/...'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Activos disponibles
        self.fields['activo'].queryset = Activo.objects.filter(
            estado__nombre__in=['Disponible', 'En bodega']
        ).select_related('marca')
        self.fields['activo'].widget.attrs.update({'class': 'form-select select2-field'})
        self.fields['activo'].label = "Activo a asignar"
        
        # Usuarios activos
        self.fields['usuario_asignado'].queryset = User.objects.filter(
        is_active=True
        ).order_by('first_name', 'last_name')
        self.fields['usuario_asignado'].label_from_instance = lambda obj: f"{obj.get_full_name() or obj.username} ({obj.username})"
        self.fields['usuario_asignado'].widget.attrs.update({'class': 'form-select select2-field'})
        self.fields['usuario_asignado'].label = "Asignar a"
        
        self.fields['evidencias'].required = False
        self.fields['evidencias'].label = "Evidencias (URL)"
        
        self.fields['fecha_estimada_devolucion'].required = False
        self.fields['fecha_estimada_devolucion'].label = "Fecha estimada de devolución"
        
        self.fields['motivo'].required = True
        self.fields['motivo'].label = "Motivo de la asignación"
    
    def clean(self):
        cleaned_data = super().clean()
        activo = cleaned_data.get('activo')
        
        if activo:
            # Verificar que el activo no esté ya asignado
            if Asignacion.objects.filter(activo=activo, activo_actual=True).exists():
                raise forms.ValidationError(
                    f"El activo {activo.codigo} ya está asignado actualmente."
                )
        
        return cleaned_data

class DevolucionForm(forms.Form):
    fecha_devolucion = forms.DateTimeField(
        initial=timezone.now,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )
    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Observaciones de la devolución'})
    )
    estado_activo = forms.ChoiceField(
        choices=[
            ('BUENO', 'Buen estado'),
            ('REGULAR', 'Regular'),
            ('MALO', 'Malo'),
            ('REPARACION', 'Necesita reparación'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    observaciones_estado = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Detalles del estado del activo'})
    )

class AsignacionFiltroForm(forms.Form):
    ESTADO_CHOICES = [
        ('', 'Todos'),
        ('activas', 'Activas'),
        ('devueltas', 'Devueltas'),
        ('vencidas', 'Vencidas'),
    ]
    
    estado = forms.ChoiceField(choices=ESTADO_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    usuario = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario'}))
    activo = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código del activo'}))
    fecha_desde = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    fecha_hasta = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))