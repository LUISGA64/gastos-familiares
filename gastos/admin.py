from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html
from .models import (Aportante, CategoriaGasto, SubcategoriaGasto, Gasto, DistribucionGasto,
                     ConciliacionMensual, DetalleConciliacion, Reintegro, MetaAhorro,
                     PresupuestoCategoria, Notificacion, Pago)


@admin.register(Aportante)
class AportanteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ingreso_mensual_formateado', 'porcentaje_aporte', 'activo', 'fecha_registro']
    list_filter = ['activo', 'fecha_registro']
    search_fields = ['nombre']
    ordering = ['-activo', 'nombre']

    def ingreso_mensual_formateado(self, obj):
        return f"${obj.ingreso_mensual:,.0f}"
    ingreso_mensual_formateado.short_description = "Ingreso Mensual"

    def porcentaje_aporte(self, obj):
        return f"{obj.calcular_porcentaje_aporte():.2f}%"
    porcentaje_aporte.short_description = "% del Total"


class SubcategoriaInline(admin.TabularInline):
    model = SubcategoriaGasto
    extra = 1
    fields = ['nombre', 'tipo', 'monto_estimado', 'activo']


@admin.register(CategoriaGasto)
class CategoriaGastoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'total_subcategorias_display', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']
    inlines = [SubcategoriaInline]

    def total_subcategorias_display(self, obj):
        total = obj.total_subcategorias()
        return f"{total} subcategoría{'s' if total != 1 else ''}"
    total_subcategorias_display.short_description = "Subcategorías"


@admin.register(SubcategoriaGasto)
class SubcategoriaGastoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'tipo', 'monto_estimado_formateado', 'total_gastos', 'activo']
    list_filter = ['tipo', 'activo', 'categoria']
    search_fields = ['nombre', 'descripcion', 'categoria__nombre']
    ordering = ['categoria', 'tipo', 'nombre']

    fieldsets = (
        ('Información Principal', {
            'fields': ('categoria', 'nombre', 'tipo')
        }),
        ('Detalles', {
            'fields': ('monto_estimado', 'descripcion', 'activo')
        }),
    )

    def monto_estimado_formateado(self, obj):
        if obj.monto_estimado:
            return f"${obj.monto_estimado:,.0f}"
        return "No definido"
    monto_estimado_formateado.short_description = "Monto Estimado"

    def total_gastos(self, obj):
        total = obj.gastos.aggregate(Sum('monto'))['monto__sum'] or 0
        return f"${total:,.0f}"
    total_gastos.short_description = "Total Gastado"


class DistribucionGastoInline(admin.TabularInline):
    model = DistribucionGasto
    extra = 0
    readonly_fields = ['monto_asignado']


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ['get_nombre_completo_display', 'descripcion', 'monto_formateado', 'tipo_gasto', 'fecha', 'pagado_por', 'pagado']
    list_filter = ['subcategoria__tipo', 'subcategoria__categoria', 'pagado_por', 'pagado', 'fecha']
    search_fields = ['descripcion', 'observaciones', 'subcategoria__nombre', 'subcategoria__categoria__nombre']
    date_hierarchy = 'fecha'
    ordering = ['-fecha', '-fecha_registro']
    inlines = [DistribucionGastoInline]

    fieldsets = (
        ('Información del Gasto', {
            'fields': ('subcategoria', 'descripcion', 'monto', 'fecha', 'pagado_por')
        }),
        ('Detalles Adicionales', {
            'fields': ('observaciones', 'pagado'),
            'classes': ('collapse',)
        }),
    )

    def get_nombre_completo_display(self, obj):
        return obj.get_nombre_completo()
    get_nombre_completo_display.short_description = "Categoría → Gasto"

    def monto_formateado(self, obj):
        return f"${obj.monto:,.0f}"
    monto_formateado.short_description = "Monto"

    def tipo_gasto(self, obj):
        return obj.get_tipo_gasto()
    tipo_gasto.short_description = "Tipo"


@admin.register(DistribucionGasto)
class DistribucionGastoAdmin(admin.ModelAdmin):
    list_display = ['gasto', 'aportante', 'porcentaje', 'monto_asignado_formateado']
    list_filter = ['aportante', 'gasto__subcategoria__categoria']
    search_fields = ['gasto__descripcion', 'gasto__subcategoria__nombre', 'aportante__nombre']
    ordering = ['-gasto__fecha', 'aportante__nombre']

    def monto_asignado_formateado(self, obj):
        return f"${obj.monto_asignado:,.0f}"
    monto_asignado_formateado.short_description = "Monto Asignado"


class DetalleConciliacionInline(admin.TabularInline):
    model = DetalleConciliacion
    extra = 0
    readonly_fields = ['balance']


class ReintegroInline(admin.TabularInline):
    model = Reintegro
    extra = 0


@admin.register(ConciliacionMensual)
class ConciliacionMensualAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'familia', 'total_gastos_formateado', 'estado', 'fecha_cierre', 'cerrada_por']
    list_filter = ['estado', 'anio', 'mes', 'familia']
    search_fields = ['familia__nombre', 'observaciones']
    ordering = ['-anio', '-mes']
    readonly_fields = ['fecha_creacion', 'fecha_cierre']
    inlines = [DetalleConciliacionInline, ReintegroInline]

    fieldsets = (
        ('Información', {
            'fields': ('familia', 'mes', 'anio', 'total_gastos')
        }),
        ('Estado', {
            'fields': ('estado', 'cerrada_por', 'fecha_creacion', 'fecha_cierre')
        }),
        ('Detalles', {
            'fields': ('observaciones',)
        }),
    )

    def total_gastos_formateado(self, obj):
        return f"${obj.total_gastos:,.0f}"
    total_gastos_formateado.short_description = "Total Gastos"


@admin.register(DetalleConciliacion)
class DetalleConciliacionAdmin(admin.ModelAdmin):
    list_display = ['conciliacion', 'aportante', 'porcentaje_esperado', 'monto_debe_pagar_fmt', 'monto_pago_real_fmt', 'balance_fmt', 'confirmado']
    list_filter = ['confirmado', 'conciliacion__estado']
    search_fields = ['aportante__nombre', 'conciliacion__familia__nombre']
    ordering = ['-conciliacion__anio', '-conciliacion__mes', 'aportante__nombre']

    def monto_debe_pagar_fmt(self, obj):
        return f"${obj.monto_debe_pagar:,.0f}"
    monto_debe_pagar_fmt.short_description = "Debe Pagar"

    def monto_pago_real_fmt(self, obj):
        return f"${obj.monto_pago_real:,.0f}"
    monto_pago_real_fmt.short_description = "Pagó"

    def balance_fmt(self, obj):
        return f"${obj.balance:,.0f}"
    balance_fmt.short_description = "Balance"


@admin.register(Reintegro)
class ReintegroAdmin(admin.ModelAdmin):
    list_display = ['conciliacion', 'de_aportante', 'para_aportante', 'monto_fmt', 'pagado', 'fecha_pago']
    list_filter = ['pagado', 'conciliacion__estado']
    search_fields = ['de_aportante__nombre', 'para_aportante__nombre', 'comprobante']
    ordering = ['-conciliacion__anio', '-conciliacion__mes']

    def monto_fmt(self, obj):
        return f"${obj.monto:,.0f}"
    monto_fmt.short_description = "Monto"


@admin.register(MetaAhorro)
class MetaAhorroAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'familia', 'monto_objetivo_fmt', 'monto_actual_fmt', 'porcentaje_display',
                    'prioridad', 'estado', 'fecha_objetivo', 'dias_restantes_display']
    list_filter = ['estado', 'prioridad', 'familia']
    search_fields = ['nombre', 'descripcion', 'familia__nombre']
    ordering = ['-fecha_objetivo', '-prioridad']
    date_hierarchy = 'fecha_inicio'

    fieldsets = (
        ('Información de la Meta', {
            'fields': ('familia', 'nombre', 'descripcion', 'icono')
        }),
        ('Montos', {
            'fields': ('monto_objetivo', 'monto_actual')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_objetivo')
        }),
        ('Estado', {
            'fields': ('prioridad', 'estado')
        }),
    )

    def monto_objetivo_fmt(self, obj):
        return f"${obj.monto_objetivo:,.0f}"
    monto_objetivo_fmt.short_description = "Objetivo"

    def monto_actual_fmt(self, obj):
        return f"${obj.monto_actual:,.0f}"
    monto_actual_fmt.short_description = "Ahorrado"

    def porcentaje_display(self, obj):
        return f"{obj.porcentaje_completado:.1f}%"
    porcentaje_display.short_description = "% Completado"

    def dias_restantes_display(self, obj):
        dias = obj.dias_restantes
        if dias > 0:
            return f"{dias} días"
        return "Vencida"
    dias_restantes_display.short_description = "Días Restantes"


@admin.register(PresupuestoCategoria)
class PresupuestoCategoriaAdmin(admin.ModelAdmin):
    list_display = ['categoria', 'familia', 'mes_anio_display', 'monto_presupuestado_fmt',
                    'monto_gastado_display', 'porcentaje_usado_display', 'estado_visual', 'activo']
    list_filter = ['activo', 'anio', 'mes', 'familia', 'categoria']
    search_fields = ['categoria__nombre', 'familia__nombre', 'notas']
    ordering = ['-anio', '-mes', 'categoria__nombre']

    fieldsets = (
        ('Información', {
            'fields': ('familia', 'categoria', 'mes', 'anio')
        }),
        ('Presupuesto', {
            'fields': ('monto_presupuestado', 'alertar_en')
        }),
        ('Estado', {
            'fields': ('activo', 'notas')
        }),
    )

    def mes_anio_display(self, obj):
        meses = ['', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        return f"{meses[obj.mes]} {obj.anio}"
    mes_anio_display.short_description = "Período"

    def monto_presupuestado_fmt(self, obj):
        return f"${obj.monto_presupuestado:,.0f}"
    monto_presupuestado_fmt.short_description = "Presupuesto"

    def monto_gastado_display(self, obj):
        return f"${obj.monto_gastado:,.0f}"
    monto_gastado_display.short_description = "Gastado"

    def porcentaje_usado_display(self, obj):
        return f"{obj.porcentaje_usado:.1f}%"
    porcentaje_usado_display.short_description = "% Usado"


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'usuario', 'familia', 'tipo', 'leida', 'importante', 'creada_en']
    list_filter = ['tipo', 'leida', 'importante', 'creada_en']
    search_fields = ['titulo', 'mensaje', 'usuario__username', 'familia__nombre']
    ordering = ['-creada_en']
    date_hierarchy = 'creada_en'

    readonly_fields = ['creada_en', 'leida_en']

    fieldsets = (
        ('Destinatario', {
            'fields': ('usuario', 'familia')
        }),
        ('Contenido', {
            'fields': ('tipo', 'titulo', 'mensaje', 'icono', 'link')
        }),
        ('Estado', {
            'fields': ('leida', 'importante', 'creada_en', 'leida_en')
        }),
    )

    actions = ['marcar_como_leidas', 'marcar_como_no_leidas']

    def marcar_como_leidas(self, request, queryset):
        for notif in queryset:
            notif.marcar_como_leida()
        self.message_user(request, f"{queryset.count()} notificaciones marcadas como leídas.")
    marcar_como_leidas.short_description = "Marcar como leídas"

    def marcar_como_no_leidas(self, request, queryset):
        queryset.update(leida=False, leida_en=None)
        self.message_user(request, f"{queryset.count()} notificaciones marcadas como no leídas.")
    marcar_como_no_leidas.short_description = "Marcar como no leídas"


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['referencia_pago', 'familia', 'plan', 'monto_fmt', 'metodo_pago',
                    'estado_display', 'fecha_pago', 'tiene_comprobante', 'acciones_rapidas']
    list_filter = ['estado', 'metodo_pago', 'plan', 'fecha_pago']
    search_fields = ['referencia_pago', 'familia__nombre', 'numero_transaccion']
    readonly_fields = ['referencia_pago', 'fecha_pago', 'fecha_aprobacion', 'datos_qr',
                       'ver_comprobante']
    ordering = ['-fecha_pago']

    fieldsets = (
        ('Información del Pago', {
            'fields': ('familia', 'plan', 'monto', 'referencia_pago', 'fecha_pago')
        }),
        ('Método de Pago', {
            'fields': ('metodo_pago', 'datos_qr')
        }),
        ('Comprobante', {
            'fields': ('comprobante', 'ver_comprobante', 'numero_transaccion')
        }),
        ('Estado y Verificación', {
            'fields': ('estado', 'verificado_por', 'fecha_aprobacion', 'notas')
        }),
    )

    actions = ['aprobar_pagos', 'rechazar_pagos', 'marcar_verificando']

    def monto_fmt(self, obj):
        return f"${obj.monto:,.0f}"
    monto_fmt.short_description = "Monto"

    def estado_display(self, obj):
        colores = {
            'PENDIENTE': '#95a5a6',
            'VERIFICANDO': '#f39c12',
            'APROBADO': '#27ae60',
            'RECHAZADO': '#e74c3c',
            'REEMBOLSADO': '#3498db'
        }
        color = colores.get(obj.estado, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-weight: bold;">{}</span>',
            color, obj.get_estado_display()
        )
    estado_display.short_description = "Estado"

    def tiene_comprobante(self, obj):
        if obj.comprobante:
            return format_html('<span style="color: green;">✓ Sí</span>')
        return format_html('<span style="color: red;">✗ No</span>')
    tiene_comprobante.short_description = "Comprobante"

    def ver_comprobante(self, obj):
        if obj.comprobante:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-width: 200px; max-height: 200px;"/>'
                '</a>',
                obj.comprobante.url, obj.comprobante.url
            )
        return "Sin comprobante"
    ver_comprobante.short_description = "Vista Previa"

    def acciones_rapidas(self, obj):
        if obj.estado == 'VERIFICANDO':
            return format_html(
                '<a class="button" href="/admin/gastos/pago/{}/change/">Revisar</a>',
                obj.pk
            )
        return "-"
    acciones_rapidas.short_description = "Acciones"

    def aprobar_pagos(self, request, queryset):
        count = 0
        for pago in queryset.filter(estado__in=['PENDIENTE', 'VERIFICANDO']):
            pago.aprobar_pago(verificado_por=request.user)
            pago.save()
            pago.familia.save()
            count += 1
        self.message_user(request, f"{count} pagos aprobados correctamente.")
    aprobar_pagos.short_description = "✓ Aprobar pagos seleccionados"

    def rechazar_pagos(self, request, queryset):
        count = queryset.filter(estado__in=['PENDIENTE', 'VERIFICANDO']).update(
            estado='RECHAZADO',
            verificado_por=request.user,
            notas='Rechazado desde admin'
        )
        self.message_user(request, f"{count} pagos rechazados.")
    rechazar_pagos.short_description = "✗ Rechazar pagos seleccionados"

    def marcar_verificando(self, request, queryset):
        count = queryset.filter(estado='PENDIENTE').update(estado='VERIFICANDO')
        self.message_user(request, f"{count} pagos marcados como 'En Verificación'.")
    marcar_verificando.short_description = "⏳ Marcar como 'En Verificación'"

