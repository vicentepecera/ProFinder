from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from django.utils import timezone
from Prueba.models import User, BloqueHorario, Reserva
from categorias.models import Categoria
import json


def tablero(request):
    from Prueba.models import Ramo

    ramos = {
        "M1": [
            "Números: enteros, racionales, porcentaje, potencias y raíces",
            "Álgebra y funciones: expresiones algebraicas, proporcionalidad",
            "Álgebra y funciones: ecuaciones, inecuaciones y función lineal",
            "Álgebra y funciones: función cuadrática",
            "Geometría: figuras y cuerpos geométricos",
            "Geometría: transformaciones isométricas y semejanza",
            "Probabilidad y estadística: tablas, gráficos y medidas de posición",
            "Probabilidad y estadística: reglas de probabilidades",
        ],
        "M2": [
            "Números: reales, matemática financiera y logaritmos",
            "Álgebra y funciones: sistemas de ecuaciones, funciones potencia y exponencial",
            "Álgebra y funciones: funciones trigonométricas",
            "Geometría: homotecia, razones trigonométricas y circunferencia",
            "Geometría: esferas y rectas en el plano",
            "Probabilidad y estadística: medidas de dispersión y probabilidad condicional",
            "Probabilidad y estadística: permutación, combinatoria y modelos probabilísticos",
        ],
        "Competencia Lectora": [
            "Localizar: extraer e identificar información explícita",
            "Interpretar: relaciones, inferencias e ideas principales",
            "Interpretar: función de elementos textuales y recursos literarios",
            "Evaluar: intención comunicativa y juicio de la información",
            "Evaluar: perspectiva, ideología y relación con otros contextos",
            "Textos no literarios: expositivos y argumentativos",
            "Textos literarios: narraciones",
        ],
        "Historia y Cs. Sociales": [
            "Historia: Estado-nación siglo XIX en América, Europa y Chile",
            "Historia: Chile siglo XIX — República, economía y sociedad",
            "Historia: Primera mitad siglo XX — totalitarismos y populismo",
            "Historia: Segunda mitad siglo XX — Guerra Fría y América Latina",
            "Historia: Dictadura Militar (1973-1990) y retorno a la democracia",
            "Formación ciudadana: democracia, institucionalidad y sistema judicial",
            "Sistema económico: mercado, modelos de desarrollo y derechos laborales",
        ],
        "Ciencias - Biología": [
            "Organización, estructura y actividad celular",
            "Procesos y funciones biológicas",
            "Herencia y evolución",
            "Organismo y ambiente",
        ],
        "Ciencias - Física": [
            "Ondas",
            "Mecánica",
            "Energía – Tierra",
            "Electricidad",
        ],
        "Ciencias - Química": [
            "Estructura atómica",
            "Química orgánica",
            "Reacciones químicas y estequiometría",
        ],
    }

    depto_activo = request.GET.get("depto", "")
    ramo_activo  = request.GET.get("ramo", "")

    if depto_activo not in ramos:
        depto_activo = ""
        ramo_activo  = ""

    ramos_del_depto = ramos.get(depto_activo, [])
    if ramo_activo not in ramos_del_depto:
        ramo_activo = ""

    profesores_filtrados = []
    if ramo_activo:
        ramo_obj = Ramo.objects.filter(nombre=ramo_activo).first()
        if ramo_obj:
            usuarios = User.objects.filter(ramos=ramo_obj)
            for u in usuarios:
                profesores_filtrados.append({
                    "id":     u.id,
                    "nombre": u.apodo or u.username,
                    "foto":   u.foto.url if u.foto else None,
                    "ramos":  list(u.ramos.values_list('nombre', flat=True)),
                    "precio": u.precio,
                })

    return render(request, "tablero.html", {
        "titulo":          "¿Para qué prueba necesitas ayuda?",
        "secciones":       list(ramos.keys()),
        "ramos_del_depto": ramos_del_depto,
        "depto_activo":    depto_activo,
        "ramo_activo":     ramo_activo,
        "profesores":      profesores_filtrados,
    })


def register_user(request):
    from Prueba.models import Ramo

    ramos_qs = Ramo.objects.all().order_by('depto', 'nombre')
    ramos_por_depto = {}
    for r in ramos_qs:
        ramos_por_depto.setdefault(r.depto, []).append(r)

    if request.method == 'GET':
        return render(request, "register_user.html", {
            'ramos_por_depto': ramos_por_depto,
        })

    elif request.method == 'POST':
        nombre     = request.POST['nombre']
        contraseña = request.POST['contraseña']
        apodo      = request.POST['apodo']
        mail       = request.POST['mail']
        telefono   = request.POST.get('telefono', '')
        biografia  = request.POST.get('biografia', '')
        tipo       = request.POST.get('tipo', 'estudiante')
        carrera    = request.POST.get('carrera', '')
        empleo     = request.POST.get('empleo', '')
        rol        = request.POST.get('rol', 'estudiante')
        precio     = request.POST.get('precio', 0) or 0
        ramos_ids  = request.POST.getlist('ramos')

        user = User.objects.create_user(
            username=nombre,
            password=contraseña,
            email=mail,
            apodo=apodo,
            telefono=telefono,
            biografia=biografia,
            tipo=tipo,
            carrera=carrera if tipo == 'estudiante' else '',
            empleo=empleo   if tipo == 'trabajador' else '',
            rol=rol,
            precio=int(precio) if rol == 'profesor' else 0,
        )

        if rol == 'profesor' and ramos_ids:
            user.ramos.set(Ramo.objects.filter(id__in=ramos_ids))

        try:
            from Prueba.email_utils import enviar_bienvenida
            enviar_bienvenida(user)
            print(f"[EMAIL] Bienvenida enviada a {user.email}")
        except Exception as e:
            print(f"[EMAIL ERROR] {e}")

        login(request, user)
        return HttpResponseRedirect('/tablero')


def login_user(request):
    if request.method == 'GET':
        return render(request, "login.html")
    if request.method == 'POST':
        username   = request.POST['username']
        contraseña = request.POST['password']
        usuario    = authenticate(username=username, password=contraseña)
        if usuario is not None:
            login(request, usuario)
            return HttpResponseRedirect('/tablero')
        else:
            return render(request, "login.html", {'error': True})


def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')


def perfil(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')

    from Prueba.models import Ramo
    from datetime import date, timedelta

    horas = [f"{h}:00" for h in range(8, 22)]
    dias  = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']

    todos_los_ramos = Ramo.objects.all().order_by('depto', 'nombre')
    ramos_por_depto = {}
    for ramo in todos_los_ramos:
        ramos_por_depto.setdefault(ramo.depto, []).append(ramo)

    mis_ramos_ids     = list(request.user.ramos.values_list('id', flat=True))
    bloques_guardados = BloqueHorario.objects.filter(usuario=request.user).values_list('dia', 'hora')
    horario_guardado  = json.dumps([f"{dia}_{hora}" for dia, hora in bloques_guardados])

    # Semana
    hoy           = date.today()
    semana_offset = max(0, int(request.GET.get('semana', 0)))
    lunes         = hoy - timedelta(days=hoy.weekday()) + timedelta(weeks=semana_offset)
    sabado        = lunes + timedelta(days=5)
    fechas_semana = {
        'Lun': lunes,
        'Mar': lunes + timedelta(days=1),
        'Mié': lunes + timedelta(days=2),
        'Jue': lunes + timedelta(days=3),
        'Vie': lunes + timedelta(days=4),
        'Sáb': lunes + timedelta(days=5),
    }

    hoy = timezone.localdate()

    # Reservas recibidas (como profesor)
    reservas_recibidas = Reserva.objects.filter(
        profesor=request.user
    ).exclude(
        estado='confirmada',
        fecha__lt=hoy
    ).select_related('estudiante').order_by('fecha', 'dia', 'hora')

    # Reservas hechas (como estudiante)
    mis_clases = Reserva.objects.filter(
        estudiante=request.user
    ).exclude(
        estado='confirmada',
        fecha__lt=hoy
    ).select_related('profesor').order_by('fecha', 'hora')

    # Reservas de esta semana para pintar el horario (como profesor)
    reservas_semana_prof = Reserva.objects.filter(
        profesor=request.user,
        fecha__in=list(fechas_semana.values()),
    )
    reservas_confirmadas_json = json.dumps([
        f"{r.dia}_{r.hora}" for r in reservas_semana_prof if r.estado == 'confirmada'
    ])
    reservas_pendientes_json = json.dumps([
        f"{r.dia}_{r.hora}" for r in reservas_semana_prof if r.estado == 'pendiente'
    ])
    bloques_ocupados_json = json.dumps([
        f"{r.dia}_{r.hora}" for r in reservas_semana_prof
        if r.estado in ('pendiente', 'confirmada')
    ])

    # Reservas del estudiante en esta semana (para pintar horario de estudiante)
    reservas_semana_est = Reserva.objects.filter(
        estudiante=request.user,
        fecha__in=list(fechas_semana.values()),
    ).values('dia', 'hora', 'estado')
    mis_reservas_semana_json = json.dumps(list(reservas_semana_est))

    # Tiene alguna reserva como estudiante (para decidir si mostrar horario o bienvenida)
    tiene_reservas_como_estudiante = Reserva.objects.filter(
        estudiante=request.user
    ).exists()

    # Estudiantes con hora confirmada vigente con este profesor
    mis_estudiantes = User.objects.filter(
        reservas_hechas__profesor=request.user,
        reservas_hechas__estado='confirmada',
        reservas_hechas__fecha__gte=hoy,
    ).distinct()

    # Profesores con hora confirmada vigente para el estudiante
    mis_profesores = User.objects.filter(
        reservas_recibidas__estudiante=request.user,
        reservas_recibidas__estado='confirmada',
        reservas_recibidas__fecha__gte=hoy,
    ).distinct()

    return render(request, 'perfil.html', {
        'user':               request.user,
        'horas':              horas,
        'dias':               dias,
        'horario_guardado':   horario_guardado,
        'ramos_por_depto':    ramos_por_depto,
        'mis_ramos_ids':      mis_ramos_ids,
        'reservas_recibidas': reservas_recibidas,
        'mis_estudiantes':    mis_estudiantes,
        'mis_profesores':     mis_profesores,
        'mis_clases':         mis_clases,
        'reservas_json':      reservas_confirmadas_json,
        'pendientes_json':    reservas_pendientes_json,
        'bloques_ocupados_json': bloques_ocupados_json,
        'mis_reservas_semana_json': mis_reservas_semana_json,
        'tiene_reservas_como_estudiante': tiene_reservas_como_estudiante,
        'fechas_semana':      {k: v.isoformat() for k, v in fechas_semana.items()},
        'semana_offset':      semana_offset,
        'lunes':              lunes,
        'sabado':             sabado,
    })


def perfil_publico(request, user_id):
    from Prueba.models import Ramo
    from datetime import date, timedelta

    profesor = User.objects.filter(id=user_id).first()
    if not profesor:
        return HttpResponseRedirect('/tablero')

    horas = [f"{h}:00" for h in range(8, 22)]
    dias  = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']

    hoy           = date.today()
    semana_offset = max(0, int(request.GET.get('semana', 0)))
    lunes         = hoy - timedelta(days=hoy.weekday()) + timedelta(weeks=semana_offset)
    sabado        = lunes + timedelta(days=5)
    fechas_semana = {
        'Lun': lunes,
        'Mar': lunes + timedelta(days=1),
        'Mié': lunes + timedelta(days=2),
        'Jue': lunes + timedelta(days=3),
        'Vie': lunes + timedelta(days=4),
        'Sáb': lunes + timedelta(days=5),
    }

    bloques = BloqueHorario.objects.filter(usuario=profesor).values_list('dia', 'hora')
    horario = json.dumps([f"{dia}_{hora}" for dia, hora in bloques])

    reservas_semana = Reserva.objects.filter(
        profesor=profesor,
        fecha__in=list(fechas_semana.values()),
    )
    reservas_json   = json.dumps([
        f"{r.dia}_{r.hora}" for r in reservas_semana if r.estado == 'confirmada'
    ])
    pendientes_json = json.dumps([
        f"{r.dia}_{r.hora}" for r in reservas_semana if r.estado == 'pendiente'
    ])

    mis_reservas     = []
    tiene_confirmada = False
    if request.user.is_authenticated:
        hoy = timezone.localdate()
        qs = Reserva.objects.filter(
            profesor=profesor,
            estudiante=request.user
        ).exclude(
            estado='confirmada',
            fecha__lt=hoy
        ).order_by('fecha', 'hora').values('dia', 'hora', 'fecha', 'estado')

        mis_reservas = list(qs)
        for r in mis_reservas:
            r['fecha_display'] = r['fecha'].strftime('%d/%m/%Y') if r['fecha'] else '—'

        tiene_confirmada = any(r['estado'] == 'confirmada' for r in mis_reservas)

    ORDEN_DEPTOS = [
        'M1', 'M2', 'Competencia Lectora', 'Historia y Cs. Sociales',
        'Ciencias - Biología', 'Ciencias - Física', 'Ciencias - Química'
    ]
    ramos_ordenados = sorted(
        profesor.ramos.all(),
        key=lambda r: (
            ORDEN_DEPTOS.index(r.depto) if r.depto in ORDEN_DEPTOS else 99,
            r.nombre
        )
    )

    es_mi_perfil = request.user.is_authenticated and request.user.id == profesor.id

    return render(request, 'perfil_publico.html', {
        'profesor':          profesor,
        'ramos_ordenados':   ramos_ordenados,
        'horas':             horas,
        'dias':              dias,
        'horario_guardado':  horario,
        'reservas':          reservas_json,
        'pendientes':        pendientes_json,
        'mis_reservas':      mis_reservas,
        'tiene_confirmada':  tiene_confirmada,
        'es_mi_perfil':      es_mi_perfil,
        'profesor_id':       profesor.id,
        'fechas_semana':     {k: v.isoformat() for k, v in fechas_semana.items()},
        'semana_offset':     semana_offset,
        'lunes':             lunes,
        'sabado':            sabado,
    })


@require_POST
def guardar_horario(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'}, status=401)

    data    = json.loads(request.body)
    bloques = data.get('bloques', [])

    ocupados = set(
        f"{r.dia}_{r.hora}" for r in Reserva.objects.filter(
            profesor=request.user,
            estado__in=('pendiente', 'confirmada')
        )
    )

    BloqueHorario.objects.filter(usuario=request.user).delete()
    for bloque in bloques:
        try:
            dia, hora = bloque.split('_', 1)
            BloqueHorario.objects.create(usuario=request.user, dia=dia, hora=hora)
        except ValueError:
            pass

    for clave in ocupados:
        try:
            dia, hora = clave.split('_', 1)
            BloqueHorario.objects.get_or_create(usuario=request.user, dia=dia, hora=hora)
        except Exception:
            pass

    return JsonResponse({'ok': True})


@require_POST
def guardar_ramos(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'}, status=401)

    from Prueba.models import Ramo
    data   = json.loads(request.body)
    ids    = data.get('ramos', [])
    precio = data.get('precio', 0)

    request.user.ramos.set(Ramo.objects.filter(id__in=ids))
    request.user.precio = precio
    request.user.save()

    return JsonResponse({'ok': True})


@require_POST
def guardar_datos(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'}, status=401)

    data      = json.loads(request.body)
    telefono  = data.get('telefono', '')
    biografia = data.get('biografia', '')
    tipo      = data.get('tipo', 'estudiante')
    carrera   = data.get('carrera', '')
    empleo    = data.get('empleo', '')

    request.user.telefono  = telefono
    request.user.biografia = biografia
    request.user.tipo      = tipo
    request.user.carrera   = carrera if tipo == 'estudiante' else ''
    request.user.empleo    = empleo  if tipo == 'trabajador' else ''
    request.user.save()

    return JsonResponse({'ok': True})


@require_POST
def guardar_cursos(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'}, status=401)

    from Prueba.models import Ramo
    data = json.loads(request.body)
    ids  = data.get('cursos', [])
    request.user.ramos_tomados.set(Ramo.objects.filter(id__in=ids))
    return JsonResponse({'ok': True})


@require_POST
def agendar_hora(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'}, status=401)

    from datetime import date
    from Prueba.models import Notificacion

    data        = json.loads(request.body)
    profesor_id = data.get('profesor_id')
    dia         = data.get('dia')
    hora        = data.get('hora')
    fecha_str   = data.get('fecha')

    profesor = User.objects.filter(id=profesor_id).first()
    if not profesor:
        return JsonResponse({'error': 'Profesor no encontrado'}, status=404)

    if not BloqueHorario.objects.filter(usuario=profesor, dia=dia, hora=hora).exists():
        return JsonResponse({'error': 'Bloque no disponible'}, status=400)

    try:
        fecha = date.fromisoformat(fecha_str)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Fecha inválida'}, status=400)

    if Reserva.objects.filter(
        profesor=profesor, fecha=fecha, hora=hora,
        estado__in=('pendiente', 'confirmada')
    ).exists():
        return JsonResponse({'error': 'Ya reservado para esa fecha'}, status=400)

    Reserva.objects.create(
        profesor=profesor,
        estudiante=request.user,
        dia=dia,
        hora=hora,
        fecha=fecha,
    )

    Notificacion.objects.create(
        usuario=request.user,
        tipo='reserva_creada',
        mensaje=f"Reservaste una clase con {profesor.apodo or profesor.username} "
                f"el {fecha.strftime('%d/%m/%Y')} ({dia}) a las {hora}. "
                f"Precio acordado: ${profesor.precio:,}/hr. "
                f"Esperando confirmación del profesor."
    )
    Notificacion.objects.create(
        usuario=profesor,
        tipo='reserva_creada',
        mensaje=f"{request.user.apodo or request.user.username} reservó una clase contigo "
                f"el {fecha.strftime('%d/%m/%Y')} ({dia}) a las {hora}. "
                f"Precio: ${profesor.precio:,}/hr."
    )

    return JsonResponse({'ok': True})


@require_POST
def gestionar_reserva(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'}, status=401)

    from Prueba.models import Notificacion

    data       = json.loads(request.body)
    reserva_id = data.get('reserva_id')
    accion     = data.get('accion')

    reserva = Reserva.objects.filter(id=reserva_id, profesor=request.user).first()
    if not reserva:
        return JsonResponse({'error': 'Reserva no encontrada'}, status=404)

    if accion == 'confirmar':
        reserva.estado = 'confirmada'
    elif accion == 'cancelar':
        reserva.estado = 'cancelada'
    else:
        return JsonResponse({'error': 'Acción inválida'}, status=400)

    reserva.save()

    if accion == 'confirmar':
        Notificacion.objects.create(
            usuario=reserva.estudiante,
            tipo='reserva_confirmada',
            mensaje=f"Tu clase con {reserva.profesor.apodo or reserva.profesor.username} "
                    f"el {reserva.fecha.strftime('%d/%m/%Y')} ({reserva.dia}) a las {reserva.hora} "
                    f"fue confirmada. Precio: ${reserva.profesor.precio:,}/hr."
        )
    elif accion == 'cancelar':
        Notificacion.objects.create(
            usuario=reserva.estudiante,
            tipo='reserva_cancelada',
            mensaje=f"Tu clase con {reserva.profesor.apodo or reserva.profesor.username} "
                    f"el {reserva.fecha.strftime('%d/%m/%Y')} ({reserva.dia}) a las {reserva.hora} "
                    f"fue rechazada."
        )

    return JsonResponse({'ok': True})


def notificaciones(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')

    from Prueba.models import Notificacion
    notifs = Notificacion.objects.filter(usuario=request.user)
    notifs.filter(leida=False).update(leida=True)

    return render(request, 'notificaciones.html', {
        'notificaciones': notifs,
    })


def notificaciones_count(request):
    if not request.user.is_authenticated:
        return JsonResponse({'count': 0})
    from Prueba.models import Notificacion
    count = Notificacion.objects.filter(usuario=request.user, leida=False).count()
    return JsonResponse({'count': count})

def inicio(request):
    return render(request, 'inicio.html')

def admin_usuarios(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return HttpResponseRedirect('/login')

    rol_filtro  = request.GET.get('rol', '')
    tipo_filtro = request.GET.get('tipo', '')
    busqueda    = request.GET.get('q', '').strip()

    usuarios = User.objects.all().order_by('-date_joined')

    if rol_filtro:
        usuarios = usuarios.filter(rol=rol_filtro)
    if tipo_filtro:
        usuarios = usuarios.filter(tipo=tipo_filtro)
    if busqueda:
        from django.db.models import Q
        usuarios = usuarios.filter(
            Q(username__icontains=busqueda) |
            Q(apodo__icontains=busqueda) |
            Q(email__icontains=busqueda)
        )

    return render(request, 'admin_usuarios.html', {
        'usuarios':    usuarios,
        'rol_filtro':  rol_filtro,
        'tipo_filtro': tipo_filtro,
        'busqueda':    busqueda,
        'total':       User.objects.count(),
        'total_prof':  User.objects.filter(rol='profesor').count(),
        'total_est':   User.objects.filter(rol='estudiante').count(),
    })


def mis_profesores(request):
    if not request.user.is_authenticated:
        return JsonResponse({'profesores': []})

    reservas = Reserva.objects.filter(
        estudiante=request.user,
        estado='confirmada'
    ).select_related('profesor').distinct()

    vistos = set()
    profesores = []
    for r in reservas:
        if r.profesor.id not in vistos:
            vistos.add(r.profesor.id)
            profesores.append({
                'id':     r.profesor.id,
                'nombre': r.profesor.apodo or r.profesor.username,
                'foto':   r.profesor.foto.url if r.profesor.foto else None,
                'ramos':  list(r.profesor.ramos.values_list('nombre', flat=True)),
                'precio': r.profesor.precio,
            })

    return JsonResponse({'profesores': profesores})

@require_POST
def subir_foto(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'}, status=401)
    foto = request.FILES.get('foto')
    if not foto:
        return JsonResponse({'error': 'No se recibió imagen'}, status=400)
    if not foto.content_type.startswith('image/'):
        return JsonResponse({'error': 'El archivo debe ser una imagen'}, status=400)
    if foto.size > 5 * 1024 * 1024:
        return JsonResponse({'error': 'La imagen no puede superar 5 MB'}, status=400)
    request.user.foto = foto
    request.user.save()
    return JsonResponse({'url': request.user.foto.url})


def recuperar_contrasena(request):
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.encoding import force_bytes
    from django.utils.http import urlsafe_base64_encode
    from Prueba.email_utils import enviar_recuperacion

    if request.method == 'GET':
        return render(request, 'recuperar_contrasena.html', {})

    email = request.POST.get('email', '').strip()
    user  = User.objects.filter(email=email).first()
    if user:
        uid   = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        try:
            enviar_recuperacion(user, token, uid)
        except Exception:
            pass
    # Siempre muestra la misma pantalla para no revelar si el email existe
    return render(request, 'recuperar_contrasena.html', {'enviado': True})


def recuperar_contrasena_confirmar(request, uid64, token):
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.encoding import force_str
    from django.utils.http import urlsafe_base64_decode

    try:
        uid  = force_str(urlsafe_base64_decode(uid64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, OverflowError):
        user = None

    token_valido = user is not None and default_token_generator.check_token(user, token)

    if request.method == 'GET':
        return render(request, 'recuperar_contrasena_confirmar.html', {'valido': token_valido})

    if not token_valido:
        return render(request, 'recuperar_contrasena_confirmar.html', {'valido': False})

    nueva = request.POST.get('password', '')
    confirmar = request.POST.get('password2', '')
    if len(nueva) < 8:
        return render(request, 'recuperar_contrasena_confirmar.html', {
            'valido': True, 'error': 'La contraseña debe tener al menos 8 caracteres.'
        })
    if nueva != confirmar:
        return render(request, 'recuperar_contrasena_confirmar.html', {
            'valido': True, 'error': 'Las contraseñas no coinciden.'
        })
    user.set_password(nueva)
    user.save()
    return render(request, 'recuperar_contrasena_confirmar.html', {'exito': True})
