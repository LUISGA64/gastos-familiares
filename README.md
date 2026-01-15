# Gestor de Gastos Familiares 💰

Sistema web completo para la gestión y control de gastos familiares con distribución automática según ingresos, conciliación mensual y múltiples planes de suscripción.

## 🌟 Características Principales

### ✅ Gestión de Familias
- Sistema multi-tenant (múltiples familias aisladas)
- Aislamiento total de datos entre familias
- Creación automática de familia al registrarse
- Seguridad multinivel con middleware personalizado

### 💰 Gestión de Gastos
- Registro de gastos con distribución automática
- Clasificación por categorías y subcategorías
- Gastos fijos y variables
- Adjuntar comprobantes (según plan)
- Historial completo de gastos

### 👥 Aportantes
- Registro de aportantes con ingresos mensuales
- Cálculo automático de porcentajes de aporte
- Distribución proporcional de gastos
- Gestión de emails para notificaciones

### 📊 Conciliación Mensual
- Cálculo automático de reintegros
- Cierre de períodos mensuales
- Historial de conciliaciones
- Notificaciones por email a aportantes

### 📈 Reportes y Análisis
- Dashboard con métricas en tiempo real
- Reportes avanzados (Plan Básico+)
- Gráficos interactivos
- Exportación a Excel/PDF (Plan Premium)

### 💳 Sistema de Suscripciones
- Plan Gratuito (limitado)
- Plan Básico ($9,900/mes) - Recomendado
- Plan Premium ($15,900/mes)
- Plan Empresarial ($49,900/mes)

### 💰 Pagos con Códigos QR
- Bancolombia (Transferencia con QR)
- Nequi (Pago con QR)
- Upload de comprobantes
- Verificación manual de pagos
- Activación automática de suscripción

## 🚀 Tecnologías

- **Backend:** Django 5.0
- **Base de Datos:** SQLite (desarrollo) / PostgreSQL (producción recomendada)
- **Frontend:** Bootstrap 5, Chart.js
- **Python:** 3.12+
- **Librerías:** qrcode, Pillow, openpyxl

## 📋 Requisitos

```bash
Python 3.12 o superior
Django 5.0
pillow
qrcode
openpyxl (opcional, para exportar Excel)
```

## 🛠️ Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/[TU_USUARIO]/DjangoProject.git
cd DjangoProject
```

### 2. Crear entorno virtual

```bash
python -m venv .venv
```

### 3. Activar entorno virtual

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Aplicar migraciones

```bash
python manage.py migrate
```

### 6. Crear superusuario

```bash
python manage.py createsuperuser
```

### 7. Cargar datos de ejemplo (opcional)

```bash
python manage.py cargar_datos_ejemplo
```

### 8. Ejecutar servidor

```bash
python manage.py runserver
```

Accede a: `http://localhost:8000`

## 📱 Uso

### Registro de Usuario

1. Ir a `/registro/`
2. Completar formulario
3. Ingresar código de invitación (ver `CODIGOS_GENERADOS.md`)
4. Sistema crea automáticamente tu familia

### Configuración Inicial

1. Dashboard → Aportantes → Crear aportantes
2. Dashboard → Categorías → Crear categorías
3. Dashboard → Gastos → Registrar gastos

### Conciliación Mensual

1. Dashboard → Conciliación
2. Revisar distribución de gastos
3. Cerrar conciliación
4. Confirmar y enviar notificaciones

## 💳 Planes de Suscripción

### Plan Gratuito ($0/mes)
- 2 aportantes
- 30 gastos/mes
- 5 categorías
- Historial 3 meses

### Plan Básico ($9,900/mes) ⭐ Recomendado
- 4 aportantes
- 100 gastos/mes
- 15 categorías
- ✅ Reportes avanzados
- ✅ Conciliación automática
- ✅ Notificaciones email
- ✅ Historial ilimitado
- ✅ 1 archivo adjunto

### Plan Premium ($15,900/mes)
- 8 aportantes
- 500 gastos/mes
- 50 categorías
- ✅ Todo del Básico +
- ✅ Exportar Excel/PDF
- ✅ 5 archivos adjuntos
- ✅ Soporte prioritario

### Plan Empresarial ($49,900/mes)
- Ilimitado todo
- 10 archivos adjuntos
- Soporte dedicado
- Capacitación incluida

## 🔒 Seguridad

- ✅ Aislamiento total de datos por familia
- ✅ Middleware de seguridad personalizado
- ✅ Autenticación requerida
- ✅ CSRF Protection
- ✅ Validación de permisos multinivel
- ✅ Passwords hasheados (Django Auth)

## 📞 Contacto

- **WhatsApp:** +57 311 700 9855
- **Email:** soporte@gastosfamiliares.com

## 📄 Documentación

- `INICIO_RAPIDO.md` - Guía de inicio rápido
- `AISLAMIENTO_FAMILIAS.md` - Sistema de seguridad
- `SISTEMA_PAGOS_QR.md` - Pagos con QR
- `DIFERENCIACION_PLANES.md` - Planes y precios
- `MODELO_COMERCIALIZACION.md` - Modelo de negocio

## 🧪 Testing

Ejecutar pruebas de aislamiento:

```bash
python test_aislamiento.py
```

## 🗂️ Estructura del Proyecto

```
DjangoProject/
├── DjangoProject/          # Configuración del proyecto
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── gastos/                 # App principal
│   ├── models.py           # Modelos de datos
│   ├── views.py            # Vistas principales
│   ├── views_auth.py       # Autenticación
│   ├── views_pagos.py      # Sistema de pagos
│   ├── qr_utils.py         # Utilidades QR
│   ├── middleware.py       # Seguridad
│   └── templates/          # Templates HTML
├── templates/              # Templates globales
├── static/                 # Archivos estáticos
├── media/                  # Archivos subidos
├── requirements.txt        # Dependencias
└── manage.py              # Django CLI
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/mejora`)
3. Commit cambios (`git commit -am 'Agrega nueva función'`)
4. Push a la rama (`git push origin feature/mejora`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es de código abierto bajo licencia MIT.

## 🎯 Roadmap

- [ ] Integración PSE
- [ ] API REST
- [ ] App móvil nativa
- [ ] Pagos recurrentes automáticos
- [ ] OCR para comprobantes
- [ ] Dashboard mejorado con más gráficos
- [ ] Exportación automática mensual
- [ ] Notificaciones push

## 👨‍💻 Autor

Desarrollado con ❤️ para familias colombianas

---

**¿Preguntas o sugerencias?** Contáctanos por WhatsApp: +57 311 700 9855

