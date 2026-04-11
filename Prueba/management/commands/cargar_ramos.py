from django.core.management.base import BaseCommand
from Prueba.models import Ramo

class Command(BaseCommand):
    help = 'Carga los ramos PAES iniciales'

    def handle(self, *args, **kwargs):
        ramos = [
            # M1
            ('Números: enteros, racionales, porcentaje, potencias y raíces', 'M1'),
            ('Álgebra y funciones: expresiones algebraicas, proporcionalidad', 'M1'),
            ('Álgebra y funciones: ecuaciones, inecuaciones y función lineal', 'M1'),
            ('Álgebra y funciones: función cuadrática', 'M1'),
            ('Geometría: figuras y cuerpos geométricos', 'M1'),
            ('Geometría: transformaciones isométricas y semejanza', 'M1'),
            ('Probabilidad y estadística: tablas, gráficos y medidas de posición', 'M1'),
            ('Probabilidad y estadística: reglas de probabilidades', 'M1'),
            # M2
            ('Números: reales, matemática financiera y logaritmos', 'M2'),
            ('Álgebra y funciones: sistemas de ecuaciones, funciones potencia y exponencial', 'M2'),
            ('Álgebra y funciones: funciones trigonométricas', 'M2'),
            ('Geometría: homotecia, razones trigonométricas y circunferencia', 'M2'),
            ('Geometría: esferas y rectas en el plano', 'M2'),
            ('Probabilidad y estadística: medidas de dispersión y probabilidad condicional', 'M2'),
            ('Probabilidad y estadística: permutación, combinatoria y modelos probabilísticos', 'M2'),
            # Competencia Lectora
            ('Localizar: extraer e identificar información explícita', 'Competencia Lectora'),
            ('Interpretar: relaciones, inferencias e ideas principales', 'Competencia Lectora'),
            ('Interpretar: función de elementos textuales y recursos literarios', 'Competencia Lectora'),
            ('Evaluar: intención comunicativa y juicio de la información', 'Competencia Lectora'),
            ('Evaluar: perspectiva, ideología y relación con otros contextos', 'Competencia Lectora'),
            ('Textos no literarios: expositivos y argumentativos', 'Competencia Lectora'),
            ('Textos literarios: narraciones', 'Competencia Lectora'),
            # Historia
            ('Historia: Estado-nación siglo XIX en América, Europa y Chile', 'Historia y Cs. Sociales'),
            ('Historia: Chile siglo XIX — República, economía y sociedad', 'Historia y Cs. Sociales'),
            ('Historia: Primera mitad siglo XX — totalitarismos y populismo', 'Historia y Cs. Sociales'),
            ('Historia: Segunda mitad siglo XX — Guerra Fría y América Latina', 'Historia y Cs. Sociales'),
            ('Historia: Dictadura Militar (1973-1990) y retorno a la democracia', 'Historia y Cs. Sociales'),
            ('Formación ciudadana: democracia, institucionalidad y sistema judicial', 'Historia y Cs. Sociales'),
            ('Sistema económico: mercado, modelos de desarrollo y derechos laborales', 'Historia y Cs. Sociales'),
            # Biología
            ('Organización, estructura y actividad celular', 'Ciencias - Biología'),
            ('Procesos y funciones biológicas', 'Ciencias - Biología'),
            ('Herencia y evolución', 'Ciencias - Biología'),
            ('Organismo y ambiente', 'Ciencias - Biología'),
            # Física
            ('Ondas', 'Ciencias - Física'),
            ('Mecánica', 'Ciencias - Física'),
            ('Energía – Tierra', 'Ciencias - Física'),
            ('Electricidad', 'Ciencias - Física'),
            # Química
            ('Estructura atómica', 'Ciencias - Química'),
            ('Química orgánica', 'Ciencias - Química'),
            ('Reacciones químicas y estequiometría', 'Ciencias - Química'),
        ]

        creados = 0
        for nombre, depto in ramos:
            _, created = Ramo.objects.get_or_create(nombre=nombre, depto=depto)
            if created:
                creados += 1

        self.stdout.write(self.style.SUCCESS(f'{creados} ramos creados.'))