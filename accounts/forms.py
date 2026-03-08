from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
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
        label='Contraseña',
        help_text='Mínimo 10 caracteres, con mayúsculas, números y caracteres especiales.'
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
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Las contraseñas no coinciden')

        return cleaned_data

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            validate_password(password)
        return password

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya existe')
        import re
        if not re.match(r'^[\w.@+-]+$', username):
            raise forms.ValidationError('El nombre de usuario contiene caracteres no válidos.')
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
            Perfil.objects.update_or_create(
                usuario=user,
                defaults={
                    'telefono': self.cleaned_data.get('telefono'),
                    'departamento': self.cleaned_data.get('departamento'),
                    'cargo': self.cleaned_data.get('cargo')
                }
            )
        return user


# Validador de teléfono
phone_validator = RegexValidator(
    regex=r'^\+?[\d\s\-\(\)]{7,20}$',
    message='Ingresa un número de teléfono válido (7-20 dígitos).'
)


class PerfilForm(forms.Form):
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label='Nombre',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label='Apellido',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    telefono = forms.CharField(
        max_length=20,
        required=False,
        label='Teléfono',
        validators=[phone_validator],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+57 300 123 4567'}),
    )
    departamento = forms.CharField(
        max_length=100,
        required=False,
        label='Departamento',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    cargo = forms.CharField(
        max_length=100,
        required=False,
        label='Cargo',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.user and User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError('Este email ya está registrado por otro usuario.')
        return email