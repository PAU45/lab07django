from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    contraseña = models.CharField(max_length=128) 

    def set_contraseña(self, raw_password):
        self.contraseña = make_password(raw_password)

    def check_contraseña(self, raw_password):
        return check_password(raw_password, self.contraseña)

    def __str__(self):
        return self.nombre


class Evento(models.Model):
    nombre = models.CharField(max_length=200)
    fecha = models.DateTimeField()
    lugar = models.CharField(max_length=200)
    organizador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='eventos_organizados')  # Cambié 'User' por 'Usuario'
    descripcion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.nombre


class RegistroEvento(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='registros')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='registros_eventos')  # Cambié 'User' por 'Usuario'
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.nombre_completo} - {self.evento.nombre}"
