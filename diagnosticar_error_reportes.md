# 🔍 Diagnóstico Error 500 en Reportes - Producción

## 🚨 Problema Reportado
Error 500 al acceder a `/reportes/` después del despliegue en OVH

## 📋 Pasos de Diagnóstico

### 1. Revisar Logs en Producción

```bash
# Conectar al servidor
ssh usuario@tu-servidor-ovh.com

# Ver últimos 50 errores
sudo tail -50 /var/log/gunicorn/error.log

# Ver errores en tiempo real
sudo tail -f /var/log/gunicorn/error.log

# Filtrar solo errores de reportes
sudo grep -A 10 "reportes" /var/log/gunicorn/error.log | tail -50
```

### 2. Errores Comunes y Soluciones

#### Error A: "NameError: name 'Familia' is not defined"

**Causa:** Falta importar el modelo Familia

**Solución:**
```python
# En gastos/views.py, línea ~667 en función reportes()
from .models import Familia  # Agregar esta importación

def reportes(request):
    familia_id = request.session.get('familia_id')
    # ...
    familia = Familia.objects.get(id=familia_id)  # Aquí se usa
```

#### Error B: "'NoneType' object has no attribute 'count'"

**Causa:** Variable aportantes puede ser None

**Solución:**
```python
# Verificar que aportantes no sea None
aportantes = Aportante.objects.filter(familia_id=familia_id, activo=True)
if not aportantes.exists():
    messages.warning(request, 'No hay aportantes activos en la familia.')
    return redirect('dashboard')
```

#### Error C: "unsupported operand type(s) for /: 'Decimal' and 'int'"

**Causa:** División entre Decimal e int

**Solución:**
```python
from decimal import Decimal

# Cambiar:
monto_por_aportante = gasto.monto / num_aportantes

# Por:
monto_por_aportante = gasto.monto / Decimal(str(num_aportantes))
```

#### Error D: "Cannot resolve keyword 'familia' into field"

**Causa:** Query incorrecta en prefetch_related

**Solución:**
Verificar que las relaciones en el query sean correctas.

---

## 🔧 Fix Rápido - Aplicar en Producción

### Opción 1: Fix Completo (Recomendado)

```bash
# 1. En tu máquina local, crear fix
cd C:\Users\luisg\PycharmProjects\DjangoProject

# 2. Editar gastos/views.py y aplicar fix (ver abajo)

# 3. Probar localmente
python manage.py check
python manage.py runserver
# Ir a http://127.0.0.1:8000/reportes/ y verificar

# 4. Commit y push
git add gastos/views.py
git commit -m "Fix: Error 500 en reportes - importaciones y validaciones"
git push origin main

# 5. Desplegar en producción
ssh usuario@servidor
cd /var/www/html/FinanBot
git pull origin main
source venv/bin/activate
python manage.py check
sudo systemctl reload gunicorn
```

### Opción 2: Fix Directo en Servidor (Emergencia)

```bash
# Solo si necesitas fix INMEDIATO
ssh usuario@servidor
cd /var/www/html/FinanBot
nano gastos/views.py

# Hacer cambios
# Ctrl+O para guardar, Ctrl+X para salir

# Verificar
python manage.py check

# Reiniciar
sudo systemctl reload gunicorn
```

---

## 🛠️ Código Fix para gastos/views.py

### Fix 1: Agregar Import de Familia

```python
# Al inicio del archivo gastos/views.py, alrededor de línea 12
from .models import (
    Aportante, CategoriaGasto, SubcategoriaGasto, Gasto, 
    DistribucionGasto, MetaAhorro, Familia  # <-- Agregar Familia aquí
)
```

### Fix 2: Validación en función reportes()

```python
@login_required
def reportes(request):
    """Vista de reportes y estadísticas"""
    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    # AGREGAR ESTA IMPORTACIÓN Y TRY/EXCEPT
    from .models import Familia
    
    try:
        familia = Familia.objects.get(id=familia_id)
    except Familia.DoesNotExist:
        messages.error(request, 'Familia no encontrada.')
        return redirect('seleccionar_familia')

    # Parámetros de fecha
    mes_param = request.GET.get('mes', str(timezone.now().month))
    anio_param = request.GET.get('anio', str(timezone.now().year))
    
    try:
        mes = int(mes_param)
        anio = int(anio_param)
    except (ValueError, TypeError):
        mes = timezone.now().month
        anio = timezone.now().year

    # Obtener aportantes activos
    aportantes = Aportante.objects.filter(familia_id=familia_id, activo=True).order_by('nombre')
    
    # VALIDAR QUE HAY APORTANTES
    if not aportantes.exists():
        messages.warning(request, 'No hay aportantes activos. Por favor, agrega aportantes primero.')
        return redirect('lista_aportantes')

    # Gastos del período de la familia (solo compartidos)
    gastos_periodo = Gasto.objects.filter(
        subcategoria__categoria__familia_id=familia_id,
        fecha__month=mes,
        fecha__year=anio,
        tipo_gasto='COMPARTIDO'
    ).select_related('subcategoria__categoria', 'pagado_por').prefetch_related('distribuciones__aportante').order_by('fecha', 'id')

    # Calcular distribuciones por gasto y aportante
    gastos_detallados = []
    for gasto in gastos_periodo:
        distribuciones = {}
        distribuciones_gasto = gasto.distribuciones.all()
        
        # Si no hay distribuciones, distribuir equitativamente
        if not distribuciones_gasto.exists():
            num_aportantes = aportantes.count()
            if num_aportantes > 0:
                # FIX: Usar Decimal para evitar errores de tipo
                from decimal import Decimal
                monto_por_aportante = gasto.monto / Decimal(str(num_aportantes))
                for aportante in aportantes:
                    distribuciones[aportante.id] = monto_por_aportante
        else:
            for dist in distribuciones_gasto:
                distribuciones[dist.aportante.id] = dist.monto_asignado

        gastos_detallados.append({
            'gasto': gasto,
            'distribuciones': distribuciones
        })

    # ... resto del código ...
```

### Fix 3: Validación de Totales

```python
    # Totales
    total_gastos = gastos_periodo.aggregate(total=Sum('monto'))['total'] or Decimal('0')
    gastos_fijos = gastos_periodo.filter(subcategoria__tipo='FIJO').aggregate(total=Sum('monto'))['total'] or Decimal('0')
    gastos_variables = gastos_periodo.filter(subcategoria__tipo='VARIABLE').aggregate(total=Sum('monto'))['total'] or Decimal('0')

    # Ingresos totales de la familia
    total_ingresos = aportantes.aggregate(total=Sum('ingreso_mensual'))['total'] or Decimal('0')

    # Calcular totales por aportante con validación
    totales_por_aportante = {}
    for aportante in aportantes:
        total_asignado = DistribucionGasto.objects.filter(
            aportante=aportante,
            gasto__fecha__month=mes,
            gasto__fecha__year=anio,
            gasto__tipo_gasto='COMPARTIDO'
        ).aggregate(total=Sum('monto_asignado'))['total']
        
        # FIX: Asegurar que sea Decimal
        if total_asignado:
            totales_por_aportante[aportante.id] = Decimal(str(total_asignado))
        else:
            totales_por_aportante[aportante.id] = Decimal('0')
```

---

## 🧪 Script de Test Rápido

Crear archivo `test_reportes.py` en el servidor:

```python
# test_reportes.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FinanBot.settings')
django.setup()

from gastos.models import Familia, Aportante, Gasto
from django.utils import timezone
from decimal import Decimal

# Test básico
print("🧪 Testing reportes...")

try:
    # Test 1: Importaciones
    from gastos.models import Familia
    print("✅ Import Familia OK")
    
    # Test 2: Query básica
    familias = Familia.objects.all()
    print(f"✅ Familias en DB: {familias.count()}")
    
    # Test 3: Aportantes
    if familias.exists():
        familia = familias.first()
        aportantes = Aportante.objects.filter(familia=familia, activo=True)
        print(f"✅ Aportantes activos: {aportantes.count()}")
        
        # Test 4: Gastos
        mes = timezone.now().month
        anio = timezone.now().year
        gastos = Gasto.objects.filter(
            subcategoria__categoria__familia=familia,
            fecha__month=mes,
            fecha__year=anio
        )
        print(f"✅ Gastos del mes: {gastos.count()}")
        
    print("✅ Todos los tests pasaron!")
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
```

Ejecutar:
```bash
cd /var/www/html/FinanBot
source venv/bin/activate
python test_reportes.py
```

---

## 📊 Checklist de Verificación

### En Servidor
- [ ] Logs revisados: `sudo tail -50 /var/log/gunicorn/error.log`
- [ ] Error específico identificado
- [ ] Import de Familia agregado
- [ ] Validaciones agregadas
- [ ] `python manage.py check` sin errores
- [ ] Gunicorn reiniciado: `sudo systemctl reload gunicorn`
- [ ] Test en `/reportes/` exitoso

### En Local (antes de push)
- [ ] Fix aplicado en código local
- [ ] `python manage.py check` sin errores
- [ ] Servidor local funciona: `python manage.py runserver`
- [ ] `/reportes/` carga correctamente en local
- [ ] Commit y push realizados

---

## 🚀 Comando Rápido Todo-en-Uno

Si identificaste el error en los logs:

```bash
# En servidor
cd /var/www/html/FinanBot
git pull origin main
source venv/bin/activate
python manage.py check
sudo systemctl reload gunicorn
sudo tail -20 /var/log/gunicorn/error.log
```

---

## 📞 Siguiente Paso

**IMPORTANTE:** Necesito ver el error exacto de los logs.

Ejecuta en el servidor:
```bash
sudo tail -100 /var/log/gunicorn/error.log
```

Y copia el error completo aquí para darte la solución exacta.

