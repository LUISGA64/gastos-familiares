# 🚀 ACTIVACIÓN DEL SISTEMA - PASOS FINALES

## ✅ Lo que está implementado

Todo el código está listo. Solo faltan estos pasos finales:

---

## 📋 PASO 1: Aplicar Migraciones

```bash
cd C:\Users\luisg\PycharmProjects\DjangoProject

# Eliminar base de datos antigua (solo esta vez)
Remove-Item db.sqlite3

# Eliminar migraciones antiguas
Remove-Item gastos\migrations\0001_initial.py

# Crear nuevas migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

---

## 📋 PASO 2: Crear Planes de Suscripción

```bash
python manage.py shell
```

Luego copiar y pegar:

```python
from gastos.models import PlanSuscripcion
from decimal import Decimal

# Plan Gratuito
PlanSuscripcion.objects.create(
    nombre="Plan Gratuito",
    tipo="GRATIS",
    precio_mensual=Decimal('0'),
    max_aportantes=2,
    max_gastos_mes=30,
    max_categorias=5,
    dias_prueba=0,
    caracteristicas="Ideal para comenzar\nSoporte básico"
)

# Plan Básico
PlanSuscripcion.objects.create(
    nombre="Plan Básico",
    tipo="BASICO",
    precio_mensual=Decimal('9900'),
    max_aportantes=4,
    max_gastos_mes=100,
    max_categorias=15,
    dias_prueba=15,
    caracteristicas="Perfecto para parejas\nSoporte por email\n15 días de prueba gratis"
)

# Plan Premium
PlanSuscripcion.objects.create(
    nombre="Plan Premium",
    tipo="PREMIUM",
    precio_mensual=Decimal('19900'),
    max_aportantes=999,
    max_gastos_mes=999999,
    max_categorias=999,
    dias_prueba=15,
    caracteristicas="Todo ilimitado\nSoporte prioritario\nExportación de datos\nReportes avanzados"
)

# Plan Empresarial
PlanSuscripcion.objects.create(
    nombre="Plan Empresarial",
    tipo="EMPRESARIAL",
    precio_mensual=Decimal('49900'),
    max_aportantes=999,
    max_gastos_mes=999999,
    max_categorias=999,
    dias_prueba=30,
    caracteristicas="Múltiples familias\nAPI personalizada\nSoporte 24/7\nCapacitación incluida"
)

print("✅ Planes creados exitosamente")
exit()
```

---

## 📋 PASO 3: Generar Códigos de Invitación

```bash
python manage.py shell
```

Luego:

```python
from gastos.models import CodigoInvitacion, PlanSuscripcion
import random
import string

def generar_codigo():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

# Obtener planes
plan_gratis = PlanSuscripcion.objects.get(tipo='GRATIS')
plan_basico = PlanSuscripcion.objects.get(tipo='BASICO')
plan_premium = PlanSuscripcion.objects.get(tipo='PREMIUM')

# Generar códigos para plan GRATIS (para pruebas)
print("\n📌 CÓDIGOS PLAN GRATUITO (Para pruebas):")
for i in range(5):
    codigo = generar_codigo()
    CodigoInvitacion.objects.create(codigo=codigo, plan=plan_gratis)
    print(f"  {codigo}")

# Generar códigos para plan BÁSICO (Para vender)
print("\n💰 CÓDIGOS PLAN BÁSICO ($9,900/mes):")
for i in range(10):
    codigo = generar_codigo()
    CodigoInvitacion.objects.create(codigo=codigo, plan=plan_basico)
    print(f"  {codigo}")

# Generar códigos para plan PREMIUM (Para vender)
print("\n⭐ CÓDIGOS PLAN PREMIUM ($19,900/mes):")
for i in range(5):
    codigo = generar_codigo()
    CodigoInvitacion.objects.create(codigo=codigo, plan=plan_premium)
    print(f"  {codigo}")

print("\n✅ Códigos generados exitosamente")
exit()
```

---

## 📋 PASO 4: Iniciar Servidor

```bash
python manage.py runserver
```

---

## 🧪 PASO 5: Probar el Sistema

### Test 1: Ver Planes
```
http://127.0.0.1:8000/planes/
```
Deberías ver la página de precios con los 4 planes.

### Test 2: Registro con Código
```
1. Ir a: http://127.0.0.1:8000/registro/
2. Llenar formulario
3. Usar uno de los códigos generados
4. Debería crear cuenta y loguearte automáticamente
```

### Test 3: Login
```
1. Logout
2. Ir a: http://127.0.0.1:8000/login/
3. Ingresar con usuario creado
4. Debería acceder al dashboard
```

### Test 4: Límites del Plan
```
Si te registraste con plan GRATIS:
1. Crear 2 aportantes → OK
2. Intentar crear 3er aportante → Debería mostrar error "Límite alcanzado"

Si te registraste con plan BÁSICO:
1. Crear 4 aportantes → OK
2. Intentar crear 5to aportante → Debería mostrar error
```

---

## 💡 COMANDOS ÚTILES

### Ver todos los códigos disponibles:
```python
python manage.py shell

from gastos.models import CodigoInvitacion
codigos = CodigoInvitacion.objects.filter(usado=False)
for c in codigos:
    print(f"{c.codigo} - {c.plan.nombre}")
exit()
```

### Ver todas las familias registradas:
```python
python manage.py shell

from gastos.models import Familia
familias = Familia.objects.all()
for f in familias:
    print(f"{f.nombre} - {f.plan.nombre} - Activa: {f.esta_suscripcion_activa()}")
exit()
```

### Aprobar un pago manualmente:
```python
python manage.py shell

from gastos.models import Pago
pago = Pago.objects.filter(estado='PENDIENTE').first()
if pago:
    pago.aprobar_pago()
    print("Pago aprobado y suscripción extendida")
exit()
```

---

## 🎯 FLUJO COMERCIAL

### Para VENDER un código:

```
1. Cliente quiere Plan Básico ($9,900/mes)
2. Cliente paga (Nequi, transferencia, etc.)
3. Tú generas código en shell
4. Envías código por email al cliente
5. Cliente se registra con el código
6. Cliente tiene 15 días de prueba gratis
7. Después de 15 días:
   - Si configuraste pago recurrente → Cobra automático
   - Si no → Cliente debe renovar manual
```

### Para GENERAR código individual:

```python
python manage.py shell

from gastos.models import CodigoInvitacion, PlanSuscripcion
import random, string

# Cliente compró Plan Premium
plan = PlanSuscripcion.objects.get(tipo='PREMIUM')

# Generar código único
codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

# Crear código
CodigoInvitacion.objects.create(codigo=codigo, plan=plan)

print(f"Código generado: {codigo}")
print("Envía este código al cliente por email")
exit()
```

---

## 📧 EMAIL AL CLIENTE (Plantilla)

```
Asunto: Tu código de acceso a Gastos Familiares

Hola Juan,

¡Gracias por tu compra del Plan Premium!

Tu código de invitación es: ABC123XYZ456

Para activar tu cuenta:
1. Ve a: http://tudominio.com/registro/
2. Completa el formulario
3. Ingresa tu código en el campo "Código de Invitación"
4. ¡Listo! Tendrás 15 días de prueba gratis

Características de tu Plan Premium:
✅ Aportantes ilimitados
✅ Gastos ilimitados
✅ Categorías ilimitadas
✅ Soporte prioritario
✅ Reportes avanzados

¿Dudas? Responde este email o escríbenos por WhatsApp.

¡Disfruta gestionando tus finanzas!

Equipo Gastos Familiares
```

---

## 🔧 TROUBLESHOOTING

### Error: "No module named 'gastos.views_auth'"
```bash
# Verificar que el archivo existe
dir gastos\views_auth.py

# Si no existe, lo creaste mal. Revisa los archivos creados.
```

### Error al hacer migraciones
```bash
# Eliminar todo y empezar de nuevo:
Remove-Item db.sqlite3
Remove-Item gastos\migrations\*.py -Exclude __init__.py
python manage.py makemigrations gastos
python manage.py migrate
```

### No aparecen los planes
```bash
# Verificar en shell:
python manage.py shell

from gastos.models import PlanSuscripcion
print(PlanSuscripcion.objects.all())

# Si está vacío, volver a crear los planes (Paso 2)
```

---

## ✅ CHECKLIST FINAL

Antes de lanzar públicamente, verifica:

- [ ] Migraciones aplicadas
- [ ] Planes creados (4 planes)
- [ ] Códigos generados (al menos 20)
- [ ] Superusuario creado
- [ ] Probado registro con código
- [ ] Probado login
- [ ] Probado límites de plan
- [ ] Página de planes funciona
- [ ] Logo y branding personalizados
- [ ] Email de contacto configurado
- [ ] WhatsApp de soporte configurado

---

## 🚀 LISTO PARA LANZAR

Una vez completados estos pasos:

✅ Sistema 100% funcional
✅ Usuarios pueden registrarse
✅ Solo con códigos válidos
✅ Planes y límites funcionando
✅ Privacidad garantizada
✅ Listo para monetizar

**¡A vender! 💰**

---

*Guía de Activación - Enero 13, 2026*

