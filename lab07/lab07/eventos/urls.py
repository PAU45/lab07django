from django.urls import path
from . import views

urlpatterns = [
    path('registrar/', views.registrar_usuario, name='registrar_usuario'),
    path('iniciar-sesion/',views.iniciar_sesion, name='iniciar_sesion'),
    path('cerrar-sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('mis-eventos/', views.listar_mis_eventos, name='listar_mis_eventos'),
    path('eventos-otros/', views.listar_eventos_otros, name='listar_eventos_otros'),
    path('eventos/crear/', views.crear_evento, name='crear_evento'),
    path('eventos/<int:evento_id>/', views.ver_evento, name='ver_evento'),
     path('presentacion/<int:evento_id>/', views.presentacion_evento, name='presentacion_evento'),
    path('eventos/<int:evento_id>/gestionar/', views.gestionar_registros, name='gestionar_registros'),
    path('eventos/eliminar/<int:evento_id>/', views.eliminar_evento, name='eliminar_evento'),  # Añadir esta línea
    path('eventos/<int:evento_id>/registrar/', views.registrar_en_evento, name='registrar_en_evento'),
    path('registros/eliminar/<int:registro_id>/', views.eliminar_registro, name='eliminar_registro'),
     path('eventos/cancelar_registro/<int:registro_id>/',views.cancelar_registro, name='eliminar_registro'),
       path('eventos/editar/<int:evento_id>/',views.editar_evento, name='editar_evento'),
       path('editar-usuario/',views.editar_usuario, name='editar_usuario'),
           path('dashboard/', views.dashboard, name='dashboard'),
            path('eventos/editar/<int:evento_id>/', views.editar_evento, name='editar_evento'),
            
]
