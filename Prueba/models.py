from django.db import models
from django.utils import timezone
from categorias.models import Categoria
from django.contrib.auth.models import AbstractUser

class Ramo(models.Model):
    DEPTOS = [
        ('M1', 'M1'),
        ('M2', 'M2'),
        ('Competencia Lectora', 'Competencia Lectora'),
        ('Historia y Cs. Sociales', 'Historia y Cs. Sociales'),
        ('Ciencias - Biología', 'Ciencias - Biología'),
        ('Ciencias - Física', 'Ciencias - Física'),
        ('Ciencias - Química', 'Ciencias - Química'),
    ]
    nombre = models.CharField(max_length=100)
    depto  = models.CharField(max_length=30, choices=DEPTOS)

    def __str__(self):
        return self.nombre

class User(AbstractUser):
    TIPO_CHOICES = [
        ('estudiante', 'Estudiante'),
        ('trabajador', 'Trabajador'),
    ]
    CARRERAS = [
        ('ing_civil', 'Ingeniería Civil'),
        ('ing_comercial', 'Ingeniería Comercial'),
        ('medicina', 'Medicina'),
        ('derecho', 'Derecho'),
        ('psicologia', 'Psicología'),
        ('pedagogia', 'Pedagogía'),
        ('arquitectura', 'Arquitectura'),
        ('administracion', 'Administración de Empresas'),
        ('otro', 'Otro'),
    ]
    EMPLEOS = [
        ('profesor', 'Profesor/a'),
        ('ingeniero', 'Ingeniero/a'),
        ('medico', 'Médico/a'),
        ('abogado', 'Abogado/a'),
        ('contador', 'Contador/a'),
        ('diseñador', 'Diseñador/a'),
        ('estudiante_posgrado', 'Estudiante de posgrado'),
        ('otro', 'Otro'),
    ]

    ROL_CHOICES = [
    ('estudiante', 'Estudiante'),
    ('profesor', 'Profesor'),
]

    rol           = models.CharField(max_length=15, choices=ROL_CHOICES, default='estudiante')
    ramos_tomados = models.ManyToManyField('Ramo', blank=True, related_name='estudiantes')

    apodo     = models.CharField(max_length=30)
    foto      = models.TextField(blank=True, default='')
    ramos     = models.ManyToManyField(Ramo, blank=True)
    precio    = models.IntegerField(default=0)
    telefono  = models.CharField(max_length=20, blank=True, default='')
    biografia = models.TextField(max_length=300, blank=True, default='')
    tipo      = models.CharField(max_length=20, choices=TIPO_CHOICES, default='estudiante')
    carrera   = models.CharField(max_length=30, choices=CARRERAS, blank=True, default='')
    empleo    = models.CharField(max_length=30, choices=EMPLEOS, blank=True, default='')

class BloqueHorario(models.Model):
    DIAS = [('Lun','Lun'),('Mar','Mar'),('Mié','Mié'),('Jue','Jue'),('Vie','Vie'),('Sáb','Sáb')]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='horario')
    dia     = models.CharField(max_length=5, choices=DIAS)
    hora    = models.CharField(max_length=10)

    class Meta:
        unique_together = ('usuario', 'dia', 'hora')

    def __str__(self):
        return f"{self.usuario.username} - {self.dia} {self.hora}"

from datetime import date

class Reserva(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    ]
    profesor   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservas_recibidas')
    estudiante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservas_hechas')
    dia        = models.CharField(max_length=5)
    hora       = models.CharField(max_length=10)
    fecha      = models.DateField(null=True, blank=True)  # fecha exacta del bloque
    estado     = models.CharField(max_length=15, choices=ESTADOS, default='pendiente')
    creada_el  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profesor', 'fecha', 'hora')

    def __str__(self):
        return f"{self.estudiante.username} → {self.profesor.username} {self.fecha} {self.hora}"

class Resena(models.Model):
    profesor   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resenas_recibidas')
    estudiante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resenas_hechas')
    puntaje    = models.IntegerField()
    comentario = models.TextField(blank=True, default='')
    creada_el  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profesor', 'estudiante')

    def __str__(self):
        return f"{self.estudiante.username} → {self.profesor.username} ({self.puntaje}★)"


class Notificacion(models.Model):
    TIPOS = [
        ('reserva_creada', 'Reserva creada'),
        ('reserva_confirmada', 'Reserva confirmada'),
        ('reserva_cancelada', 'Reserva cancelada'),
    ]
    usuario   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    tipo      = models.CharField(max_length=30, choices=TIPOS)
    mensaje   = models.TextField()
    leida     = models.BooleanField(default=False)
    creada_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creada_el']

    def __str__(self):
        return f"{self.usuario.username} — {self.tipo}"