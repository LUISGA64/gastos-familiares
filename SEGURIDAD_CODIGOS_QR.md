# 🔐 SEGURIDAD EN CÓDIGOS QR DE PAGO - ANÁLISIS Y RECOMENDACIONES

## ⚠️ RIESGOS DE SEGURIDAD AL COMPARTIR CÓDIGOS QR

### 🎯 Riesgos Principales

#### 1. **Exposición de Datos Bancarios** 🏦
**Riesgo**: MEDIO-ALTO

**Qué contiene un QR de Bancolombia/Nequi**:
- ✅ Número de cuenta (visible)
- ✅ Nombre del titular (visible)
- ✅ Monto de la transacción
- ✅ Referencia de pago
- ❌ NO contiene claves ni contraseñas

**Implicaciones**:
```
✓ Alguien puede VER tu número de cuenta
✓ Alguien puede VER tu nombre
✗ NO pueden retirar dinero de tu cuenta
✗ NO pueden acceder a tu banca online
✓ PUEDEN hacerte transferencias (positivo)
```

**Nivel de riesgo**: Similar a compartir tu número de cuenta públicamente

---

#### 2. **QR Maliciosos (QR Phishing)** 🎣
**Riesgo**: ALTO

**Escenario de ataque**:
```
1. Atacante crea QR falso
2. Usuario escanea el QR
3. QR redirige a:
   - Sitio web falso de banco
   - Descarga de malware
   - Formulario de phishing
4. Usuario ingresa credenciales
5. Atacante roba las credenciales
```

**En tu aplicación**:
- ✅ Los QR se generan INTERNAMENTE (más seguro)
- ✅ Los usuarios NO pueden subir QRs externos
- ⚠️ Los usuarios SÍ suben comprobantes (imágenes)

---

#### 3. **Modificación de QR (QR Jacking)** 🔄
**Riesgo**: MEDIO

**Escenario**:
```
1. QR legítimo generado
2. Atacante intercepta/modifica el QR
3. Cambia número de cuenta destino
4. Usuario escanea QR modificado
5. Dinero va a cuenta del atacante
```

**Protección en tu app**:
- ✅ QR se genera en servidor (backend)
- ✅ QR se muestra directamente al usuario
- ✅ No hay intermediarios
- ⚠️ FALTA: Firma digital del QR

---

#### 4. **Ingeniería Social** 👥
**Riesgo**: ALTO

**Escenarios comunes**:
```
❌ "Escanea este QR para recibir un premio"
❌ "QR para verificar tu cuenta bancaria"
❌ "Paga aquí para desbloquear tu cuenta"
❌ "QR de reembolso - ingresa tu clave"
```

**Protección**:
- ✅ Educación del usuario
- ✅ Mensajes claros en la interfaz
- ⚠️ FALTA: Advertencias de seguridad

---

#### 5. **Captura de Pantalla/Reutilización** 📸
**Riesgo**: MEDIO

**Problema**:
```
1. Usuario genera QR de pago
2. Usuario toma screenshot
3. Screenshot se comparte/filtra
4. Otra persona escanea el mismo QR
5. Paga a la misma cuenta/referencia
```

**Implicaciones**:
- ✅ El dinero llega a TU cuenta (positivo si es legítimo)
- ❌ Referencia puede duplicarse
- ❌ Difícil rastrear origen del pago

**Protección en tu app**:
- ✅ Referencia única por QR
- ⚠️ FALTA: Expiración del QR
- ⚠️ FALTA: QR de un solo uso

---

## 🛡️ ANÁLISIS DEL SISTEMA ACTUAL

### Lo que YA está Protegido ✅

#### 1. Generación Segura de QR
```python
# En qr_utils.py
@staticmethod
def generar_referencia_unica():
    """Genera referencia única imposible de predecir"""
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    random_str = uuid.uuid4().hex[:8].upper()
    return f"PAG-{timestamp}-{random_str}"
```
✅ **Bueno**: UUID + timestamp = muy difícil de duplicar

#### 2. Aislamiento de Familias
```python
familia = get_object_or_404(Familia, id=familia_id)
# Solo muestra datos de la familia del usuario
```
✅ **Bueno**: No hay cross-contamination de datos

#### 3. Validación de Comprobantes
```python
def validar_comprobante(archivo):
    # Valida tamaño y tipo de archivo
    extensiones_permitidas = ['jpg', 'jpeg', 'png', 'pdf']
    max_size = 5 * 1024 * 1024  # 5MB
```
✅ **Bueno**: Previene subida de archivos maliciosos grandes

#### 4. Verificación Manual
```python
# views_pagos.py
@login_required
def verificar_pagos(request):
    if not request.user.is_staff:
        return redirect('dashboard')
```
✅ **Bueno**: Humano verifica cada pago antes de aprobar

---

### Lo que FALTA Implementar ⚠️

#### 1. **Expiración de QR**
**Riesgo actual**: QR válidos indefinidamente

**Recomendación**:
```python
# Agregar campo en modelo Pago
expira_en = models.DateTimeField(
    default=lambda: timezone.now() + timedelta(hours=24)
)

# Validar en vista
if pago.expira_en < timezone.now():
    return JsonResponse({'error': 'QR expirado'}, status=400)
```

#### 2. **Límite de Intentos de Pago**
**Riesgo actual**: Infinitos intentos con el mismo QR

**Recomendación**:
```python
# Agregar campo
intentos_pago = models.IntegerField(default=0)
max_intentos = models.IntegerField(default=3)

# Validar
if pago.intentos_pago >= pago.max_intentos:
    pago.estado = 'BLOQUEADO'
```

#### 3. **Firma Digital de QR**
**Riesgo actual**: QR puede ser modificado

**Recomendación**:
```python
import hmac
import hashlib

def firmar_qr(datos, secret_key):
    """Firma digital para validar integridad del QR"""
    mensaje = f"{datos['referencia']}{datos['monto']}{datos['cuenta']}"
    firma = hmac.new(
        secret_key.encode(),
        mensaje.encode(),
        hashlib.sha256
    ).hexdigest()
    return firma
```

#### 4. **Rate Limiting**
**Riesgo actual**: Puede generar infinitos QR

**Recomendación**:
```python
from django.core.cache import cache

def rate_limit_qr(user_id):
    key = f'qr_generation_{user_id}'
    count = cache.get(key, 0)
    
    if count >= 10:  # Máximo 10 QR por hora
        return False
    
    cache.set(key, count + 1, 3600)  # 1 hora
    return True
```

#### 5. **Logging de Actividad Sospechosa**
**Riesgo actual**: No hay registro de intentos fallidos

**Recomendación**:
```python
import logging

logger = logging.getLogger('security')

# En cada intento de pago
logger.warning(f'Intento de pago fallido: {pago.id} - IP: {request.META["REMOTE_ADDR"]}')
```

#### 6. **Advertencias de Seguridad**
**Riesgo actual**: Usuario no está educado sobre riesgos

**Recomendación**: Agregar mensajes en UI

---

## 🚨 RECOMENDACIONES CRÍTICAS

### Para el Desarrollador (TÚ) 👨‍💻

#### Prioridad ALTA 🔴

1. **Implementar Expiración de QR**
   ```
   Tiempo: 30 minutos
   Impacto: ALTO
   Dificultad: Baja
   ```

2. **Agregar HTTPS Obligatorio**
   ```python
   # En settings.py
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```

3. **Validar Origen de Comprobantes**
   ```python
   # Escanear archivos con antivirus
   # O usar servicio como VirusTotal API
   ```

#### Prioridad MEDIA 🟡

4. **Rate Limiting de Generación de QR**
5. **Logging de Seguridad**
6. **Firma Digital de QR**

#### Prioridad BAJA 🟢

7. **Notificaciones de Actividad Sospechosa**
8. **2FA para Administradores**

---

### Para los Usuarios 👥

#### Nunca Compartas ❌

1. ❌ QR en redes sociales públicas
2. ❌ QR por WhatsApp a desconocidos
3. ❌ Screenshots de QR sin necesidad
4. ❌ QR en grupos públicos

#### Siempre Verifica ✅

1. ✅ El monto es correcto
2. ✅ El número de cuenta es tuyo
3. ✅ La referencia es única
4. ✅ Estás en el sitio oficial (https://)
5. ✅ Elimina screenshots después de usar

#### En Caso de Sospecha 🚨

1. 🛑 NO escanees QR de fuentes desconocidas
2. 📞 Contacta a soporte antes de pagar
3. 🔍 Verifica siempre en tu app bancaria
4. 🚫 Nunca ingreses claves en enlaces de QR

---

## 🔒 MEJORES PRÁCTICAS IMPLEMENTADAS

### Comparación con la Industria

| Medida de Seguridad | Tu App | Bancolombia | Nequi | PSE |
|---------------------|--------|-------------|-------|-----|
| Generación segura QR | ✅ | ✅ | ✅ | ✅ |
| Referencias únicas | ✅ | ✅ | ✅ | ✅ |
| Validación comprobantes | ✅ | ✅ | ✅ | ✅ |
| Expiración QR | ❌ | ✅ | ✅ | ✅ |
| Firma digital | ❌ | ✅ | ✅ | ✅ |
| Rate limiting | ❌ | ✅ | ✅ | ✅ |
| HTTPS | ⚠️ | ✅ | ✅ | ✅ |
| 2FA Admin | ❌ | ✅ | ✅ | ✅ |

**Tu nivel de seguridad**: 6/10 (Bueno, pero mejorable)

---

## 💡 RESPUESTA A TU PREGUNTA

### "¿Qué implicaciones tiene compartir un código QR?"

#### Riesgos REALES 🎯

1. **Tu número de cuenta es visible** 
   - Similar a dar tu número de CBU/CLABE
   - Alguien puede hacerte transferencias
   - NO pueden sacar dinero

2. **Tu nombre es visible**
   - Dato público, no crítico
   - Ya está en muchas bases de datos

3. **Pueden hacer pagos a tu cuenta**
   - ✅ Positivo si es legítimo
   - ❌ Puede generar confusión si no esperas el pago

4. **Reutilización del QR**
   - Alguien podría pagar dos veces
   - Ambos pagos llegan a ti (no es pérdida)
   - Pero genera problemas de conciliación

#### Riesgos MÍNIMOS ✅

1. ❌ NO pueden acceder a tu cuenta bancaria
2. ❌ NO pueden robar tu dinero
3. ❌ NO pueden hacer transacciones no autorizadas
4. ❌ NO expones tus contraseñas

#### Recomendación Final 📌

**Compartir QR de pago es SEGURO si**:
- ✅ Lo compartes solo con quien debe pagar
- ✅ Es por canal privado (WhatsApp personal, email)
- ✅ Verificas que el QR es el correcto antes de enviar
- ✅ Eliminas el QR después de recibir el pago
- ✅ NO lo publicas en redes sociales

**Es RIESGOSO si**:
- ❌ Lo publicas en redes sociales públicas
- ❌ Lo compartes en grupos masivos
- ❌ No verificas a quién lo envías
- ❌ Reutilizas el mismo QR múltiples veces

---

## 🛠️ MEJORAS A IMPLEMENTAR

### Plan de Acción Recomendado

#### Fase 1: Seguridad Básica (1-2 días) 🔴
```
1. Agregar expiración de QR (24 horas)
2. Implementar HTTPS obligatorio
3. Agregar advertencias en UI
4. Validar tamaño máximo de comprobantes
```

#### Fase 2: Seguridad Avanzada (3-5 días) 🟡
```
5. Rate limiting de generación QR
6. Logging de actividad sospechosa
7. Firma digital de QR
8. Escaneo antivirus de comprobantes
```

#### Fase 3: Seguridad Empresarial (1-2 semanas) 🟢
```
9. 2FA para administradores
10. Notificaciones automáticas de pagos
11. Dashboard de seguridad
12. Auditoría de transacciones
```

---

## 📊 CONCLUSIÓN

### Nivel de Seguridad Actual: 6/10

**Puntos Fuertes** ✅:
- Generación segura de referencias
- Validación de comprobantes
- Verificación manual de pagos
- Aislamiento de datos por familia

**Puntos a Mejorar** ⚠️:
- Expiración de QR
- Rate limiting
- Firma digital
- HTTPS obligatorio
- Logging de seguridad

### Riesgo de Compartir QR: MEDIO-BAJO

**No expones**: Contraseñas, acceso bancario, capacidad de retiro  
**Sí expones**: Número de cuenta, nombre (datos ya parcialmente públicos)  
**Recomendación**: Compartir solo con personas de confianza, canales privados

---

**Fecha**: 18/01/2026  
**Autor**: Análisis de Ciberseguridad  
**Versión**: 1.0
