# 🎮 PLAN DE IMPLEMENTACIÓN: Sistema de Gamificación

## 📅 Tiempo estimado: 1 semana
## 🎯 Objetivo: Implementar sistema completo de logros, niveles y puntos

---

## 📋 FASE 1: MODELOS (Día 1)

### Nuevos Modelos en `models.py`:

```python
class PerfilUsuario(models.Model):
    """Perfil extendido del usuario con gamificación"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Gamificación
    puntos_totales = models.IntegerField(default=0)
    nivel = models.IntegerField(default=1)
    experiencia_nivel_actual = models.IntegerField(default=0)
    
    # Estadísticas
    dias_consecutivos = models.IntegerField(default=0)
    ultima_actividad = models.DateField(auto_now=True)
    fecha_registro_app = models.DateField(auto_now_add=True)
    total_gastos_registrados = models.IntegerField(default=0)
    total_ahorrado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Racha
    racha_actual = models.IntegerField(default=0)
    mejor_racha = models.IntegerField(default=0)
    
    def calcular_nivel(self):
        """Calcula nivel basado en puntos"""
        niveles = {
            1: 0, 2: 100, 3: 300, 4: 600, 5: 1000,
            6: 1500, 7: 2100, 8: 2800, 9: 3600, 10: 5000
        }
        for nivel, puntos_req in sorted(niveles.items(), reverse=True):
            if self.puntos_totales >= puntos_req:
                return nivel
        return 1
    
    def agregar_puntos(self, puntos, razon):
        """Agrega puntos y registra el logro"""
        self.puntos_totales += puntos
        nivel_anterior = self.nivel
        self.nivel = self.calcular_nivel()
        self.save()
        
        # Registrar historial
        HistorialPuntos.objects.create(
            perfil=self,
            puntos=puntos,
            razon=razon
        )
        
        # Si subió de nivel, crear notificación
        if self.nivel > nivel_anterior:
            NotificacionLogro.objects.create(
                perfil=self,
                tipo='NIVEL',
                mensaje=f'¡Felicitaciones! Alcanzaste el nivel {self.nivel}'
            )


class Logro(models.Model):
    """Catálogo de logros disponibles"""
    TIPO_LOGRO = [
        ('ACTIVIDAD', 'Actividad Diaria'),
        ('AHORRO', 'Ahorro'),
        ('DISCIPLINA', 'Disciplina Financiera'),
        ('SOCIAL', 'Social'),
        ('ESPECIAL', 'Especial'),
    ]
    
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_LOGRO)
    puntos_recompensa = models.IntegerField(default=10)
    icono = models.CharField(max_length=50, default='🏆')
    requisito_numero = models.IntegerField(default=1, help_text="Ej: 7 días, 3 meses, $50000")
    requisito_tipo = models.CharField(max_length=50, help_text="dias_consecutivos, meses_cumplidos, monto_ahorrado")
    activo = models.BooleanField(default=True)
    es_secreto = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Logro"
        verbose_name_plural = "Logros"
    
    def __str__(self):
        return f"{self.icono} {self.nombre} ({self.puntos_recompensa} pts)"


class LogroDesbloqueado(models.Model):
    """Logros que ha desbloqueado cada usuario"""
    perfil = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name='logros')
    logro = models.ForeignKey(Logro, on_delete=models.CASCADE)
    fecha_desbloqueo = models.DateTimeField(auto_now_add=True)
    visto = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('perfil', 'logro')
        ordering = ['-fecha_desbloqueo']


class DesafioMensual(models.Model):
    """Desafíos especiales cada mes"""
    ESTADO = [
        ('ACTIVO', 'Activo'),
        ('FINALIZADO', 'Finalizado'),
        ('PROXIMO', 'Próximo'),
    ]
    
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    mes = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    anio = models.IntegerField()
    icono = models.CharField(max_length=50, default='🎯')
    puntos_premio = models.IntegerField(default=150)
    
    # Requisitos
    meta_reduccion_categoria = models.CharField(max_length=50, blank=True)
    meta_porcentaje = models.IntegerField(default=0)
    meta_monto = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    estado = models.CharField(max_length=20, choices=ESTADO, default='PROXIMO')
    
    def __str__(self):
        return f"{self.icono} {self.nombre} ({self.mes}/{self.anio})"


class ParticipacionDesafio(models.Model):
    """Participación de usuarios en desafíos"""
    perfil = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE)
    desafio = models.ForeignKey(DesafioMensual, on_delete=models.CASCADE)
    completado = models.BooleanField(default=False)
    progreso_porcentaje = models.IntegerField(default=0)
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_completado = models.DateField(null=True, blank=True)
    
    class Meta:
        unique_together = ('perfil', 'desafio')


class HistorialPuntos(models.Model):
    """Historial de puntos ganados"""
    perfil = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name='historial_puntos')
    puntos = models.IntegerField()
    razon = models.CharField(max_length=200)
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha']


class NotificacionLogro(models.Model):
    """Notificaciones de logros y niveles"""
    TIPO = [
        ('LOGRO', 'Logro Desbloqueado'),
        ('NIVEL', 'Subida de Nivel'),
        ('DESAFIO', 'Desafío Completado'),
        ('RACHA', 'Racha Alcanzada'),
    ]
    
    perfil = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name='notificaciones_logro')
    tipo = models.CharField(max_length=20, choices=TIPO)
    mensaje = models.CharField(max_length=200)
    visto = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha']
```

---

## 📋 FASE 2: CATÁLOGO DE LOGROS (Día 2)

### Script de inicialización `crear_logros_iniciales.py`:

```python
from gastos.models import Logro

logros_iniciales = [
    # ACTIVIDAD DIARIA
    {
        'codigo': 'primera_semana',
        'nombre': 'Primera Semana',
        'descripcion': 'Registra gastos durante 7 días consecutivos',
        'tipo': 'ACTIVIDAD',
        'puntos_recompensa': 10,
        'icono': '🏆',
        'requisito_numero': 7,
        'requisito_tipo': 'dias_consecutivos'
    },
    {
        'codigo': 'mes_completo',
        'nombre': 'Mes Completo',
        'descripcion': 'Registra gastos todos los días durante 30 días',
        'tipo': 'ACTIVIDAD',
        'puntos_recompensa': 50,
        'icono': '📅',
        'requisito_numero': 30,
        'requisito_tipo': 'dias_consecutivos'
    },
    {
        'codigo': 'racha_100',
        'nombre': 'Racha Imparable',
        'descripcion': 'Alcanza una racha de 100 días',
        'tipo': 'ACTIVIDAD',
        'puntos_recompensa': 200,
        'icono': '🔥',
        'requisito_numero': 100,
        'requisito_tipo': 'dias_consecutivos'
    },
    
    # AHORRO
    {
        'codigo': 'ahorrador_novato',
        'nombre': 'Ahorrador Novato',
        'descripcion': 'Ahorra $50,000 en un mes',
        'tipo': 'AHORRO',
        'puntos_recompensa': 25,
        'icono': '💰',
        'requisito_numero': 50000,
        'requisito_tipo': 'monto_ahorrado_mes'
    },
    {
        'codigo': 'ahorrador_experto',
        'nombre': 'Ahorrador Experto',
        'descripcion': 'Ahorra $200,000 en un mes',
        'tipo': 'AHORRO',
        'puntos_recompensa': 75,
        'icono': '💎',
        'requisito_numero': 200000,
        'requisito_tipo': 'monto_ahorrado_mes'
    },
    {
        'codigo': 'millonario',
        'nombre': 'Millonario',
        'descripcion': 'Acumula $1,000,000 en ahorros totales',
        'tipo': 'AHORRO',
        'puntos_recompensa': 200,
        'icono': '🏅',
        'requisito_numero': 1000000,
        'requisito_tipo': 'ahorro_acumulado'
    },
    
    # DISCIPLINA
    {
        'codigo': 'precision',
        'nombre': 'Precisión',
        'descripcion': 'Cumple tu presupuesto 3 meses seguidos',
        'tipo': 'DISCIPLINA',
        'puntos_recompensa': 50,
        'icono': '🎯',
        'requisito_numero': 3,
        'requisito_tipo': 'meses_cumplidos'
    },
    {
        'codigo': 'disciplina_acero',
        'nombre': 'Disciplina de Acero',
        'descripcion': '6 meses sin sobrepasar presupuesto',
        'tipo': 'DISCIPLINA',
        'puntos_recompensa': 300,
        'icono': '🛡️',
        'requisito_numero': 6,
        'requisito_tipo': 'meses_cumplidos'
    },
    
    # SOCIAL
    {
        'codigo': 'analista',
        'nombre': 'Analista',
        'descripcion': 'Revisa tu dashboard 30 veces',
        'tipo': 'SOCIAL',
        'puntos_recompensa': 15,
        'icono': '📊',
        'requisito_numero': 30,
        'requisito_tipo': 'visitas_dashboard'
    },
    
    # ESPECIALES
    {
        'codigo': 'tentacion_resistida',
        'nombre': 'Tentación Resistida',
        'descripcion': 'Marca un gasto como "evitado"',
        'tipo': 'ESPECIAL',
        'puntos_recompensa': 20,
        'icono': '🚫',
        'requisito_numero': 1,
        'requisito_tipo': 'gastos_evitados'
    },
    {
        'codigo': 'madrugador',
        'nombre': 'Madrugador Financiero',
        'descripcion': 'Registra un gasto antes de las 7 AM',
        'tipo': 'ESPECIAL',
        'puntos_recompensa': 5,
        'icono': '🌅',
        'requisito_numero': 1,
        'requisito_tipo': 'gasto_madrugador',
        'es_secreto': True
    },
]

# Crear todos los logros
for logro_data in logros_iniciales:
    Logro.objects.get_or_create(
        codigo=logro_data['codigo'],
        defaults=logro_data
    )
```

---

## 📋 FASE 3: LÓGICA DE VERIFICACIÓN (Día 3)

### Servicio de gamificación `gamificacion_service.py`:

```python
from django.utils import timezone
from datetime import timedelta
from .models import (
    PerfilUsuario, Logro, LogroDesbloqueado, 
    NotificacionLogro, HistorialPuntos
)

class GamificacionService:
    
    @staticmethod
    def verificar_logros_usuario(user):
        """Verifica todos los logros posibles para un usuario"""
        perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
        logros_nuevos = []
        
        # Obtener todos los logros activos no desbloqueados
        logros_disponibles = Logro.objects.filter(activo=True).exclude(
            id__in=perfil.logros.values_list('logro_id', flat=True)
        )
        
        for logro in logros_disponibles:
            if GamificacionService._cumple_requisito(perfil, logro):
                # Desbloquear logro
                logro_desbloqueado = LogroDesbloqueado.objects.create(
                    perfil=perfil,
                    logro=logro
                )
                
                # Agregar puntos
                perfil.agregar_puntos(
                    logro.puntos_recompensa,
                    f'Logro desbloqueado: {logro.nombre}'
                )
                
                # Crear notificación
                NotificacionLogro.objects.create(
                    perfil=perfil,
                    tipo='LOGRO',
                    mensaje=f'¡Desbloqueaste {logro.icono} {logro.nombre}! +{logro.puntos_recompensa} puntos'
                )
                
                logros_nuevos.append(logro)
        
        return logros_nuevos
    
    @staticmethod
    def _cumple_requisito(perfil, logro):
        """Verifica si cumple el requisito de un logro específico"""
        tipo_req = logro.requisito_tipo
        valor_req = logro.requisito_numero
        
        if tipo_req == 'dias_consecutivos':
            return perfil.racha_actual >= valor_req
            
        elif tipo_req == 'monto_ahorrado_mes':
            # Calcular ahorro del mes actual
            from .models import Gasto
            mes_actual = timezone.now().month
            anio_actual = timezone.now().year
            
            total_gastos = Gasto.objects.filter(
                familia=perfil.user.familia_set.first(),
                fecha__month=mes_actual,
                fecha__year=anio_actual
            ).aggregate(total=Sum('monto'))['total'] or 0
            
            # Asumir ingreso fijo (debería venir del modelo)
            ingreso_mensual = 3500000  # TODO: obtener de perfil
            ahorro = ingreso_mensual - total_gastos
            
            return ahorro >= valor_req
            
        elif tipo_req == 'ahorro_acumulado':
            return perfil.total_ahorrado >= valor_req
            
        elif tipo_req == 'meses_cumplidos':
            # TODO: implementar lógica de meses cumplidos
            return False
            
        elif tipo_req == 'visitas_dashboard':
            # TODO: implementar contador de visitas
            return False
            
        elif tipo_req == 'gastos_evitados':
            # TODO: implementar funcionalidad de gastos evitados
            return False
        
        return False
    
    @staticmethod
    def actualizar_racha(user):
        """Actualiza la racha de días consecutivos"""
        perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
        hoy = timezone.now().date()
        
        # Si última actividad fue ayer, incrementar racha
        if perfil.ultima_actividad == hoy - timedelta(days=1):
            perfil.racha_actual += 1
            if perfil.racha_actual > perfil.mejor_racha:
                perfil.mejor_racha = perfil.racha_actual
                
        # Si última actividad fue hoy, no hacer nada
        elif perfil.ultima_actividad == hoy:
            pass
            
        # Si fue antes de ayer, resetear racha
        else:
            perfil.racha_actual = 1
        
        perfil.ultima_actividad = hoy
        perfil.save()
        
        # Verificar logros de racha
        GamificacionService.verificar_logros_usuario(user)
    
    @staticmethod
    def registrar_gasto_creado(user):
        """Se llama cuando un usuario registra un gasto"""
        perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
        perfil.total_gastos_registrados += 1
        perfil.save()
        
        # Actualizar racha
        GamificacionService.actualizar_racha(user)
        
        # Puntos por registrar gasto
        perfil.agregar_puntos(1, 'Gasto registrado')
```

---

## 📋 FASE 4: INTERFAZ DE USUARIO (Día 4-5)

### Vista de Logros `views_gamificacion.py`:

```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import PerfilUsuario, LogroDesbloqueado, Logro
from .gamificacion_service import GamificacionService

@login_required
def dashboard_gamificacion(request):
    """Dashboard de gamificación del usuario"""
    perfil, _ = PerfilUsuario.objects.get_or_create(user=request.user)
    
    # Obtener logros desbloqueados
    logros_desbloqueados = LogroDesbloqueado.objects.filter(
        perfil=perfil
    ).select_related('logro')
    
    # Obtener logros disponibles
    logros_disponibles = Logro.objects.filter(
        activo=True,
        es_secreto=False
    ).exclude(
        id__in=logros_desbloqueados.values_list('logro_id', flat=True)
    )
    
    # Calcular porcentaje de completado
    total_logros = Logro.objects.filter(activo=True).count()
    porcentaje_completado = (logros_desbloqueados.count() / total_logros * 100) if total_logros > 0 else 0
    
    # Puntos para siguiente nivel
    niveles_puntos = {
        1: 0, 2: 100, 3: 300, 4: 600, 5: 1000,
        6: 1500, 7: 2100, 8: 2800, 9: 3600, 10: 5000
    }
    puntos_siguiente_nivel = niveles_puntos.get(perfil.nivel + 1, 5000)
    puntos_para_siguiente = puntos_siguiente_nivel - perfil.puntos_totales
    
    context = {
        'perfil': perfil,
        'logros_desbloqueados': logros_desbloqueados,
        'logros_disponibles': logros_disponibles,
        'porcentaje_completado': porcentaje_completado,
        'puntos_para_siguiente': puntos_para_siguiente,
        'puntos_siguiente_nivel': puntos_siguiente_nivel,
    }
    
    return render(request, 'gastos/gamificacion/dashboard.html', context)
```

---

## 📋 FASE 5: TEMPLATES (Día 6)

### Template `dashboard.html`:

```html
{% extends 'gastos/base.html' %}

{% block content %}
<div class="container mt-4">
    <!-- Header de Perfil -->
    <div class="card mb-4" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
        <div class="card-body">
            <div class="row align-items-center">
                <div class="col-md-3 text-center">
                    <div class="nivel-badge" style="font-size: 4rem;">
                        {% if perfil.nivel <= 2 %}🥉
                        {% elif perfil.nivel <= 4 %}🥈
                        {% elif perfil.nivel <= 6 %}🥇
                        {% elif perfil.nivel <= 8 %}💎
                        {% else %}👑{% endif %}
                    </div>
                    <h2 class="mb-0">Nivel {{ perfil.nivel }}</h2>
                </div>
                <div class="col-md-6">
                    <h3>{{ request.user.get_full_name|default:request.user.username }}</h3>
                    <div class="mb-2">
                        <small>{{ perfil.puntos_totales }} puntos totales</small>
                    </div>
                    <!-- Barra de progreso -->
                    <div class="progress" style="height: 25px; background: rgba(255,255,255,0.3);">
                        <div class="progress-bar" role="progressbar" 
                             style="width: {{ perfil.puntos_totales|floatformat:0 }}%; background: linear-gradient(90deg, #38ef7d, #11998e);"
                             aria-valuenow="{{ perfil.puntos_totales }}" 
                             aria-valuemin="0" 
                             aria-valuemax="{{ puntos_siguiente_nivel }}">
                            {{ puntos_para_siguiente }} pts para nivel {{ perfil.nivel|add:1 }}
                        </div>
                    </div>
                </div>
                <div class="col-md-3 text-center">
                    <div class="racha-info">
                        <div style="font-size: 2.5rem;">🔥</div>
                        <h3 class="mb-0">{{ perfil.racha_actual }}</h3>
                        <small>días de racha</small>
                        <div class="mt-2">
                            <small>Mejor: {{ perfil.mejor_racha }} días</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Stats Cards -->
    <div class="row mb-4">
        <div class="col-md-4">
            <div class="card text-center">
                <div class="card-body">
                    <div style="font-size: 2.5rem;">🏆</div>
                    <h4>{{ logros_desbloqueados.count }}</h4>
                    <p class="text-muted mb-0">Logros Desbloqueados</p>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card text-center">
                <div class="card-body">
                    <div style="font-size: 2.5rem;">📊</div>
                    <h4>{{ porcentaje_completado|floatformat:0 }}%</h4>
                    <p class="text-muted mb-0">Completado</p>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card text-center">
                <div class="card-body">
                    <div style="font-size: 2.5rem;">💰</div>
                    <h4>${{ perfil.total_ahorrado|floatformat:0 }}</h4>
                    <p class="text-muted mb-0">Total Ahorrado</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Logros Desbloqueados -->
    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0"><i class="bi bi-trophy-fill me-2"></i>Logros Desbloqueados</h5>
        </div>
        <div class="card-body">
            <div class="row">
                {% for logro_desbloqueado in logros_desbloqueados %}
                <div class="col-md-4 mb-3">
                    <div class="card h-100" style="border-left: 4px solid #667eea;">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start">
                                <div style="font-size: 2.5rem;">{{ logro_desbloqueado.logro.icono }}</div>
                                <span class="badge bg-success">+{{ logro_desbloqueado.logro.puntos_recompensa }} pts</span>
                            </div>
                            <h6 class="mt-2">{{ logro_desbloqueado.logro.nombre }}</h6>
                            <p class="text-muted small mb-0">{{ logro_desbloqueado.logro.descripcion }}</p>
                            <small class="text-muted">{{ logro_desbloqueado.fecha_desbloqueo|date:"d/m/Y" }}</small>
                        </div>
                    </div>
                </div>
                {% empty %}
                <div class="col-12 text-center text-muted">
                    <p>Aún no has desbloqueado ningún logro. ¡Comienza a registrar gastos!</p>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>

    <!-- Logros Disponibles -->
    <div class="card">
        <div class="card-header">
            <h5 class="mb-0"><i class="bi bi-target me-2"></i>Logros por Desbloquear</h5>
        </div>
        <div class="card-body">
            <div class="row">
                {% for logro in logros_disponibles %}
                <div class="col-md-4 mb-3">
                    <div class="card h-100 logro-bloqueado" style="opacity: 0.6; border: 2px dashed #ddd;">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start">
                                <div style="font-size: 2.5rem; filter: grayscale(1);">{{ logro.icono }}</div>
                                <span class="badge bg-secondary">{{ logro.puntos_recompensa }} pts</span>
                            </div>
                            <h6 class="mt-2">{{ logro.nombre }}</h6>
                            <p class="text-muted small mb-0">{{ logro.descripcion }}</p>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</div>

<style>
.logro-bloqueado:hover {
    opacity: 1;
    border-color: #667eea;
    transition: all 0.3s ease;
}
</style>
{% endblock %}
```

---

## 📋 FASE 6: INTEGRACIÓN (Día 7)

### Modificar `views.py` para integrar gamificación:

```python
# En la vista de crear gasto
@login_required
def crear_gasto(request):
    if request.method == 'POST':
        # ... código existente ...
        
        if form.is_valid():
            gasto = form.save()
            
            # NUEVO: Integrar gamificación
            from .gamificacion_service import GamificacionService
            GamificacionService.registrar_gasto_creado(request.user)
            
            messages.success(request, 'Gasto registrado exitosamente!')
            return redirect('gastos_lista')
```

### Agregar URLs:

```python
# urls.py
path('gamificacion/', views_gamificacion.dashboard_gamificacion, name='gamificacion_dashboard'),
```

### Agregar al navbar:

```html
<!-- En base.html -->
<li class="nav-item">
    <a class="nav-link" href="{% url 'gamificacion_dashboard' %}">
        <i class="bi bi-trophy-fill"></i> Logros
        {% if perfil.logros.filter(visto=False).count > 0 %}
        <span class="badge bg-danger">{{ perfil.logros.filter(visto=False).count }}</span>
        {% endif %}
    </a>
</li>
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

### Día 1: Modelos
- [ ] Crear modelo PerfilUsuario
- [ ] Crear modelo Logro
- [ ] Crear modelo LogroDesbloqueado
- [ ] Crear modelo DesafioMensual
- [ ] Crear modelo ParticipacionDesafio
- [ ] Crear modelo HistorialPuntos
- [ ] Crear modelo NotificacionLogro
- [ ] Ejecutar migraciones

### Día 2: Datos Iniciales
- [ ] Crear script de logros iniciales
- [ ] Ejecutar script
- [ ] Verificar logros en admin

### Día 3: Lógica
- [ ] Crear gamificacion_service.py
- [ ] Implementar verificar_logros_usuario
- [ ] Implementar actualizar_racha
- [ ] Implementar registrar_gasto_creado
- [ ] Tests unitarios

### Día 4-5: Vistas y Templates
- [ ] Crear views_gamificacion.py
- [ ] Crear dashboard.html
- [ ] Crear componentes de logros
- [ ] Estilos CSS

### Día 6: Integración
- [ ] Integrar en crear_gasto
- [ ] Agregar URLs
- [ ] Actualizar navbar
- [ ] Testing de integración

### Día 7: Pulimiento
- [ ] Animaciones de logro desbloqueado
- [ ] Notificaciones toast
- [ ] Optimizaciones
- [ ] Documentación

---

## 🚀 RESULTADO ESPERADO

Al finalizar, el usuario podrá:

✅ Ver su nivel y puntos  
✅ Ver racha de días  
✅ Desbloquear logros automáticamente  
✅ Recibir notificaciones de logros  
✅ Ver progreso hacia siguiente nivel  
✅ Competir con otros usuarios (futuro)  

**Tiempo total**: 7 días  
**Complejidad**: Media  
**Impacto**: ALTO 🚀  
**Diferenciación**: ⭐⭐⭐⭐⭐  

---

*Sistema completo de gamificación listo en 1 semana* 🎮
