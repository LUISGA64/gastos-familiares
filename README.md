# 💰 Gestor de Gastos Familiares

> Aplicación web profesional para la administración inteligente de gastos familiares con gamificación, chatbot IA y sistema de pagos integrado.

[![Django](https://img.shields.io/badge/Django-5.0-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()

---

## 🌟 Características Principales

### ✅ Sistema de Gestión de Gastos
- **Multi-tenant**: Múltiples familias aisladas con total seguridad
- **Aportantes**: Gestión de ingresos mensuales por miembro
- **Categorías personalizables**: Fijas y variables con colores únicos
- **Distribución automática**: Cálculo proporcional de gastos según ingresos
- **Conciliación mensual**: Cierre y revisión de períodos
- **Metas de ahorro**: Seguimiento visual de objetivos financieros
- **📊 Exportación PDF/Excel**: Reportes profesionales del dashboard (Premium)

### 🏆 Gamificación Completa
- **17 logros automáticos**: Desbloqueables por acciones del usuario
- **Sistema de niveles**: Del 1 al 10 con progreso visual
- **Racha de días**: Contador de días consecutivos con fuego 🔥
- **Ranking competitivo**: Top 100 con podio visual
- **Notificaciones organizadas**: Por tipo (logros, niveles, rachas)
- **Timeline de progreso**: Historial completo de puntos

### 🤖 Chatbot IA (FinanBot)
- **Groq API (GRATIS)**: Llama 3.3 70B integrado
- **14,400 mensajes/día gratuitos**: Sin costo para usuarios
- **Análisis conversacional**: Entiende lenguaje natural
- **Recomendaciones personalizadas**: Basadas en datos reales
- **Predicción de gastos**: Oportunidades de ahorro
- **Multi-proveedor**: Soporte para Groq, OpenAI o modo demo

### 💳 Sistema de Pagos
- **4 planes de suscripción**: Gratuito, Básico, Premium, Empresarial
- **QR dinámicos**: Bancolombia y Nequi
- **Subida de comprobantes**: Validación de pagos
- **Panel de verificación**: Para administradores
- **Estados en tiempo real**: Pendiente, verificado, rechazado

### 🎨 Diseño Moderno
- **Onboarding interactivo**: Tutorial de 6 pasos para nuevos usuarios
- **Alertas con autoclose**: 5 segundos con barra de progreso
- **Confetti en logros**: Celebración visual al desbloquear
- **Animaciones sutiles**: Float, bounce, fadeIn, slideUp
- **Responsive completo**: Móvil, tablet y desktop

---

## 🚀 Tecnologías Utilizadas

### Backend
- **Django 5.0.0** - Framework web principal
- **Python 3.14** - Lenguaje de programación
- **SQLite** - Base de datos (desarrollo)
- **PostgreSQL** - Recomendado para producción

### Frontend
- **Bootstrap 5.3.0** - Framework CSS
- **Chart.js 4.4.0** - Gráficos interactivos
- **Bootstrap Icons 1.11.0** - Iconografía
- **SweetAlert2** - Alertas bonitas
- **Canvas-confetti** - Animaciones de celebración

### IA y APIs
- **Groq API** - IA conversacional (Llama 3.3 70B) - GRATIS
- **OpenAI GPT-4** - Opcional para plan premium

### Reportes y Exportación
- **ReportLab 4.0.7** - Generación de PDF profesionales
- **XlsxWriter 3.1.9** - Exportación a Excel (.xlsx)
- **Openpyxl 3.1.2** - Lectura/escritura Excel

---

## 🛠️ Instalación Rápida

### 1. Clonar Repositorio
```bash
git clone https://github.com/LUISGA64/gastos-familiares.git
cd gastos-familiares
```

### 2. Crear Entorno Virtual
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
Crea archivo `.env`:
```env
AI_PROVIDER=groq
GROQ_API_KEY=tu_groq_api_key_aqui
```

**Obtener API Key de Groq (GRATIS)**:
1. Ve a https://console.groq.com/
2. Crea cuenta (sin tarjeta)
3. Genera API key
4. Pégala en `.env`

### 5. Configurar Base de Datos
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Ejecutar Servidor
```bash
python manage.py runserver
```

Abre: **http://127.0.0.1:8000/**

---

## 💰 Planes de Suscripción

| Plan | Precio | Aportantes | Gastos/mes |
|------|--------|------------|------------|
| **Gratuito** | $0 | 2 | 50 |
| **Básico** | $9,900/mes | 5 | 200 |
| **Premium** | $15,900/mes | 10 | Ilimitado |
| **Empresarial** | $49,900/mes | Ilimitado | Ilimitado |

**Todos incluyen**:
- ✅ Gamificación completa
- ✅ Chatbot IA (14,400 msgs/día gratis)
- ✅ Reportes PDF/Excel
- ✅ Metas de ahorro

---

## 🎮 Sistema de Gamificación

### 17 Logros Disponibles

#### 🎯 Ahorro (4)
- Primer Ahorro, Meta Alcanzada, Ahorrador Constante, Maestro del Ahorro

#### 💰 Gastos (4)
- Primer Paso, Organizador, Experto Financiero, Maestro de Finanzas

#### 📊 Disciplina (4)
- Racha Inicial (3 días), Disciplinado (7 días), Hábito Formado (30 días), Leyenda (100 días)

#### 🏆 Especial (3)
- Presupuestado, Equilibrio Perfecto, Inversionista

#### 🎯 Meta (2)
- Visionario, Cumplidor

### Sistema de Niveles
- **Nivel 1-3**: Novato (0-1000 pts)
- **Nivel 4-6**: Intermedio (1001-3000 pts)
- **Nivel 7-9**: Avanzado (3001-7000 pts)
- **Nivel 10**: Maestro (7001+ pts)

---

## 🤖 Chatbot IA - Configuración

### Groq (Recomendado - GRATIS)
```env
AI_PROVIDER=groq
GROQ_API_KEY=gsk_tu_key_aqui
```
- ✅ Completamente gratis
- ✅ 14,400 requests/día
- ✅ Llama 3.3 70B
- ✅ 10x más rápido que GPT-4

### OpenAI (Opcional - Pago)
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-proj-tu_key_aqui
```
- ✅ Más inteligente
- ❌ ~$0.02 por mensaje

### Demo (Sin API)
```env
AI_PROVIDER=demo
```
- ✅ 100% gratis
- ✅ Respuestas predefinidas inteligentes

---

## 📊 Estadísticas del Proyecto

- **~10,000** líneas de código
- **18** modelos de BD
- **50+** vistas Django
- **40+** templates HTML
- **95+** URLs configuradas
- **17** logros automáticos
- **~25 horas** de desarrollo

---

## 🚀 Deploy a Producción

### Railway (Recomendado)
1. Crea cuenta en railway.app
2. Conecta repositorio GitHub
3. Configura variables de entorno
4. Deploy automático

### Render
1. Crea cuenta en render.com
2. Nuevo Web Service
3. Build: `pip install -r requirements.txt`
4. Start: `gunicorn DjangoProject.wsgi:application`

---

## 📞 Soporte

- 💬 **WhatsApp**: +57 311 700 9855
- 📧 **Email**: soporte@gastosfamiliares.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/LUISGA64/gastos-familiares/issues)

---

## 👥 Autor

**Luis García**
- GitHub: [@LUISGA64](https://github.com/LUISGA64)
- WhatsApp: +57 311 700 9855

---

## 🙏 Agradecimientos

- **Django Framework** - Excelente framework web
- **Groq** - API gratuita de IA
- **Bootstrap** - Componentes UI
- **Chart.js** - Gráficos interactivos
- **Comunidad Open Source**

---

<div align="center">

**⭐ Dale una estrella si te fue útil ⭐**

**Hecho con ❤️ en Colombia 🇨🇴**

**Gestor de Gastos Familiares © 2026**

</div>
