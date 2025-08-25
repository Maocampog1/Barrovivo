# Autor: Maria Alejandra Ocampo
from django import forms
from django.contrib.auth.models import User

class CrearCuentaForm(forms.Form):
    """Formulario de registro de CuentaCliente."""
    nombre = forms.CharField(
        label="Nombre completo",
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "Ingresa tu nombre"})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Ingresa tu email"})
    )
    contrasena1 = forms.CharField(
        label="Contraseña",
        min_length=8,
        widget=forms.PasswordInput(attrs={"placeholder": "Mínimo 8 caracteres"})
    )
    contrasena2 = forms.CharField(
        label="Confirmar contraseña",
        min_length=8,
        widget=forms.PasswordInput(attrs={"placeholder": "Confirma tu contraseña"})
    )

    def clean_email(self):
        correo = self.cleaned_data["email"].lower().strip()
        # Evitamos duplicados (usamos email como username)
        if User.objects.filter(username=correo).exists() or User.objects.filter(email=correo).exists():
            raise forms.ValidationError("Ya existe una cuenta con este email.")
        return correo

    def clean(self):
        datos = super().clean()
        p1 = datos.get("contrasena1")
        p2 = datos.get("contrasena2")
        if p1 and p2 and p1 != p2:
            self.add_error("contrasena2", "Las contraseñas no coinciden.")
        return datos

    def save(self):
        datos = self.cleaned_data
        user = User.objects.create_user(
            username=datos["email"],  # usamos el email como username
            email=datos["email"],
            first_name=datos["nombre"],
            password=datos["contrasena1"],
        )
        return user
