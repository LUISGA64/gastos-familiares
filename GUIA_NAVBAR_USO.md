# 📱 Guía de Uso del Navbar Profesional

## 🎯 Características Principales

### ✨ Diseño Profesional
- Glassmorphism con backdrop-filter
- Animaciones suaves y elegantes
- Sistema de navegación intuitivo
- Totalmente responsivo

### 🎨 Experiencia Visual
- Efectos hover interactivos
- Estados activos destacados
- Transiciones fluidas
- Dark mode integrado

## 📋 Estructura del Navbar

```html
<nav class="navbar navbar-expand-lg navbar-dark">
    <div class="container-fluid px-4">
        <!-- Brand -->
        <a class="navbar-brand" href="/">
            <i class="bi bi-piggy-bank-fill"></i>
            <span>Gastos Familiares</span>
        </a>
        
        <!-- Toggler para móviles -->
        <button class="navbar-toggler" ...>
        
        <!-- Navegación -->
        <div class="collapse navbar-collapse">
            <ul class="navbar-nav ms-auto">
                <!-- Items de navegación -->
            </ul>
        </div>
    </div>
</nav>
```

## 🔧 Cómo Agregar Nuevos Enlaces

### 1. Enlace Simple

```html
<li class="nav-item">
    <a class="nav-link {% if 'ruta' in request.path %}active{% endif %}" 
       href="{% url 'nombre_vista' %}">
        <i class="bi bi-icono"></i>
        <span>Texto</span>
    </a>
</li>
```

### 2. Enlace con Dropdown

```html
<li class="nav-item dropdown">
    <a class="nav-link dropdown-toggle" href="#" 
       id="dropdownId" role="button" 
       data-bs-toggle="dropdown" aria-expanded="false">
        <i class="bi bi-icono"></i>
        <span>Categoría</span>
    </a>
    <ul class="dropdown-menu dropdown-menu-end">
        <li><h6 class="dropdown-header">Sección</h6></li>
        <li>
            <a class="dropdown-item" href="#">
                <i class="bi bi-icono"></i>
                <span>Opción 1</span>
            </a>
        </li>
        <li><hr class="dropdown-divider"></li>
        <li>
            <a class="dropdown-item" href="#">
                <i class="bi bi-icono"></i>
                <span>Opción 2</span>
            </a>
        </li>
    </ul>
</li>
```

## 🎨 Iconos Disponibles (Bootstrap Icons)

### Navegación Principal
- `bi-house-door-fill` - Inicio
- `bi-receipt` - Gastos/Facturas
- `bi-people-fill` - Usuarios/Aportantes
- `bi-tags-fill` - Categorías
- `bi-bar-chart-fill` - Reportes/Estadísticas
- `bi-calculator-fill` - Cálculos/Conciliación
- `bi-piggy-bank` - Ahorros/Metas

### Acciones
- `bi-plus-circle` - Agregar
- `bi-pencil` - Editar
- `bi-trash` - Eliminar
- `bi-eye` - Ver
- `bi-download` - Descargar
- `bi-upload` - Subir
- `bi-search` - Buscar

### Usuario
- `bi-person-circle` - Perfil
- `bi-gear-fill` - Configuración
- `bi-star-fill` - Premium/Favoritos
- `bi-box-arrow-right` - Cerrar sesión

### Estados
- `bi-check-circle` - Completado
- `bi-clock` - Pendiente
- `bi-exclamation-triangle` - Advertencia
- `bi-info-circle` - Información

## 🎯 Clase Active Dinámica

### Método 1: Por URL Name
```html
{% if request.resolver_match.url_name == 'dashboard' %}active{% endif %}
```

### Método 2: Por Path
```html
{% if 'gastos' in request.path %}active{% endif %}
```

### Método 3: Por Múltiples Condiciones
```html
{% if request.resolver_match.url_name in 'lista_gastos,crear_gasto,editar_gasto' %}active{% endif %}
```

## 🎨 Personalización de Colores

### Variables CSS (en `:root`)
```css
--navbar-bg: rgba(44, 62, 80, 0.98);
--nav-link-color: rgba(255, 255, 255, 0.9);
--nav-link-hover-bg: rgba(52, 152, 219, 0.2);
--nav-link-active-bg: rgba(52, 152, 219, 0.3);
--brand-color: #3498db;
```

### Cambiar Color del Brand
```css
.navbar-brand i {
    color: #e74c3c; /* Rojo */
    /* o */
    color: #27ae60; /* Verde */
}
```

## 📱 Responsive Breakpoints

### Desktop (≥ 992px)
- Navbar horizontal
- Dropdowns con animación
- Separador visual

### Tablet (768px - 991px)
- Navbar colapsable
- Botones de ancho completo
- Touch-friendly

### Mobile (< 768px)
- Navbar vertical
- Texto del brand oculto (solo icono)
- Padding aumentado

## 🔧 JavaScript Necesario

### Toggle Theme
```javascript
function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Cambiar icono
    const icon = document.getElementById('theme-icon');
    if (newTheme === 'dark') {
        icon.classList.remove('bi-moon-fill');
        icon.classList.add('bi-sun-fill');
    } else {
        icon.classList.remove('bi-sun-fill');
        icon.classList.add('bi-moon-fill');
    }
}
```

### Cargar Tema al Iniciar
```javascript
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    const icon = document.getElementById('theme-icon');
    if (savedTheme === 'dark' && icon) {
        icon.classList.remove('bi-moon-fill');
        icon.classList.add('bi-sun-fill');
    }
});
```

### Navbar Scroll Effect (Opcional)
```javascript
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});
```

## ✅ Mejores Prácticas

### 1. Accesibilidad
- ✓ Usar `aria-label` en botones
- ✓ Usar `aria-expanded` en dropdowns
- ✓ Asegurar contraste de colores
- ✓ Navegación con teclado (Tab)

### 2. Performance
- ✓ Usar clases en vez de IDs
- ✓ Minimizar animaciones pesadas
- ✓ Lazy load de iconos si es necesario
- ✓ Optimizar backdrop-filter

### 3. UX
- ✓ Indicar página actual (active)
- ✓ Feedback visual en hover
- ✓ Transiciones suaves
- ✓ Mobile-first approach

### 4. Organización
- ✓ Agrupar items relacionados
- ✓ Usar dropdowns para submenús
- ✓ Máximo 7±2 items en navbar
- ✓ Separadores visuales

## 🚫 Errores Comunes a Evitar

### ❌ NO hacer:
```html
<!-- Demasiados items en navbar -->
<li><a>Item 1</a></li>
<li><a>Item 2</a></li>
<li><a>Item 3</a></li>
... (15 items más)

<!-- Texto sin icono -->
<a class="nav-link">Solo Texto</a>

<!-- Dropdown sin header -->
<ul class="dropdown-menu">
    <li><a>Opción 1</a></li>
    <li><a>Opción 2</a></li>
</ul>
```

### ✅ SI hacer:
```html
<!-- Items agrupados -->
<li class="nav-item dropdown">
    <a>Gestión</a>
    <ul>
        <li><h6 class="dropdown-header">Sección 1</h6></li>
        <li><a>Item 1</a></li>
        ...
    </ul>
</li>

<!-- Icono + Texto -->
<a class="nav-link">
    <i class="bi bi-house-fill"></i>
    <span>Inicio</span>
</a>
```

## 🎯 Casos de Uso Comunes

### 1. Agregar Notificaciones
```html
<li class="nav-item">
    <a class="nav-link position-relative" href="#">
        <i class="bi bi-bell-fill"></i>
        <span>Notificaciones</span>
        <span class="badge bg-danger position-absolute top-0 start-100 translate-middle">
            3
        </span>
    </a>
</li>
```

### 2. Búsqueda en Navbar
```html
<li class="nav-item">
    <form class="d-flex" role="search">
        <input class="form-control me-2" type="search" 
               placeholder="Buscar..." aria-label="Buscar">
        <button class="btn btn-outline-light" type="submit">
            <i class="bi bi-search"></i>
        </button>
    </form>
</li>
```

### 3. Avatar de Usuario
```html
<li class="nav-item dropdown">
    <a class="nav-link dropdown-toggle user-badge" href="#" ...>
        <img src="avatar.jpg" alt="Avatar" 
             class="rounded-circle" 
             style="width: 32px; height: 32px;">
        <span>Usuario</span>
    </a>
    <ul class="dropdown-menu">...</ul>
</li>
```

## 🔗 Recursos Adicionales

### Documentación
- [Bootstrap 5.3 Navbar](https://getbootstrap.com/docs/5.3/components/navbar/)
- [Bootstrap Icons](https://icons.getbootstrap.com/)
- [MDN Backdrop Filter](https://developer.mozilla.org/en-US/docs/Web/CSS/backdrop-filter)

### Herramientas
- [CSS Gradient Generator](https://cssgradient.io/)
- [Coolors - Paletas de Colores](https://coolors.co/)
- [Can I Use - Compatibilidad](https://caniuse.com/)

---

**Fecha**: 17/01/2026  
**Versión**: 2.0  
**Autor**: GitHub Copilot
