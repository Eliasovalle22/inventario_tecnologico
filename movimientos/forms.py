from django import forms
from .models import Movimiento
from inventario.models import Activo
from catalogos.models import Ubicacion, Estado
from django.contrib.auth.models import User

class MovimientoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        fields = ['activo', 'tipo', 'ubicacion_destino', 'estado_destino',                 'responsable_nuevo', 'observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Personalizar campos
        self.fields['activo'].queryset = Activo.objects.filter(estado__nombre__in=['Disponible', 'Asignado', 'En bodega'])
        self.fields['activo'].widget.attrs.update({'class': 'form-select'})
        
        self.fields['tipo'].widget.attrs.update({'class': 'form-select'})
        
        self.fields['ubicacion_destino'].queryset = Ubicacion.objects.all()
        self.fields['ubicacion_destino'].widget.attrs.update({'class': 'form-select'})
        self.fields['ubicacion_destino'].required = False
        
        self.fields['estado_destino'].queryset = Estado.objects.all()
        self.fields['estado_destino'].widget.attrs.update({'class': 'form-select'})
        self.fields['estado_destino'].required = False
        
        self.fields['responsable_nuevo'].queryset = User.objects.filter(is_active=True)
        self.fields['responsable_nuevo'].widget.attrs.update({'class': 'form-select'})
        self.fields['responsable_nuevo'].required = False
        
        # Configurar dependencias entre campos
        self.fields['ubicacion_destino'].help_text = "Obligatorio para traslados"
        self.fields['estado_destino'].help_text = "Obligatorio para cambios de estado"
        self.fields['responsable_nuevo'].help_text = "Obligatorio para asignaciones"
    
    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        ubicacion = cleaned_data.get('ubicacion_destino')
        estado = cleaned_data.get('estado_destino')
        responsable = cleaned_data.get('responsable_nuevo')
        
        if tipo == 'TRASLADO' and not ubicacion:
            raise forms.ValidationError("Para traslados debe especificar una ubicación de destino")
        
        if tipo == 'ASIGNACION' and not responsable:
            raise forms.ValidationError("Para asignaciones debe especificar un responsable")
        
        if tipo == 'CAMBIO_ESTADO' and not estado:
            raise forms.ValidationError("Para cambios de estado debe especificar un estado nuevo")
        
        return cleaned_data

class MovimientoFiltroForm(forms.Form):
    TIPO_CHOICES = [('', 'Todos')] + Movimiento.TIPO_MOVIMIENTO
    
    fecha_desde = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    fecha_hasta = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    tipo = forms.ChoiceField(choices=TIPO_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    activo = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código del activo'}))
    usuario = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario que realizó'}))