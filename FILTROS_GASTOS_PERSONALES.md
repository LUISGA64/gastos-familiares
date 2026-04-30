# Filtros en Gastos Personales

## 📅 Cambios Implementados

### ✅ Nueva Funcionalidad: Filtros por Mes y Aportante

Se han agregado filtros completos en la vista de gastos personales para mejorar la capacidad de análisis y seguimiento de gastos individuales.

---

## 🎯 Características Implementadas

### 1. **Filtro por Período (Mes/Año)**
- Selector dropdown con los últimos 12 meses disponibles
- Cambio automático al seleccionar el mes (sin necesidad de hacer clic en "Filtrar")
- Formato legible: "Enero 2026", "Febrero 2026", etc.
- El mes actual aparece seleccionado por defecto

### 2. **Filtro por Aportante**
- Selector dropdown con todos los aportantes activos de la familia
- Opción "Todos los aportantes" para ver gastos sin filtrar
- Permite ver gastos personales específicos de cada miembro

### 3. **Combinación de Filtros**
- Los filtros funcionan de manera independiente o combinada
- Puedes ver:
  - Gastos de todos los aportantes en un mes específico
  - Gastos de un aportante específico en un mes específico
  - Gastos de un aportante específico en todos los meses

---

## 📊 Estadísticas Actualizadas

Las siguientes métricas se actualizan dinámicamente según los filtros aplicados:

### **Card 1: Total del Mes**
- Muestra el total de gastos personales del mes seleccionado
- Se adapta si se filtra por aportante

### **Card 2: Total de Registros**
- Cantidad de gastos personales encontrados con los filtros activos

### **Card 3: Categorías Usadas**
- Número de categorías diferentes utilizadas en los gastos filtrados

### **Gráfico de Distribución**
- Muestra gastos por aportante del mes seleccionado
- Incluye barra de progreso visual
- Porcentajes relativos al total del mes

---

## 🎨 Interfaz de Usuario

### **Diseño del Filtro**
- **Layout Responsive:** 3 columnas en desktop, se adapta a móviles
- **Iconos Intuitivos:** 
  - 📅 Calendario para el selector de mes
  - 👤 Persona para el selector de aportante
- **Botones Claros:**
  - "Filtrar" (azul) para aplicar filtros
  - "Limpiar" (gris) para resetear todos los filtros

### **Experiencia de Usuario**
- El selector de mes aplica el filtro automáticamente al cambiar
- El filtro por aportante requiere hacer clic en "Filtrar"
- Botón "Limpiar" regresa a la vista sin filtros (mes actual, todos los aportantes)

---

## 🔧 Archivos Modificados

### `gastos/views.py`
**Función:** `lista_gastos_personales()`

**Cambios:**
- Agregado parámetro `mes_seleccionado` y `anio_seleccionado` desde GET
- Lógica para determinar el mes/año de filtrado (default: mes actual)
- Filtrado de gastos por mes y año
- Generación de lista `meses_disponibles` con últimos 12 meses
- Actualización del contexto con variables necesarias para la plantilla

### `templates/gastos/gastos_personales/lista_gastos_personales.html`

**Cambios:**
- Nuevo selector dropdown para mes/año con los últimos 12 meses
- Reorganización del formulario de filtros en 3 columnas
- JavaScript para manejar el cambio automático del selector de mes
- Descomposición del valor "mes-año" en campos separados para el submit

---

## 💡 Cómo Usar

### **Filtrar por Mes:**
1. Abre la página de Gastos Personales
2. En la sección de filtros, selecciona el mes deseado del dropdown "Período"
3. El sistema aplicará el filtro automáticamente

### **Filtrar por Aportante:**
1. En el dropdown "Aportante", selecciona el miembro de la familia
2. Haz clic en el botón "Filtrar"
3. Se mostrarán solo los gastos de ese aportante

### **Combinar Filtros:**
1. Selecciona el mes deseado
2. Selecciona el aportante deseado
3. Haz clic en "Filtrar"
4. Verás los gastos personales del aportante en ese mes específico

### **Limpiar Filtros:**
1. Haz clic en el botón "Limpiar"
2. Regresarás a la vista predeterminada (mes actual, todos los aportantes)

---

## 📈 Beneficios

### **Para el Usuario:**
- ✅ Análisis detallado de gastos personales por período
- ✅ Seguimiento individual por aportante
- ✅ Comparación de gastos entre diferentes meses
- ✅ Identificación de patrones de gasto

### **Para la Familia:**
- ✅ Transparencia en gastos personales de cada miembro
- ✅ Control financiero más preciso
- ✅ Mejor planificación financiera individual
- ✅ Datos históricos accesibles

---

## 🔍 Validaciones

- ✅ El sistema valida que los valores de mes y año sean numéricos
- ✅ Si hay error en los parámetros, se usa el mes actual como respaldo
- ✅ Los filtros respetan la pertenencia a la familia (seguridad)
- ✅ Solo se muestran aportantes activos de la familia

---

## 🚀 Próximas Mejoras Sugeridas

1. **Filtro por Rango de Fechas:** Permitir seleccionar inicio y fin
2. **Filtro por Categoría:** Agregar filtro por tipo de gasto
3. **Exportar Filtrados:** Botón para exportar solo los datos filtrados
4. **Gráficos Comparativos:** Comparar gastos entre diferentes meses
5. **Alertas de Gastos:** Notificar cuando se supere un límite en un mes

---

## 📝 Notas Técnicas

- Los filtros usan parámetros GET en la URL
- La lista de meses se genera dinámicamente considerando los últimos 12 meses
- El JavaScript maneja el envío automático del formulario al cambiar el mes
- Se utiliza DataTables para la paginación y búsqueda en la tabla
- Los valores monetarios respetan la configuración de privacidad del usuario

---

## 🎨 Diseño y UX

- **Colores:** Se mantiene la paleta profesional del aplicativo
- **Gradientes:** Header con gradiente moderno (rosa-rojo)
- **Iconos:** Bootstrap Icons para consistencia visual
- **Responsive:** Totalmente adaptable a dispositivos móviles
- **Accesibilidad:** Labels claros y navegación con teclado

---

**Fecha de Implementación:** 30 de Abril de 2026  
**Versión:** 2.1.0  
**Desarrollador:** FinanBot Team

