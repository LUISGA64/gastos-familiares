# 🎫 Guía de Códigos de Invitación - Sistema de Gastos Familiares

## 📋 Resumen

El sistema de Gastos Familiares utiliza **códigos de invitación** para el registro de nuevos usuarios. Cada código está asociado a un plan específico y solo puede usarse una vez.

---

## 🚀 Scripts Disponibles

### 1. `crear_codigos_nuevos.py` - Generar Códigos Nuevos

**Descripción:** Crea los planes de suscripción (si no existen) y genera códigos de invitación nuevos.

**Uso:**
```bash
python crear_codigos_nuevos.py
```

**Lo que hace:**
- ✅ Verifica si los planes existen, si no los crea
- ✅ Genera códigos únicos para cada plan:
  - **5 códigos** para Plan Gratuito
  - **10 códigos** para Plan Básico
  - **5 códigos** para Plan Premium
  - **3 códigos** para Plan Empresarial
- ✅ Muestra todos los códigos generados con sus detalles

**Cuándo usarlo:**
- Primera vez que configuras el sistema
- Cuando necesitas más códigos para nuevos usuarios

---

### 2. `listar_codigos.py` - Listar Códigos Disponibles

**Descripción:** Muestra todos los códigos disponibles y usados sin generar nuevos.

**Uso:**
```bash
python listar_codigos.py
```

**Lo que hace:**
- 📊 Muestra estadísticas generales
- ✅ Lista códigos disponibles por plan
- ❌ Lista códigos ya usados (con usuario y fecha)
- 📅 Muestra fecha de creación de cada código

**Cuándo usarlo:**
- Para consultar códigos disponibles
- Para verificar quién usó un código
- Para revisar el inventario de códigos

---

## 📦 Planes de Suscripción

### 🆓 Plan Gratuito ($0/mes)
- 👥 Hasta 2 aportantes
- 📝 Hasta 30 gastos/mes
- 📂 Hasta 5 categorías
- ⏱️ Sin período de prueba
- **Ideal para:** Comenzar a usar el sistema

### 💳 Plan Básico ($9,900/mes)
- 👥 Hasta 4 aportantes
- 📝 Hasta 100 gastos/mes
- 📂 Hasta 15 categorías
- ⏱️ **15 días de prueba gratis**
- **Ideal para:** Parejas y familias pequeñas

### ⭐ Plan Premium ($19,900/mes)
- 👥 Hasta 999 aportantes
- 📝 Hasta 9,999 gastos/mes
- 📂 Hasta 50 categorías
- ⏱️ **15 días de prueba gratis**
- **Ideal para:** Familias grandes

### 🏢 Plan Empresarial ($49,900/mes)
- 👥 Hasta 9,999 aportantes
- 📝 Hasta 99,999 gastos/mes
- 📂 Hasta 100 categorías
- ⏱️ **30 días de prueba gratis**
- **Ideal para:** Empresas y organizaciones

---

## 🎯 Cómo Usar los Códigos

### Para Usuarios Finales:

1. **Inicia el servidor:**
   ```bash
   python manage.py runserver
   ```

2. **Abre tu navegador:**
   ```
   http://127.0.0.1:8000/registro/
   ```

3. **Completa el formulario:**
   - Nombre de usuario
   - Email
   - Contraseña
   - Nombre de familia
   - **Código de invitación** (elige uno de los disponibles)

4. **¡Listo!** Ya puedes acceder al sistema

---

## 📊 Códigos Generados Actualmente

**Total:** 23 códigos disponibles

### Por Plan:
- 🆓 Plan Gratuito: **5 códigos**
- 💳 Plan Básico: **10 códigos**
- ⭐ Plan Premium: **5 códigos**
- 🏢 Plan Empresarial: **3 códigos**

> **Nota:** Para ver los códigos específicos, ejecuta: `python listar_codigos.py`

---

## 🔧 Gestión de Códigos

### Verificar Códigos Disponibles
```bash
python listar_codigos.py
```

### Generar Más Códigos
```bash
python crear_codigos_nuevos.py
```

### Ver Códigos en la Base de Datos (Django Shell)
```bash
python manage.py shell
```
```python
from gastos.models import CodigoInvitacion

# Ver códigos disponibles
CodigoInvitacion.objects.filter(usado=False)

# Ver códigos usados
CodigoInvitacion.objects.filter(usado=True)

# Contar códigos por plan
from gastos.models import PlanSuscripcion
plan = PlanSuscripcion.objects.get(tipo='BASICO')
CodigoInvitacion.objects.filter(plan=plan, usado=False).count()
```

---

## 💡 Características de los Códigos

### Seguridad:
- ✅ 12 caracteres alfanuméricos
- ✅ Únicos en el sistema
- ✅ No se pueden reutilizar

### Información Almacenada:
- 🔑 Código único
- 📋 Plan asociado
- 📅 Fecha de creación
- ✅ Estado (usado/disponible)
- 👤 Usuario que lo usó (si aplica)
- 📅 Fecha de uso (si aplica)

### Validaciones:
- ❌ No se puede usar un código dos veces
- ❌ No se puede registrar sin código válido
- ❌ El código debe existir en la base de datos
- ✅ Se asocia automáticamente al plan correspondiente

---

## 📝 Ejemplos de Códigos Generados

### Plan Gratuito:
```
I7ZZAXDROMXV
Z9H976Y6LS31
N0V5NC8ZL9KL
```

### Plan Básico:
```
FEB2CM1U6O8E
ND8VUEW9BRX1
RJWIMATQQE4S
```

### Plan Premium:
```
SMLGKH6RVR6M
MUNUHW6NWMEM
K5ZP2UK63LGS
```

### Plan Empresarial:
```
PXH3XN1ILNV8
QDTYROF9XLVE
3NOOGRDCY928
```

> **⚠️ Importante:** Estos son solo ejemplos. Los códigos reales varían con cada generación.

---

## 🔄 Flujo de Registro

```
Usuario accede a /registro/
    ↓
Completa el formulario
    ↓
Ingresa código de invitación
    ↓
Sistema valida el código
    ↓
Código es válido y no usado?
    ├─ SÍ → Crea usuario y familia
    │        Asocia plan del código
    │        Marca código como usado
    │        Redirige a login
    │
    └─ NO → Muestra error
             Usuario intenta de nuevo
```

---

## 📈 Monitoreo

### Ver Estadísticas:
```bash
python listar_codigos.py
```

### Información Mostrada:
- 📊 Total de códigos en sistema
- ✅ Códigos disponibles
- ❌ Códigos usados
- 📅 Fechas de creación y uso
- 👥 Usuarios que usaron códigos

---

## ⚙️ Configuración Personalizada

Si deseas cambiar la cantidad de códigos generados, edita `crear_codigos_nuevos.py`:

```python
# Línea ~103
cantidad_por_plan = {
    'GRATIS': 5,        # Cambia este número
    'BASICO': 10,       # Cambia este número
    'PREMIUM': 5,       # Cambia este número
    'EMPRESARIAL': 3    # Cambia este número
}
```

---

## 🐛 Solución de Problemas

### "Plan no encontrado"
**Solución:** Ejecuta `python crear_codigos_nuevos.py` para crear los planes.

### "Código ya usado"
**Solución:** Genera nuevos códigos con `python crear_codigos_nuevos.py`

### "No hay códigos disponibles"
**Solución:** Ejecuta `python crear_codigos_nuevos.py` para generar más códigos.

### Error en la base de datos
**Solución:** Asegúrate de que las migraciones estén aplicadas:
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 📚 Archivos Relacionados

- `crear_codigos_nuevos.py` - Genera códigos nuevos
- `listar_codigos.py` - Lista códigos disponibles/usados
- `CODIGOS_GENERADOS.md` - Lista de códigos generados
- `gastos/models.py` - Modelos de Plan y Código
- `gastos/views_auth.py` - Lógica de registro

---

## ✅ Checklist de Configuración Inicial

- [ ] Ejecutar migraciones: `python manage.py migrate`
- [ ] Generar códigos: `python crear_codigos_nuevos.py`
- [ ] Verificar códigos: `python listar_codigos.py`
- [ ] Probar registro con un código
- [ ] Verificar que el código se marque como usado

---

**¡Sistema listo para registrar nuevos usuarios!** 🎉

