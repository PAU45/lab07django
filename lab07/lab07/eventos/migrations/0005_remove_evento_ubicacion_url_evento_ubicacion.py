# Generated by Django 5.1.1 on 2024-10-09 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0004_evento_es_gratuito_evento_precio_normal_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='evento',
            name='ubicacion_url',
        ),
        migrations.AddField(
            model_name='evento',
            name='ubicacion',
            field=models.TextField(blank=True, null=True),
        ),
    ]
