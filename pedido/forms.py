# Autor: Luis Angel Nerio
from django import forms

METODOS_PAGO = (
    ("credito", "Crédito"),
    ("debito", "Débito"),
)

class FormularioFacturacion(forms.Form):
    #Datos de facturación del cliente.
    correo = forms.EmailField(label="Dirección correo electrónico*", widget=forms.EmailInput(attrs={
        "placeholder": "correo@dominio.com", "class": "form-control"
    }))
    nombres = forms.CharField(label="Nombres*", max_length=120, widget=forms.TextInput(attrs={
        "class": "form-control"
    }))
    apellidos = forms.CharField(label="Apellido*", max_length=120, widget=forms.TextInput(attrs={
        "class": "form-control"
    }))
    cedula = forms.CharField(label="Cédula*", max_length=30, widget=forms.TextInput(attrs={
        "class": "form-control"
    }))


class FormularioEnvio(forms.Form):
    #Dirección de envío.
    departamento = forms.CharField(label="Departamento*", max_length=120, widget=forms.TextInput(attrs={
        "class": "form-control"
    }))
    municipio = forms.CharField(label="Municipio*", max_length=120, widget=forms.TextInput(attrs={
        "class": "form-control"
    }))
    direccion = forms.CharField(label="Dirección*", max_length=255, widget=forms.TextInput(attrs={
        "class": "form-control"
    }))
    apto_info = forms.CharField(
        label="Número de apto o info adicional",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    telefono = forms.CharField(label="Número de contacto*", max_length=30, widget=forms.TextInput(attrs={
        "class": "form-control"
    }))


class FormularioPago(forms.Form):
    #Solo simulación de pago (no procesa tarjetas reales).
    metodo = forms.ChoiceField(label="Selecciona método de pago*", choices=METODOS_PAGO, widget=forms.RadioSelect)
    numero_tarjeta = forms.CharField(label="Número de tarjeta*", max_length=19, widget=forms.TextInput(attrs={
        "class": "form-control", "placeholder": "1111 2222 3333 4444"
    }))
    fecha_exp = forms.CharField(label="Fecha de expiración*", max_length=7, widget=forms.TextInput(attrs={
        "class": "form-control", "placeholder": "MM/AA"
    }))
    cvc = forms.CharField(label="CVC*", max_length=4, widget=forms.TextInput(attrs={
        "class": "form-control", "placeholder": "123"
    }))
    nombre_en_tarjeta = forms.CharField(label="Nombre como aparece en la tarjeta*", max_length=120, widget=forms.TextInput(attrs={
        "class": "form-control"
    }))
    cedula = forms.CharField(label="Cédula*", max_length=30, widget=forms.TextInput(attrs={
        "class": "form-control"
    }))
