from django import forms
from django.contrib.auth.models import User
from .models import Persona
import re


def validar_rut_chileno(rut):
    
    if not rut:
        raise forms.ValidationError("RUT es obligatorio.")
    
    rut_limpio = rut.upper().replace(".", "").replace("-", "").replace(" ", "")
    
    if not re.match(r"^\d{1,8}[0-9K]$", rut_limpio):
        raise forms.ValidationError(
            "Formato de RUT inválido. Debe contener solo números y terminar en dígito o K. "
            "Ejemplos: 12345678-9, 1234567-K"
        )
    
    cuerpo = rut_limpio[:-1]
    dv_ingresado = rut_limpio[-1]
    
    suma = 0
    multiplicador = 2
    
    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2
    
    resto = suma % 11
    dv_calculado = 11 - resto
    
    if dv_calculado == 11:
        dv_calculado = '0'
    elif dv_calculado == 10:
        dv_calculado = 'K'
    else:
        dv_calculado = str(dv_calculado)
    
    if dv_calculado != dv_ingresado:
        raise forms.ValidationError(
            f"RUT inválido: el dígito verificador debería ser {dv_calculado}, "
            f"pero se ingresó {dv_ingresado}."
        )
    
    return rut_limpio


def formatear_rut(rut):
    if len(rut) < 2:
        return rut
    
    cuerpo = rut[:-1]
    dv = rut[-1]
    
    cuerpo_formateado = ""
    for i, digito in enumerate(reversed(cuerpo)):
        if i > 0 and i % 3 == 0:
            cuerpo_formateado = "." + cuerpo_formateado
        cuerpo_formateado = digito + cuerpo_formateado
    
    return f"{cuerpo_formateado}-{dv}"


class RegistroForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        label="Usuario",
        help_text="Nombre de usuario único para iniciar sesión",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Nombre de usuario'
        })
    )
    
    password = forms.CharField(
        label="Contraseña",
        min_length=8,
        help_text="Mínimo 8 caracteres",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Contraseña'
        })
    )
    
    password_confirm = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Confirmar contraseña'
        })
    )
    
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'correo@ejemplo.com'
        })
    )
    
    rut = forms.CharField(
        label="RUT",
        help_text="Formato: 12345678-9 o 12.345.678-9",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Ej: 12.345.678-9'
        })
    )

    class Meta:
        model = Persona
        fields = ['rut']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        rut_limpio = validar_rut_chileno(rut)
        
        if Persona.objects.filter(rut=rut_limpio).exists():
            raise forms.ValidationError("Este RUT ya está registrado.")
        
        return rut_limpio

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        
        return password_confirm

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email']
        )
        
        persona = super().save(commit=False)
        persona.user = user
        
        if commit:
            persona.save()
        
        return persona