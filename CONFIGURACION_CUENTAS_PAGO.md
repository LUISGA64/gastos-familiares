# 🏦 CONFIGURACIÓN DE CUENTAS DE PAGO - GUÍA COMPLETA

## 📋 Resumen

Se ha implementado un **sistema editable de cuentas de pago** que permite configurar las cuentas de Bancolombia y Nequi desde el panel de administración de Django, sin necesidad de modificar código.

---

## ✅ Lo que se Implementó

### 1. **Modelo ConfiguracionCuentaPago**
Base de datos para almacenar la configuración de cuentas.

**Campos**:
- `metodo`: BANCOLOMBIA, NEQUI, DAVIPLATA, OTRO
- `activo`: Si la cuenta está activa o no
- `nombre_banco`: Nombre del banco/entidad
- `tipo_cuenta`: Ahorros, Corriente, Nequi, etc.
- `numero_cuenta`: Número de cuenta o celular
- `titular`: Nombre del titular
- `nit`: NIT (opcional)
- `color`: Color del botón (#FFDD00)
- `icono`: Emoji (🏦, 💰)
- `instrucciones`: Texto con instrucciones para el usuario

### 2. **Panel de Administración**
Interfaz gráfica para editar las cuentas en `/admin/`

### 3. **Sistema Dinámico**
El código ahora lee las cuentas desde la base de datos automáticamente.

---

## 🚀 Cómo Configurar TUS Cuentas Reales

### Opción 1: Desde el Admin de Django (Recomendado)

#### Paso 1: Acceder al Admin
```
1. Ir a: http://127.0.0.1:8000/admin/
2. Iniciar sesión con tu usuario administrador
```

#### Paso 2: Buscar Configuraciones
```
3. En el menú lateral, buscar: "Configuraciones de Cuentas de Pago"
4. Hacer clic para ver la lista
```

#### Paso 3: Editar Bancolombia
```
5. Hacer clic en "Bancolombia"
6. Modificar los siguientes campos:
   
   ✏️ Número de Cuenta/Celular:
      Cambiar de: 12345678901
      A: TU_NUMERO_DE_CUENTA_REAL
   
   ✏️ Titular de la Cuenta:
      Cambiar de: Gestor Gastos Familiares SAS
      A: TU_NOMBRE_O_EMPRESA
   
   ✏️ NIT (opcional):
      Cambiar de: 900.123.456-7
      A: TU_NIT_REAL (o dejar vacío)

7. Hacer clic en "GUARDAR"
```

#### Paso 4: Editar Nequi
```
8. Volver a la lista de cuentas
9. Hacer clic en "Nequi"
10. Modificar:
   
   ✏️ Número de Cuenta/Celular:
      Cambiar de: 300 123 4567
      A: TU_NUMERO_NEQUI_REAL (ej: 311 700 9855)
   
   ✏️ Titular de la Cuenta:
      Cambiar de: Gestor Gastos Familiares
      A: TU_NOMBRE_REAL

11. Hacer clic en "GUARDAR"
```

#### Paso 5: Verificar
```
12. Ir a: http://127.0.0.1:8000/suscripcion/pagar/
13. Verificar que los datos mostrados sean los correctos
```

---

### Opción 2: Desde la Shell de Django (Avanzado)

```python
python manage.py shell

# En la shell:
from gastos.models import ConfiguracionCuentaPago

# Actualizar Bancolombia
bancolombia = ConfiguracionCuentaPago.objects.get(metodo='BANCOLOMBIA')
bancolombia.numero_cuenta = '98765432109'  # TU CUENTA REAL
bancolombia.titular = 'Tu Nombre o Empresa'
bancolombia.nit = '900.XXX.XXX-X'  # Tu NIT
bancolombia.save()
print("✅ Bancolombia actualizada")

# Actualizar Nequi
nequi = ConfiguracionCuentaPago.objects.get(metodo='NEQUI')
nequi.numero_cuenta = '311 700 9855'  # TU NEQUI REAL
nequi.titular = 'Tu Nombre'
nequi.save()
print("✅ Nequi actualizada")
```

---

### Opción 3: Editar el Script `configurar_cuentas_pago.py`

```python
# Editar el archivo: configurar_cuentas_pago.py

# Línea 24 - Bancolombia
'numero_cuenta': 'TU_CUENTA_REAL',  # ← Cambiar aquí
'titular': 'Tu Nombre/Empresa',     # ← Cambiar aquí
'nit': 'TU_NIT',                    # ← Cambiar aquí

# Línea 42 - Nequi
'numero_cuenta': 'TU_NEQUI',  # ← Cambiar aquí (ej: 311 700 9855)
'titular': 'Tu Nombre',        # ← Cambiar aquí

# Ejecutar:
python configurar_cuentas_pago.py
```

---

## 📊 Campos Disponibles para Editar

### Bancolombia
| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| Número de cuenta | Tu número de cuenta Bancolombia | `98765432109` |
| Titular | Nombre del titular | `Juan Pérez` o `Mi Empresa SAS` |
| NIT | NIT de la empresa (opcional) | `900.123.456-7` |
| Color | Color del botón (hexadecimal) | `#FFDD00` (amarillo Bancolombia) |
| Icono | Emoji para el botón | `🏦` |
| Instrucciones | Pasos para el usuario | Una por línea |

### Nequi
| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| Número | Tu número de celular Nequi | `311 700 9855` |
| Titular | Tu nombre | `Juan Pérez` |
| Color | Color del botón | `#FF006B` (morado Nequi) |
| Icono | Emoji | `💰` |
| Instrucciones | Pasos para el usuario | Una por línea |

---

## 🎨 Personalización Adicional

### Cambiar Colores de los Botones
```
1. En el admin, editar la cuenta
2. Campo "Color del Botón"
3. Ingresar código hexadecimal, ej:
   - Bancolombia: #FFDD00 (amarillo)
   - Nequi: #FF006B (morado)
   - DaviPlata: #ED1C24 (rojo)
   - Personalizado: #3498db (azul)
```

### Cambiar Iconos
```
1. Campo "Emoji/Icono"
2. Usar emojis:
   🏦 - Banco
   💰 - Dinero
   💳 - Tarjeta
   📱 - Celular
   ✅ - Check
```

### Editar Instrucciones
```
1. Campo "Instrucciones para el Usuario"
2. Una instrucción por línea, ej:

Abre la app de Bancolombia
Ve a "Transferencias"
Selecciona "Código QR"
Escanea el código
Confirma el monto
Completa el pago
Sube tu comprobante
```

---

## 🔒 Activar/Desactivar Métodos de Pago

### Desactivar un Método
```
1. En el admin, editar la cuenta
2. Desmarcar "Activo"
3. Guardar
→ El método NO aparecerá en la página de pagos
```

### Reactivar un Método
```
1. Marcar "Activo"
2. Guardar
→ El método volverá a aparecer
```

---

## ➕ Agregar Nuevos Métodos de Pago

### Ejemplo: Agregar DaviPlata

```python
python manage.py shell

from gastos.models import ConfiguracionCuentaPago

daviplata = ConfiguracionCuentaPago.objects.create(
    metodo='DAVIPLATA',
    activo=True,
    nombre_banco='DaviPlata',
    tipo_cuenta='DAVIPLATA',
    numero_cuenta='300 765 4321',  # Tu número DaviPlata
    titular='Tu Nombre',
    color='#ED1C24',
    icono='📱',
    instrucciones='''Abre la app DaviPlata
Ve a "Enviar plata"
Ingresa el número destino
Confirma el monto
Completa la transferencia
Sube el comprobante'''
)

print("✅ DaviPlata agregado")
```

---

## 🧪 Verificar que Funciona

### Test 1: Ver en Página de Pagos
```
1. Ir a: http://127.0.0.1:8000/suscripcion/pagar/
2. Verificar que aparezcan tus métodos de pago
3. Los datos mostrados deben ser los que configuraste
```

### Test 2: Generar QR
```
1. Seleccionar un plan
2. Elegir método (Bancolombia o Nequi)
3. El QR generado debe contener TUS datos reales
```

### Test 3: Información de Cuenta
```
1. En la página del QR
2. Verificar que se muestren:
   ✅ Tu número de cuenta/celular correcto
   ✅ Tu nombre como titular
   ✅ Instrucciones personalizadas
```

---

## 📁 Archivos del Sistema

### Archivos Creados
- `gastos/models.py` - Modelo `ConfiguracionCuentaPago` (línea 1363)
- `gastos/admin.py` - Admin `ConfiguracionCuentaPagoAdmin` (línea 598)
- `configurar_cuentas_pago.py` - Script de configuración inicial
- `CONFIGURACION_CUENTAS_PAGO.md` - Esta guía

### Archivos Modificados
- `gastos/qr_utils.py` - Función `obtener_info_cuentas()` y `get_info_cuentas_colombia()`
- `gastos/views_pagos.py` - Usa `get_info_cuentas_colombia()` dinámicamente

### Migración Aplicada
- `gastos/migrations/0010_configuracioncuentapago.py`

---

## ❓ Preguntas Frecuentes

### ¿Dónde se almacenan las cuentas?
En la **base de datos** (tabla `gastos_configuracioncuentapago`).

### ¿Necesito reiniciar el servidor después de editar?
**No**, los cambios se aplican inmediatamente.

### ¿Puedo tener múltiples cuentas del mismo método?
No, solo una cuenta por método (BANCOLOMBIA, NEQUI, etc.). Si necesitas cambiar la cuenta, edita la existente.

### ¿Qué pasa si borro una cuenta por error?
Ejecuta de nuevo: `python configurar_cuentas_pago.py` para recrearla con datos de ejemplo.

### ¿Los QR funcionan con datos de ejemplo?
**No**, debes configurar **tus datos reales** para que los pagos lleguen a tu cuenta.

### ¿Puedo agregar otros métodos como PSE o tarjetas?
Sí, pero requiere desarrollo adicional para integrarse con las pasarelas de pago.

---

## 🎉 Resultado Final

### Antes
```python
# Datos hardcodeados en qr_utils.py
INFO_CUENTAS_COLOMBIA = {
    'bancolombia': {
        'numero': '12345678901',  # ← No editable sin tocar código
        ...
    }
}
```

### Ahora
```
1. Ir a /admin/
2. Clic en "Configuraciones de Cuentas de Pago"
3. Editar visualmente
4. Guardar
✅ Cambios aplicados automáticamente
```

---

## 📞 Soporte

Si necesitas ayuda:
1. Verifica que ejecutaste: `python configurar_cuentas_pago.py`
2. Verifica que aplicaste las migraciones: `python manage.py migrate`
3. Accede al admin: `http://127.0.0.1:8000/admin/`

---

**Fecha**: 18/01/2026  
**Estado**: ✅ Sistema de configuración editable implementado  
**Ubicación Admin**: `/admin/` → "Configuraciones de Cuentas de Pago"
