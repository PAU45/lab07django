# Generated by Django 5.1.1 on 2024-10-08 04:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('correo', models.EmailField(max_length=254, unique=True)),
                ('contraseña', models.CharField(max_length=128)),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
                ('telefono', models.CharField(blank=True, max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='Evento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField()),
                ('lugar', models.CharField(max_length=100)),
                ('descripcion', models.TextField()),
                ('imagen_url', models.URLField(blank=True)),
                ('ubicacion_url', models.URLField(blank=True)),
                ('categoria', models.CharField(blank=True, max_length=50)),
                ('organizador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='eventos_organizados', to='eventos.usuario')),
            ],
        ),
        migrations.CreateModel(
            name='RegistroEvento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
                ('tipo_de_entrada', models.CharField(choices=[('normal', 'Normal'), ('vip', 'VIP'), ('gratuita', 'Gratuita')], max_length=10)),
                ('precio', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('estado', models.CharField(default='activo', max_length=20)),
                ('codigo_registro', models.UUIDField(editable=False, unique=True)),
                ('numero_ticket', models.CharField(max_length=50, unique=True)),
                ('evento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registros', to='eventos.evento')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registros_eventos', to='eventos.usuario')),
            ],
            options={
                'unique_together': {('evento', 'usuario')},
            },
        ),
    ]
