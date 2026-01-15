from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class PlanSuscripcion(models.Model):
    """Planes de suscripción para comercializar la aplicación"""
    TIPO_PLAN = [
        ('GRATIS', 'Plan Gratuito'),
        ('BASICO', 'Plan Básico'),
        ('PREMIUM', 'Plan Premium'),
        ('EMPRESARIAL', 'Plan Empresarial'),
    ]

    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre del Plan")
    tipo = models.CharField(max_length=20, choices=TIPO_PLAN, verbose_name="Tipo de Plan")
    precio_mensual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Precio Mensual (COP)"
    )
    max_aportantes = models.IntegerField(
        default=2,
        validators=[MinValueValidator(1)],
        verbose_name="Máximo de Aportantes"
    )
    max_gastos_mes = models.IntegerField(
        default=50,
        validators=[MinValueValidator(1)],
        verbose_name="Máximo de Gastos por Mes"
    )
    max_categorias = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1)],
        verbose_name="Máximo de Categorías"
    )
    dias_prueba = models.IntegerField(
        default=0,
        verbose_name="Días de Prueba Gratis"
    )
    activo = models.BooleanField(default=True, verbose_name="Plan Activo")
    caracteristicas = models.TextField(
        blank=True,
        verbose_name="Características del Plan",
        help_text="Una característica por línea"
    )

    # Características Premium
    permite_reportes_avanzados = models.BooleanField(
        default=False,
        verbose_name="Reportes Avanzados",
        help_text="Gráficos detallados, exportación PDF/Excel, análisis de tendencias"
    )
    permite_conciliacion_automatica = models.BooleanField(
        default=False,
        verbose_name="Conciliación Automática",
        help_text="Cálculo automático de reintegros y distribución"
    )
    permite_notificaciones_email = models.BooleanField(
        default=False,
        verbose_name="Notificaciones por Email",
        help_text="Alertas de vencimientos, recordatorios, resúmenes mensuales"
    )
    permite_historial_completo = models.BooleanField(
        default=False,
        verbose_name="Historial Completo",
        help_text="Acceso ilimitado al historial (Gratis solo 3 meses)"
    )
    permite_exportar_datos = models.BooleanField(
        default=False,
        verbose_name="Exportar Datos",
        help_text="Descargar datos en Excel, PDF, CSV"
    )
    soporte_prioritario = models.BooleanField(
        default=False,
        verbose_name="Soporte Prioritario",
        help_text="Respuesta en menos de 24 horas"
    )
    max_archivos_adjuntos = models.IntegerField(
        default=0,
        verbose_name="Archivos Adjuntos por Gasto",
        help_text="Comprobantes, facturas, recibos (0 = sin adjuntos)"
    )

    class Meta:
        verbose_name = "Plan de Suscripción"
        verbose_name_plural = "Planes de Suscripción"
        ordering = ['precio_mensual']

    def __str__(self):
        return f"{self.nombre} - ${self.precio_mensual:,.0f}/mes"


class Familia(models.Model):
    """Modelo para representar una familia/hogar independiente"""
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la Familia")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    creado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='familias_creadas',
        verbose_name="Creado por"
    )
    miembros = models.ManyToManyField(
        User,
        related_name='familias',
        verbose_name="Miembros con acceso"
    )
    # Suscripción y pago
    plan = models.ForeignKey(
        PlanSuscripcion,
        on_delete=models.PROTECT,
        related_name='familias',
        verbose_name="Plan de Suscripción"
    )
    fecha_inicio_suscripcion = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha Inicio Suscripción"
    )
    fecha_fin_suscripcion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha Fin Suscripción"
    )
    suscripcion_activa = models.BooleanField(
        default=True,
        verbose_name="Suscripción Activa"
    )
    en_periodo_prueba = models.BooleanField(
        default=False,
        verbose_name="En Período de Prueba"
    )
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Familia"
        verbose_name_plural = "Familias"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def puede_acceder(self, user):
        """Verifica si un usuario tiene acceso a esta familia"""
        return user.is_superuser or self.miembros.filter(id=user.id).exists()

    def esta_suscripcion_activa(self):
        """Verifica si la suscripción está activa y no ha expirado"""
        if not self.suscripcion_activa:
            return False

        # Si está en período de prueba
        if self.en_periodo_prueba:
            dias_transcurridos = (timezone.now() - self.fecha_inicio_suscripcion).days
            return dias_transcurridos <= self.plan.dias_prueba

        # Si tiene fecha de fin, verificar que no haya expirado
        if self.fecha_fin_suscripcion:
            return timezone.now() <= self.fecha_fin_suscripcion

        return True

    def dias_restantes_suscripcion(self):
        """Calcula días restantes de suscripción"""
        if self.en_periodo_prueba:
            dias_transcurridos = (timezone.now() - self.fecha_inicio_suscripcion).days
            return max(0, self.plan.dias_prueba - dias_transcurridos)

        if self.fecha_fin_suscripcion:
            dias = (self.fecha_fin_suscripcion - timezone.now()).days
            return max(0, dias)

        return 999  # Suscripción sin límite

    def puede_agregar_aportante(self):
        """Verifica si puede agregar más aportantes según el plan"""
        total_aportantes = self.aportantes.filter(activo=True).count()
        return total_aportantes < self.plan.max_aportantes

    def puede_agregar_categoria(self):
        """Verifica si puede agregar más categorías según el plan"""
        total_categorias = self.categorias.filter(activo=True).count()
        return total_categorias < self.plan.max_categorias

    # Métodos para verificar características premium
    def tiene_reportes_avanzados(self):
        """Verifica si tiene acceso a reportes avanzados"""
        return self.esta_suscripcion_activa() and self.plan.permite_reportes_avanzados

    def tiene_conciliacion_automatica(self):
        """Verifica si tiene conciliación automática"""
        return self.esta_suscripcion_activa() and self.plan.permite_conciliacion_automatica

    def tiene_notificaciones_email(self):
        """Verifica si tiene notificaciones por email"""
        return self.esta_suscripcion_activa() and self.plan.permite_notificaciones_email

    def tiene_historial_completo(self):
        """Verifica si tiene acceso al historial completo"""
        return self.esta_suscripcion_activa() and self.plan.permite_historial_completo

    def tiene_exportar_datos(self):
        """Verifica si puede exportar datos"""
        return self.esta_suscripcion_activa() and self.plan.permite_exportar_datos

    def tiene_soporte_prioritario(self):
        """Verifica si tiene soporte prioritario"""
        return self.esta_suscripcion_activa() and self.plan.soporte_prioritario

    def puede_adjuntar_archivos(self):
        """Verifica si puede adjuntar archivos"""
        return self.esta_suscripcion_activa() and self.plan.max_archivos_adjuntos > 0

    def max_archivos_permitidos(self):
        """Retorna el máximo de archivos adjuntos permitidos"""
        if not self.esta_suscripcion_activa():
            return 0
        return self.plan.max_archivos_adjuntos


class Pago(models.Model):
    """Registro de pagos de suscripciones"""
    ESTADO_PAGO = [
        ('PENDIENTE', 'Pendiente'),
        ('VERIFICANDO', 'En Verificación'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
        ('REEMBOLSADO', 'Reembolsado'),
    ]

    METODO_PAGO = [
        ('TARJETA', 'Tarjeta de Crédito/Débito'),
        ('PSE', 'PSE'),
        ('NEQUI', 'Nequi'),
        ('DAVIPLATA', 'Daviplata'),
        ('BANCOLOMBIA', 'Transferencia Bancolombia'),
        ('EFECTY', 'Efecty'),
        ('BALOTO', 'Baloto'),
        ('QR_BANCOLOMBIA', 'QR Bancolombia'),
        ('QR_NEQUI', 'QR Nequi'),
    ]

    familia = models.ForeignKey(
        Familia,
        on_delete=models.CASCADE,
        related_name='pagos',
        verbose_name="Familia"
    )
    plan = models.ForeignKey(
        PlanSuscripcion,
        on_delete=models.PROTECT,
        verbose_name="Plan"
    )
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Monto (COP)"
    )
    metodo_pago = models.CharField(
        max_length=20,
        choices=METODO_PAGO,
        verbose_name="Método de Pago"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_PAGO,
        default='PENDIENTE',
        verbose_name="Estado del Pago"
    )
    referencia_pago = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Referencia de Pago"
    )
    # Nuevos campos para QR y comprobantes
    comprobante = models.ImageField(
        upload_to='comprobantes/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="Comprobante de Pago"
    )
    numero_transaccion = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Número de Transacción"
    )
    datos_qr = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Datos del QR",
        help_text="Información usada para generar el QR"
    )
    fecha_pago = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Pago")
    fecha_aprobacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Aprobación")
    verificado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Verificado Por"
    )
    notas = models.TextField(blank=True, verbose_name="Notas")

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-fecha_pago']

    def __str__(self):
        return f"{self.familia.nombre} - ${self.monto:,.0f} - {self.estado}"

    def aprobar_pago(self, verificado_por=None):
        """Aprueba el pago y extiende la suscripción"""
        if self.estado in ['PENDIENTE', 'VERIFICANDO']:
            self.estado = 'APROBADO'
            self.fecha_aprobacion = timezone.now()
            if verificado_por:
                self.verificado_por = verificado_por

            # Extender suscripción por 30 días
            if self.familia.fecha_fin_suscripcion:
                self.familia.fecha_fin_suscripcion += timedelta(days=30)
            else:
                self.familia.fecha_fin_suscripcion = timezone.now() + timedelta(days=30)

            self.familia.suscripcion_activa = True
            self.familia.en_periodo_prueba = False
            self.familia.save()
            self.save()


class CodigoInvitacion(models.Model):
    """Códigos de invitación para registro controlado"""
    codigo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Código de Invitación"
    )
    plan = models.ForeignKey(
        PlanSuscripcion,
        on_delete=models.CASCADE,
        verbose_name="Plan Asignado"
    )
    usado = models.BooleanField(default=False, verbose_name="Código Usado")
    usado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usado por"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_uso = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Uso")
    fecha_expiracion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Expiración")
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='codigos_creados',
        verbose_name="Creado por"
    )

    class Meta:
        verbose_name = "Código de Invitación"
        verbose_name_plural = "Códigos de Invitación"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.codigo} - {self.plan.nombre} - {'Usado' if self.usado else 'Disponible'}"

    def esta_valido(self):
        """Verifica si el código es válido"""
        if self.usado:
            return False
        if self.fecha_expiracion and timezone.now() > self.fecha_expiracion:
            return False
        return True

    def marcar_como_usado(self, user):
        """Marca el código como usado"""
        self.usado = True
        self.usado_por = user
        self.fecha_uso = timezone.now()
        self.save()


class Aportante(models.Model):
    """Modelo para representar un aportante de ingresos en la familia"""
    familia = models.ForeignKey(
        Familia,
        on_delete=models.CASCADE,
        related_name='aportantes',
        verbose_name="Familia"
    )
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    email = models.EmailField(blank=True, null=True, verbose_name="Email", help_text="Email para notificaciones y confirmaciones")
    ingreso_mensual = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Ingreso Mensual (COP)"
    )
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_registro = models.DateField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        verbose_name = "Aportante"
        verbose_name_plural = "Aportantes"
        ordering = ['-activo', 'nombre']

    def __str__(self):
        return f"{self.nombre} - ${self.ingreso_mensual:,.0f}"

    def calcular_porcentaje_aporte(self):
        """Calcula el porcentaje que representa el ingreso de este aportante del total"""
        total_ingresos = Aportante.objects.filter(
            familia=self.familia,
            activo=True
        ).aggregate(total=Sum('ingreso_mensual'))['total'] or 0

        if total_ingresos == 0:
            return 0

        return (self.ingreso_mensual / total_ingresos) * 100

    def calcular_aporte_mensual(self):
        """Retorna el ingreso mensual formateado"""
        return self.ingreso_mensual

    def calcular_pagos_realizados(self, mes, anio):
        """Calcula el total de pagos que realizó este aportante en un mes"""
        from django.db.models import Sum
        total_pagado = self.gastos_pagados.filter(
            fecha__month=mes,
            fecha__year=anio
        ).aggregate(total=Sum('monto'))['total'] or 0
        return total_pagado

    def calcular_gastos_asignados(self, mes, anio):
        """Calcula el total de gastos que le corresponden según su porcentaje en un mes"""
        from django.db.models import Sum
        total_asignado = self.distribuciones.filter(
            gasto__fecha__month=mes,
            gasto__fecha__year=anio
        ).aggregate(total=Sum('monto_asignado'))['total'] or 0
        return total_asignado

    def calcular_balance_conciliacion(self, mes, anio):
        """Calcula el balance de conciliación: lo que pagó - lo que le corresponde
        Positivo: pagó de más, debe recibir reintegro
        Negativo: pagó de menos, debe pagar
        """
        pagado = self.calcular_pagos_realizados(mes, anio)
        asignado = self.calcular_gastos_asignados(mes, anio)
        return pagado - asignado


class CategoriaGasto(models.Model):
    """Modelo para categorizar los gastos - Categoría principal (ej: Servicios Públicos, Alimentación)"""
    familia = models.ForeignKey(
        Familia,
        on_delete=models.CASCADE,
        related_name='categorias',
        verbose_name="Familia"
    )
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la Categoría")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateField(auto_now_add=True, null=True, blank=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Categoría de Gasto"
        verbose_name_plural = "Categorías de Gastos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def total_subcategorias(self):
        """Retorna el número de subcategorías activas"""
        return self.subcategorias.filter(activo=True).count()


class SubcategoriaGasto(models.Model):
    """Modelo para subcategorías de gastos específicos dentro de una categoría
    Ejemplo: Dentro de 'Servicios Públicos' -> 'Internet', 'Acueducto', 'Luz', etc.
    """
    TIPO_CHOICES = [
        ('FIJO', 'Gasto Fijo'),
        ('VARIABLE', 'Gasto Variable'),
    ]

    categoria = models.ForeignKey(
        CategoriaGasto,
        on_delete=models.CASCADE,
        related_name='subcategorias',
        verbose_name="Categoría Principal"
    )
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Gasto")
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        verbose_name="Tipo de Gasto",
        help_text="Fijo: monto constante mensual. Variable: depende del consumo o uso."
    )
    monto_estimado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        verbose_name="Monto Estimado (COP)",
        help_text="Monto promedio o estimado mensual (opcional)"
    )
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateField(auto_now_add=True, null=True, blank=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Subcategoría de Gasto"
        verbose_name_plural = "Subcategorías de Gastos"
        ordering = ['categoria', 'tipo', 'nombre']
        unique_together = ['categoria', 'nombre']

    def __str__(self):
        return f"{self.categoria.nombre} → {self.nombre} ({self.get_tipo_display()})"

    def get_tipo_badge_class(self):
        """Retorna la clase CSS para el badge según el tipo"""
        return 'badge-fijo' if self.tipo == 'FIJO' else 'badge-variable'


class Gasto(models.Model):
    """Modelo para registrar los gastos del hogar"""
    subcategoria = models.ForeignKey(
        SubcategoriaGasto,
        on_delete=models.PROTECT,
        related_name='gastos',
        verbose_name="Tipo de Gasto"
    )
    descripcion = models.CharField(
        max_length=200,
        verbose_name="Descripción",
        blank=True,
        help_text="Descripción adicional (opcional, ej: 'Factura de enero')"
    )
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Monto (COP)"
    )
    fecha = models.DateField(verbose_name="Fecha del Gasto")
    pagado_por = models.ForeignKey(
        Aportante,
        on_delete=models.PROTECT,
        related_name='gastos_pagados',
        verbose_name="Pagado por",
        help_text="Aportante que realizó el pago de este gasto"
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    pagado = models.BooleanField(default=False, verbose_name="Pagado")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"
        ordering = ['-fecha', '-fecha_registro']

    def __str__(self):
        if self.descripcion:
            return f"{self.subcategoria.nombre} - {self.descripcion} - ${self.monto:,.0f} ({self.fecha})"
        return f"{self.subcategoria.nombre} - ${self.monto:,.0f} ({self.fecha})"

    def get_tipo_gasto(self):
        """Retorna el tipo de gasto (Fijo o Variable)"""
        return self.subcategoria.get_tipo_display()

    def get_categoria_principal(self):
        """Retorna la categoría principal"""
        return self.subcategoria.categoria.nombre

    def get_nombre_completo(self):
        """Retorna el nombre completo: Categoría → Subcategoría"""
        return f"{self.subcategoria.categoria.nombre} → {self.subcategoria.nombre}"


class DistribucionGasto(models.Model):
    """Modelo para registrar cómo se distribuye cada gasto entre los aportantes"""
    gasto = models.ForeignKey(
        Gasto,
        on_delete=models.CASCADE,
        related_name='distribuciones',
        verbose_name="Gasto"
    )
    aportante = models.ForeignKey(
        Aportante,
        on_delete=models.PROTECT,
        related_name='distribuciones',
        verbose_name="Aportante"
    )
    porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Porcentaje (%)"
    )
    monto_asignado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Monto Asignado (COP)"
    )

    class Meta:
        verbose_name = "Distribución de Gasto"
        verbose_name_plural = "Distribuciones de Gastos"
        unique_together = ['gasto', 'aportante']

    def __str__(self):
        return f"{self.aportante.nombre} - {self.porcentaje}% de {self.gasto.descripcion}"

    def save(self, *args, **kwargs):
        """Calcula automáticamente el monto asignado basado en el porcentaje"""
        if self.gasto and self.porcentaje:
            self.monto_asignado = (self.gasto.monto * self.porcentaje) / 100
        super().save(*args, **kwargs)


class ConciliacionMensual(models.Model):
    """Modelo para registrar conciliaciones mensuales cerradas"""
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('CERRADA', 'Cerrada'),
        ('CANCELADA', 'Cancelada'),
    ]

    familia = models.ForeignKey(
        Familia,
        on_delete=models.CASCADE,
        related_name='conciliaciones',
        verbose_name="Familia"
    )
    mes = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name="Mes"
    )
    anio = models.IntegerField(
        validators=[MinValueValidator(2020)],
        verbose_name="Año"
    )
    total_gastos = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Total de Gastos del Mes"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE',
        verbose_name="Estado"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_cierre = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Cierre")
    cerrada_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conciliaciones_cerradas',
        verbose_name="Cerrada por"
    )
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")

    class Meta:
        verbose_name = "Conciliación Mensual"
        verbose_name_plural = "Conciliaciones Mensuales"
        ordering = ['-anio', '-mes']
        unique_together = ['familia', 'mes', 'anio']

    def __str__(self):
        meses = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        return f"{self.familia.nombre} - {meses[self.mes]} {self.anio} ({self.estado})"

    def cerrar_conciliacion(self, user):
        """Cierra la conciliación"""
        self.estado = 'CERRADA'
        self.fecha_cierre = timezone.now()
        self.cerrada_por = user
        self.save()


class DetalleConciliacion(models.Model):
    """Detalle de cada aportante en una conciliación"""
    conciliacion = models.ForeignKey(
        ConciliacionMensual,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name="Conciliación"
    )
    aportante = models.ForeignKey(
        Aportante,
        on_delete=models.CASCADE,
        related_name='detalles_conciliacion',
        verbose_name="Aportante"
    )
    porcentaje_esperado = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="% Esperado"
    )
    monto_debe_pagar = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Monto que Debe Pagar"
    )
    monto_pago_real = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Monto que Pagó Realmente"
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Balance (Pagó - Debe)"
    )
    confirmado = models.BooleanField(default=False, verbose_name="Confirmado por el Aportante")
    fecha_confirmacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Confirmación")
    codigo_confirmacion = models.CharField(max_length=6, blank=True, verbose_name="Código de Confirmación")
    email_enviado = models.BooleanField(default=False, verbose_name="Email Enviado")
    fecha_envio_email = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Envío de Email")

    class Meta:
        verbose_name = "Detalle de Conciliación"
        verbose_name_plural = "Detalles de Conciliación"
        unique_together = ['conciliacion', 'aportante']

    def __str__(self):
        return f"{self.aportante.nombre} - {self.conciliacion}"

    def generar_codigo_confirmacion(self):
        """Genera un código de confirmación de 6 dígitos"""
        import random
        self.codigo_confirmacion = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        self.save()
        return self.codigo_confirmacion


class Reintegro(models.Model):
    """Registro de reintegros necesarios en una conciliación"""
    conciliacion = models.ForeignKey(
        ConciliacionMensual,
        on_delete=models.CASCADE,
        related_name='reintegros',
        verbose_name="Conciliación"
    )
    de_aportante = models.ForeignKey(
        Aportante,
        on_delete=models.CASCADE,
        related_name='reintegros_debe_pagar',
        verbose_name="De (Quien Debe Pagar)"
    )
    para_aportante = models.ForeignKey(
        Aportante,
        on_delete=models.CASCADE,
        related_name='reintegros_debe_recibir',
        verbose_name="Para (Quien Debe Recibir)"
    )
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Monto a Reintegrar"
    )
    pagado = models.BooleanField(default=False, verbose_name="Reintegro Pagado")
    fecha_pago = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Pago")
    comprobante = models.CharField(max_length=200, blank=True, verbose_name="Comprobante/Referencia")

    class Meta:
        verbose_name = "Reintegro"
        verbose_name_plural = "Reintegros"

    def __str__(self):
        return f"{self.de_aportante.nombre} → {self.para_aportante.nombre}: ${self.monto:,.0f}"


class MetaAhorro(models.Model):
    """Metas de ahorro de la familia"""
    PRIORIDAD_CHOICES = [
        ('ALTA', 'Alta'),
        ('MEDIA', 'Media'),
        ('BAJA', 'Baja'),
    ]

    ESTADO_CHOICES = [
        ('ACTIVA', 'Activa'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    ]

    familia = models.ForeignKey(
        'Familia',
        on_delete=models.CASCADE,
        related_name='metas_ahorro',
        verbose_name="Familia"
    )
    nombre = models.CharField(max_length=200, verbose_name="Nombre de la Meta")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    monto_objetivo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Monto Objetivo"
    )
    monto_actual = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Monto Ahorrado Actual"
    )
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_objetivo = models.DateField(verbose_name="Fecha Objetivo")
    prioridad = models.CharField(
        max_length=10,
        choices=PRIORIDAD_CHOICES,
        default='MEDIA',
        verbose_name="Prioridad"
    )
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='ACTIVA',
        verbose_name="Estado"
    )
    icono = models.CharField(
        max_length=50,
        default='piggy-bank',
        verbose_name="Icono",
        help_text="Nombre del ícono de Bootstrap Icons (ej: piggy-bank, house, car, etc.)"
    )
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")

    class Meta:
        verbose_name = "Meta de Ahorro"
        verbose_name_plural = "Metas de Ahorro"
        ordering = ['-fecha_objetivo', '-prioridad']

    def __str__(self):
        return f"{self.nombre} - ${self.monto_objetivo:,.0f}"

    @property
    def porcentaje_completado(self):
        """Calcula el porcentaje de la meta completado"""
        if self.monto_objetivo > 0:
            return (self.monto_actual / self.monto_objetivo) * 100
        return 0

    @property
    def monto_restante(self):
        """Calcula cuánto falta para completar la meta"""
        return max(0, self.monto_objetivo - self.monto_actual)

    @property
    def dias_restantes(self):
        """Calcula días restantes para la fecha objetivo"""
        from datetime import date
        if self.fecha_objetivo > date.today():
            return (self.fecha_objetivo - date.today()).days
        return 0

    def agregar_ahorro(self, monto):
        """Agrega un monto al ahorro actual"""
        self.monto_actual += monto
        if self.monto_actual >= self.monto_objetivo:
            self.estado = 'COMPLETADA'
        self.save()


class PresupuestoCategoria(models.Model):
    """Presupuesto mensual por categoría"""
    familia = models.ForeignKey(
        'Familia',
        on_delete=models.CASCADE,
        related_name='presupuestos',
        verbose_name="Familia"
    )
    categoria = models.ForeignKey(
        CategoriaGasto,
        on_delete=models.CASCADE,
        related_name='presupuestos',
        verbose_name="Categoría"
    )
    monto_presupuestado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Monto Presupuestado"
    )
    mes = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name="Mes"
    )
    anio = models.IntegerField(verbose_name="Año")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    alertar_en = models.IntegerField(
        default=80,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name="Alertar al %",
        help_text="Porcentaje del presupuesto para enviar alerta (ej: 80 para alertar al 80%)"
    )
    notas = models.TextField(blank=True, verbose_name="Notas")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")

    class Meta:
        verbose_name = "Presupuesto de Categoría"
        verbose_name_plural = "Presupuestos de Categorías"
        ordering = ['-anio', '-mes', 'categoria__nombre']
        unique_together = ['familia', 'categoria', 'mes', 'anio']

    def __str__(self):
        return f"{self.categoria.nombre} - {self.mes}/{self.anio} - ${self.monto_presupuestado:,.0f}"

    @property
    def monto_gastado(self):
        """Calcula cuánto se ha gastado en esta categoría en el mes/año"""
        total = Gasto.objects.filter(
            categoria=self.categoria,
            fecha__month=self.mes,
            fecha__year=self.anio
        ).aggregate(total=Sum('monto'))['total'] or 0
        return total

    @property
    def monto_disponible(self):
        """Calcula cuánto queda disponible del presupuesto"""
        return max(0, self.monto_presupuestado - self.monto_gastado)

    @property
    def porcentaje_usado(self):
        """Calcula el porcentaje del presupuesto usado"""
        if self.monto_presupuestado > 0:
            return (self.monto_gastado / self.monto_presupuestado) * 100
        return 0

    @property
    def esta_en_alerta(self):
        """Verifica si se alcanzó el porcentaje de alerta"""
        return self.porcentaje_usado >= self.alertar_en

    @property
    def esta_excedido(self):
        """Verifica si se excedió el presupuesto"""
        return self.monto_gastado > self.monto_presupuestado

    @property
    def estado_visual(self):
        """Retorna un estado visual para mostrar en la UI"""
        if self.esta_excedido:
            return 'danger'  # Rojo
        elif self.esta_en_alerta:
            return 'warning'  # Amarillo
        elif self.porcentaje_usado > 50:
            return 'info'  # Azul
        else:
            return 'success'  # Verde


class Notificacion(models.Model):
    """Sistema de notificaciones para usuarios"""
    TIPO_CHOICES = [
        ('GASTO', 'Gasto Registrado'),
        ('PRESUPUESTO_ALERTA', 'Alerta de Presupuesto'),
        ('PRESUPUESTO_EXCEDIDO', 'Presupuesto Excedido'),
        ('META_LOGRADA', 'Meta Alcanzada'),
        ('META_PROGRESO', 'Progreso de Meta'),
        ('CONCILIACION', 'Conciliación Disponible'),
        ('REINTEGRO', 'Reintegro Pendiente'),
        ('SUSCRIPCION', 'Información de Suscripción'),
        ('SISTEMA', 'Notificación del Sistema'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notificaciones',
        verbose_name="Usuario"
    )
    familia = models.ForeignKey(
        'Familia',
        on_delete=models.CASCADE,
        related_name='notificaciones',
        verbose_name="Familia",
        null=True,
        blank=True
    )
    tipo = models.CharField(
        max_length=30,
        choices=TIPO_CHOICES,
        verbose_name="Tipo de Notificación"
    )
    titulo = models.CharField(max_length=200, verbose_name="Título")
    mensaje = models.TextField(verbose_name="Mensaje")
    leida = models.BooleanField(default=False, verbose_name="Leída")
    importante = models.BooleanField(default=False, verbose_name="Importante")
    link = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Enlace",
        help_text="URL relacionada con la notificación"
    )
    icono = models.CharField(
        max_length=50,
        default='bell',
        verbose_name="Icono",
        help_text="Nombre del ícono de Bootstrap Icons"
    )
    creada_en = models.DateTimeField(auto_now_add=True, verbose_name="Creada en")
    leida_en = models.DateTimeField(null=True, blank=True, verbose_name="Leída en")

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-creada_en']

    def __str__(self):
        return f"{self.usuario.username} - {self.titulo}"

    def marcar_como_leida(self):
        """Marca la notificación como leída"""
        if not self.leida:
            self.leida = True
            self.leida_en = timezone.now()
            self.save()


