from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import json
from .models import Aportante, CategoriaGasto, SubcategoriaGasto, Gasto, DistribucionGasto
from .forms import AportanteForm, CategoriaGastoForm, SubcategoriaGastoForm, GastoForm


def dashboard(request):
    """Vista principal con resumen de gastos e ingresos - Versión Premium"""
    # Obtener aportantes activos
    aportantes = Aportante.objects.filter(activo=True)
    total_ingresos = aportantes.aggregate(total=Sum('ingreso_mensual'))['total'] or 0

    # Calcular gastos del mes actual
    mes_actual = timezone.now().month
    anio_actual = timezone.now().year

    gastos_mes = Gasto.objects.filter(
        fecha__month=mes_actual,
        fecha__year=anio_actual
    )

    total_gastos_mes = gastos_mes.aggregate(total=Sum('monto'))['total'] or 0
    gastos_fijos_mes = gastos_mes.filter(subcategoria__tipo='FIJO').aggregate(total=Sum('monto'))['total'] or 0
    gastos_variables_mes = gastos_mes.filter(subcategoria__tipo='VARIABLE').aggregate(total=Sum('monto'))['total'] or 0

    # Calcular balance
    balance = total_ingresos - total_gastos_mes

    # Gastos por categoría principal
    gastos_por_categoria = CategoriaGasto.objects.filter(
        subcategorias__gastos__fecha__month=mes_actual,
        subcategorias__gastos__fecha__year=anio_actual
    ).annotate(
        total=Sum('subcategorias__gastos__monto'),
        cantidad=Count('subcategorias__gastos')
    ).order_by('-total')[:5]

    # Últimos gastos
    ultimos_gastos = Gasto.objects.all().order_by('-fecha', '-fecha_registro')[:10]

    # ========== DATOS PARA GRÁFICOS ==========

    # Histórico de 6 meses para gráfico de tendencia
    meses_labels = []
    ingresos_historico = []
    gastos_historico = []

    for i in range(5, -1, -1):
        fecha = timezone.now() - timedelta(days=30*i)
        mes = fecha.month
        anio = fecha.year

        # Etiqueta del mes
        meses_labels.append(fecha.strftime('%b %Y'))

        # Ingresos (asumimos constantes, pero se puede mejorar)
        ingresos_historico.append(float(total_ingresos) if total_ingresos else 0)

        # Gastos del mes
        gastos_del_mes = Gasto.objects.filter(
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

    context = {
        'aportantes': aportantes,
        'total_ingresos': total_ingresos,
        'total_gastos_mes': total_gastos_mes,
        'gastos_fijos_mes': gastos_fijos_mes,
        'gastos_variables_mes': gastos_variables_mes,
        'balance': balance,
        'gastos_por_categoria': gastos_por_categoria,
        'ultimos_gastos': ultimos_gastos,
        'gastos_recientes': ultimos_gastos,
        'mes_actual': timezone.now().strftime('%B %Y'),

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

    return render(request, 'gastos/dashboard_premium.html', context)


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

    context = {
        'aportantes': aportantes,
        'total_ingresos': total_ingresos,
        'hay_aportantes_sin_email': hay_aportantes_sin_email,
    }
    return render(request, 'gastos/aportantes_lista.html', context)


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


def editar_aportante(request, pk):
    """Editar un aportante existente"""
    aportante = get_object_or_404(Aportante, pk=pk)

    if request.method == 'POST':
        form = AportanteForm(request.POST, instance=aportante)
        if form.is_valid():
            aportante = form.save()
            messages.success(request, f'Aportante "{aportante.nombre}" actualizado exitosamente.')
            return redirect('lista_aportantes')
    else:
        form = AportanteForm(instance=aportante)

    return render(request, 'gastos/aportante_form.html', {'form': form, 'titulo': 'Editar Aportante'})


def lista_categorias(request):
    """Lista de categorías de gastos con sus subcategorías"""
    categorias = CategoriaGasto.objects.prefetch_related('subcategorias').all()
    return render(request, 'gastos/categorias_lista.html', {'categorias': categorias})


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


def lista_subcategorias(request):
    """Lista de subcategorías de gastos"""
    subcategorias = SubcategoriaGasto.objects.select_related('categoria').all()
    return render(request, 'gastos/subcategorias_lista.html', {'subcategorias': subcategorias})


def crear_subcategoria(request):
    """Crear una nueva subcategoría"""
    if request.method == 'POST':
        form = SubcategoriaGastoForm(request.POST)
        if form.is_valid():
            subcategoria = form.save()
            messages.success(request, f'Subcategoría "{subcategoria.nombre}" creada exitosamente en "{subcategoria.categoria.nombre}".')
            return redirect('lista_subcategorias')
    else:
        form = SubcategoriaGastoForm()

    return render(request, 'gastos/subcategoria_form.html', {'form': form, 'titulo': 'Nueva Subcategoría'})


def editar_subcategoria(request, pk):
    """Editar una subcategoría existente"""
    subcategoria = get_object_or_404(SubcategoriaGasto, pk=pk)

    if request.method == 'POST':
        form = SubcategoriaGastoForm(request.POST, instance=subcategoria)
        if form.is_valid():
            subcategoria = form.save()
            messages.success(request, f'Subcategoría "{subcategoria.nombre}" actualizada exitosamente.')
            return redirect('lista_subcategorias')
    else:
        form = SubcategoriaGastoForm(instance=subcategoria)

    return render(request, 'gastos/subcategoria_form.html', {'form': form, 'titulo': 'Editar Subcategoría'})


def lista_gastos(request):
    """Lista de todos los gastos con filtros"""
    gastos = Gasto.objects.all().select_related('subcategoria__categoria')

    # Filtros
    tipo = request.GET.get('tipo')
    categoria_id = request.GET.get('categoria')
    subcategoria_id = request.GET.get('subcategoria')
    mes = request.GET.get('mes')
    anio = request.GET.get('anio')

    if tipo:
        gastos = gastos.filter(subcategoria__tipo=tipo)
    if categoria_id:
        gastos = gastos.filter(subcategoria__categoria_id=categoria_id)
    if subcategoria_id:
        gastos = gastos.filter(subcategoria_id=subcategoria_id)
    if mes and anio:
        gastos = gastos.filter(fecha__month=mes, fecha__year=anio)
    elif anio:
        gastos = gastos.filter(fecha__year=anio)

    # Totales
    total = gastos.aggregate(total=Sum('monto'))['total'] or 0

    categorias = CategoriaGasto.objects.filter(activo=True)
    subcategorias = SubcategoriaGasto.objects.filter(activo=True).select_related('categoria')

    context = {
        'gastos': gastos,
        'total': total,
        'categorias': categorias,
        'subcategorias': subcategorias,
    }

    return render(request, 'gastos/gastos_lista.html', context)


def crear_gasto(request):
    """Crear un nuevo gasto"""
    if request.method == 'POST':
        form = GastoForm(request.POST)
        if form.is_valid():
            gasto = form.save()

            # Si se marcó distribuir automáticamente
            if form.cleaned_data.get('distribuir_automaticamente'):
                aportantes_activos = Aportante.objects.filter(activo=True)

                for aportante in aportantes_activos:
                    porcentaje = aportante.calcular_porcentaje_aporte()
                    DistribucionGasto.objects.create(
                        gasto=gasto,
                        aportante=aportante,
                        porcentaje=porcentaje
                    )

                messages.success(request, f'Gasto "{gasto.subcategoria.nombre}" creado y distribuido automáticamente.')
            else:
                messages.success(request, f'Gasto "{gasto.subcategoria.nombre}" creado exitosamente.')

            return redirect('lista_gastos')
        else:
            # Mostrar errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en {field}: {error}')
    else:
        form = GastoForm(initial={'fecha': timezone.now().date()})

    return render(request, 'gastos/gasto_form.html', {'form': form, 'titulo': 'Nuevo Gasto'})


def editar_gasto(request, pk):
    """Editar un gasto existente"""
    gasto = get_object_or_404(Gasto, pk=pk)

    if request.method == 'POST':
        form = GastoForm(request.POST, instance=gasto)
        if form.is_valid():
            gasto = form.save()
            messages.success(request, f'Gasto "{gasto.descripcion}" actualizado exitosamente.')
            return redirect('lista_gastos')
    else:
        form = GastoForm(instance=gasto)

    return render(request, 'gastos/gasto_form.html', {'form': form, 'titulo': 'Editar Gasto'})


def detalle_gasto(request, pk):
    """Ver detalle de un gasto incluyendo su distribución"""
    gasto = get_object_or_404(Gasto, pk=pk)
    distribuciones = gasto.distribuciones.all().select_related('aportante')

    context = {
        'gasto': gasto,
        'distribuciones': distribuciones,
    }

    return render(request, 'gastos/gasto_detalle.html', context)


def reportes(request):
    """Vista de reportes y estadísticas"""
    # Parámetros de fecha
    mes = request.GET.get('mes', timezone.now().month)
    anio = request.GET.get('anio', timezone.now().year)

    # Gastos del período
    gastos_periodo = Gasto.objects.filter(
        fecha__month=mes,
        fecha__year=anio
    )

    # Totales
    total_gastos = gastos_periodo.aggregate(total=Sum('monto'))['total'] or 0
    gastos_fijos = gastos_periodo.filter(subcategoria__tipo='FIJO').aggregate(total=Sum('monto'))['total'] or 0
    gastos_variables = gastos_periodo.filter(subcategoria__tipo='VARIABLE').aggregate(total=Sum('monto'))['total'] or 0

    # Ingresos totales
    total_ingresos = Aportante.objects.filter(activo=True).aggregate(total=Sum('ingreso_mensual'))['total'] or 0

    # Distribución por aportante
    aportantes_con_gastos = []
    for aportante in Aportante.objects.filter(activo=True):
        total_asignado = DistribucionGasto.objects.filter(
            aportante=aportante,
            gasto__fecha__month=mes,
            gasto__fecha__year=anio
        ).aggregate(total=Sum('monto_asignado'))['total'] or 0

        aportantes_con_gastos.append({
            'aportante': aportante,
            'total_asignado': total_asignado,
            'ingreso': aportante.ingreso_mensual,
            'balance': aportante.ingreso_mensual - total_asignado,
        })

    # Gastos por categoría principal
    gastos_por_categoria = CategoriaGasto.objects.filter(
        subcategorias__gastos__fecha__month=mes,
        subcategorias__gastos__fecha__year=anio
    ).annotate(
        total=Sum('subcategorias__gastos__monto'),
        cantidad=Count('subcategorias__gastos', distinct=True)
    ).order_by('-total')

    context = {
        'mes': mes,
        'anio': anio,
        'total_gastos': total_gastos,
        'gastos_fijos': gastos_fijos,
        'gastos_variables': gastos_variables,
        'total_ingresos': total_ingresos,
        'balance': total_ingresos - total_gastos,
        'aportantes_con_gastos': aportantes_con_gastos,
        'gastos_por_categoria': gastos_por_categoria,
    }

    return render(request, 'gastos/reportes.html', context)


def conciliacion(request):
    """Vista de conciliación de gastos mensuales"""
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
    total_ingresos = aportantes.aggregate(total=Sum('ingreso_mensual'))['total'] or 0

    # Calcular total de gastos del mes de la familia
    total_gastos_mes = Gasto.objects.filter(
        subcategoria__categoria__familia_id=familia_id,
        fecha__month=mes,
        fecha__year=anio
    ).aggregate(total=Sum('monto'))['total'] or 0

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

    # Detalles de pagos por aportante
    detalles_pagos = {}
    for aportante in aportantes:
        gastos_pagados = Gasto.objects.filter(
            subcategoria__categoria__familia_id=familia_id,
            pagado_por=aportante,
            fecha__month=mes,
            fecha__year=anio
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

    context = {
        'mes': mes,
        'anio': anio,
        'total_ingresos': total_ingresos,
        'total_gastos_mes': total_gastos_mes,
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
            return redirect('conciliacion')

        total_ingresos = aportantes.aggregate(total=Sum('ingreso_mensual'))['total'] or 0
        total_gastos_mes = Gasto.objects.filter(
            subcategoria__categoria__familia=familia,
            fecha__month=mes,
            fecha__year=anio
        ).aggregate(total=Sum('monto'))['total'] or 0

        conciliacion.total_gastos = total_gastos_mes
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

    return redirect('conciliacion')


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
            return redirect('conciliacion')

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
            # Todos confirmaron, cerrar automáticamente
            conciliacion.cerrar_conciliacion(request.user if request.user.is_authenticated else None)

            # Enviar notificación de cierre
            enviar_notificacion_conciliacion_cerrada(conciliacion)

            messages.success(
                request,
                f'🎉 <strong>¡Conciliación Cerrada!</strong><br>'
                f'Todos los aportantes ({confirmados}/{total_detalles}) han confirmado.<br>'
                f'La conciliación de {conciliacion} ha sido cerrada exitosamente.<br>'
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

    return redirect('conciliacion')


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


