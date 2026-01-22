# 📝 SISTEMA DE LOGS - GUÍA DE USO

## ✅ CONFIGURACIÓN HABILITADA

El sistema de logging ya está configurado y funcionando automáticamente.

## 📊 ARCHIVOS DE LOG GENERADOS

Todos los logs se guardan en el directorio `logs/`:

```
gastos-familiares/
└── logs/
    ├── errors.log          # Solo errores (ERROR y CRITICAL)
    ├── application.log     # Todo lo de la aplicación (INFO, WARNING, ERROR)
    └── django.log          # Logs del framework Django
```

### 🔴 errors.log
Contiene solo errores críticos:
- Excepciones no manejadas
- Errores 500
- Errores de base de datos
- Errores de código

**Ejemplo:**
```
[ERROR] 2026-01-22 15:30:45 django.request request get_response:197 - Internal Server Error: /gastos/nuevo/
Traceback (most recent call last):
  File "...views.py", line 45, in crear_gasto
    gasto.save()
...
```

### 📘 application.log
Contiene toda la actividad de la aplicación:
- Información general (INFO)
- Advertencias (WARNING)
- Errores (ERROR)

**Ejemplo:**
```
[INFO] 2026-01-22 15:25:12 gastos.views crear_gasto:42 - Usuario 'admin' creó nuevo gasto
[WARNING] 2026-01-22 15:26:30 gastos.middleware process_request:15 - Usuario sin familia asignada
[ERROR] 2026-01-22 15:30:45 gastos.views crear_gasto:45 - Error al guardar gasto
```

### ⚙️ django.log
Contiene logs del framework Django:
- Advertencias del sistema
- Configuración
- Middleware

---

## 🎯 CÓMO USAR EN TU CÓDIGO

### En cualquier view o archivo Python:

```python
import logging

logger = logging.getLogger('gastos')

def mi_funcion(request):
    # Log de información
    logger.info(f"Usuario {request.user.username} accedió a la función")
    
    # Log de advertencia
    if not request.user.familia:
        logger.warning(f"Usuario {request.user.username} sin familia asignada")
    
    # Log de error
    try:
        # Código que puede fallar
        gasto.save()
    except Exception as e:
        logger.error(f"Error al guardar gasto: {e}", exc_info=True)
        # exc_info=True incluye el traceback completo
    
    # Log de debug (solo se muestra en desarrollo)
    logger.debug(f"Valor de variable: {mi_variable}")
```

### Niveles de log disponibles:

```python
logger.debug("Mensaje de depuración")      # Solo desarrollo
logger.info("Mensaje informativo")          # Información general
logger.warning("Mensaje de advertencia")    # Posibles problemas
logger.error("Mensaje de error")            # Errores que requieren atención
logger.critical("Mensaje crítico")          # Errores graves del sistema
```

---

## 📖 VER LOS LOGS

### En el servidor VPS:

```bash
# Ver los últimos errores
tail -f /var/www/gastos-familiares/logs/errors.log

# Ver todos los logs de la aplicación
tail -f /var/www/gastos-familiares/logs/application.log

# Ver logs de Django
tail -f /var/www/gastos-familiares/logs/django.log

# Ver las últimas 50 líneas de errores
tail -n 50 /var/www/gastos-familiares/logs/errors.log

# Buscar un error específico
grep "ValueError" /var/www/gastos-familiares/logs/errors.log

# Ver logs en tiempo real mientras usas la aplicación
tail -f /var/www/gastos-familiares/logs/application.log
```

### En desarrollo local (Windows):

```powershell
# Ver errores
Get-Content logs\errors.log -Tail 50

# Ver en tiempo real
Get-Content logs\application.log -Wait
```

---

## 🔄 ROTACIÓN DE ARCHIVOS

Los logs se rotan automáticamente:
- **Tamaño máximo por archivo:** 10 MB
- **Archivos de respaldo:** 5 para errors.log y application.log, 3 para django.log
- **Archivos antiguos:** Se renombran a `.log.1`, `.log.2`, etc.

Ejemplo:
```
logs/
├── errors.log        # Actual
├── errors.log.1      # Backup 1
├── errors.log.2      # Backup 2
└── ...
```

---

## 🎛️ CONFIGURACIÓN

### Cambiar nivel de detalle de logs:

En `settings.py`, busca la sección `LOGGING`:

```python
# Para ver queries SQL en desarrollo
'django.db.backends': {
    'handlers': ['console'],
    'level': 'DEBUG',  # Cambiar de WARNING a DEBUG
    'propagate': False,
},
```

### En producción vs desarrollo:

**Desarrollo (DEBUG=True):**
- Logs en consola y archivos
- Nivel DEBUG habilitado
- Más verboso

**Producción (DEBUG=False):**
- Logs solo en archivos
- Consola solo para errores
- Emails de errores a administradores

---

## 🚀 DESPLEGAR EN SERVIDOR VPS

Después de subir los cambios:

```bash
# Conectar al servidor
ssh ubuntu@tu-servidor

# Ir al proyecto
cd /var/www/gastos-familiares

# Actualizar código
git pull

# El directorio logs/ se creará automáticamente

# Reiniciar Gunicorn
sudo systemctl restart gunicorn

# Ver logs en tiempo real
tail -f logs/application.log
```

---

## 📊 EJEMPLOS DE USO PRÁCTICO

### 1. Registrar creación de gastos:

```python
# En gastos/views.py
import logging
logger = logging.getLogger('gastos')

def crear_gasto(request):
    if request.method == 'POST':
        form = GastoForm(request.POST)
        if form.is_valid():
            gasto = form.save(commit=False)
            gasto.pagado_por = request.user
            gasto.save()
            logger.info(f"Gasto creado: {gasto.descripcion} - Monto: ${gasto.monto} - Usuario: {request.user.username}")
            return redirect('dashboard')
        else:
            logger.warning(f"Formulario de gasto inválido - Usuario: {request.user.username} - Errores: {form.errors}")
```

### 2. Registrar errores de pagos:

```python
# En gastos/views_pagos.py
import logging
logger = logging.getLogger('gastos')

def procesar_pago(request, pago_id):
    try:
        pago = Pago.objects.get(id=pago_id)
        # Procesar pago...
        logger.info(f"Pago procesado exitosamente: ID {pago_id} - Usuario: {request.user.username}")
    except Pago.DoesNotExist:
        logger.error(f"Pago no encontrado: ID {pago_id} - Usuario: {request.user.username}")
    except Exception as e:
        logger.error(f"Error al procesar pago {pago_id}: {str(e)}", exc_info=True)
```

### 3. Registrar uso del chatbot:

```python
# En gastos/views_chatbot.py
import logging
logger = logging.getLogger('gastos')

def chatbot_respuesta(request):
    mensaje = request.POST.get('mensaje')
    logger.info(f"Chatbot - Usuario: {request.user.username} - Mensaje: {mensaje[:50]}...")
    
    try:
        respuesta = obtener_respuesta_ia(mensaje)
        logger.debug(f"Chatbot - Respuesta generada: {respuesta[:100]}...")
        return JsonResponse({'respuesta': respuesta})
    except Exception as e:
        logger.error(f"Error en chatbot: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Error al generar respuesta'}, status=500)
```

---

## 🔍 MONITOREO Y ANÁLISIS

### Comandos útiles:

```bash
# Contar errores del día
grep "$(date +%Y-%m-%d)" logs/errors.log | wc -l

# Ver errores únicos
grep ERROR logs/errors.log | cut -d'-' -f4 | sort | uniq

# Ver usuarios más activos en logs
grep "Usuario:" logs/application.log | cut -d':' -f4 | sort | uniq -c | sort -rn

# Ver los últimos 10 errores
grep ERROR logs/errors.log | tail -10

# Filtrar por usuario específico
grep "admin" logs/application.log

# Ver solo warnings
grep WARNING logs/application.log
```

---

## ✅ VENTAJAS DEL SISTEMA DE LOGS

1. **Debugging más fácil:** Ver exactamente qué pasó y cuándo
2. **Monitoreo:** Detectar problemas antes de que los usuarios los reporten
3. **Auditoría:** Saber quién hizo qué y cuándo
4. **Rendimiento:** Identificar queries lentas (con DEBUG en db.backends)
5. **Seguridad:** Detectar intentos de acceso no autorizado

---

## 🎓 MEJORES PRÁCTICAS

1. **Usar el nivel correcto:**
   - `DEBUG`: Solo para desarrollo
   - `INFO`: Eventos normales importantes
   - `WARNING`: Algo inesperado pero no crítico
   - `ERROR`: Error que impide una operación
   - `CRITICAL`: Error grave del sistema

2. **Incluir contexto:**
   ```python
   # ❌ Malo
   logger.error("Error al guardar")
   
   # ✅ Bueno
   logger.error(f"Error al guardar gasto {gasto.id} - Usuario: {user.username}", exc_info=True)
   ```

3. **No loggear información sensible:**
   ```python
   # ❌ Malo
   logger.info(f"Password: {password}")
   
   # ✅ Bueno
   logger.info(f"Usuario {username} intentó login")
   ```

4. **Usar exc_info=True para excepciones:**
   ```python
   try:
       # código
   except Exception as e:
       logger.error(f"Error: {e}", exc_info=True)  # Incluye traceback
   ```

---

## 📝 RESUMEN RÁPIDO

**El sistema de logs está ACTIVO y funcionando.**

**Archivos generados:**
- `logs/errors.log` - Solo errores
- `logs/application.log` - Todo
- `logs/django.log` - Framework

**Para ver logs:**
```bash
tail -f logs/errors.log
```

**Para usar en código:**
```python
import logging
logger = logging.getLogger('gastos')
logger.info("Mensaje informativo")
logger.error("Mensaje de error", exc_info=True)
```

**Los logs se rotan automáticamente** cuando alcanzan 10 MB.

---

**Los logs te ayudarán a identificar y resolver problemas más rápidamente.** 🚀
