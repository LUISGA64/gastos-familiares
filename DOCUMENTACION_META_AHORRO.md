# 📊 Funcionalidad de Meta de Ahorro - Documentación Completa

## 📋 Resumen Ejecutivo

La funcionalidad de **Meta de Ahorro** permite a las familias establecer objetivos financieros específicos y hacer seguimiento de su progreso. Actualmente, el modelo está **implementado en la base de datos** pero **NO tiene vistas ni templates** para gestión desde la interfaz web.

---

## 🗄️ Modelo de Datos

### Clase: `MetaAhorro`

**Ubicación:** `gastos/models.py` (líneas 798-893)

### Campos del Modelo

```python
class MetaAhorro(models.Model):
    # Relación
    familia = ForeignKey('Familia')  # Familia a la que pertenece
    
    # Información básica
    nombre = CharField(max_length=200)           # Ej: "Vacaciones 2026"
    descripcion = TextField(blank=True)          # Descripción opcional
    icono = CharField(max_length=50)             # Ícono Bootstrap (ej: 'piggy-bank')
    
    # Montos
    monto_objetivo = DecimalField(max_digits=12) # Meta a alcanzar
    monto_actual = DecimalField(default=0)       # Ahorro actual
    
    # Fechas
    fecha_inicio = DateField()                   # Cuándo empezó
    fecha_objetivo = DateField()                 # Fecha límite
    
    # Prioridad y Estado
    prioridad = CharField(choices=PRIORIDAD_CHOICES)  # ALTA, MEDIA, BAJA
    estado = CharField(choices=ESTADO_CHOICES)        # ACTIVA, COMPLETADA, CANCELADA
    
    # Auditoría
    creado_en = DateTimeField(auto_now_add=True)
    actualizado_en = DateTimeField(auto_now=True)
```

### Opciones de Prioridad

```python
PRIORIDAD_CHOICES = [
    ('ALTA', 'Alta'),      # Meta urgente/importante
    ('MEDIA', 'Media'),    # Meta normal (default)
    ('BAJA', 'Baja'),      # Meta a largo plazo
]
```

### Opciones de Estado

```python
ESTADO_CHOICES = [
    ('ACTIVA', 'Activa'),          # En progreso
    ('COMPLETADA', 'Completada'),  # Objetivo alcanzado
    ('CANCELADA', 'Cancelada'),    # Meta abandonada
]
```

---

## 🔧 Propiedades y Métodos

### 1. `porcentaje_completado` (Property)

**Descripción:** Calcula el porcentaje de progreso hacia la meta.

```python
@property
def porcentaje_completado(self):
    if self.monto_objetivo > 0:
        return (self.monto_actual / self.monto_objetivo) * 100
    return 0
```

**Uso:**
```python
meta = MetaAhorro.objects.get(id=1)
print(f"Progreso: {meta.porcentaje_completado:.1f}%")
# Output: Progreso: 45.5%
```

### 2. `monto_restante` (Property)

**Descripción:** Calcula cuánto falta para completar la meta.

```python
@property
def monto_restante(self):
    return max(0, self.monto_objetivo - self.monto_actual)
```

**Uso:**
```python
meta = MetaAhorro.objects.get(id=1)
print(f"Faltan: ${meta.monto_restante:,.0f}")
# Output: Faltan: $2,500,000
```

### 3. `dias_restantes` (Property)

**Descripción:** Calcula días restantes hasta la fecha objetivo.

```python
@property
def dias_restantes(self):
    from datetime import date
    if self.fecha_objetivo > date.today():
        return (self.fecha_objetivo - date.today()).days
    return 0
```

**Uso:**
```python
meta = MetaAhorro.objects.get(id=1)
print(f"Faltan {meta.dias_restantes} días")
# Output: Faltan 45 días
```

### 4. `agregar_ahorro()` (Método)

**Descripción:** Agrega un monto al ahorro y actualiza el estado automáticamente.

```python
def agregar_ahorro(self, monto):
    self.monto_actual += monto
    if self.monto_actual >= self.monto_objetivo:
        self.estado = 'COMPLETADA'
    self.save()
```

**Uso:**
```python
meta = MetaAhorro.objects.get(id=1)
meta.agregar_ahorro(500000)  # Agrega $500,000
# Si completa el objetivo, cambia automáticamente a 'COMPLETADA'
```

---

## 📊 Relaciones con Otros Modelos

### Relación con Familia

```python
# Obtener todas las metas de una familia
familia = Familia.objects.get(id=1)
metas = familia.metas_ahorro.all()

# Filtrar por estado
metas_activas = familia.metas_ahorro.filter(estado='ACTIVA')
metas_completadas = familia.metas_ahorro.filter(estado='COMPLETADA')
```

### Meta Ordering (Ordenamiento por defecto)

```python
ordering = ['-fecha_objetivo', '-prioridad']
```

**Significa:**
1. Primero las metas con fecha objetivo más cercana
2. Luego por prioridad (ALTA > MEDIA > BAJA)

---

## 🔐 Admin de Django

### Configuración Actual

**Archivo:** `gastos/admin.py` (líneas 192-227)

```python
@admin.register(MetaAhorro)
class MetaAhorroAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 
        'familia', 
        'monto_objetivo_fmt', 
        'monto_actual_fmt', 
        'porcentaje_display',
        'prioridad', 
        'estado', 
        'fecha_objetivo', 
        'dias_restantes_display'
    ]
    
    list_filter = ['estado', 'prioridad', 'familia']
    search_fields = ['nombre', 'descripcion', 'familia__nombre']
    date_hierarchy = 'fecha_inicio'
    
    fieldsets = (
        ('Información de la Meta', {
            'fields': ('familia', 'nombre', 'descripcion', 'icono')
        }),
        ('Montos', {
            'fields': ('monto_objetivo', 'monto_actual')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_objetivo')
        }),
        ('Estado', {
            'fields': ('prioridad', 'estado')
        }),
    )
```

### Funcionalidades del Admin

✅ **Listar metas** con información clave  
✅ **Filtrar** por estado, prioridad y familia  
✅ **Buscar** por nombre, descripción o familia  
✅ **Navegación** por fecha de inicio  
✅ **Campos agrupados** en secciones lógicas  

---

## 💻 Estado de Implementación

### ✅ Implementado

1. **Modelo de datos completo** (`models.py`)
   - Todos los campos necesarios
   - Propiedades calculadas
   - Método para agregar ahorro
   - Validaciones de datos

2. **Migración creada** (`0004_metaahorro_notificacion_presupuestocategoria.py`)
   - Tabla creada en base de datos
   - Índices configurados
   - Relaciones establecidas

3. **Admin de Django** (`admin.py`)
   - CRUD completo desde admin
   - Filtros y búsquedas
   - Display personalizado

4. **Referencia en Dashboard** (`views.py`)
   - Cálculo de meta de ahorro (20% de ingresos)
   - Pasado al template como sugerencia

### ❌ NO Implementado

1. **Vistas para usuarios** (`views.py`)
   - No hay `lista_metas()`
   - No hay `crear_meta()`
   - No hay `editar_meta()`
   - No hay `eliminar_meta()`
   - No hay `agregar_ahorro_vista()`

2. **URLs** (`urls.py`)
   - No hay rutas definidas para metas

3. **Templates** (`templates/`)
   - No existe `metas_lista.html`
   - No existe `meta_form.html`
   - No existe `meta_detalle.html`

4. **Formularios** (`forms.py`)
   - No hay `MetaAhorroForm`

---

## 🎯 Uso Actual en el Sistema

### Dashboard Premium

**Archivo:** `templates/gastos/dashboard_premium.html` (línea 278)

```html
<p class="mb-0">
    Intenta ahorrar el 20% de tus ingresos: 
    <strong>${{ meta_ahorro|floatformat:0 }}</strong>
</p>
```

**Vista:** `gastos/views.py` (líneas 125-126)

```python
# Meta de ahorro (20% de ingresos)
meta_ahorro = total_ingresos * Decimal('0.20') if total_ingresos else 0
```

**Esto es solo una SUGERENCIA**, no usa el modelo `MetaAhorro`.

---

## 💡 Ejemplos de Uso Programático

### Crear una Meta de Ahorro

```python
from gastos.models import MetaAhorro, Familia
from datetime import date, timedelta

# Obtener familia
familia = Familia.objects.get(id=1)

# Crear meta
meta = MetaAhorro.objects.create(
    familia=familia,
    nombre="Vacaciones en Cartagena",
    descripcion="Viaje familiar en Semana Santa 2026",
    monto_objetivo=5000000,  # $5,000,000
    monto_actual=0,
    fecha_inicio=date.today(),
    fecha_objetivo=date(2026, 4, 1),  # 1 de abril
    prioridad='ALTA',
    estado='ACTIVA',
    icono='airplane'
)

print(f"Meta creada: {meta}")
# Output: Meta creada: Vacaciones en Cartagena - $5,000,000
```

### Agregar Ahorro a una Meta

```python
# Obtener meta
meta = MetaAhorro.objects.get(nombre="Vacaciones en Cartagena")

# Agregar ahorro
print(f"Ahorro actual: ${meta.monto_actual:,.0f}")
# Output: Ahorro actual: $0

meta.agregar_ahorro(1000000)  # Agregar $1,000,000
print(f"Ahorro actual: ${meta.monto_actual:,.0f}")
# Output: Ahorro actual: $1,000,000

print(f"Progreso: {meta.porcentaje_completado:.1f}%")
# Output: Progreso: 20.0%

print(f"Faltan: ${meta.monto_restante:,.0f}")
# Output: Faltan: $4,000,000
```

### Consultar Metas de una Familia

```python
from gastos.models import Familia

familia = Familia.objects.get(id=1)

# Todas las metas
todas = familia.metas_ahorro.all()
print(f"Total de metas: {todas.count()}")

# Metas activas
activas = familia.metas_ahorro.filter(estado='ACTIVA')
for meta in activas:
    print(f"- {meta.nombre}: {meta.porcentaje_completado:.1f}% completado")

# Metas por prioridad
urgentes = familia.metas_ahorro.filter(
    estado='ACTIVA', 
    prioridad='ALTA'
).order_by('fecha_objetivo')

for meta in urgentes:
    print(f"⚠️  {meta.nombre} - Faltan {meta.dias_restantes} días")
```

### Marcar Meta como Completada

```python
meta = MetaAhorro.objects.get(id=1)

# Agregar el monto restante
meta.agregar_ahorro(meta.monto_restante)

# Verificar estado
print(f"Estado: {meta.get_estado_display()}")
# Output: Estado: Completada
```

---

## 🎨 Propuesta de Interfaz de Usuario

### Vista de Lista de Metas

**URL sugerida:** `/metas/`

**Características:**
- Cards con barra de progreso
- Iconos personalizados
- Filtros por estado y prioridad
- Orden por fecha objetivo

**Ejemplo de Card:**
```
┌─────────────────────────────────────┐
│ ✈️  Vacaciones en Cartagena         │
│                                     │
│ ████████░░░░░░░░░░░░  45.5%        │
│                                     │
│ $2,275,000 de $5,000,000           │
│ Faltan: $2,725,000                 │
│                                     │
│ 🗓️  45 días restantes               │
│ ⚠️  Prioridad: Alta                 │
│                                     │
│ [Agregar Ahorro] [Editar]          │
└─────────────────────────────────────┘
```

### Formulario de Crear/Editar Meta

**Campos:**
- Nombre de la meta
- Descripción
- Ícono (selector de Bootstrap Icons)
- Monto objetivo
- Fecha objetivo
- Prioridad (select)

### Modal para Agregar Ahorro

**Campos:**
- Monto a agregar
- Nota (opcional)
- Fecha del ahorro

---

## 📊 Casos de Uso

### 1. Ahorro para Vacaciones

```python
MetaAhorro.objects.create(
    familia=familia,
    nombre="Vacaciones Cartagena",
    monto_objetivo=5000000,
    fecha_objetivo=date(2026, 7, 1),
    prioridad='ALTA',
    icono='airplane'
)
```

### 2. Fondo de Emergencias

```python
MetaAhorro.objects.create(
    familia=familia,
    nombre="Fondo de Emergencias",
    descripcion="6 meses de gastos",
    monto_objetivo=18000000,
    fecha_objetivo=date(2027, 1, 1),
    prioridad='ALTA',
    icono='shield-check'
)
```

### 3. Compra de Carro

```python
MetaAhorro.objects.create(
    familia=familia,
    nombre="Inicial para Carro",
    monto_objetivo=15000000,
    fecha_objetivo=date(2026, 12, 31),
    prioridad='MEDIA',
    icono='car-front'
)
```

### 4. Educación de Hijos

```python
MetaAhorro.objects.create(
    familia=familia,
    nombre="Universidad de María",
    monto_objetivo=50000000,
    fecha_objetivo=date(2030, 1, 1),
    prioridad='ALTA',
    icono='mortarboard'
)
```

---

## 🔄 Integración con Otros Módulos

### Con Gastos

Podría crear una categoría especial "Ahorro" y al registrar un gasto en esa categoría, automáticamente agregarlo a una meta.

```python
# Pseudo-código
if gasto.categoria.nombre == "Ahorro":
    # Vincular a una meta
    meta = familia.metas_ahorro.filter(estado='ACTIVA').first()
    if meta:
        meta.agregar_ahorro(gasto.monto)
```

### Con Conciliación

Al cerrar una conciliación, calcular el excedente y sugerir agregarlo a una meta.

```python
# Pseudo-código
excedente = total_ingresos - total_gastos
if excedente > 0:
    # Sugerir agregar a meta prioritaria
    meta = familia.metas_ahorro.filter(
        estado='ACTIVA',
        prioridad='ALTA'
    ).first()
```

### Con Notificaciones

Generar notificaciones automáticas:
- Meta alcanzada (100%)
- Progreso significativo (25%, 50%, 75%)
- Fecha objetivo próxima (7 días antes)
- Meta vencida sin completar

---

## 📈 Métricas Útiles

### Total Ahorrado por Familia

```python
from django.db.models import Sum

total_ahorrado = familia.metas_ahorro.aggregate(
    total=Sum('monto_actual')
)['total'] or 0

print(f"Total ahorrado: ${total_ahorrado:,.0f}")
```

### Progreso Promedio

```python
metas_activas = familia.metas_ahorro.filter(estado='ACTIVA')
if metas_activas.exists():
    promedio = sum(m.porcentaje_completado for m in metas_activas) / metas_activas.count()
    print(f"Progreso promedio: {promedio:.1f}%")
```

### Metas por Completar Este Año

```python
from datetime import date

este_anio = familia.metas_ahorro.filter(
    estado='ACTIVA',
    fecha_objetivo__year=date.today().year
)
```

---

## ✅ Ventajas del Diseño Actual

1. **Modelo completo** - Todos los campos necesarios
2. **Propiedades calculadas** - Progreso automático
3. **Actualización automática** - Estado cambia al completar
4. **Flexible** - Prioridades y estados configurables
5. **Auditable** - Fechas de creación y actualización
6. **Escalable** - Fácil agregar campos nuevos

---

## ⚠️ Limitaciones Actuales

1. **No hay UI** - Solo accesible desde admin
2. **No hay historial** - No se registran los aportes individuales
3. **No hay categorización** - No se puede categorizar el tipo de meta
4. **No hay alertas** - No notifica sobre progreso
5. **No integrado** - No se conecta con gastos/ingresos

---

## 🚀 Próximos Pasos Sugeridos

### Fase 1: UI Básica
- [ ] Crear vista de lista de metas
- [ ] Crear formulario de crear/editar
- [ ] Crear modal para agregar ahorro
- [ ] Agregar rutas en `urls.py`

### Fase 2: Historial
- [ ] Crear modelo `AporteAhorro` para registrar cada aporte
- [ ] Mostrar historial de aportes por meta
- [ ] Gráfico de evolución del ahorro

### Fase 3: Integración
- [ ] Conectar con categoría de gastos
- [ ] Sugerir metas al tener excedente
- [ ] Dashboard de metas en página principal

### Fase 4: Notificaciones
- [ ] Alerta de meta completada
- [ ] Notificación de progreso
- [ ] Recordatorio de fecha objetivo

---

## 📝 Conclusión

La funcionalidad de **Meta de Ahorro** está **completamente modelada** y lista para usarse desde el admin de Django, pero **requiere desarrollo de vistas, templates y formularios** para que los usuarios finales puedan gestionarla desde la interfaz web.

**Estado Actual:** 🟡 **Parcialmente Implementado** (30%)
- ✅ Modelo de datos
- ✅ Admin de Django
- ✅ Migraciones
- ❌ Vistas de usuario
- ❌ Templates
- ❌ Formularios
- ❌ URLs

**Potencial:** 🌟🌟🌟🌟🌟 **Muy Alto**

La funcionalidad está bien diseñada y puede convertirse en una característica premium muy valiosa para las familias que desean planificar y alcanzar objetivos financieros.

---

**Documentado por:** GitHub Copilot  
**Fecha:** 2026-01-15  
**Versión del modelo:** MetaAhorro v1.0

