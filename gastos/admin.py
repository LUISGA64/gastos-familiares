from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html
from .models import (Aportante, CategoriaGasto, SubcategoriaGasto, Gasto, DistribucionGasto,
                     ConciliacionMensual, DetalleConciliacion, Reintegro, MetaAhorro,
                     PresupuestoCategoria, Notificacion, Pago, PerfilUsuario, Logro,
                     LogroDesbloqueado, DesafioMensual, ParticipacionDesafio,
                     HistorialPuntos, NotificacionLogro, ConversacionChatbot,
                     MensajeChatbot, AnalisisIA, ConfiguracionCuentaPago, InvitacionFamilia,
                     Familia, PlanSuscripcion, CodigoInvitacion, PasswordResetToken)


@admin.register(InvitacionFamilia)
class InvitacionFamiliaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'familia', 'creado_por', 'estado', 'usos_actuales', 'usos_maximos', 'fecha_creacion', 'fecha_expiracion']
    list_filter = ['estado', 'fecha_creacion', 'fecha_expiracion']
    search_fields = ['codigo', 'familia__nombre', 'email_invitado']
    readonly_fields = ['codigo', 'fecha_creacion', 'fecha_uso', 'usos_actuales']
    ordering = ['-fecha_creacion']

    fieldsets = (
        ('Información Básica', {
            'fields': ('familia', 'codigo', 'creado_por', 'estado')
        }),
        ('Detalles de la Invitación', {
            'fields': ('email_invitado', 'mensaje_invitacion')
        }),
        ('Configuración', {
            'fields': ('usos_maximos', 'usos_actuales', 'fecha_expiracion')
        }),
        ('Uso', {
            'fields': ('usado_por', 'fecha_uso'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Las invitaciones se crean desde la interfaz web
        return False


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

    def estado_visual(self, obj):
        """Indicador visual del estado del presupuesto"""
        porcentaje = obj.porcentaje_usado

        if porcentaje >= 100:
            color = '#e74c3c'  # Rojo - excedido
            estado = 'Excedido'
            icono = '🔴'
        elif porcentaje >= obj.alertar_en:
            color = '#f39c12'  # Naranja - alerta
            estado = 'Alerta'
            icono = '⚠️'
        elif porcentaje >= 50:
            color = '#3498db'  # Azul - en progreso
            estado = 'OK'
            icono = '🔵'
        else:
            color = '#27ae60'  # Verde - bien
            estado = 'Bien'
            icono = '🟢'

        return format_html(
            '<span style="color: {};">{} {}</span>',
            color, icono, estado
        )
    estado_visual.short_description = "Estado"


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
                    'estado', 'fecha_pago']
    list_filter = ['estado', 'metodo_pago', 'plan', 'fecha_pago']
    search_fields = ['referencia_pago', 'familia__nombre', 'numero_transaccion']
    readonly_fields = ['referencia_pago', 'fecha_pago', 'fecha_aprobacion', 'datos_qr',
                       'ver_comprobante', 'expira_en', 'intentos_subida', 'ip_origen', 'firma_qr']
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
        ('Seguridad', {
            'fields': ('expira_en', 'intentos_subida', 'max_intentos', 'ip_origen', 'firma_qr'),
            'classes': ('collapse',)
        }),
    )

    actions = ['aprobar_pagos', 'rechazar_pagos', 'marcar_verificando']

    def monto_fmt(self, obj):
        return f"${obj.monto:,.0f}"
    monto_fmt.short_description = "Monto"

    def estado_display(self, obj):
        if not obj or not obj.estado:
            return "-"

        colores = {
            'PENDIENTE': '#95a5a6',
            'VERIFICANDO': '#f39c12',
            'APROBADO': '#27ae60',
            'RECHAZADO': '#e74c3c',
            'REEMBOLSADO': '#3498db'
        }
        color = colores.get(obj.estado, '#95a5a6')
        estado_texto = obj.get_estado_display() if hasattr(obj, 'get_estado_display') else obj.estado

        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-weight: bold;">{}</span>',
            color, estado_texto
        )
    estado_display.short_description = "Estado"

    def tiene_comprobante(self, obj):
        if obj.comprobante:
            return format_html('<span style="color: green;">&#10003; Sí</span>')
        return format_html('<span style="color: red;">&#10007; No</span>')
    tiene_comprobante.short_description = "Comprobante"

    def ver_comprobante(self, obj):
        if obj and obj.comprobante:
            try:
                return format_html(
                    '<a href="{}" target="_blank">'
                    '<img src="{}" style="max-width: 200px; max-height: 200px;"/>'
                    '</a>',
                    obj.comprobante.url, obj.comprobante.url
                )
            except Exception:
                return "Error al cargar comprobante"
        return "Sin comprobante"
    ver_comprobante.short_description = "Vista Previa"

    def acciones_rapidas(self, obj):
        if obj and obj.estado == 'VERIFICANDO' and obj.pk:
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


# ==================== GAMIFICACIÓN ====================

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['user', 'nivel', 'puntos_totales', 'racha_actual', 'mejor_racha', 'total_gastos_registrados']
    list_filter = ['nivel']
    search_fields = ['user__username', 'user__email']
    ordering = ['-puntos_totales']
    readonly_fields = ['fecha_registro_app', 'ultima_actividad']

    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Gamificación', {
            'fields': ('puntos_totales', 'nivel', 'experiencia_nivel_actual')
        }),
        ('Estadísticas', {
            'fields': ('total_gastos_registrados', 'total_ahorrado', 'visitas_dashboard')
        }),
        ('Racha', {
            'fields': ('racha_actual', 'mejor_racha', 'dias_consecutivos')
        }),
        ('Fechas', {
            'fields': ('fecha_registro_app', 'ultima_actividad')
        }),
    )


@admin.register(Logro)
class LogroAdmin(admin.ModelAdmin):
    list_display = ['icono_display', 'nombre', 'tipo', 'puntos_recompensa', 'requisito_numero', 'requisito_tipo', 'activo', 'es_secreto']
    list_filter = ['tipo', 'activo', 'es_secreto']
    search_fields = ['nombre', 'descripcion', 'codigo']
    ordering = ['tipo', 'puntos_recompensa']

    def icono_display(self, obj):
        return format_html('<span style="font-size: 24px;">{}</span>', obj.icono)
    icono_display.short_description = 'Icono'

    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'descripcion', 'tipo', 'icono')
        }),
        ('Recompensa', {
            'fields': ('puntos_recompensa',)
        }),
        ('Requisitos', {
            'fields': ('requisito_tipo', 'requisito_numero')
        }),
        ('Configuración', {
            'fields': ('activo', 'es_secreto')
        }),
    )


@admin.register(LogroDesbloqueado)
class LogroDesbloqueadoAdmin(admin.ModelAdmin):
    list_display = ['perfil', 'logro_display', 'fecha_desbloqueo', 'visto']
    list_filter = ['visto', 'fecha_desbloqueo', 'logro__tipo']
    search_fields = ['perfil__user__username', 'logro__nombre']
    ordering = ['-fecha_desbloqueo']
    readonly_fields = ['fecha_desbloqueo']

    def logro_display(self, obj):
        return format_html('{} {}', obj.logro.icono, obj.logro.nombre)
    logro_display.short_description = 'Logro'


@admin.register(DesafioMensual)
class DesafioMensualAdmin(admin.ModelAdmin):
    list_display = ['icono_display', 'nombre', 'mes', 'anio', 'estado', 'puntos_premio']
    list_filter = ['estado', 'anio', 'mes']
    search_fields = ['nombre', 'descripcion']
    ordering = ['-anio', '-mes']

    def icono_display(self, obj):
        return format_html('<span style="font-size: 24px;">{}</span>', obj.icono)
    icono_display.short_description = 'Icono'


@admin.register(ParticipacionDesafio)
class ParticipacionDesafioAdmin(admin.ModelAdmin):
    list_display = ['perfil', 'desafio', 'progreso_porcentaje', 'completado', 'fecha_inicio']
    list_filter = ['completado', 'fecha_inicio']
    search_fields = ['perfil__user__username', 'desafio__nombre']
    ordering = ['-fecha_inicio']


@admin.register(HistorialPuntos)
class HistorialPuntosAdmin(admin.ModelAdmin):
    list_display = ['perfil', 'puntos', 'razon', 'fecha']
    list_filter = ['fecha']
    search_fields = ['perfil__user__username', 'razon']
    ordering = ['-fecha']
    readonly_fields = ['fecha']


@admin.register(NotificacionLogro)
class NotificacionLogroAdmin(admin.ModelAdmin):
    list_display = ['perfil', 'tipo', 'mensaje_corto', 'visto', 'fecha']
    list_filter = ['tipo', 'visto', 'fecha']
    search_fields = ['perfil__user__username', 'mensaje']
    ordering = ['-fecha']
    readonly_fields = ['fecha']

    def mensaje_corto(self, obj):
        return obj.mensaje[:50] + '...' if len(obj.mensaje) > 50 else obj.mensaje
    mensaje_corto.short_description = 'Mensaje'


# ==================== CHATBOT IA ====================

class MensajeChatbotInline(admin.TabularInline):
    model = MensajeChatbot
    extra = 0
    readonly_fields = ['role', 'contenido', 'fecha', 'tokens_usados']
    can_delete = False
    max_num = 10

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ConversacionChatbot)
class ConversacionChatbotAdmin(admin.ModelAdmin):
    list_display = ['user', 'familia', 'titulo_corto', 'total_mensajes', 'activa', 'iniciada_en', 'actualizada_en']
    list_filter = ['activa', 'iniciada_en', 'familia']
    search_fields = ['user__username', 'titulo']
    ordering = ['-actualizada_en']
    readonly_fields = ['iniciada_en', 'actualizada_en']
    inlines = [MensajeChatbotInline]

    def titulo_corto(self, obj):
        return obj.titulo[:50] + '...' if len(obj.titulo) > 50 else obj.titulo
    titulo_corto.short_description = 'Título'

    def total_mensajes(self, obj):
        return obj.mensajes.count()
    total_mensajes.short_description = 'Mensajes'


@admin.register(MensajeChatbot)
class MensajeChatbotAdmin(admin.ModelAdmin):
    list_display = ['conversacion', 'role', 'contenido_corto', 'tokens_usados', 'fecha']
    list_filter = ['role', 'fecha']
    search_fields = ['conversacion__titulo', 'contenido']
    ordering = ['-fecha']
    readonly_fields = ['fecha']

    def contenido_corto(self, obj):
        return obj.contenido[:80] + '...' if len(obj.contenido) > 80 else obj.contenido
    contenido_corto.short_description = 'Contenido'


@admin.register(AnalisisIA)
class AnalisisIAAdmin(admin.ModelAdmin):
    list_display = ['user', 'familia', 'tipo', 'titulo_corto', 'relevancia', 'visto', 'fecha_generacion']
    list_filter = ['tipo', 'visto', 'relevancia', 'fecha_generacion']
    search_fields = ['user__username', 'titulo', 'contenido']
    ordering = ['-fecha_generacion']
    readonly_fields = ['fecha_generacion']

    fieldsets = (
        ('Usuario', {
            'fields': ('user', 'familia')
        }),
        ('Análisis', {
            'fields': ('tipo', 'titulo', 'contenido', 'relevancia')
        }),
        ('Datos Adicionales', {
            'fields': ('datos_json',),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('visto', 'fecha_generacion')
        }),
    )

    def titulo_corto(self, obj):
        return obj.titulo[:60] + '...' if len(obj.titulo) > 60 else obj.titulo
    titulo_corto.short_description = 'Título'


@admin.register(ConfiguracionCuentaPago)
class ConfiguracionCuentaPagoAdmin(admin.ModelAdmin):
    list_display = ['metodo', 'nombre_banco', 'numero_cuenta', 'titular', 'activo', 'actualizado_en']
    list_filter = ['metodo', 'activo', 'tipo_cuenta']
    search_fields = ['nombre_banco', 'numero_cuenta', 'titular']
    ordering = ['metodo']

    fieldsets = (
        ('Información General', {
            'fields': ('metodo', 'activo', 'nombre_banco', 'tipo_cuenta')
        }),
        ('Datos de la Cuenta', {
            'fields': ('numero_cuenta', 'titular', 'nit')
        }),
        ('Personalización', {
            'fields': ('color', 'icono', 'instrucciones')
        }),
    )

    readonly_fields = ('creado_en', 'actualizado_en')

    def activo_badge(self, obj):
        if not obj:
            return "-"
        if obj.activo:
            return format_html('<span style="color: green;">&#10003; Activo</span>')
        return format_html('<span style="color: red;">&#10007; Inactivo</span>')
    activo_badge.short_description = 'Estado'


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token_preview', 'created_at', 'expires_at', 'used_badge', 'valid_badge']
    list_filter = ['used', 'created_at', 'expires_at']
    search_fields = ['user__username', 'user__email', 'token']
    readonly_fields = ['user', 'token', 'created_at', 'expires_at', 'used', 'used_at', 'ip_address']
    ordering = ['-created_at']

    def token_preview(self, obj):
        """Muestra los primeros y últimos caracteres del token"""
        if len(obj.token) > 16:
            return f"{obj.token[:8]}...{obj.token[-8:]}"
        return obj.token
    token_preview.short_description = 'Token'

    def used_badge(self, obj):
        if obj.used:
            return format_html('<span style="color: red;">✓ Usado</span>')
        return format_html('<span style="color: green;">○ Disponible</span>')
    used_badge.short_description = 'Estado'

    def valid_badge(self, obj):
        if obj.is_valid():
            return format_html('<span style="color: green;">✓ Válido</span>')
        return format_html('<span style="color: gray;">✗ Expirado/Usado</span>')
    valid_badge.short_description = 'Validez'

    def has_add_permission(self, request):
        # Los tokens se generan automáticamente
        return False

    def has_change_permission(self, request, obj=None):
        # Los tokens no se pueden modificar
        return False

