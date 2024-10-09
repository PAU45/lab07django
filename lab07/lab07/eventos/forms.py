from django import forms
from .models import Usuario, Evento, RegistroEvento
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import uuid

from django import forms
from .models import Usuario, Evento

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'correo', 'contraseña', 'telefono']  # Agregado el campo 'telefono'

    def save(self, commit=True):
        usuario = super().save(commit=False)
        # Hash the password before saving
        usuario.set_contraseña(self.cleaned_data['contraseña'])
        if commit:
            usuario.save()
        return usuario
class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = [
            'nombre', 
            'fecha_inicio', 
            'fecha_fin', 
            'lugar', 
            'descripcion', 
            'imagen_url', 
            'ubicacion', 
            'categoria', 
            'es_gratuito', 
            'precio_normal', 
            'precio_vip'
        ]
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'lugar': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen_url': forms.URLInput(attrs={'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control'}),
            'precio_normal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'precio_vip': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'es_gratuito': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:  # Si el evento ya existe
            self.fields['precio_normal'].widget.attrs['disabled'] = self.instance.es_gratuito
            self.fields['precio_vip'].widget.attrs['disabled'] = self.instance.es_gratuito

    def clean(self):
        cleaned_data = super().clean()
        es_gratuito = cleaned_data.get("es_gratuito")
        
        if es_gratuito:
            cleaned_data['precio_normal'] = None
            cleaned_data['precio_vip'] = None
        
        return cleaned_data

    def save(self, commit=True, usuario=None):
        evento = super().save(commit=False)
        evento.organizador = usuario  # Asigna el organizador desde el usuario pasado
        if commit:
            evento.save()
        return evento

class RegistroEventoForm(forms.ModelForm):
    TIPO_ENTRADA = [
        ('normal', 'Normal'),
        ('vip', 'VIP'),
        ('gratuita', 'Gratuita'),
    ]

    tipo_de_entrada = forms.ChoiceField(
        choices=TIPO_ENTRADA,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = RegistroEvento
        fields = ['evento', 'usuario', 'tipo_de_entrada', 'precio']
        widgets = {
            'evento': forms.Select(attrs={'class': 'form-control'}),
            'usuario': forms.Select(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio', 'step': '0.01'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo_de_entrada = cleaned_data.get("tipo_de_entrada")
        evento = cleaned_data.get("evento")

        # Validar el precio según el tipo de entrada
        if evento:
            if tipo_de_entrada == 'normal':
                if evento.precio_normal is not None:
                    cleaned_data['precio'] = evento.precio_normal
                else:
                    raise ValidationError("Este evento no tiene un precio definido para la entrada normal.")
            elif tipo_de_entrada == 'vip':
                if evento.precio_vip is not None:
                    cleaned_data['precio'] = evento.precio_vip
                else:
                    raise ValidationError("Este evento no tiene un precio definido para la entrada VIP.")
            elif tipo_de_entrada == 'gratuita':
                cleaned_data['precio'] = 0  # O manejarlo como prefieras

        return cleaned_data

    def save(self, commit=True):
        registro = super().save(commit=False)
        
        # Generar un código de registro único
        registro.codigo_registro = uuid.uuid4()  # Genera un código único
        
        # Generar un número de ticket único
        while True:
            numero_ticket = uuid.uuid4().hex  # Genera un nuevo número de ticket
            if not RegistroEvento.objects.filter(numero_ticket=numero_ticket).exists():
                registro.numero_ticket = numero_ticket
                break

        if commit:
            registro.save()

        return registro
