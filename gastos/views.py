from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
import json
import locale
from .models import Aportante, CategoriaGasto, SubcategoriaGasto, Gasto, DistribucionGasto, MetaAhorro, Familia
from .forms import AportanteForm, CategoriaGastoForm, SubcategoriaGastoForm, GastoForm, MetaAhorroForm, AgregarAhorroForm

# Configurar locale a español
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'es_CO.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'Spanish_Colombia.1252')
        except:
            pass  # Si no se puede configurar, continuar

# Diccionario de nombres de meses en español
MESES_ES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

MESES_ES_CORTO = {
    1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr',
    5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago',
    9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
}

def obtener_nombre_mes(fecha, corto=False):
    """Retorna el nombre del mes en español"""
    meses = MESES_ES_CORTO if corto else MESES_ES
    return meses.get(fecha.month, fecha.strftime('%B'))


@login_required
def dashboard(request):
    """Vista principal con resumen de gastos e ingresos - Versión Premium"""
    from .models import IngresoAportante, ConciliacionMensual
    from decimal import Decimal

    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    # Obtener objeto familia
    familia = Familia.objects.get(id=familia_id)

    # Obtener aportantes activos de la familia
    aportantes = Aportante.objects.filter(familia_id=familia_id, activo=True)

    # Obtener mes y año seleccionado por el usuario (o usar actual)
    mes_seleccionado = request.GET.get('mes', None)
    anio_seleccionado = request.GET.get('anio', None)

    fecha_actual = timezone.now()

    if mes_seleccionado and anio_seleccionado:
        try:
            mes_actual = int(mes_seleccionado)
            anio_actual = int(anio_seleccionado)
        except (ValueError, TypeError):
            mes_actual = fecha_actual.month
            anio_actual = fecha_actual.year
    else:
        # Por defecto, siempre mostrar el mes actual
        mes_actual = fecha_actual.month
        anio_actual = fecha_actual.year

    # ========== CÁLCULO HÍBRIDO DE INGRESOS ==========
    # 1. Intentar obtener ingresos reales registrados en IngresoAportante
    ingresos_reales = IngresoAportante.objects.filter(
        aportante__familia_id=familia_id,
        fecha__month=mes_actual,
        fecha__year=anio_actual
    ).aggregate(total=Sum('monto'))['total']

    # 2. Si hay ingresos reales, usarlos; si no, usar ingreso_mensual de aportantes
    if ingresos_reales:
        total_ingresos = Decimal(str(ingresos_reales))
    else:
        # Fallback: usar ingreso_mensual fijo de los aportantes
        total_ingresos_fijo = aportantes.aggregate(total=Sum('ingreso_mensual'))['total']
        total_ingresos = Decimal(str(total_ingresos_fijo)) if total_ingresos_fijo else Decimal('0')

    # 3. Obtener saldo del mes anterior (de conciliación cerrada)
    mes_anterior = mes_actual - 1 if mes_actual > 1 else 12
    anio_anterior = anio_actual if mes_actual > 1 else anio_actual - 1

    try:
        conciliacion_anterior = ConciliacionMensual.objects.get(
            familia_id=familia_id,
            mes=mes_anterior,
            anio=anio_anterior,
            estado='CERRADA'
        )
        saldo_anterior = conciliacion_anterior.saldo_transferido_siguiente
    except ConciliacionMensual.DoesNotExist:
        saldo_anterior = Decimal('0')

    # ========== CÁLCULO DE GASTOS ==========
    gastos_mes = Gasto.objects.filter(
        subcategoria__categoria__familia_id=familia_id,
        fecha__month=mes_actual,
        fecha__year=anio_actual
    )

    total_gastos_mes = gastos_mes.aggregate(total=Sum('monto'))['total'] or 0
    gastos_fijos_mes = gastos_mes.filter(subcategoria__tipo='FIJO').aggregate(total=Sum('monto'))['total'] or 0
    gastos_variables_mes = gastos_mes.filter(subcategoria__tipo='VARIABLE').aggregate(total=Sum('monto'))['total'] or 0

    # ========== CÁLCULO DE BALANCE CON SALDO ANTERIOR ==========
    balance = total_ingresos + saldo_anterior - total_gastos_mes

    # Gastos por categoría principal (solo de la familia actual)
    gastos_por_categoria = CategoriaGasto.objects.filter(
        familia_id=familia_id,
        subcategorias__gastos__fecha__month=mes_actual,
        subcategorias__gastos__fecha__year=anio_actual
    ).annotate(
        total=Sum('subcategorias__gastos__monto'),
        cantidad=Count('subcategorias__gastos')
    ).order_by('-total')[:5]

    # Últimos gastos de la familia
    ultimos_gastos = Gasto.objects.filter(subcategoria__categoria__familia_id=familia_id).order_by('-fecha', '-fecha_registro')[:10]

    # ========== DATOS PARA GRÁFICOS ==========

    # Histórico de 6 meses para gráfico de tendencia
    meses_labels = []
    ingresos_historico = []
    gastos_historico = []

    for i in range(5, -1, -1):
        fecha = timezone.now() - timedelta(days=30*i)
        mes = fecha.month
        anio = fecha.year

        # Etiqueta del mes en español
        meses_labels.append(f"{MESES_ES_CORTO[mes]} {anio}")

        # Ingresos (asumimos constantes, pero se puede mejorar)
        ingresos_historico.append(float(total_ingresos) if total_ingresos else 0)

        # Gastos del mes
        gastos_del_mes = Gasto.objects.filter(
            subcategoria__categoria__familia_id=familia_id,
            fecha__month=mes,
            fecha__year=anio
        ).aggregate(total=Sum('monto'))['total'] or 0
        gastos_historico.append(float(gastos_del_mes))

    # Datos para gráfico de categorías (pie chart)
    categorias_labels = []
    categorias_data = []
    categorias_colors = [
        '#3498db', '#e74c3c', '#f39c12', '#27ae60', '#9b59b6',
        '#1abc9c', '#e67e22', '#34495e', '#16a085', '#d35400'
    ]

    for idx, cat in enumerate(gastos_por_categoria):
        categorias_labels.append(cat.nombre)
        categorias_data.append(float(cat.total))

    # Datos para gráfico de aportantes (bar chart)
    aportantes_labels = []
    aportantes_data = []

    for aportante in aportantes:
        aportantes_labels.append(aportante.nombre)
        aportantes_data.append(float(aportante.ingreso_mensual))

    # ========== ANÁLISIS Y TENDENCIAS ==========

    # Calcular tendencias (comparar con mes anterior)
    mes_anterior = (mes_actual - 1) if mes_actual > 1 else 12
    anio_anterior = anio_actual if mes_actual > 1 else anio_actual - 1

    gastos_mes_anterior = Gasto.objects.filter(
        subcategoria__categoria__familia_id=familia_id,
        fecha__month=mes_anterior,
        fecha__year=anio_anterior
    ).aggregate(total=Sum('monto'))['total'] or 0

    if gastos_mes_anterior > 0:
        tendencia_gastos = float((total_gastos_mes - gastos_mes_anterior) / gastos_mes_anterior) * 100
    else:
        tendencia_gastos = 0

    # Proyección para próximo mes (promedio últimos 3 meses)
    if len(gastos_historico) >= 3:
        proyeccion_gastos = sum(gastos_historico[-3:]) / 3
    else:
        proyeccion_gastos = float(total_gastos_mes) if total_gastos_mes else 0

    # Meta de ahorro (20% de ingresos)
    meta_ahorro = total_ingresos * Decimal('0.20') if total_ingresos else 0

    # Generar lista de meses disponibles (últimos 12 meses)
    from datetime import date
    meses_disponibles = []
    for i in range(12):
        fecha_mes = date(fecha_actual.year, fecha_actual.month, 1) - timedelta(days=30*i)
        meses_disponibles.append({
            'mes': fecha_mes.month,
            'anio': fecha_mes.year,
            'nombre': f"{MESES_ES[fecha_mes.month]} {fecha_mes.year}",
            'seleccionado': (fecha_mes.month == mes_actual and fecha_mes.year == anio_actual)
        })

    context = {
        'familia': familia,
        'aportantes': aportantes,
        'total_ingresos': total_ingresos,
        'saldo_anterior': saldo_anterior,
        'total_gastos_mes': total_gastos_mes,
        'gastos_fijos_mes': gastos_fijos_mes,
        'gastos_variables_mes': gastos_variables_mes,
        'balance': balance,
        'gastos_por_categoria': gastos_por_categoria,
        'ultimos_gastos': ultimos_gastos,
        'gastos_recientes': ultimos_gastos,
        'mes_actual': f"{MESES_ES[mes_actual]} {anio_actual}",
        'mes_seleccionado': mes_actual,
        'anio_seleccionado': anio_actual,
        'meses_disponibles': meses_disponibles,

        # Datos para gráficos (convertir a JSON)
        'meses_labels': json.dumps(meses_labels),
        'ingresos_historico': json.dumps(ingresos_historico),
        'gastos_historico': json.dumps(gastos_historico),
        'categorias_labels': json.dumps(categorias_labels),
        'categorias_data': json.dumps(categorias_data),
        'categorias_colors': json.dumps(categorias_colors[:len(categorias_labels)]),
        'aportantes_labels': json.dumps(aportantes_labels),
        'aportantes_data': json.dumps(aportantes_data),

        # Análisis y tendencias
        'tendencia_gastos': tendencia_gastos,
        'tendencia_ingresos': 0,  # Por ahora, se puede mejorar
        'proyeccion_gastos': proyeccion_gastos,
        'meta_ahorro': meta_ahorro,
    }

    # GAMIFICACIÓN: Registrar visita al dashboard
    try:
        from .gamificacion_service import GamificacionService
        GamificacionService.registrar_visita_dashboard(request.user)

        # Obtener notificaciones no vistas
        notificaciones_logros = GamificacionService.obtener_notificaciones_no_vistas(request.user)
        context['notificaciones_logros'] = notificaciones_logros
    except Exception as e:
        print(f"Error en gamificación: {e}")

    # ocultar_valores está disponible automáticamente desde context_processors.py

    return render(request, 'gastos/dashboard_premium.html', context)


@login_required
def lista_aportantes(request):
    """Lista de todos los aportantes"""
    # Filtrar por familia
    familia_id = request.session.get('familia_id')
    if familia_id:
        aportantes = Aportante.objects.filter(familia_id=familia_id)
    else:
        aportantes = Aportante.objects.all()

    total_ingresos = aportantes.filter(activo=True).aggregate(total=Sum('ingreso_mensual'))['total'] or 0

    # Verificar si hay aportantes sin email
    hay_aportantes_sin_email = aportantes.filter(email__isnull=True).exists() or aportantes.filter(email='').exists()

    # ocultar_valores está disponible automáticamente desde context_processors.py

    context = {
        'aportantes': aportantes,
        'total_ingresos': total_ingresos,
        'hay_aportantes_sin_email': hay_aportantes_sin_email,
    }
    return render(request, 'gastos/aportantes_lista.html', context)


@login_required
def crear_aportante(request):
    """Crear un nuevo aportante"""
    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.error(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    try:
        from .models import Familia
        familia = Familia.objects.get(id=familia_id)

        # Verificar que la suscripción esté activa
        if not familia.esta_suscripcion_activa():
            dias_restantes = familia.dias_restantes_suscripcion()
            if familia.en_periodo_prueba and dias_restantes > 0:
                messages.info(
                    request,
                    f'⏰ <strong>Período de prueba:</strong> Te quedan {dias_restantes} días gratis. '
                    f'<br>💳 <a href="/suscripcion/" class="alert-link">Activa tu suscripción ahora</a> y continúa sin interrupciones.',
                    extra_tags='safe'
                )
            else:
                messages.error(
                    request,
                    f'❌ <strong>Suscripción expirada:</strong> Tu acceso ha sido suspendido. '
                    f'<br>💡 <strong>Renueva tu plan ahora</strong> y recupera el acceso completo. '
                    f'<br><a href="/suscripcion/" class="btn btn-sm btn-danger mt-2"><i class="bi bi-credit-card"></i> Renovar Suscripción</a>',
                    extra_tags='safe'
                )
                return redirect('estado_suscripcion')

        # Verificar límite de aportantes según el plan
        if not familia.puede_agregar_aportante():
            total_actual = familia.aportantes.filter(activo=True).count()
            messages.warning(
                request,
                f'🔒 <strong>Límite alcanzado:</strong> Tienes {total_actual} de {familia.plan.max_aportantes} aportantes permitidos en tu {familia.plan.nombre}. '
                f'<br><br>💡 <strong>¡Actualiza a Plan Premium y agrega aportantes ilimitados!</strong> '
                f'<br>✨ Además obtendrás: gastos ilimitados, reportes avanzados y más. '
                f'<br><a href="/suscripcion/" class="btn btn-sm btn-primary mt-2"><i class="bi bi-arrow-up-circle"></i> Ver Planes y Actualizar</a>',
                extra_tags='safe'
            )
            return redirect('lista_aportantes')

    except Familia.DoesNotExist:
        messages.error(request, 'Familia no encontrada.')
        return redirect('seleccionar_familia')

    if request.method == 'POST':
        form = AportanteForm(request.POST)
        if form.is_valid():
            aportante = form.save(commit=False)
            aportante.familia = familia
            aportante.save()
            messages.success(request, f'Aportante "{aportante.nombre}" creado exitosamente.')
            return redirect('lista_aportantes')
    else:
        form = AportanteForm()

    return render(request, 'gastos/aportante_form.html', {'form': form, 'titulo': 'Nuevo Aportante'})


@login_required
def editar_aportante(request, pk):
    """Editar un aportante existente"""
    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    # Verificar que el aportante pertenezca a la familia
    aportante = get_object_or_404(Aportante, pk=pk, familia_id=familia_id)

    if request.method == 'POST':
        form = AportanteForm(request.POST, instance=aportante)
        if form.is_valid():
            aportante = form.save()
            messages.success(request, f'Aportante "{aportante.nombre}" actualizado exitosamente.')
            return redirect('lista_aportantes')
    else:
        form = AportanteForm(instance=aportante)

    return render(request, 'gastos/aportante_form.html', {'form': form, 'titulo': 'Editar Aportante'})


@login_required
def lista_categorias(request):
    """Lista de categorías de gastos con sus subcategorías"""
    # Filtrar por familia
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    categorias = CategoriaGasto.objects.filter(familia_id=familia_id).prefetch_related('subcategorias').all()
    return render(request, 'gastos/categorias_lista.html', {'categorias': categorias})


@login_required
def crear_categoria(request):
    """Crear una nueva categoría"""
    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.error(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    try:
        from .models import Familia
        familia = Familia.objects.get(id=familia_id)

        # Verificar que la suscripción esté activa
        if not familia.esta_suscripcion_activa():
            messages.error(
                request,
                f'❌ <strong>Suscripción expirada:</strong> Renueva tu plan para continuar creando categorías. '
                f'<br><a href="/suscripcion/" class="btn btn-sm btn-danger mt-2"><i class="bi bi-credit-card"></i> Renovar Ahora</a>',
                extra_tags='safe'
            )
            return redirect('estado_suscripcion')

        # Verificar límite de categorías según el plan
        if not familia.puede_agregar_categoria():
            total_actual = familia.categorias.filter(activo=True).count()
            messages.warning(
                request,
                f'🔒 <strong>Límite de categorías alcanzado:</strong> Tienes {total_actual} de {familia.plan.max_categorias} categorías en tu {familia.plan.nombre}. '
                f'<br><br>🚀 <strong>¡Actualiza tu plan y organiza mejor tus gastos!</strong> '
                f'<br>📊 Con Plan Premium tendrás categorías ilimitadas para clasificar todos tus gastos. '
                f'<br><a href="/suscripcion/" class="btn btn-sm btn-success mt-2"><i class="bi bi-star-fill"></i> Actualizar a Premium desde $19,900/mes</a>',
                extra_tags='safe'
            )
            return redirect('lista_categorias')

    except Familia.DoesNotExist:
        messages.error(request, 'Familia no encontrada.')
        return redirect('seleccionar_familia')

    if request.method == 'POST':
        form = CategoriaGastoForm(request.POST)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.familia = familia
            categoria.save()
            messages.success(request, f'Categoría "{categoria.nombre}" creada exitosamente.')
            return redirect('lista_categorias')
    else:
        form = CategoriaGastoForm()

    return render(request, 'gastos/categoria_form.html', {'form': form, 'titulo': 'Nueva Categoría'})


@login_required
def editar_categoria(request, pk):
    """Editar una categoría existente"""
    categoria = get_object_or_404(CategoriaGasto, pk=pk)

    # Verificar que pertenece a la familia del usuario
    familia_id = request.session.get('familia_id')
    if categoria.familia_id != familia_id:
        messages.error(request, 'No tienes permiso para editar esta categoría.')
        return redirect('lista_categorias')

    if request.method == 'POST':
        form = CategoriaGastoForm(request.POST, instance=categoria)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'✅ Categoría "{categoria.nombre}" actualizada exitosamente.')
            return redirect('lista_categorias')
    else:
        form = CategoriaGastoForm(instance=categoria)

    return render(request, 'gastos/categoria_form.html', {
        'form': form,
        'titulo': 'Editar Categoría',
        'categoria': categoria
    })


@login_required
def lista_subcategorias(request):
    """Lista de subcategorías de gastos"""
    # Filtrar por familia
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    subcategorias = SubcategoriaGasto.objects.filter(categoria__familia_id=familia_id).select_related('categoria').all()
    return render(request, 'gastos/subcategorias_lista.html', {'subcategorias': subcategorias})


@login_required
def crear_subcategoria(request):
    """Crear una nueva subcategoría"""
    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    if request.method == 'POST':
        form = SubcategoriaGastoForm(request.POST)
        if form.is_valid():
            subcategoria = form.save()
            # La familia se determina automáticamente por la categoría seleccionada
            messages.success(request, f'Subcategoría "{subcategoria.nombre}" creada exitosamente en "{subcategoria.categoria.nombre}".')
            return redirect('lista_subcategorias')
    else:
        form = SubcategoriaGastoForm()
        # Filtrar categorías por familia
        form.fields['categoria'].queryset = CategoriaGasto.objects.filter(familia_id=familia_id, activo=True)

    return render(request, 'gastos/subcategoria_form.html', {'form': form, 'titulo': 'Nueva Subcategoría'})


@login_required
def editar_subcategoria(request, pk):
    """Editar una subcategoría existente"""
    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    # Verificar que la subcategoría pertenezca a la familia (a través de categoria)
    subcategoria = get_object_or_404(SubcategoriaGasto, pk=pk, categoria__familia_id=familia_id)

    if request.method == 'POST':
        form = SubcategoriaGastoForm(request.POST, instance=subcategoria)
        if form.is_valid():
            subcategoria = form.save()
            messages.success(request, f'Subcategoría "{subcategoria.nombre}" actualizada exitosamente.')
            return redirect('lista_subcategorias')
    else:
        form = SubcategoriaGastoForm(instance=subcategoria)

    return render(request, 'gastos/subcategoria_form.html', {'form': form, 'titulo': 'Editar Subcategoría'})


@login_required
def lista_gastos(request):
    """Lista de todos los gastos con filtros"""
    # Filtrar por familia
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    # Obtener mes y año actual
    fecha_actual = timezone.now()
    mes_actual = fecha_actual.month
    anio_actual = fecha_actual.year

    # Filtros
    tipo = request.GET.get('tipo')
    categoria_id = request.GET.get('categoria')
    subcategoria_id = request.GET.get('subcategoria')
    mes = request.GET.get('mes', str(mes_actual))  # Por defecto: mes actual
    anio = request.GET.get('anio', str(anio_actual))  # Por defecto: año actual

    # Query base - solo gastos compartidos (no personales)
    gastos = Gasto.objects.filter(
        subcategoria__categoria__familia_id=familia_id,
        tipo_gasto='COMPARTIDO'  # Solo gastos compartidos
    ).select_related('subcategoria__categoria', 'pagado_por')

    # Aplicar filtros
    if tipo:
        gastos = gastos.filter(subcategoria__tipo=tipo)
    if categoria_id:
        gastos = gastos.filter(subcategoria__categoria_id=categoria_id)
    if subcategoria_id:
        gastos = gastos.filter(subcategoria_id=subcategoria_id)

    # Filtrar por mes y año (siempre aplicar)
    if mes and anio:
        gastos = gastos.filter(fecha__month=int(mes), fecha__year=int(anio))
    elif anio:
        gastos = gastos.filter(fecha__year=int(anio))

    # Ordenar por fecha descendente
    gastos = gastos.order_by('-fecha', '-fecha_registro')

    # Totales
    total = gastos.aggregate(total=Sum('monto'))['total'] or 0

    categorias = CategoriaGasto.objects.filter(familia_id=familia_id, activo=True)
    subcategorias = SubcategoriaGasto.objects.filter(categoria__familia_id=familia_id, activo=True).select_related('categoria')

    # Nombre del mes seleccionado
    mes_nombre = MESES_ES.get(int(mes), '') if mes else ''

    context = {
        'gastos': gastos,
        'total': total,
        'categorias': categorias,
        'subcategorias': subcategorias,
        'mes_seleccionado': int(mes) if mes else None,
        'anio_seleccionado': int(anio) if anio else None,
        'mes_nombre': mes_nombre,
        'anio': anio,
    }

    return render(request, 'gastos/gastos_lista.html', context)


@login_required
def crear_gasto(request):
    """Crear un nuevo gasto (compartido o personal)"""
    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    # Determinar tipo por defecto según parámetro URL
    tipo_por_defecto = 'PERSONAL' if request.GET.get('personal', 'false').lower() == 'true' else 'COMPARTIDO'

    if request.method == 'POST':
        form = GastoForm(request.POST, familia_id=familia_id)

        if form.is_valid():
            gasto = form.save()
            tipo_gasto = gasto.tipo_gasto

            # Si es compartido y se marcó distribuir automáticamente
            if tipo_gasto == 'COMPARTIDO' and form.cleaned_data.get('distribuir_automaticamente'):
                aportantes_activos = Aportante.objects.filter(familia_id=familia_id, activo=True)

                for aportante in aportantes_activos:
                    porcentaje = aportante.calcular_porcentaje_aporte()
                    DistribucionGasto.objects.create(
                        gasto=gasto,
                        aportante=aportante,
                        porcentaje=porcentaje
                    )

                messages.success(request, f'Gasto "{gasto.subcategoria.nombre}" creado y distribuido automáticamente.')
            else:
                tipo_texto = "personal" if tipo_gasto == 'PERSONAL' else "compartido"
                messages.success(request, f'Gasto {tipo_texto} "{gasto.subcategoria.nombre}" creado exitosamente.')

            # GAMIFICACIÓN: Registrar gasto creado
            try:
                from .gamificacion_service import GamificacionService
                GamificacionService.registrar_gasto_creado(request.user)
            except Exception as e:
                print(f"Error en gamificación: {e}")

            # Redirigir según el tipo
            if tipo_gasto == 'PERSONAL':
                return redirect('lista_gastos_personales')
            else:
                return redirect('lista_gastos')
        else:
            # Mostrar errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en {field}: {error}')
    else:
        # Inicializar formulario con tipo por defecto
        initial_data = {
            'fecha': timezone.now().date(),
            'tipo_gasto': tipo_por_defecto
        }
        form = GastoForm(initial=initial_data, familia_id=familia_id)

    context = {
        'form': form,
        'titulo': 'Nuevo Gasto',
    }

    return render(request, 'gastos/gasto_form.html', context)


@login_required
def editar_gasto(request, pk):
    """Editar un gasto existente"""
    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    # Verificar que el gasto pertenezca a la familia (a través de subcategoria)
    gasto = get_object_or_404(Gasto, pk=pk, subcategoria__categoria__familia_id=familia_id)

    if request.method == 'POST':
        form = GastoForm(request.POST, instance=gasto, familia_id=familia_id)
        if form.is_valid():
            gasto = form.save()
            messages.success(request, f'Gasto "{gasto.descripcion}" actualizado exitosamente.')
            return redirect('lista_gastos')
    else:
        form = GastoForm(instance=gasto, familia_id=familia_id)

    return render(request, 'gastos/gasto_form.html', {'form': form, 'titulo': 'Editar Gasto'})


@login_required
def detalle_gasto(request, pk):
    """Ver detalle de un gasto incluyendo su distribución"""
    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    # Verificar que el gasto pertenezca a la familia (a través de subcategoria)
    gasto = get_object_or_404(Gasto, pk=pk, subcategoria__categoria__familia_id=familia_id)
    distribuciones = gasto.distribuciones.all().select_related('aportante')

    context = {
        'gasto': gasto,
        'distribuciones': distribuciones,
    }

    return render(request, 'gastos/gasto_detalle.html', context)


@login_required
def reportes(request):
    """Vista de reportes y estadísticas"""
    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    # Parámetros de fecha
    mes_param = request.GET.get('mes', str(timezone.now().month))
    anio_param = request.GET.get('anio', str(timezone.now().year))
    
    try:
        mes = int(mes_param)
        anio = int(anio_param)
    except (ValueError, TypeError):
        mes = timezone.now().month
        anio = timezone.now().year

    # Obtener aportantes activos
    aportantes = Aportante.objects.filter(familia_id=familia_id, activo=True).order_by('nombre')

    # Gastos del período de la familia (solo compartidos)
    gastos_periodo = Gasto.objects.filter(
        subcategoria__categoria__familia_id=familia_id,
        fecha__month=mes,
        fecha__year=anio,
        tipo_gasto='COMPARTIDO'
    ).select_related('subcategoria__categoria', 'pagado_por').prefetch_related('distribuciones__aportante').order_by('fecha', 'id')

    # Calcular distribuciones por gasto y aportante
    gastos_detallados = []
    for gasto in gastos_periodo:
        distribuciones = {}
        distribuciones_gasto = gasto.distribuciones.all()
        
        # Si no hay distribuciones, distribuir equitativamente
        if not distribuciones_gasto.exists():
            num_aportantes = aportantes.count()
            if num_aportantes > 0:
                monto_por_aportante = gasto.monto / num_aportantes
                for aportante in aportantes:
                    distribuciones[aportante.id] = monto_por_aportante
        else:
            for dist in distribuciones_gasto:
                distribuciones[dist.aportante.id] = dist.monto_asignado

        gastos_detallados.append({
            'gasto': gasto,
            'distribuciones': distribuciones
        })

    # Totales
    total_gastos = gastos_periodo.aggregate(total=Sum('monto'))['total'] or Decimal('0')
    gastos_fijos = gastos_periodo.filter(subcategoria__tipo='FIJO').aggregate(total=Sum('monto'))['total'] or Decimal('0')
    gastos_variables = gastos_periodo.filter(subcategoria__tipo='VARIABLE').aggregate(total=Sum('monto'))['total'] or Decimal('0')

    # Ingresos totales de la familia
    total_ingresos = aportantes.aggregate(total=Sum('ingreso_mensual'))['total'] or Decimal('0')

    # Calcular totales por aportante
    totales_por_aportante = {}
    for aportante in aportantes:
        total_asignado = DistribucionGasto.objects.filter(
            aportante=aportante,
            gasto__fecha__month=mes,
            gasto__fecha__year=anio,
            gasto__tipo_gasto='COMPARTIDO'
        ).aggregate(total=Sum('monto_asignado'))['total'] or Decimal('0')
        
        totales_por_aportante[aportante.id] = total_asignado

    # Distribución por aportante
    aportantes_con_gastos = []
    for aportante in aportantes:
        total_asignado = totales_por_aportante.get(aportante.id, Decimal('0'))

        aportantes_con_gastos.append({
            'aportante': aportante,
            'total_asignado': total_asignado,
            'ingreso': aportante.ingreso_mensual,
            'balance': aportante.ingreso_mensual - total_asignado,
        })

    # Gastos por categoría principal de la familia
    gastos_por_categoria = CategoriaGasto.objects.filter(
        familia_id=familia_id,
        subcategorias__gastos__fecha__month=mes,
        subcategorias__gastos__fecha__year=anio,
        subcategorias__gastos__tipo_gasto='COMPARTIDO'
    ).annotate(
        total=Sum('subcategorias__gastos__monto'),
        cantidad=Count('subcategorias__gastos', distinct=True)
    ).order_by('-total')

    # Generar lista de meses disponibles (últimos 12 meses)
    fecha_actual = timezone.now()
    meses_disponibles = []
    for i in range(12):
        fecha_mes = date(fecha_actual.year, fecha_actual.month, 1) - timedelta(days=30*i)
        meses_disponibles.append({
            'mes': fecha_mes.month,
            'anio': fecha_mes.year,
            'nombre': f"{MESES_ES[fecha_mes.month]} {fecha_mes.year}",
            'seleccionado': (fecha_mes.month == mes and fecha_mes.year == anio)
        })

    context = {
        'familia': familia,
        'mes': mes,
        'anio': anio,
        'mes_nombre': MESES_ES[mes],
        'total_gastos': total_gastos,
        'gastos_fijos': gastos_fijos,
        'gastos_variables': gastos_variables,
        'total_ingresos': total_ingresos,
        'balance': total_ingresos - total_gastos,
        'aportantes': aportantes,
        'aportantes_con_gastos': aportantes_con_gastos,
        'gastos_por_categoria': gastos_por_categoria,
        'gastos_detallados': gastos_detallados,
        'totales_por_aportante': totales_por_aportante,
        'meses_disponibles': meses_disponibles,
    }

    return render(request, 'gastos/reportes.html', context)


@login_required
def conciliacion(request):
    """Vista de conciliación de gastos mensuales"""
    from .models import IngresoAportante, ConciliacionMensual
    from decimal import Decimal

    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.error(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    # Parámetros de fecha
    mes = int(request.GET.get('mes', timezone.now().month))
    anio = int(request.GET.get('anio', timezone.now().year))

    # Obtener aportantes activos de la familia
    aportantes = Aportante.objects.filter(familia_id=familia_id, activo=True)

    # ========== CÁLCULO HÍBRIDO DE INGRESOS ==========
    # 1. Intentar obtener ingresos reales registrados en IngresoAportante
    ingresos_reales = IngresoAportante.objects.filter(
        aportante__familia_id=familia_id,
        fecha__month=mes,
        fecha__year=anio
    ).aggregate(total=Sum('monto'))['total']

    # 2. Si hay ingresos reales, usarlos; si no, usar ingreso_mensual de aportantes
    if ingresos_reales:
        total_ingresos = Decimal(str(ingresos_reales))
    else:
        # Fallback: usar ingreso_mensual fijo de los aportantes
        total_ingresos_fijo = aportantes.aggregate(total=Sum('ingreso_mensual'))['total']
        total_ingresos = Decimal(str(total_ingresos_fijo)) if total_ingresos_fijo else Decimal('0')

    # 3. Obtener saldo del mes anterior (de conciliación cerrada)
    mes_anterior = mes - 1 if mes > 1 else 12
    anio_anterior = anio if mes > 1 else anio - 1

    try:
        conciliacion_anterior = ConciliacionMensual.objects.get(
            familia_id=familia_id,
            mes=mes_anterior,
            anio=anio_anterior,
            estado='CERRADA'
        )
        saldo_anterior = conciliacion_anterior.saldo_transferido_siguiente
    except ConciliacionMensual.DoesNotExist:
        saldo_anterior = Decimal('0')

    # Calcular total de gastos del mes de la familia (solo gastos compartidos)
    total_gastos_mes = Gasto.objects.filter(
        subcategoria__categoria__familia_id=familia_id,
        fecha__month=mes,
        fecha__year=anio,
        tipo_gasto='COMPARTIDO'  # Solo gastos compartidos en conciliación
    ).aggregate(total=Sum('monto'))['total'] or Decimal('0')

    # ========== CÁLCULO DE SALDO DISPONIBLE ==========
    saldo_disponible = total_ingresos + saldo_anterior - total_gastos_mes

    # Calcular conciliación por aportante
    conciliacion_aportantes = []
    for aportante in aportantes:
        # Lo que debería pagar según su porcentaje
        gastos_asignados = aportante.calcular_gastos_asignados(mes, anio)

        # Lo que realmente pagó
        pagos_realizados = aportante.calcular_pagos_realizados(mes, anio)

        # Balance de conciliación
        balance = aportante.calcular_balance_conciliacion(mes, anio)

        # Porcentaje que pagó del total
        porcentaje_pagado = (pagos_realizados / total_gastos_mes * 100) if total_gastos_mes > 0 else 0
        porcentaje_esperado = aportante.calcular_porcentaje_aporte()

        conciliacion_aportantes.append({
            'aportante': aportante,
            'porcentaje_esperado': porcentaje_esperado,
            'gastos_asignados': gastos_asignados,
            'pagos_realizados': pagos_realizados,
            'porcentaje_pagado': porcentaje_pagado,
            'balance': balance,
            'estado': 'debe_recibir' if balance > 0 else 'debe_pagar' if balance < 0 else 'equilibrado'
        })

    # Calcular reintegros necesarios
    # Los que pagaron de más deben recibir de los que pagaron de menos
    debe_recibir = [c for c in conciliacion_aportantes if c['balance'] > 0]
    debe_pagar = [c for c in conciliacion_aportantes if c['balance'] < 0]

    reintegros = []
    for paga in debe_pagar:
        for recibe in debe_recibir:
            if recibe['balance'] > 0 and abs(paga['balance']) > 0:
                # Calcular cuánto puede transferir
                monto_transferencia = min(abs(paga['balance']), recibe['balance'])

                if monto_transferencia > 0:
                    reintegros.append({
                        'de': paga['aportante'],
                        'para': recibe['aportante'],
                        'monto': monto_transferencia
                    })

                    # Actualizar balances temporales para el cálculo
                    paga['balance'] += monto_transferencia
                    recibe['balance'] -= monto_transferencia

    # Detalles de pagos por aportante (solo gastos compartidos)
    detalles_pagos = {}
    for aportante in aportantes:
        gastos_pagados = Gasto.objects.filter(
            subcategoria__categoria__familia_id=familia_id,
            pagado_por=aportante,
            fecha__month=mes,
            fecha__year=anio,
            tipo_gasto='COMPARTIDO'  # Solo gastos compartidos
        ).select_related('subcategoria__categoria')

        detalles_pagos[aportante.id] = gastos_pagados

    # Verificar si ya existe una conciliación cerrada para este mes
    from .models import ConciliacionMensual
    conciliacion_existente = ConciliacionMensual.objects.filter(
        familia_id=familia_id,
        mes=mes,
        anio=anio
    ).first()

    # Calcular progreso de confirmaciones
    confirmados_count = 0
    total_aportantes = 0
    if conciliacion_existente:
        total_aportantes = conciliacion_existente.detalles.count()
        confirmados_count = conciliacion_existente.detalles.filter(confirmado=True).count()

    # Verificar si hay aportantes sin email
    hay_aportantes_sin_email = any(not a.email for a in aportantes)

    # Calcular balance (ahora incluye saldo anterior)
    balance = total_ingresos + saldo_anterior - total_gastos_mes

    context = {
        'mes': mes,
        'anio': anio,
        'total_ingresos': total_ingresos,
        'saldo_anterior': saldo_anterior,
        'saldo_disponible': saldo_disponible,
        'total_gastos_mes': total_gastos_mes,
        'balance': balance,
        'conciliacion_aportantes': conciliacion_aportantes,
        'reintegros': reintegros,
        'detalles_pagos': detalles_pagos,
        'hay_desbalance': len(reintegros) > 0,
        'conciliacion_existente': conciliacion_existente,
        'confirmados_count': confirmados_count,
        'total_aportantes': total_aportantes,
        'hay_aportantes_sin_email': hay_aportantes_sin_email,
    }

    return render(request, 'gastos/conciliacion.html', context)


@login_required
def cerrar_conciliacion(request):
    """Iniciar proceso de cierre de conciliación enviando códigos a los aportantes"""
    if request.method != 'POST':
        return redirect('conciliacion')

    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.error(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    mes = int(request.POST.get('mes'))
    anio = int(request.POST.get('anio'))
    observaciones = request.POST.get('observaciones', '')

    from .models import Familia, ConciliacionMensual, DetalleConciliacion, Reintegro
    from .email_utils import enviar_codigo_confirmacion_conciliacion

    try:
        familia = Familia.objects.get(id=familia_id)

        # Verificar si ya existe
        conciliacion, created = ConciliacionMensual.objects.get_or_create(
            familia=familia,
            mes=mes,
            anio=anio,
            defaults={
                'total_gastos': 0,
                'observaciones': observaciones,
                'estado': 'PENDIENTE'
            }
        )

        if not created and conciliacion.estado == 'CERRADA':
            messages.warning(request, f'⚠️ La conciliación de este mes ya fue cerrada el {conciliacion.fecha_cierre.strftime("%d/%m/%Y")}.')
            return redirect('conciliacion')

        # Calcular datos de conciliación
        aportantes = Aportante.objects.filter(familia=familia, activo=True)

        # Verificar que todos los aportantes tengan email
        aportantes_sin_email = [a.nombre for a in aportantes if not a.email]
        if aportantes_sin_email:
            messages.error(
                request,
                f'❌ <strong>No se puede enviar códigos de confirmación</strong><br>'
                f'Los siguientes aportantes no tienen email registrado:<br>'
                f'<ul class="mb-2">' + ''.join([f'<li><strong>{nombre}</strong></li>' for nombre in aportantes_sin_email]) + '</ul>'
                f'<a href="/aportantes/" class="btn btn-sm btn-primary mt-2">'
                f'<i class="bi bi-pencil"></i> Ir a editar aportantes</a>',
                extra_tags='safe'
            )
            from django.urls import reverse
            url = reverse('conciliacion') + f'?mes={mes}&anio={anio}'
            return redirect(url)

        # ========== CÁLCULO HÍBRIDO DE INGRESOS ==========
        from .models import IngresoAportante
        from decimal import Decimal

        # 1. Intentar obtener ingresos reales registrados
        ingresos_reales = IngresoAportante.objects.filter(
            aportante__familia=familia,
            fecha__month=mes,
            fecha__year=anio
        ).aggregate(total=Sum('monto'))['total']

        # 2. Si hay ingresos reales, usarlos; si no, usar ingreso_mensual
        if ingresos_reales:
            total_ingresos = Decimal(str(ingresos_reales))
        else:
            total_ingresos_fijo = aportantes.aggregate(total=Sum('ingreso_mensual'))['total']
            total_ingresos = Decimal(str(total_ingresos_fijo)) if total_ingresos_fijo else Decimal('0')

        # 3. Obtener saldo del mes anterior
        mes_anterior = mes - 1 if mes > 1 else 12
        anio_anterior = anio if mes > 1 else anio - 1

        try:
            conciliacion_anterior = ConciliacionMensual.objects.get(
                familia=familia,
                mes=mes_anterior,
                anio=anio_anterior,
                estado='CERRADA'
            )
            saldo_anterior = conciliacion_anterior.saldo_transferido_siguiente
        except ConciliacionMensual.DoesNotExist:
            saldo_anterior = Decimal('0')

        total_gastos_mes = Gasto.objects.filter(
            subcategoria__categoria__familia=familia,
            fecha__month=mes,
            fecha__year=anio,
            tipo_gasto='COMPARTIDO'  # Solo gastos compartidos en conciliación
        ).aggregate(total=Sum('monto'))['total'] or Decimal('0')

        # Actualizar conciliación con los valores calculados
        conciliacion.total_ingresos = total_ingresos
        conciliacion.total_gastos = total_gastos_mes
        conciliacion.saldo_anterior = saldo_anterior
        conciliacion.saldo_disponible = total_ingresos + saldo_anterior - total_gastos_mes
        conciliacion.observaciones = observaciones
        conciliacion.save()

        # Limpiar detalles y reintegros anteriores
        conciliacion.detalles.all().delete()
        conciliacion.reintegros.all().delete()

        # Crear detalles de conciliación y enviar códigos
        debe_recibir_list = []
        debe_pagar_list = []
        emails_enviados = 0
        emails_fallidos = []

        for aportante in aportantes:
            gastos_asignados = aportante.calcular_gastos_asignados(mes, anio)
            pagos_realizados = aportante.calcular_pagos_realizados(mes, anio)
            balance = pagos_realizados - gastos_asignados
            porcentaje = aportante.calcular_porcentaje_aporte()

            detalle = DetalleConciliacion.objects.create(
                conciliacion=conciliacion,
                aportante=aportante,
                porcentaje_esperado=porcentaje,
                monto_debe_pagar=gastos_asignados,
                monto_pago_real=pagos_realizados,
                balance=balance
            )

            # Enviar email con código de confirmación
            if aportante.email:
                if enviar_codigo_confirmacion_conciliacion(detalle):
                    emails_enviados += 1
                else:
                    emails_fallidos.append(aportante.nombre)
            else:
                emails_fallidos.append(f"{aportante.nombre} (sin email)")

            if balance > 0:
                debe_recibir_list.append({'aportante': aportante, 'balance': balance})
            elif balance < 0:
                debe_pagar_list.append({'aportante': aportante, 'balance': abs(balance)})

        # Crear registros de reintegros
        for paga_dict in debe_pagar_list:
            for recibe_dict in debe_recibir_list:
                if recibe_dict['balance'] > 0 and paga_dict['balance'] > 0:
                    monto_transferencia = min(paga_dict['balance'], recibe_dict['balance'])

                    if monto_transferencia > 0:
                        Reintegro.objects.create(
                            conciliacion=conciliacion,
                            de_aportante=paga_dict['aportante'],
                            para_aportante=recibe_dict['aportante'],
                            monto=monto_transferencia
                        )

                        paga_dict['balance'] -= monto_transferencia
                        recibe_dict['balance'] -= monto_transferencia

        # Mensaje de éxito
        mensaje_exito = (
            f'📧 <strong>Códigos de confirmación enviados</strong><br>'
            f'📅 Período: {conciliacion}<br>'
            f'💰 Total gastos: ${total_gastos_mes:,.0f}<br>'
            f'✉️ Emails enviados: {emails_enviados} de {aportantes.count()}<br>'
        )

        if emails_fallidos:
            mensaje_exito += f'⚠️ Advertencia: No se pudo enviar a: {", ".join(emails_fallidos)}<br>'

        mensaje_exito += (
            f'<br><strong>Siguiente paso:</strong> Cada aportante debe ingresar su código de confirmación.<br>'
            f'La conciliación se cerrará automáticamente cuando todos confirmen.'
        )

        messages.success(request, mensaje_exito, extra_tags='safe')

    except Familia.DoesNotExist:
        messages.error(request, 'Familia no encontrada.')
    except Exception as e:
        messages.error(request, f'Error al procesar conciliación: {str(e)}')

    # Redirigir manteniendo los parámetros de mes y año
    from django.urls import reverse
    url = reverse('conciliacion') + f'?mes={mes}&anio={anio}'
    return redirect(url)


@login_required
def confirmar_conciliacion(request):
    """Confirmar conciliación con código enviado por email"""
    if request.method != 'POST':
        return redirect('conciliacion')

    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.error(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    mes = int(request.POST.get('mes'))
    anio = int(request.POST.get('anio'))
    aportante_id = int(request.POST.get('aportante_id'))
    codigo = request.POST.get('codigo', '').strip()

    from .models import ConciliacionMensual, DetalleConciliacion
    from .email_utils import enviar_notificacion_conciliacion_cerrada

    try:
        # Buscar la conciliación
        conciliacion = ConciliacionMensual.objects.get(
            familia_id=familia_id,
            mes=mes,
            anio=anio
        )

        # Buscar el detalle del aportante
        detalle = DetalleConciliacion.objects.get(
            conciliacion=conciliacion,
            aportante_id=aportante_id
        )

        # Verificar el código
        if detalle.codigo_confirmacion != codigo:
            messages.error(request, f'❌ Código incorrecto para {detalle.aportante.nombre}. Por favor verifica el código enviado a tu email.')
            from django.urls import reverse
            url = reverse('conciliacion') + f'?mes={mes}&anio={anio}'
            return redirect(url)

        # Confirmar
        if not detalle.confirmado:
            detalle.confirmado = True
            detalle.fecha_confirmacion = timezone.now()
            detalle.save()

            messages.success(request, f'✅ ¡Confirmado! {detalle.aportante.nombre} ha aceptado la conciliación.')
        else:
            messages.info(request, f'ℹ️ {detalle.aportante.nombre} ya había confirmado anteriormente.')

        # Verificar si todos confirmaron
        total_detalles = conciliacion.detalles.count()
        confirmados = conciliacion.detalles.filter(confirmado=True).count()

        if confirmados == total_detalles and total_detalles > 0:
            # Todos confirmaron, pero si hay saldo positivo, pedir destino antes de cerrar
            if conciliacion.saldo_disponible > 0 and not conciliacion.destino_saldo:
                messages.warning(
                    request,
                    f'✅ Todos han confirmado, pero hay un saldo positivo de ${conciliacion.saldo_disponible:,.0f}.<br>'
                    f'Por favor, selecciona el destino del saldo sobrante para completar el cierre.',
                    extra_tags='safe'
                )
            else:
                # Cerrar la conciliación con el destino seleccionado (o con déficit)
                destino = conciliacion.destino_saldo if conciliacion.destino_saldo else 'SIGUIENTE_MES'
                conciliacion.cerrar_conciliacion(request.user if request.user.is_authenticated else None, destino)

                # Enviar notificación de cierre
                enviar_notificacion_conciliacion_cerrada(conciliacion)

                messages.success(
                    request,
                    f'🎉 <strong>¡Conciliación Cerrada!</strong><br>'
                    f'Todos los aportantes ({confirmados}/{total_detalles}) han confirmado.<br>'
                    f'La conciliación de {conciliacion} ha sido cerrada exitosamente.<br>'
                    f'Saldo transferido al siguiente mes: ${conciliacion.saldo_transferido_siguiente:,.0f}<br>'
                    f'Se han enviado notificaciones a todos los aportantes.',
                    extra_tags='safe'
                )
        else:
            messages.info(
                request,
                f'📊 Progreso: {confirmados} de {total_detalles} aportantes han confirmado.<br>'
                f'Faltan {total_detalles - confirmados} confirmaciones para cerrar la conciliación.',
                extra_tags='safe'
            )

    except ConciliacionMensual.DoesNotExist:
        messages.error(request, 'No se encontró la conciliación para este período.')
    except DetalleConciliacion.DoesNotExist:
        messages.error(request, 'No se encontró el detalle del aportante.')
    except Exception as e:
        messages.error(request, f'Error al confirmar: {str(e)}')

    # Redirigir manteniendo los parámetros de mes y año
    from django.urls import reverse
    url = reverse('conciliacion') + f'?mes={mes}&anio={anio}'
    return redirect(url)


@login_required
def asignar_destino_saldo(request):
    """Asignar destino del saldo sobrante de una conciliación"""
    if request.method != 'POST':
        return redirect('conciliacion')

    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.error(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    mes = int(request.POST.get('mes'))
    anio = int(request.POST.get('anio'))
    destino_saldo = request.POST.get('destino_saldo')

    from .models import ConciliacionMensual, MetaAhorro
    from .email_utils import enviar_notificacion_conciliacion_cerrada
    from decimal import Decimal

    try:
        # Buscar la conciliación
        conciliacion = ConciliacionMensual.objects.get(
            familia_id=familia_id,
            mes=mes,
            anio=anio
        )

        # Verificar que todos hayan confirmado
        total_detalles = conciliacion.detalles.count()
        confirmados = conciliacion.detalles.filter(confirmado=True).count()

        if confirmados != total_detalles:
            messages.error(request, 'No se puede asignar destino. Aún faltan confirmaciones de aportantes.')
            return redirect('conciliacion')

        # Verificar que haya saldo positivo
        if conciliacion.saldo_disponible <= 0:
            messages.warning(request, 'No hay saldo positivo para asignar.')
            return redirect('conciliacion')

        # Asignar el destino y cerrar la conciliación
        saldo_transferido = conciliacion.cerrar_conciliacion(request.user, destino_saldo)

        # Procesar según el destino seleccionado
        mensaje_destino = ""

        if destino_saldo == 'AHORRO':
            # Crear o actualizar meta de ahorro familiar
            meta_ahorro_familiar, created = MetaAhorro.objects.get_or_create(
                familia_id=familia_id,
                nombre='Ahorro Familiar General',
                defaults={
                    'monto_objetivo': Decimal('0'),
                    'monto_actual': Decimal('0'),
                    'estado': 'ACTIVA',
                    'prioridad': 'MEDIA'
                }
            )
            meta_ahorro_familiar.monto_actual += conciliacion.saldo_disponible
            meta_ahorro_familiar.save()
            mensaje_destino = f'💰 ${conciliacion.saldo_disponible:,.0f} agregados a Ahorro Familiar'

        elif destino_saldo == 'EMERGENCIA':
            # Crear o actualizar fondo de emergencia
            fondo_emergencia, created = MetaAhorro.objects.get_or_create(
                familia_id=familia_id,
                nombre='Fondo de Emergencia',
                defaults={
                    'monto_objetivo': Decimal('0'),
                    'monto_actual': Decimal('0'),
                    'estado': 'ACTIVA',
                    'prioridad': 'ALTA'
                }
            )
            fondo_emergencia.monto_actual += conciliacion.saldo_disponible
            fondo_emergencia.save()
            mensaje_destino = f'🚨 ${conciliacion.saldo_disponible:,.0f} agregados a Fondo de Emergencia'

        elif destino_saldo == 'SIGUIENTE_MES':
            mensaje_destino = f'📅 ${saldo_transferido:,.0f} transferidos al próximo mes'

        elif destino_saldo == 'DISTRIBUIR_PROPORCION':
            # Distribuir proporcionalmente según ingreso de cada aportante
            mensaje_destino = f'🎁 ${conciliacion.saldo_disponible:,.0f} distribuidos proporcionalmente entre aportantes'

        elif destino_saldo == 'DISTRIBUIR_IGUAL':
            # Distribuir en partes iguales
            mensaje_destino = f'🎁 ${conciliacion.saldo_disponible:,.0f} distribuidos en partes iguales entre aportantes'

        # Enviar notificación de cierre
        enviar_notificacion_conciliacion_cerrada(conciliacion)

        messages.success(
            request,
            f'🎉 <strong>¡Conciliación Cerrada Exitosamente!</strong><br>'
            f'📅 Período: {conciliacion}<br>'
            f'{mensaje_destino}<br>'
            f'Se han enviado notificaciones a todos los aportantes.',
            extra_tags='safe'
        )

    except ConciliacionMensual.DoesNotExist:
        messages.error(request, 'No se encontró la conciliación para este período.')
    except Exception as e:
        messages.error(request, f'Error al asignar destino: {str(e)}')

    return redirect('conciliacion')


@login_required
def historial_conciliaciones(request):
    """Ver historial de conciliaciones cerradas"""
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.error(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    from .models import ConciliacionMensual

    conciliaciones = ConciliacionMensual.objects.filter(
        familia_id=familia_id
    ).select_related('cerrada_por').prefetch_related('detalles__aportante', 'reintegros')

    context = {
        'conciliaciones': conciliaciones,
    }

    return render(request, 'gastos/historial_conciliaciones.html', context)


# =====================================================
# VISTAS DE METAS DE AHORRO
# =====================================================

@login_required
def lista_metas(request):
    """Lista de metas de ahorro de la familia"""
    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    try:
        familia = Familia.objects.get(id=familia_id)

        # Verificar que la suscripción esté activa
        if not familia.esta_suscripcion_activa():
            messages.error(request, 'Tu suscripción ha expirado. Renueva para continuar usando esta funcionalidad.')
            return redirect('estado_suscripcion')

        # Obtener todas las metas de la familia
        metas_activas = familia.metas_ahorro.filter(estado='ACTIVA').order_by('-prioridad', 'fecha_objetivo')
        metas_completadas = familia.metas_ahorro.filter(estado='COMPLETADA').order_by('-actualizado_en')[:5]
        metas_canceladas = familia.metas_ahorro.filter(estado='CANCELADA').order_by('-actualizado_en')[:3]

        # Calcular totales
        total_objetivo = metas_activas.aggregate(total=Sum('monto_objetivo'))['total'] or 0
        total_ahorrado = metas_activas.aggregate(total=Sum('monto_actual'))['total'] or 0

        context = {
            'metas_activas': metas_activas,
            'metas_completadas': metas_completadas,
            'metas_canceladas': metas_canceladas,
            'total_objetivo': total_objetivo,
            'total_ahorrado': total_ahorrado,
            'familia': familia,
        }

        return render(request, 'gastos/metas/lista.html', context)

    except Familia.DoesNotExist:
        messages.error(request, 'Familia no encontrada.')
        return redirect('seleccionar_familia')


@login_required
def crear_meta(request):
    """Crear una nueva meta de ahorro"""
    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    try:
        familia = Familia.objects.get(id=familia_id)

        # Verificar suscripción activa
        if not familia.esta_suscripcion_activa():
            messages.error(request, 'Tu suscripción ha expirado. Renueva para crear metas de ahorro.')
            return redirect('estado_suscripcion')

        if request.method == 'POST':
            form = MetaAhorroForm(request.POST)
            if form.is_valid():
                meta = form.save(commit=False)
                meta.familia = familia
                meta.fecha_inicio = date.today()
                meta.monto_actual = 0
                meta.estado = 'ACTIVA'
                meta.save()

                messages.success(request, f'✅ Meta "{meta.nombre}" creada exitosamente. ¡Comienza a ahorrar!')
                return redirect('lista_metas')
        else:
            form = MetaAhorroForm()

        context = {
            'form': form,
            'familia': familia,
        }

        return render(request, 'gastos/metas/form.html', context)

    except Familia.DoesNotExist:
        messages.error(request, 'Familia no encontrada.')
        return redirect('seleccionar_familia')


@login_required
def editar_meta(request, pk):
    """Editar una meta de ahorro existente"""
    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    # Verificar que la meta pertenezca a la familia
    meta = get_object_or_404(MetaAhorro, pk=pk, familia_id=familia_id)

    if request.method == 'POST':
        form = MetaAhorroForm(request.POST, instance=meta)
        if form.is_valid():
            meta = form.save()
            messages.success(request, f'✅ Meta "{meta.nombre}" actualizada exitosamente.')
            return redirect('detalle_meta', pk=meta.pk)
    else:
        form = MetaAhorroForm(instance=meta)

    context = {
        'form': form,
        'meta': meta,
    }

    return render(request, 'gastos/metas/form.html', context)


@login_required
def detalle_meta(request, pk):
    """Ver detalle de una meta de ahorro"""
    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    # Verificar que la meta pertenezca a la familia
    meta = get_object_or_404(MetaAhorro, pk=pk, familia_id=familia_id)

    context = {
        'meta': meta,
    }

    return render(request, 'gastos/metas/detalle.html', context)


@login_required
def agregar_ahorro(request, pk):
    """Agregar ahorro a una meta existente"""
    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    # Verificar que la meta pertenezca a la familia
    meta = get_object_or_404(MetaAhorro, pk=pk, familia_id=familia_id, estado='ACTIVA')

    if request.method == 'POST':
        form = AgregarAhorroForm(request.POST)
        if form.is_valid():
            monto = form.cleaned_data['monto']
            nota = form.cleaned_data.get('nota', '')

            # Agregar el ahorro
            meta.agregar_ahorro(monto)

            # Verificar si completó la meta
            if meta.estado == 'COMPLETADA':
                messages.success(
                    request,
                    f'🎉 ¡Felicidades! Has completado tu meta "{meta.nombre}". ¡Alcanzaste ${meta.monto_objetivo:,.0f}!',
                    extra_tags='celebration'
                )
            else:
                porcentaje = meta.porcentaje_completado
                messages.success(
                    request,
                    f'✅ ¡Excelente! Agregaste ${monto:,.0f} a tu meta. Llevas {porcentaje:.1f}% completado.'
                )

            return redirect('detalle_meta', pk=meta.pk)
    else:
        form = AgregarAhorroForm()

    context = {
        'meta': meta,
        'form': form,
    }

    return render(request, 'gastos/metas/agregar_ahorro.html', context)


@login_required
def cambiar_estado_meta(request, pk):
    """Cambiar el estado de una meta (cancelar o reactivar)"""
    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    # Verificar que la meta pertenezca a la familia
    meta = get_object_or_404(MetaAhorro, pk=pk, familia_id=familia_id)

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')

        if nuevo_estado in ['ACTIVA', 'CANCELADA']:
            estado_anterior = meta.get_estado_display()
            meta.estado = nuevo_estado
            meta.save()

            if nuevo_estado == 'CANCELADA':
                messages.info(request, f'Meta "{meta.nombre}" ha sido cancelada.')
            else:
                messages.success(request, f'Meta "{meta.nombre}" ha sido reactivada.')

            return redirect('lista_metas')

    return redirect('detalle_meta', pk=pk)


@login_required
def eliminar_meta(request, pk):
    """Eliminar una meta de ahorro"""
    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    # Verificar que la meta pertenezca a la familia
    meta = get_object_or_404(MetaAhorro, pk=pk, familia_id=familia_id)

    if request.method == 'POST':
        nombre = meta.nombre
        meta.delete()
        messages.success(request, f'Meta "{nombre}" eliminada exitosamente.')
        return redirect('lista_metas')

    return redirect('detalle_meta', pk=pk)


# ==================== ONBOARDING ====================

@login_required
@require_http_methods(["POST"])
def marcar_onboarding_completado(request):
    """Marcar el onboarding como completado"""
    request.session['onboarding_completed'] = True
    request.session['show_onboarding'] = False
    return JsonResponse({'success': True})


# ==================== PREFERENCIAS DE PRIVACIDAD ====================

@login_required
@require_http_methods(["POST"])
def toggle_privacidad_valores(request):
    """Alterna la privacidad de valores monetarios"""
    from .models import PreferenciasUsuario

    # Obtener o crear preferencias del usuario
    preferencias, created = PreferenciasUsuario.objects.get_or_create(usuario=request.user)

    # Alternar el valor
    preferencias.ocultar_valores_monetarios = not preferencias.ocultar_valores_monetarios
    preferencias.save()

    return JsonResponse({
        'success': True,
        'ocultar': preferencias.ocultar_valores_monetarios,
        'mensaje': 'Valores ocultos' if preferencias.ocultar_valores_monetarios else 'Valores visibles'
    })


# ==================== GESTIÓN DE INGRESOS ====================

@login_required
def lista_ingresos(request):
    """Lista de ingresos de aportantes"""
    from .models import IngresoAportante
    from .forms import IngresoAportanteForm

    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    familia = get_object_or_404(Familia, id=familia_id)

    # Obtener ingresos de todos los aportantes de la familia
    ingresos = IngresoAportante.objects.filter(
        aportante__familia_id=familia_id
    ).select_related('aportante').order_by('-fecha', '-fecha_registro')

    # Obtener estadísticas
    mes_actual = timezone.now().month
    anio_actual = timezone.now().year

    # Ingresos del mes actual
    ingresos_mes = ingresos.filter(fecha__month=mes_actual, fecha__year=anio_actual)

    # Asegurar que total_ingresos_mes sea un número, no None
    total_result = ingresos_mes.aggregate(total=Sum('monto'))['total']
    total_ingresos_mes = Decimal(str(total_result)) if total_result else Decimal('0')

    # Ingresos por tipo
    ingresos_por_tipo = ingresos_mes.values('tipo_ingreso').annotate(
        total=Sum('monto')
    ).order_by('-total')

    # Ingresos por aportante
    ingresos_por_aportante = ingresos_mes.values('aportante__nombre').annotate(
        total=Sum('monto')
    ).order_by('-total')

    context = {
        'familia': familia,
        'ingresos': ingresos,
        'total_ingresos_mes': total_ingresos_mes,
        'ingresos_por_tipo': ingresos_por_tipo,
        'ingresos_por_aportante': ingresos_por_aportante,
        'mes_actual': f"{MESES_ES[timezone.now().month]} {timezone.now().year}",
    }

    return render(request, 'gastos/ingresos/lista_ingresos.html', context)


@login_required
def crear_ingreso(request):
    """Crear un nuevo ingreso"""
    from .models import IngresoAportante
    from .forms import IngresoAportanteForm

    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    if request.method == 'POST':
        form = IngresoAportanteForm(request.POST, familia_id=familia_id)
        if form.is_valid():
            ingreso = form.save()
            messages.success(request, f'Ingreso de {ingreso.aportante.nombre} registrado correctamente.')
            return redirect('lista_ingresos')
    else:
        # Pre-llenar con la fecha actual
        initial_data = {'fecha': timezone.now().date()}
        form = IngresoAportanteForm(familia_id=familia_id, initial=initial_data)

    context = {
        'form': form,
        'titulo': 'Registrar Nuevo Ingreso',
        'boton_texto': 'Guardar Ingreso',
    }

    return render(request, 'gastos/ingresos/form_ingreso.html', context)


@login_required
def editar_ingreso(request, pk):
    """Editar un ingreso existente"""
    from .models import IngresoAportante
    from .forms import IngresoAportanteForm

    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    # Verificar que el ingreso pertenece a la familia del usuario
    ingreso = get_object_or_404(IngresoAportante, pk=pk, aportante__familia_id=familia_id)

    if request.method == 'POST':
        form = IngresoAportanteForm(request.POST, instance=ingreso, familia_id=familia_id)
        if form.is_valid():
            ingreso = form.save()
            messages.success(request, 'Ingreso actualizado correctamente.')
            return redirect('lista_ingresos')
    else:
        form = IngresoAportanteForm(instance=ingreso, familia_id=familia_id)

    context = {
        'form': form,
        'ingreso': ingreso,
        'titulo': 'Editar Ingreso',
        'boton_texto': 'Actualizar Ingreso',
    }

    return render(request, 'gastos/ingresos/form_ingreso.html', context)


@login_required
def eliminar_ingreso(request, pk):
    """Eliminar un ingreso"""
    from .models import IngresoAportante

    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    # Verificar que el ingreso pertenece a la familia del usuario
    ingreso = get_object_or_404(IngresoAportante, pk=pk, aportante__familia_id=familia_id)

    if request.method == 'POST':
        ingreso.delete()
        messages.success(request, 'Ingreso eliminado correctamente.')
        return redirect('lista_ingresos')

    context = {
        'ingreso': ingreso,
    }

    return render(request, 'gastos/ingresos/confirmar_eliminar.html', context)


# ==================== GASTOS PERSONALES ====================

@login_required
def lista_gastos_personales(request):
    """Lista de gastos personales (no compartidos) del usuario"""
    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    familia = get_object_or_404(Familia, id=familia_id)

    # Obtener aportantes de la familia
    aportantes = Aportante.objects.filter(familia_id=familia_id, activo=True)

    # Filtros
    aportante_id = request.GET.get('aportante')
    mes_seleccionado = request.GET.get('mes')
    anio_seleccionado = request.GET.get('anio')

    # Determinar mes y año para filtros
    fecha_actual = timezone.now()
    if mes_seleccionado and anio_seleccionado:
        try:
            mes_filtro = int(mes_seleccionado)
            anio_filtro = int(anio_seleccionado)
        except (ValueError, TypeError):
            mes_filtro = fecha_actual.month
            anio_filtro = fecha_actual.year
    else:
        mes_filtro = fecha_actual.month
        anio_filtro = fecha_actual.year

    # Obtener mes y año actual
    mes_actual = timezone.now().month
    anio_actual = timezone.now().year

    # Obtener solo gastos personales del mes actual
    gastos = Gasto.objects.filter(
        subcategoria__categoria__familia_id=familia_id,
        tipo_gasto='PERSONAL',
        fecha__month=mes_actual,
        fecha__year=anio_actual
    ).select_related('subcategoria__categoria', 'pagado_por')

    # Filtrar por aportante si se especifica
    if aportante_id:
        gastos = gastos.filter(pagado_por_id=aportante_id)

    # Filtrar por mes y año
    gastos_mes = gastos.filter(fecha__month=mes_filtro, fecha__year=anio_filtro)

    # Ordenar
    gastos_mostrar = gastos_mes.order_by('-fecha', '-fecha_registro')

    # Asegurar que total_gastos_mes sea un número, no None
    total_result = gastos_mes.aggregate(total=Sum('monto'))['total']
    total_gastos_mes = Decimal(str(total_result)) if total_result else Decimal('0')

    # Gastos por aportante este mes
    gastos_por_aportante = gastos_mes.values('pagado_por__nombre').annotate(
        total=Sum('monto')
    ).order_by('-total')

    # Gastos por categoría este mes
    gastos_por_categoria = gastos_mes.values('subcategoria__categoria__nombre').annotate(
        total=Sum('monto')
    ).order_by('-total')

    # Generar lista de meses disponibles (últimos 12 meses)
    meses_disponibles = []
    for i in range(12):
        fecha_mes = date(fecha_actual.year, fecha_actual.month, 1) - timedelta(days=30*i)
        meses_disponibles.append({
            'mes': fecha_mes.month,
            'anio': fecha_mes.year,
            'nombre': f"{MESES_ES[fecha_mes.month]} {fecha_mes.year}",
            'seleccionado': (fecha_mes.month == mes_filtro and fecha_mes.year == anio_filtro)
        })

    context = {
        'familia': familia,
        'gastos': gastos_mostrar,
        'aportantes': aportantes,
        'aportante_seleccionado': aportante_id,
        'total_gastos_mes': total_gastos_mes,
        'gastos_por_aportante': gastos_por_aportante,
        'gastos_por_categoria': gastos_por_categoria,
        'mes_actual': f"{MESES_ES[mes_filtro]} {anio_filtro}",
        'mes_seleccionado': mes_filtro,
        'anio_seleccionado': anio_filtro,
        'meses_disponibles': meses_disponibles,
    }

    return render(request, 'gastos/gastos_personales/lista_gastos_personales.html', context)
