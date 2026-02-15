from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User, Group
from .models import Perfil

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )

class RegistroUsuarioForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Contraseña'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirmar contraseña'
    )
    grupo = forms.ChoiceField(
        choices=[('Asistente', 'Asistente'), ('DirectorTI', 'Director TI')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Rol'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=True
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Nombre',
        required=True
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Apellido',
        required=True
    )
    
    # Campos del perfil
    telefono = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Teléfono',
        required=False
    )
    departamento = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Departamento',
        required=False
    )
    cargo = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Cargo',
        required=False
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Las contraseñas no coinciden')
        
        return cleaned_data
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya existe')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email ya está registrado')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Crear o actualizar perfil
            Perfil.objects.update_or_create(
                usuario=user,
                defaults={
                    'telefono': self.cleaned_data.get('telefono'),
                    'departamento': self.cleaned_data.get('departamento'),
                    'cargo': self.cleaned_data.get('cargo')
                }
            )
        return user