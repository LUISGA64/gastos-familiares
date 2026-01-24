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
from .models import Aportante, CategoriaGasto, SubcategoriaGasto, Gasto, DistribucionGasto, MetaAhorro, Familia
from .forms import AportanteForm, CategoriaGastoForm, SubcategoriaGastoForm, GastoForm, MetaAhorroForm, AgregarAhorroForm


@login_required
def dashboard(request):
    """Vista principal con resumen de gastos e ingresos - Versión Premium"""
    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    # Obtener objeto familia
    familia = Familia.objects.get(id=familia_id)

    # Obtener aportantes activos de la familia
    aportantes = Aportante.objects.filter(familia_id=familia_id, activo=True)
    total_ingresos = aportantes.aggregate(total=Sum('ingreso_mensual'))['total'] or 0

    # Calcular gastos del mes actual
    mes_actual = timezone.now().month
    anio_actual = timezone.now().year

    gastos_mes = Gasto.objects.filter(
        subcategoria__categoria__familia_id=familia_id,
        fecha__month=mes_actual,
        fecha__year=anio_actual
    )

    total_gastos_mes = gastos_mes.aggregate(total=Sum('monto'))['total'] or 0
    gastos_fijos_mes = gastos_mes.filter(subcategoria__tipo='FIJO').aggregate(total=Sum('monto'))['total'] or 0
    gastos_variables_mes = gastos_mes.filter(subcategoria__tipo='VARIABLE').aggregate(total=Sum('monto'))['total'] or 0

    # Calcular balance
    balance = total_ingresos - total_gastos_mes

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

        # Etiqueta del mes
        meses_labels.append(fecha.strftime('%b %Y'))

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

    context = {
        'familia': familia,
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

    # GAMIFICACIÓN: Registrar visita al dashboard
    try:
        from .gamificacion_service import GamificacionService
        GamificacionService.registrar_visita_dashboard(request.user)

        # Obtener notificaciones no vistas
        notificaciones_logros = GamificacionService.obtener_notificaciones_no_vistas(request.user)
        context['notificaciones_logros'] = notificaciones_logros
    except Exception as e:
        print(f"Error en gamificación: {e}")

    # PREFERENCIAS DE PRIVACIDAD
    try:
        from .models import PreferenciasUsuario
        preferencias, created = PreferenciasUsuario.objects.get_or_create(usuario=request.user)
        context['ocultar_valores'] = preferencias.ocultar_valores_monetarios
    except Exception as e:
        print(f"Error al obtener preferencias: {e}")
        context['ocultar_valores'] = False

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

    gastos = Gasto.objects.filter(subcategoria__categoria__familia_id=familia_id).select_related('subcategoria__categoria')

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

    categorias = CategoriaGasto.objects.filter(familia_id=familia_id, activo=True)
    subcategorias = SubcategoriaGasto.objects.filter(categoria__familia_id=familia_id, activo=True).select_related('categoria')

    context = {
        'gastos': gastos,
        'total': total,
        'categorias': categorias,
        'subcategorias': subcategorias,
    }

    return render(request, 'gastos/gastos_lista.html', context)


@login_required
def crear_gasto(request):
    """Crear un nuevo gasto"""
    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    if request.method == 'POST':
        form = GastoForm(request.POST, familia_id=familia_id)
        if form.is_valid():
            gasto = form.save()
            # La familia se determina automáticamente por la subcategoría seleccionada

            # Si se marcó distribuir automáticamente
            if form.cleaned_data.get('distribuir_automaticamente'):
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
                messages.success(request, f'Gasto "{gasto.subcategoria.nombre}" creado exitosamente.')

            # GAMIFICACIÓN: Registrar gasto creado
            try:
                from .gamificacion_service import GamificacionService
                GamificacionService.registrar_gasto_creado(request.user)
            except Exception as e:
                # No detener el flujo si falla la gamificación
                print(f"Error en gamificación: {e}")

            return redirect('lista_gastos')
        else:
            # Mostrar errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en {field}: {error}')
    else:
        form = GastoForm(initial={'fecha': timezone.now().date()}, familia_id=familia_id)

    return render(request, 'gastos/gasto_form.html', {'form': form, 'titulo': 'Nuevo Gasto'})


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
    mes = request.GET.get('mes', timezone.now().month)
    anio = request.GET.get('anio', timezone.now().year)

    # Gastos del período de la familia
    gastos_periodo = Gasto.objects.filter(
        subcategoria__categoria__familia_id=familia_id,
        fecha__month=mes,
        fecha__year=anio
    )

    # Totales
    total_gastos = gastos_periodo.aggregate(total=Sum('monto'))['total'] or 0
    gastos_fijos = gastos_periodo.filter(subcategoria__tipo='FIJO').aggregate(total=Sum('monto'))['total'] or 0
    gastos_variables = gastos_periodo.filter(subcategoria__tipo='VARIABLE').aggregate(total=Sum('monto'))['total'] or 0

    # Ingresos totales de la familia
    total_ingresos = Aportante.objects.filter(familia_id=familia_id, activo=True).aggregate(total=Sum('ingreso_mensual'))['total'] or 0

    # Distribución por aportante
    aportantes_con_gastos = []
    for aportante in Aportante.objects.filter(familia_id=familia_id, activo=True):
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

    # Gastos por categoría principal de la familia
    gastos_por_categoria = CategoriaGasto.objects.filter(
        familia_id=familia_id,
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


@login_required
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

    # Calcular balance
    balance = total_ingresos - total_gastos_mes

    context = {
        'mes': mes,
        'anio': anio,
        'total_ingresos': total_ingresos,
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



