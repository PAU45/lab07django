from django import forms
from .models import Usuario, Evento, RegistroEvento

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'correo', 'contraseña']

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
        fields = ['nombre', 'fecha', 'lugar', 'descripcion'] 
        widgets = {
            'fecha': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control', 
            }),
            'descripcion': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
            }),
            'lugar': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
            }),
        }

    def save(self, commit=True, usuario=None):
        evento = super().save(commit=False)
        evento.organizador = usuario  # Asigna el organizador desde el usuario pasado
        if commit:
            evento.save()
        return evento


class RegistroEventoForm(forms.ModelForm):
    class Meta:
        model = RegistroEvento
        fields = ['evento', 'usuario']  # Assuming you want to register a user to an event
