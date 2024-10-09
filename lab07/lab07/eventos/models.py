from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
import uuid
class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    contraseña = models.CharField(max_length=128)
    fecha_registro = models.DateTimeField(auto_now_add=True)  # Fecha de registro del usuario
    telefono = models.CharField(max_length=15, blank=True)  # Campo opcional para número de teléfono

    def set_contraseña(self, raw_password):
        self.contraseña = make_password(raw_password)

    def check_contraseña(self, raw_password):
        return check_password(raw_password, self.contraseña)

    def __str__(self):
        return self.nombre

class Evento(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateField()  # Fecha de inicio del evento
    fecha_fin = models.DateField()      # Fecha de finalización del evento
    lugar = models.CharField(max_length=100)
    descripcion = models.TextField()
    
    imagen_url = models.URLField(max_length=200, blank=True)  # URL de la imagen
    organizador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='eventos_organizados')  # Cambié 'User' por 'Usuario'
    ubicacion = models.TextField(blank=True, null=True)   # URL de ubicación
    categoria = models.CharField(max_length=50, blank=True)  # Categoría opcional
    
    es_gratuito = models.BooleanField(default=False)  # Campo para indicar si el evento es gratuito
    precio_normal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Precio de entrada normal
    precio_vip = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Precio de entrada VIP

    def clean(self):
        # Validación para asegurarse de que la fecha de inicio sea anterior a la de finalización
        if self.fecha_inicio >= self.fecha_fin:
            raise ValidationError("La fecha de inicio debe ser anterior a la fecha de finalización.")
        

        if not self.es_gratuito and (self.precio_normal is None or self.precio_vip is None):
            raise ValidationError("Debes establecer precios para las entradas si el evento no es gratuito.")


    def save(self, *args, **kwargs):
        self.clean()  # Llama a la validación antes de guardar
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

class RegistroEvento(models.Model):
    TIPO_ENTRADA = [
        ('normal', 'Normal'),
        ('vip', 'VIP'),
        ('gratuita', 'Gratuita'),
    ]

    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='registros')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='registros_eventos')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    tipo_de_entrada = models.CharField(max_length=10, choices=TIPO_ENTRADA)  # Campo para tipo de entrada
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Precio de la entrada
    estado = models.CharField(max_length=20, default='activo')  # Estado del registro (activo, cancelado, utilizado)
    codigo_registro = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Código único de registro
    numero_ticket = models.CharField(max_length=10)

    class Meta:
        unique_together = ('evento', 'usuario')  # Restricción para evitar registros duplicados

    def __str__(self):
        return f"{self.usuario.nombre} - {self.evento.nombre} ({self.tipo_de_entrada})"