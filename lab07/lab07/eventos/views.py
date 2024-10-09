from django.shortcuts import render, redirect, get_object_or_404
from .models import Evento, RegistroEvento, Usuario
from .forms import EventoForm, UsuarioForm
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count

from django.contrib import messages
import random
import string

def registrar_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.set_contraseña(form.cleaned_data['contraseña'])  # Hashear contraseña
            usuario.save()
            return redirect('iniciar_sesion')  # Redirige a iniciar sesión
    else:
        form = UsuarioForm()
    return render(request, 'eventos/registrar_usuario.html', {'form': form})

def iniciar_sesion(request):
    if request.method == 'POST':
        correo = request.POST['correo']
        contraseña = request.POST['contraseña']
        try:
            usuario = Usuario.objects.get(correo=correo)
            if usuario.check_contraseña(contraseña):
                request.session['usuario_id'] = usuario.id
                return redirect('listar_mis_eventos')  # Redirige a los eventos del usuario
            else:
                # Manejar el caso de contraseña incorrecta
                return render(request, 'eventos/iniciar_sesion.html', {'error': 'Contraseña incorrecta.'})
        except Usuario.DoesNotExist:
            # Manejar el caso de usuario no encontrado
            return render(request, 'eventos/iniciar_sesion.html', {'error': 'Usuario no encontrado.'})
    return render(request, 'eventos/iniciar_sesion.html')


def cerrar_sesion(request):
    request.session.flush()  # Elimina la sesión del usuario
    return redirect('iniciar_sesion')

def listar_mis_eventos(request):
    if 'usuario_id' not in request.session:
        return redirect('iniciar_sesion')
    
    usuario = get_object_or_404(Usuario, id=request.session['usuario_id'])
    eventos = Evento.objects.filter(organizador=usuario)
    return render(request, 'eventos/mis_eventos.html', {
        'eventos': eventos,
        'usuario_nombre': usuario.nombre,  # Asegúrate de que 'nombre' es el campo correcto
    })


def listar_eventos_otros(request):
    if 'usuario_id' not in request.session:
        return redirect('iniciar_sesion')
    
    usuario_actual = Usuario.objects.get(id=request.session['usuario_id'])
    eventos = Evento.objects.exclude(organizador=usuario_actual)  # Excluye eventos del usuario actual
    return render(request, 'eventos/listar_eventos_otros.html', {'eventos': eventos})


def crear_evento(request):
    if 'usuario_id' not in request.session:
        return redirect('iniciar_sesion')
    
    usuario = get_object_or_404(Usuario, id=request.session['usuario_id'])  # Obtiene el usuario autenticado
    
    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.organizador = usuario  # Asigna el organizador como el usuario autenticado
            evento.save()
            return redirect('listar_mis_eventos')  # Redirige a mis eventos
    else:
        form = EventoForm()

    return render(request, 'eventos/crear_evento.html', {'form': form})

def ver_evento(request, evento_id):
    # Obtener el evento por ID o devolver un 404 si no existe
    evento = get_object_or_404(Evento, id=evento_id)
    
    # Obtener los registros asociados a este evento, incluyendo el usuario
    registros = RegistroEvento.objects.filter(evento=evento).select_related('usuario')

    # Obtener el usuario actual, si está autenticado
    usuario_actual = request.user if request.user.is_authenticated else None

    # Renderizar la plantilla con el evento, registros y el usuario actual
    return render(request, 'eventos/ver_evento.html', {
        'evento': evento,
        'registros': registros,
        'usuario': usuario_actual,  # Pasar el usuario autenticado
    })

def eliminar_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)

    if request.method == 'POST':
        evento.delete()
        return redirect('listar_mis_eventos')  # Redirige a la lista de eventos

    return render(request, 'eventos/eliminar_evento.html', {'evento': evento})


def gestionar_registros(request, evento_id):
    if 'usuario_id' not in request.session:
        return redirect('iniciar_sesion')
    
    evento = get_object_or_404(Evento, id=evento_id)
    registros = RegistroEvento.objects.filter(evento=evento)
    return render(request, 'eventos/gestionar_registros.html', {'evento': evento, 'registros': registros})

from django.utils import timezone

def generar_numero_ticket(length=10):
    """Genera un número de ticket aleatorio."""
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(random.choices(caracteres, k=length))

def presentacion_evento(request, evento_id):
    if 'usuario_id' not in request.session:
        return redirect('iniciar_sesion')

    evento = get_object_or_404(Evento, id=evento_id)
    usuario = get_object_or_404(Usuario, id=request.session['usuario_id'])

    # Verificar si el usuario ya está registrado en el evento
    ya_registrado = RegistroEvento.objects.filter(evento=evento, usuario=usuario).exists()

    return render(request, 'eventos/presentacion_evento.html', {
        'evento': evento,
        'ya_registrado': ya_registrado,
        'usuario': usuario,
    })

def registrar_en_evento(request, evento_id):
    if 'usuario_id' not in request.session:
        return redirect('iniciar_sesion')

    evento = get_object_or_404(Evento, id=evento_id)
    usuario = get_object_or_404(Usuario, id=request.session['usuario_id'])

    # Verificar si el usuario ya está registrado
    ya_registrado = RegistroEvento.objects.filter(evento=evento, usuario=usuario).exists()

    if ya_registrado:
        messages.info(request, f'Ya estás registrado en el evento {evento.nombre}.')
        return redirect('registro_exitoso')

    if evento.es_gratuito:
        # Registrar directamente si el evento es gratuito
        registro = RegistroEvento.objects.create(
            evento=evento,
            usuario=usuario,
            fecha_registro=timezone.now(),
            tipo_de_entrada='gratuita',
        )
        # Generar el número de ticket
        registro.numero_ticket = generar_numero_ticket()
        registro.save()

        messages.success(request, f'Te has registrado exitosamente en el evento {evento.nombre}.')
        return redirect('registro_exitoso')

    else:
        # Si es de pago, redirigir a la vista de pago
        return redirect('pago_evento', evento_id=evento.id)

def registro_exitoso(request):
    if 'usuario_id' not in request.session:
        return redirect('iniciar_sesion')

    usuario = get_object_or_404(Usuario, id=request.session['usuario_id'])
    
    # Asegúrate de obtener el último registro del usuario para el evento correspondiente
    registro = RegistroEvento.objects.filter(usuario=usuario).last()  # O usa algún otro criterio para obtener el registro
    evento = registro.evento if registro else None  # Asegúrate de que exista un registro

    return render(request, 'eventos/registro_evento.html', {
        'registro': registro,
        'evento': evento,
        'usuario': usuario,
    }) 

def eliminar_registro(request, registro_id):
    registro = get_object_or_404(RegistroEvento, id=registro_id)
    evento_id = registro.evento.id
    registro.delete()
    return redirect('gestionar_registros', evento_id=evento_id)


def cancelar_registro(request, registro_id):
    if request.method == 'POST':
        registro = get_object_or_404(RegistroEvento, id=registro_id)
        registro.delete()
        return redirect('listar_eventos_otros')  



def editar_evento(request, evento_id):
    if 'usuario_id' not in request.session:
        return redirect('iniciar_sesion')

    evento = get_object_or_404(Evento, id=evento_id)

    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento)
        if form.is_valid():
            form.save(usuario=get_object_or_404(Usuario, id=request.session['usuario_id']))  # Usamos el id en la sesión
            return redirect('listar_mis_eventos')
    else:
        form = EventoForm(instance=evento)

    return render(request, 'eventos/editar_evento.html', {'form': form, 'evento': evento})
def editar_usuario(request):
    if 'usuario_id' not in request.session:
        return redirect('iniciar_sesion')

    usuario = get_object_or_404(Usuario, id=request.session['usuario_id'])

    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('listar_mis_eventos')  # Redirige a la página deseada después de guardar
    else:
        form = UsuarioForm(instance=usuario)

    return render(request, 'eventos/editar_usuario.html', {'form': form})


from django.db.models import Count
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from .models import RegistroEvento, Evento, Usuario

def dashboard(request):
    # Obtener el ID del evento y del usuario desde la solicitud GET
    event_id = request.GET.get('event_id', 1)  # Por defecto, se usa 1
    user_id = request.GET.get('user_id', 1)    # Por defecto, se usa 1

    # 1. ¿Cuántos usuarios están registrados en un evento específico?
    user_count = RegistroEvento.objects.filter(evento_id=event_id).count()

    # 2. ¿Cuántos eventos se están llevando a cabo este mes?
    now = timezone.now()
    event_count_this_month = Evento.objects.filter(
        fecha_inicio__year=now.year,
        fecha_inicio__month=now.month
    ).count()

    # 3. ¿Quiénes son los usuarios más activos en términos de participación en eventos?
    active_users = Usuario.objects.annotate(participation_count=Count('registros_eventos')).order_by('-participation_count')[:10]

    # 4. ¿Cuántos eventos ha organizado un usuario en particular?
    organized_event_count = Evento.objects.filter(organizador_id=user_id).count()

    context = {
        'user_count': user_count,
        'event_count_this_month': event_count_this_month,
        'active_users': active_users,
        'organized_event_count': organized_event_count,
        'event_id': event_id,
        'user_id': user_id,
    }

    return render(request, 'eventos/dashboard.html', context)


def cancelar_ticket(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)

    if request.method == 'POST':
        numero_ticket = request.POST.get('numero_ticket')
        registro = RegistroEvento.objects.filter(numero_ticket=numero_ticket, evento=evento).first()

        if registro:
            registro.delete()  # Cancela el registro
            messages.success(request, f'Registro con ticket {numero_ticket} cancelado exitosamente.')
        else:
            messages.error(request, f'No se encontró ningún registro con el ticket {numero_ticket} para el evento {evento.nombre}.')
        
        return redirect('ver_evento', evento_id=evento_id) # O redirige a donde necesites

    # Obtén los registros para el evento específico
    registros = RegistroEvento.objects.filter(evento=evento)

    return render(request, 'eventos/cancelar_ticket.html', {'evento': evento, 'registros': registros})



def pago_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)

    if request.method == 'POST':
        # Simula lógica de pago
        tipo_entrada = request.POST.get('tipo_de_entrada')
        pago_exitoso = True  # Cambia esto según tu lógica real de pago si es necesario

        if evento.es_gratuito or tipo_entrada == 'gratuita':
            pago_exitoso = True  # No se requiere pago para eventos gratuitos

        if pago_exitoso:
            usuario = get_object_or_404(Usuario, id=request.session['usuario_id'])
            registro = RegistroEvento.objects.create(
                evento=evento,
                usuario=usuario,
                fecha_registro=timezone.now(),
                tipo_de_entrada=tipo_entrada,
                precio=evento.precio_normal if tipo_entrada == 'normal' else evento.precio_vip,
            )
            registro.numero_ticket = generar_numero_ticket()
            registro.save()

            messages.success(request, f'Te has registrado exitosamente en el evento {evento.nombre}.')
            return redirect('registro_exitoso')
        else:
            messages.error(request, 'El pago no fue exitoso. Intenta de nuevo.')

    return render(request, 'eventos/tarjeta.html', {'evento': evento})


def mis_compras(request):
    # Verifica si el usuario está autenticado a través de la sesión
    if 'usuario_id' not in request.session:
        return redirect('iniciar_sesion')

    # Obtiene el usuario a partir del ID de la sesión
    usuario = get_object_or_404(Usuario, id=request.session['usuario_id'])

    # Obtiene todos los registros de eventos del usuario
    registros = RegistroEvento.objects.filter(usuario=usuario)

    return render(request, 'eventos/mis_compras.html', {
        'registros': registros,
        'usuario_nombre': usuario.nombre,  # Asegúrate de que 'nombre' es el campo correcto
    })
