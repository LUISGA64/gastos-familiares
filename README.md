# 💰 FinanBot - Gestión Inteligente de Gastos Familiares

<div align="center">

![Version](https://img.shields.io/badge/version-2.0-blue.svg)
![Django](https://img.shields.io/badge/Django-6.0-green.svg)
![Python](https://img.shields.io/badge/Python-3.11-yellow.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Status](https://img.shields.io/badge/status-Production-success.svg)

**Sistema moderno de gestión financiera familiar con inteligencia artificial**

[Características](#-características-principales) • [Instalación](#-instalación) • [Deploy](#-deploy) • [Contacto](#-contacto)

</div>

---

## 📋 Descripción

**FinanBot** es una aplicación web profesional desarrollada en Django para la gestión inteligente de gastos familiares. Permite a las familias controlar sus finanzas de manera colaborativa, distribuyendo gastos automáticamente según los ingresos de cada aportante, con análisis mediante inteligencia artificial y gamificación para motivar el ahorro.

### 🎯 Problema que Resuelve

- ❌ Dificultad para dividir gastos familiares equitativamente
- ❌ Falta de visibilidad de los gastos compartidos  
- ❌ No hay registro histórico de gastos
- ❌ Difícil controlar presupuestos y metas de ahorro
- ❌ Poca motivación para reducir gastos innecesarios

### ✅ Solución

FinanBot automatiza la distribución de gastos según ingresos, proporciona análisis inteligentes con IA, gamifica el ahorro con logros y recompensas, y ofrece reportes detallados en tiempo real.

---

## ⚡ Características Principales

### 💳 Gestión de Gastos

- **Registro de Gastos Compartidos y Personales**
  - Gastos familiares con distribución automática
  - Gastos personales privados por aportante
  - Categorización (Fijos/Variables)
  - Subcategorías personalizables
  
- **Distribución Inteligente**
  - Cálculo automático según porcentaje de ingresos
  - Balances individuales y familiares
  - Reintegros calculados automáticamente
  - Conciliación mensual con cierre de período

### 📊 Dashboard Premium

- **Visualización en Tiempo Real**
  - KPIs principales (Ingresos, Gastos, Balance)
  - Gráficos interactivos (Chart.js)
  - Tendencias de 6 meses
  - Distribución por categoría
  
- **Selector de Período**
  - Navegación entre meses (últimos 12 meses)
  - Comparación histórica
  - Exportación PDF/Excel

### 💰 Ingresos Personales

- **Registro de Ingresos**
  - Salarios mensuales
  - Ingresos extraordinarios
  - Bonificaciones y comisiones
  - Otros ingresos
  
- **Análisis de Ingresos**
  - Total por aportante
  - Distribución por tipo
  - Estadísticas mensuales

### 🎯 Metas de Ahorro

- **Creación de Metas**
  - Metas individuales o familiares
  - Fecha objetivo
  - Monto objetivo
  - Seguimiento de progreso
  
- **Gamificación**
  - 17+ logros desbloqueables
  - Sistema de niveles (1-10)
  - Notificaciones de hitos
  - Racha de días consecutivos
  - Ranking competitivo

### 🤖 Chatbot con IA

- **Asistente Financiero Inteligente**
  - Powered by Groq AI (LLaMA 3.3 70B)
  - Análisis de gastos en lenguaje natural
  - Recomendaciones personalizadas
  - Predicciones de gastos
  - Consejos de ahorro
  
- **14,400 mensajes/día GRATIS**
  - API Groq completamente gratuita
  - Sin límites para usuarios
  - Contexto personalizado
  - Histórico de conversaciones

### 🔐 Privacidad y Seguridad

- **Control de Privacidad**
  - Toggle instantáneo de valores monetarios (sin recarga)
  - Datos encriptados en tránsito (HTTPS)
  - Aislamiento de datos por familia
  - Autenticación segura
  
- **Auditoría**
  - Registro de actividad (Logs)
  - Historial de cambios
  - Trazabilidad completa

### 💎 Sistema de Suscripciones

| Plan | Precio | Familias | Aportantes | Características |
|------|--------|----------|------------|-----------------|
| **Gratuito** | $0 | 1 | 3 | Funcionalidades básicas |
| **Básico** | $9,900/mes | 2 | 5 | PDF/Excel, Sin anuncios |
| **Premium** | $15,900/mes | Ilimitadas | Ilimitados | IA ilimitada, Dashboard avanzado |
| **Empresarial** | $49,900/mes | Ilimitadas | Ilimitados | API REST, Soporte 24/7 |

### 💳 Métodos de Pago

- **Disponibles**
  - ✅ Transferencia Bancolombia (QR)
  - ✅ Nequi (QR)
  
- **Próximamente**
  - 🔜 Tarjetas de crédito
  - 🔜 PSE
  - 🔜 PayPal

### 📱 PWA (Progressive Web App)

- ✅ Instalable en dispositivos
- ✅ Funciona offline (básico)
- ✅ Notificaciones push
- ✅ Icono en pantalla de inicio
- ✅ Experiencia nativa

### 🎨 Diseño Moderno

- **UI/UX Profesional**
  - Sidebar colapsable moderno
  - Dark mode automático
  - Responsive design (Mobile-first)
  - Animaciones suaves (confetti, float, bounce)
  - Paleta de colores empresarial profesional
  
- **Componentes**
  - Cards con espaciado optimizado (24px)
  - Tablas con DataTables
  - Formularios con validación
  - Notificaciones auto-close (SweetAlert2, Toasts)
  - Progress bars animadas
  - Onboarding interactivo (6 pasos)

---

## 🛠️ Tecnologías

### Backend

- **Django 6.0.1** - Framework web Python
- **PostgreSQL** - Base de datos (producción)
- **SQLite** - Base de datos (desarrollo)
- **Gunicorn** - WSGI HTTP Server
- **Whitenoise** - Servir archivos estáticos

### Frontend

- **Bootstrap 5.3** - Framework CSS
- **Chart.js 4.4** - Gráficos interactivos
- **SweetAlert2 11** - Notificaciones elegantes
- **Bootstrap Icons 1.11** - Iconografía
- **JavaScript ES6+** - Interactividad
- **DataTables** - Tablas avanzadas

### IA y APIs

- **Groq API** - LLaMA 3.3 70B (Chatbot)
- **qrcode 7.4** - Generación de códigos QR
- **Pillow 10.3** - Procesamiento de imágenes
- **reportlab** - Generación de PDFs
- **openpyxl** - Generación de Excel

### DevOps

- **Git/GitHub** - Control de versiones
- **Nginx** - Proxy inverso (producción)
- **Let's Encrypt** - Certificados SSL
- **Gunicorn** - Servidor WSGI

---

## 📦 Instalación

### Prerrequisitos

- Python 3.11+
- pip
- virtualenv
- PostgreSQL (producción) o SQLite (desarrollo)

### Instalación Local

```bash
# Clonar el repositorio
git clone https://github.com/LUISGA64/gastos-familiares.git
cd gastos-familiares

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
# Crear archivo .env en la raíz del proyecto
SECRET_KEY=tu-clave-secreta-django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
GROQ_API_KEY=gsk_tu_api_key_aqui
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Cargar datos iniciales (opcional)
python crear_planes_iniciales.py
python crear_logros_iniciales.py

# Ejecutar servidor de desarrollo
python manage.py runserver
```

### Acceder a la Aplicación

```
http://127.0.0.1:8000/
```

---

## ⚙️ Configuración

### Variables de Entorno

```env
# Django
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,gastosweb.com

# Base de Datos PostgreSQL (Producción)
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/finanbot

# Email (Gmail)
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password-de-16-caracteres

# Groq API (Chatbot IA - GRATIS)
GROQ_API_KEY=gsk_tu_api_key_aqui

# Seguridad
ENCRYPTION_KEY=tu-clave-de-encriptacion-base64

# URLs
SITE_URL=https://gastosweb.com
```

### Obtener API Keys

**Groq API (100% Gratis):**
1. Registrarse en https://console.groq.com
2. Ir a API Keys
3. Crear nueva API Key
4. Copiar a `GROQ_API_KEY`
5. Límite: 14,400 requests/día GRATIS

**Gmail App Password:**
1. Activar verificación en 2 pasos en Google
2. Ir a https://myaccount.google.com/apppasswords
3. Crear contraseña de aplicación "Django"
4. Copiar la clave de 16 caracteres a `EMAIL_HOST_PASSWORD`

---

## 🚀 Deploy

### Producción en VPS (Ubuntu)

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install python3.11 python3.11-venv python3-pip postgresql nginx -y

# Clonar repositorio
cd /var/www
sudo git clone https://github.com/LUISGA64/gastos-familiares.git
cd gastos-familiares

# Crear entorno virtual
python3.11 -m venv .venv
source .venv/bin/activate

# Instalar dependencias de producción
pip install -r requirements-production.txt

# Configurar PostgreSQL
sudo -u postgres psql
CREATE DATABASE finanbot;
CREATE USER finanbot_user WITH PASSWORD 'tu_contraseña_segura';
GRANT ALL PRIVILEGES ON DATABASE finanbot TO finanbot_user;
\q

# Variables de entorno
sudo nano /etc/environment
# Agregar variables

# Colectar archivos estáticos
python manage.py collectstatic --noinput

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Configurar Gunicorn
sudo nano /etc/systemd/system/gunicorn.service
```

**Archivo gunicorn.service:**

```ini
[Unit]
Description=Gunicorn daemon for FinanBot
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/gastos-familiares
Environment="PATH=/var/www/gastos-familiares/.venv/bin"
ExecStart=/var/www/gastos-familiares/.venv/bin/gunicorn \
          --workers 4 \
          --bind unix:/var/www/gastos-familiares/gunicorn.sock \
          DjangoProject.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Iniciar Gunicorn
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

### Configurar Nginx

```nginx
server {
    listen 80;
    server_name gastosweb.com www.gastosweb.com;

    location / {
        proxy_pass http://unix:/var/www/gastos-familiares/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/gastos-familiares/staticfiles/;
    }

    location /media/ {
        alias /var/www/gastos-familiares/media/;
    }

    client_max_body_size 10M;
}
```

```bash
# Activar sitio
sudo ln -s /etc/nginx/sites-available/finanbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL con Let's Encrypt

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtener certificado
sudo certbot --nginx -d gastosweb.com -d www.gastosweb.com

# Auto-renovación
sudo certbot renew --dry-run

# Crontab para renovación automática
0 0 * * * certbot renew --quiet
```

---

## 📊 Estructura del Proyecto

```
DjangoProject/
├── gastos/                          # App principal
│   ├── models.py                   # 15+ modelos de datos
│   ├── views.py                    # Vistas principales
│   ├── views_auth.py               # Autenticación
│   ├── views_gamificacion.py       # Gamificación
│   ├── views_export.py             # Exportación PDF/Excel
│   ├── urls.py                     # URLs (80+ rutas)
│   ├── forms.py                    # Formularios
│   ├── chatbot_service.py          # Servicio de IA
│   ├── gamificacion_service.py     # Sistema de logros
│   ├── notifications.py            # Emails
│   ├── context_processors.py       # Contexto global
│   ├── qr_utils.py                 # Generación QR
│   └── admin.py                    # Panel admin
├── templates/                       # Templates HTML
│   └── gastos/
│       ├── base.html               # Template base (2100+ líneas)
│       ├── dashboard_premium.html  # Dashboard principal
│       ├── dashboard.html          # Dashboard normal
│       ├── conciliacion.html       # Conciliación
│       ├── reportes.html           # Reportes
│       ├── auth/                   # Login/Registro
│       ├── chatbot/                # Chat IA
│       ├── gamificacion/           # Gamificación
│       ├── metas/                  # Metas ahorro
│       ├── ingresos/               # Ingresos
│       └── suscripcion/            # Pagos
├── static/                          # Archivos estáticos
│   ├── css/
│   ├── js/
│   ├── icons/                      # PWA icons (152x152, 192x192, 512x512)
│   ├── manifest.json               # PWA manifest
│   └── sw.js                       # Service Worker
├── media/                           # Archivos subidos
│   ├── comprobantes/               # Comprobantes de pago
│   └── qr_codes/                   # Códigos QR generados
├── DjangoProject/                   # Configuración
│   ├── settings.py                 # Configuración (381 líneas)
│   ├── urls.py                     # URLs raíz
│   └── wsgi.py                     # WSGI
├── requirements.txt                 # Dependencias desarrollo
├── requirements-production.txt      # Dependencias producción
├── manage.py                        # CLI Django
├── crear_planes_iniciales.py       # Script setup
├── crear_logros_iniciales.py       # Script setup
└── README.md                        # Este archivo
```

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
python manage.py test

# Tests específicos
python manage.py test gastos.tests.test_models
python manage.py test gastos.tests.test_views
python manage.py test gastos.tests.test_chatbot
python manage.py test gastos.tests.test_gamificacion

# Con cobertura
pip install coverage
coverage run --source='gastos' manage.py test
coverage report
coverage html
# Abrir htmlcov/index.html
```

---

## 📚 Documentación Técnica

### Modelos Principales

- **Familia** - Grupo familiar (multi-tenant)
- **Aportante** - Miembro con ingreso mensual
- **CategoriaGasto** - Categoría (Fijo/Variable)
- **SubcategoriaGasto** - Subcategoría
- **Gasto** - Gasto registrado (compartido/personal)
- **DistribucionGasto** - Distribución por aportante
- **IngresoAportante** - Ingresos registrados
- **Conciliacion** - Cierre mensual
- **MetaAhorro** - Metas de ahorro
- **PerfilUsuario** - Gamificación (nivel, puntos, racha)
- **Logro** - Definición de logros
- **LogroDesbloqueado** - Logros del usuario
- **ConversacionChatbot** - Chats con IA
- **MensajeChatbot** - Mensajes individuales
- **AnalisisIA** - Análisis generados
- **Suscripcion** - Suscripción del usuario
- **Plan** - Planes de pago
- **Pago** - Pagos registrados
- **ConfiguracionCuentaPago** - Cuentas bancarias

### APIs Principales

```python
# Vistas principales
GET  /dashboard/                    # Dashboard premium
GET  /gastos/                       # Lista gastos
POST /gastos/crear/                 # Crear gasto
GET  /conciliacion/                 # Conciliación
GET  /reportes/                     # Reportes
GET  /metas/                        # Metas ahorro
GET  /gamificacion/                 # Gamificación
POST /chatbot/conversacion/nueva/  # Nueva conversación IA
POST /chatbot/mensaje/              # Enviar mensaje IA
GET  /ingresos/                     # Lista ingresos
POST /suscripcion/pagar/            # Procesar pago

# Toggle privacidad (AJAX)
POST /toggle-privacidad-valores/    # Ocultar/mostrar valores

# Exportación
GET  /exportar-pdf/                 # Exportar dashboard PDF
GET  /exportar-excel/               # Exportar dashboard Excel
```

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas!

### Proceso

1. Fork el proyecto
2. Crea tu rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Guía de Estilo

- **Python:** Seguir PEP 8
- **Commits:** Formato: `Add/Fix/Update: descripción`
- **Comentarios:** En español
- **Tests:** Incluir tests para nuevas features
- **Documentación:** Actualizar README si es necesario

---

## 🐛 Reportar Bugs

Si encuentras un bug, crea un [issue](https://github.com/LUISGA64/gastos-familiares/issues) con:

- **Descripción clara** del problema
- **Pasos para reproducir**
- **Comportamiento esperado** vs **actual**
- **Screenshots** (si aplica)
- **Entorno:** OS, navegador, versión

---

## 📝 Changelog

### v2.0.0 (2026-02-02) - Actualización Mayor

**🆕 Nuevas Características:**
- ✨ Chatbot con IA (Groq LLaMA 3.3 70B)
- ✨ Sistema de gamificación completo (17+ logros)
- ✨ Gastos personales privados
- ✨ Registro de ingresos por aportante
- ✨ Dashboard premium con selector de mes
- ✨ Toggle de privacidad instantáneo (sin recarga)
- ✨ Sistema de suscripciones (4 planes)
- ✨ Pagos con QR (Bancolombia/Nequi)
- ✨ PWA instalable
- ✨ Onboarding interactivo

**🎨 Mejoras de Diseño:**
- Sidebar colapsable moderno
- Dark mode completo
- Paleta de colores profesional (verde teal #009c8c)
- Espaciado optimizado (24px en cards)
- Responsive mejorado (mobile-first)
- Animaciones (confetti, float, bounce)
- Alertas auto-close (5s)

**⚡ Performance:**
- Toggle privacidad 7-13x más rápido
- Optimización de queries
- Lazy loading de imágenes
- Minificación de assets

**🔐 Seguridad:**
- Encriptación de datos sensibles
- Aislamiento multi-tenant mejorado
- Auditoría de logs
- CSRF tokens en AJAX
- Validación de inputs

### v1.0.0 (2025-12-01) - Release Inicial

- Sistema básico de gastos compartidos
- Distribución automática
- Conciliación mensual
- Reportes PDF/Excel
- Dashboard básico

---

## 🔮 Roadmap

### Q2 2026

- [ ] Integración con bancos (Open Banking Colombia)
- [ ] App móvil nativa (Flutter)
- [ ] Notificaciones push en tiempo real
- [ ] Análisis predictivo con ML
- [ ] Multi-idioma (Inglés, Portugués)

### Q3 2026

- [ ] Exportación a software contable (SIIGO, Alegra)
- [ ] Marketplace de plantillas de presupuesto
- [ ] Comparación anónima con otras familias
- [ ] Módulo de inversiones
- [ ] Calculadora de préstamos

### Q4 2026

- [ ] API pública REST
- [ ] Integración con Alexa/Google Assistant
- [ ] OCR para escaneo de facturas
- [ ] Dashboard personalizable con widgets
- [ ] Versión white-label para empresas

---

## 👥 Equipo

- **Luis García** - *Desarrollador Principal* - [@LUISGA64](https://github.com/LUISGA64)

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver [LICENSE](LICENSE) para detalles.

```
MIT License

Copyright (c) 2026 Luis García

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 🌟 Agradecimientos

- **Django Team** - Framework increíble
- **Bootstrap Team** - UI framework elegante  
- **Groq** - API de IA gratuita y potente
- **Chart.js** - Gráficos hermosos
- **SweetAlert2** - Alertas elegantes
- **DataTables** - Tablas avanzadas
- **Comunidad Open Source** - Inspiración y apoyo

---

## 📞 Contacto

- **Website:** [gastosweb.com](https://gastosweb.com)
- **Email:** soporte@gastosweb.com
- **WhatsApp:** [+57 311 700 9855](https://wa.me/573117009855)
- **GitHub:** [@LUISGA64](https://github.com/LUISGA64)
- **LinkedIn:** [Luis García](https://linkedin.com/in/luisgarcia64)

---

## 💡 Soporte

Si este proyecto te ayuda, considera:

- ⭐ **Dar una estrella en GitHub**
- 🐛 **Reportar bugs** para mejorar
- 💡 **Sugerir features** nuevas
- 🤝 **Contribuir con código**
- ☕ **[Invitarme un café](https://www.buymeacoffee.com/luisga64)**
- 💬 **Compartir** con otros desarrolladores

---

## 📊 Estadísticas del Proyecto

- **Líneas de código:** ~25,000+
- **Modelos:** 20+
- **Vistas:** 80+
- **Templates:** 50+
- **Archivos:** 150+
- **Commits:** 500+
- **Features:** 100+

---

## 🏆 Logros del Proyecto

- ✅ Sistema multi-tenant robusto
- ✅ IA integrada con Groq (gratis)
- ✅ Gamificación completa
- ✅ PWA funcional
- ✅ Responsive 100%
- ✅ Dark mode completo
- ✅ Sistema de pagos
- ✅ Deploy en producción
- ✅ SSL configurado
- ✅ Exportación PDF/Excel
- ✅ 14,400 mensajes IA/día gratis

---

<div align="center">

**Desarrollado con ❤️ en Colombia 🇨🇴**

**FinanBot** - *Gestión Inteligente de Gastos Familiares*

[![GitHub stars](https://img.shields.io/github/stars/LUISGA64/gastos-familiares?style=social)](https://github.com/LUISGA64/gastos-familiares/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/LUISGA64/gastos-familiares?style=social)](https://github.com/LUISGA64/gastos-familiares/network/members)
[![GitHub watchers](https://img.shields.io/github/watchers/LUISGA64/gastos-familiares?style=social)](https://github.com/LUISGA64/gastos-familiares/watchers)

[⬆ Volver arriba](#-finanbot---gestión-inteligente-de-gastos-familiares)

</div>
