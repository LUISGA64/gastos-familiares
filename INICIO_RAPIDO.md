# 🚀 Guía de Inicio Rápido

## Pasos para empezar a usar la aplicación

### 1. Crear un superusuario (si aún no lo has hecho)
```bash
python manage.py createsuperuser
```
Sigue las instrucciones en pantalla para crear tu usuario administrador.

### 2. Cargar datos de ejemplo (opcional pero recomendado)
```bash
python manage.py cargar_datos_ejemplo
```
Este comando creará:
- 2 aportantes de ejemplo (Juan y María)
- 8 categorías (4 fijas y 4 variables)
- 8 gastos del mes actual con distribución automática

### 3. Iniciar el servidor
```bash
python manage.py runserver
```

### 4. Acceder a la aplicación
- **Aplicación Principal**: http://127.0.0.1:8000/
- **Panel Admin**: http://127.0.0.1:8000/admin/

## 📱 Navegación Principal

### Dashboard (Inicio)
- Resumen de ingresos y gastos del mes
- Lista de aportantes con sus porcentajes
- Últimos gastos registrados
- Accesos rápidos

### Aportantes
- Ver lista de todos los aportantes
- Crear nuevo aportante
- Editar información y salarios
- Ver porcentaje de aporte calculado automáticamente

### Categorías
- Ver categorías de gastos fijos y variables
- Crear nuevas categorías personalizadas

### Gastos
- Registrar nuevos gastos
- Filtrar por tipo, categoría, mes y año
- Ver detalle de cada gasto
- Editar gastos existentes
- Activar distribución automática al crear gastos

### Reportes
- Seleccionar mes y año
- Ver balance general
- Análisis de gastos por tipo (fijos vs variables)
- Balance individual por aportante
- Gastos por categoría

## 💡 Primeros Pasos Recomendados

1. **Explora el Dashboard**: Familiarízate con la interfaz
2. **Revisa los aportantes de ejemplo**: Ve cómo se calcula el porcentaje
3. **Mira los gastos**: Observa cómo se distribuyen automáticamente
4. **Abre el detalle de un gasto**: Ve la distribución visual
5. **Consulta los reportes**: Analiza el balance mensual

## 🎯 Flujo de Trabajo Típico

1. **Configurar aportantes** con sus salarios reales
2. **Crear categorías** según tus necesidades
3. **Registrar gastos** a medida que ocurren
4. **Activar "Distribuir automáticamente"** para calcular aportes
5. **Revisar reportes** mensualmente para análisis

## ⚙️ Panel de Administración

El panel admin de Django te permite:
- Editar datos de forma avanzada
- Realizar búsquedas y filtros complejos
- Ver relaciones entre modelos
- Acciones en masa

Accede en: http://127.0.0.1:8000/admin/

## 🔄 Reiniciar Datos

Si quieres empezar desde cero:
```bash
python manage.py cargar_datos_ejemplo
```
El comando te preguntará si deseas eliminar datos existentes.

## 📊 Ejemplo de Uso Real

### Configuración:
- **Aportante 1**: Pedro - $2,000,000 (40%)
- **Aportante 2**: Laura - $3,000,000 (60%)
- **Total familia**: $5,000,000

### Gasto Registrado:
- **Arriendo**: $1,200,000
- Con distribución automática:
  - Pedro paga: $480,000 (40%)
  - Laura paga: $720,000 (60%)

### Balance:
- **Ingresos totales**: $5,000,000
- **Gastos del mes**: $3,450,000
- **Balance**: $1,550,000 ✅

---

**¡Listo! Ya puedes gestionar los gastos de tu familia de manera eficiente! 🏠💰**

