from django.contrib import admin
from .models import Evento, RegistroEvento,Usuario

admin.site.register(Evento)
admin.site.register(RegistroEvento)
admin.site.register(Usuario)