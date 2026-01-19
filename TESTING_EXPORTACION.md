# 🧪 GUÍA DE TESTING - EXPORTACIÓN PDF Y EXCEL

## 📋 Objetivo
Verificar que la funcionalidad de exportación de dashboard a PDF y Excel funciona correctamente.

---

## ✅ Pre-requisitos

### 1. Servidor Corriendo
```bash
cd C:\Users\luisg\PycharmProjects\DjangoProject
.\.venv\Scripts\activate
python manage.py runserver
```

### 2. Usuario con Plan Premium
Necesitas tener un usuario con plan Premium o Empresarial activo.

**Opción A - Crear usuario de prueba:**
```bash
python manage.py createsuperuser
```

**Opción B - Actualizar plan de usuario existente:**
```python
python manage.py shell

# En la shell:
from gastos.models import PerfilGamificacion, PlanSuscripcion
from django.contrib.auth.models import User

# Obtener plan premium
plan_premium = PlanSuscripcion.objects.get(nombre='Premium')

# Obtener tu usuario
usuario = User.objects.get(username='tu_usuario')

# Actualizar suscripción
perfil = usuario.perfil_gamificacion
perfil.plan = plan_premium
perfil.fecha_inicio_suscripcion = timezone.now()
perfil.fecha_fin_suscripcion = timezone.now() + timedelta(days=30)
perfil.save()

print(f"✅ Plan actualizado a Premium")
print(f"✅ Puede exportar: {perfil.tiene_exportar_datos()}")
```

---

## 🧪 Casos de Prueba

### Test 1: Usuario Premium - Exportar PDF ✅

**Pasos:**
1. Iniciar sesión con usuario Premium
2. Ir al Dashboard: `http://127.0.0.1:8000/dashboard/`
3. Hacer clic en el botón **"Exportar PDF"** (ícono de PDF)

**Resultado Esperado:**
- ✅ Muestra toast: "Generando reporte en formato PDF..."
- ✅ Se descarga archivo: `reporte_dashboard_Enero_2026.pdf`
- ✅ PDF contiene:
  - Título con nombre de familia
  - Resumen ejecutivo (ingresos, gastos, balance)
  - Tabla de aportantes
  - Gastos por categoría
  - Metas de ahorro (si existen)
  - Pie de página con fecha

**Verificar:**
- [ ] Archivo se descarga correctamente
- [ ] PDF se abre sin errores
- [ ] Datos son correctos
- [ ] Formato es profesional (colores, tablas)

---

### Test 2: Usuario Premium - Exportar Excel ✅

**Pasos:**
1. En el Dashboard
2. Hacer clic en el botón **"Excel"** (ícono verde de Excel)

**Resultado Esperado:**
- ✅ Muestra toast: "Generando reporte en formato EXCEL..."
- ✅ Se descarga archivo: `reporte_dashboard_Enero_2026.xlsx`
- ✅ Excel contiene 5 hojas:
  1. **Resumen** - KPIs principales
  2. **Aportantes** - Detalle de ingresos
  3. **Gastos por Categoría** - Análisis
  4. **Metas de Ahorro** - Progreso (si hay metas)
  5. **Detalle de Gastos** - Todos los gastos

**Verificar:**
- [ ] Archivo se descarga correctamente
- [ ] Excel se abre sin errores
- [ ] 5 hojas están presentes
- [ ] Datos con formato (moneda, porcentaje)
- [ ] Colores en encabezados

---

### Test 3: Usuario Gratuito - Restricción ❌

**Pasos:**
1. Iniciar sesión con usuario de plan Gratuito
2. Ir al Dashboard
3. Intentar hacer clic en **"Exportar PDF"**

**Resultado Esperado:**
- ✅ Muestra alerta SweetAlert2:
  - **Título**: "Función Premium"
  - **Texto**: "Esta función requiere Plan Premium o superior"
  - **Botones**: "Ver Planes" | "Cerrar"
- ✅ NO se descarga ningún archivo
- ✅ Si hace clic en "Ver Planes" → redirige a `/planes/`

**Verificar:**
- [ ] Alerta se muestra correctamente
- [ ] NO se genera archivo
- [ ] Botón "Ver Planes" funciona

---

### Test 4: Usuario Básico - Restricción ❌

**Pasos:**
1. Iniciar sesión con usuario de plan Básico
2. Ir al Dashboard
3. Intentar hacer clic en **"Excel"**

**Resultado Esperado:**
- ✅ Misma alerta de restricción
- ✅ NO se descarga archivo

**Verificar:**
- [ ] Restricción funciona igual que plan Gratuito

---

### Test 5: Sin Familia Seleccionada ⚠️

**Pasos:**
1. Usuario Premium sin familia en sesión
2. Acceder directamente a: `http://127.0.0.1:8000/dashboard/exportar-pdf/`

**Resultado Esperado:**
- ✅ Redirige a `/familia/seleccionar/`
- ✅ Mensaje: "Debes seleccionar una familia primero"

**Verificar:**
- [ ] No genera archivo
- [ ] Redirige correctamente

---

### Test 6: Sin Gastos Registrados 📊

**Pasos:**
1. Usuario Premium con familia nueva (sin gastos)
2. Exportar PDF o Excel

**Resultado Esperado:**
- ✅ Se descarga archivo
- ✅ Muestra mensaje: "No hay gastos registrados en este período"
- ✅ Resumen ejecutivo muestra $0

**Verificar:**
- [ ] No genera error
- [ ] Archivo se crea con datos en cero

---

### Test 7: Con Datos Completos 📊

**Pasos:**
1. Usuario Premium con:
   - Al menos 2 aportantes
   - Al menos 3 categorías con gastos
   - Al menos 1 meta de ahorro
2. Exportar PDF y Excel

**Resultado Esperado:**
- ✅ PDF con todas las secciones llenas
- ✅ Excel con 5 hojas completas
- ✅ Datos correctos y formateados

**Verificar:**
- [ ] Todas las secciones tienen datos
- [ ] Cálculos son correctos (totales, porcentajes)
- [ ] Balance correcto (ingresos - gastos)

---

## 🔍 Puntos de Verificación

### Seguridad
- [ ] Solo usuarios autenticados pueden acceder
- [ ] Solo usuarios Premium/Empresarial pueden descargar
- [ ] Solo ven datos de su familia
- [ ] No hay SQL injection
- [ ] No hay path traversal

### Formato PDF
- [ ] Título profesional
- [ ] Tablas bien formateadas
- [ ] Colores apropiados
- [ ] Texto legible
- [ ] Sin errores de renderizado

### Formato Excel
- [ ] Columnas con ancho apropiado
- [ ] Formato de moneda: $12,345
- [ ] Formato de porcentaje: 25.5%
- [ ] Encabezados con color
- [ ] Cada hoja con título

### Performance
- [ ] Generación rápida (< 3 segundos)
- [ ] No bloquea la interfaz
- [ ] Memoria se libera correctamente

---

## 🐛 Errores Comunes

### Error: "Package requirements not satisfied"
**Solución:**
```bash
pip install reportlab==4.0.7 xlsxwriter==3.1.9
```

### Error: "No module named 'views_export'"
**Solución:**
- Verificar que existe: `gastos/views_export.py`
- Reiniciar servidor

### Error 403: "Esta función requiere Plan Premium"
**Solución:**
```python
# Actualizar plan del usuario
python manage.py shell
from gastos.models import *
from django.contrib.auth.models import User
user = User.objects.get(username='tu_usuario')
plan = PlanSuscripcion.objects.get(nombre='Premium')
user.perfil_gamificacion.plan = plan
user.perfil_gamificacion.save()
```

### Archivo vacío o corrupto
**Solución:**
- Verificar que hay datos en la familia
- Verificar logs del servidor
- Reiniciar servidor

---

## 📊 Script de Prueba Automatizado

Crea datos de prueba:

```python
# testing_exportacion.py
from django.contrib.auth.models import User
from gastos.models import *
from decimal import Decimal
from django.utils import timezone

# Obtener usuario
usuario = User.objects.get(username='tu_usuario')

# Crear familia de prueba
familia = Familia.objects.create(
    nombre='Familia Testing',
    creado_por=usuario
)

# Agregar a sesión
# request.session['familia_id'] = familia.id

# Crear aportantes
Aportante.objects.create(
    familia=familia,
    nombre='Juan Pérez',
    ingreso_mensual=Decimal('5000000'),
    activo=True
)

Aportante.objects.create(
    familia=familia,
    nombre='María García',
    ingreso_mensual=Decimal('4000000'),
    activo=True
)

# Crear categorías
cat_mercado = CategoriaGasto.objects.create(
    familia=familia,
    nombre='Mercado',
    tipo_principal='VARIABLE'
)

cat_servicios = CategoriaGasto.objects.create(
    familia=familia,
    nombre='Servicios',
    tipo_principal='FIJO'
)

# Crear subcategorías
sub_alimentos = SubcategoriaGasto.objects.create(
    categoria=cat_mercado,
    nombre='Alimentos',
    tipo='VARIABLE'
)

sub_luz = SubcategoriaGasto.objects.create(
    categoria=cat_servicios,
    nombre='Luz',
    tipo='FIJO'
)

# Crear gastos
Gasto.objects.create(
    subcategoria=sub_alimentos,
    monto=Decimal('350000'),
    fecha=timezone.now(),
    descripcion='Compra de mercado'
)

Gasto.objects.create(
    subcategoria=sub_luz,
    monto=Decimal('150000'),
    fecha=timezone.now(),
    descripcion='Factura de luz'
)

# Crear meta de ahorro
MetaAhorro.objects.create(
    familia=familia,
    nombre='Vacaciones',
    monto_objetivo=Decimal('5000000'),
    monto_actual=Decimal('1500000'),
    fecha_objetivo=timezone.now() + timedelta(days=180),
    activa=True
)

print("✅ Datos de prueba creados")
print(f"✅ Familia: {familia.nombre}")
print(f"✅ Aportantes: {familia.aportantes.count()}")
print(f"✅ Categorías: {familia.categorias.count()}")
print(f"✅ Metas: {familia.metas.count()}")
```

---

## ✅ Checklist Final

Antes de considerar la funcionalidad completa:

- [ ] Ambas exportaciones funcionan (PDF y Excel)
- [ ] Restricciones de plan funcionan
- [ ] Datos son correctos
- [ ] Formato es profesional
- [ ] No hay errores en consola
- [ ] Performance es aceptable
- [ ] Documentación está completa
- [ ] Tests manuales pasados

---

## 📞 Soporte

Si encuentras errores:
1. Revisar logs del servidor
2. Verificar versiones de dependencias
3. Consultar `EXPORTACION_PDF_EXCEL_IMPLEMENTADA.md`

---

**Última actualización**: 18/01/2026  
**Autor**: GitHub Copilot
