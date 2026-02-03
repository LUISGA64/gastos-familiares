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

    # Campos de seguridad
    expira_en = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Expira En",
        help_text="Fecha de expiración del QR (24 horas por defecto)"
    )
    intentos_subida = models.IntegerField(
        default=0,
        verbose_name="Intentos de Subida",
        help_text="Número de veces que se intentó subir comprobante"
    )
    max_intentos = models.IntegerField(
        default=5,
        verbose_name="Máximo de Intentos",
        help_text="Máximo número de intentos permitidos"
    )
    ip_origen = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP de Origen",
        help_text="IP desde donde se generó el pago"
    )
    firma_qr = models.CharField(
        max_length=64,
        blank=True,
        verbose_name="Firma del QR",
        help_text="Firma digital para validar integridad"
    )
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

    def esta_expirado(self):
        """Verifica si el QR está expirado"""
        if not self.expira_en:
            return False
        return timezone.now() > self.expira_en

    def puede_subir_comprobante(self):
        """Verifica si puede subir más comprobantes"""
        if self.estado in ['APROBADO', 'RECHAZADO']:
            return False
        if self.esta_expirado():
            return False
        if self.intentos_subida >= self.max_intentos:
            return False
        return True

    def registrar_intento_subida(self):
        """Registra un intento de subida de comprobante"""
        self.intentos_subida += 1
        self.save(update_fields=['intentos_subida'])

    def generar_firma(self):
        """Genera firma digital del QR para validar integridad"""
        import hashlib
        import hmac
        from django.conf import settings

        # Usar SECRET_KEY de Django como clave
        secret = settings.SECRET_KEY.encode()
        mensaje = f"{self.referencia_pago}{self.monto}{self.familia_id}{self.plan_id}".encode()

        firma = hmac.new(secret, mensaje, hashlib.sha256).hexdigest()
        return firma

    def validar_firma(self, firma_recibida):
        """Valida la firma del QR"""
        firma_esperada = self.generar_firma()
        return hmac.compare_digest(firma_esperada, firma_recibida)

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


class InvitacionFamilia(models.Model):
    """Invitaciones para que usuarios se unan a una familia existente"""
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('ACEPTADA', 'Aceptada'),
        ('RECHAZADA', 'Rechazada'),
        ('EXPIRADA', 'Expirada'),
    ]

    familia = models.ForeignKey(
        Familia,
        on_delete=models.CASCADE,
        related_name='invitaciones',
        verbose_name="Familia"
    )
    codigo = models.CharField(
        max_length=12,
        unique=True,
        verbose_name="Código de Invitación",
        help_text="Código único para unirse a la familia"
    )
    creado_por = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='invitaciones_creadas',
        verbose_name="Creado por"
    )
    usado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invitaciones_usadas',
        verbose_name="Usado por"
    )
    email_invitado = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Email del Invitado",
        help_text="Email opcional del usuario invitado"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE',
        verbose_name="Estado"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    fecha_expiracion = models.DateTimeField(
        verbose_name="Fecha de Expiración",
        help_text="Fecha hasta la cual el código es válido"
    )
    fecha_uso = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Uso"
    )
    mensaje_invitacion = models.TextField(
        blank=True,
        verbose_name="Mensaje de Invitación",
        help_text="Mensaje personalizado para el invitado"
    )
    usos_maximos = models.IntegerField(
        default=1,
        verbose_name="Usos Máximos",
        help_text="Número máximo de veces que puede usarse el código (0 = ilimitado)"
    )
    usos_actuales = models.IntegerField(
        default=0,
        verbose_name="Usos Actuales"
    )

    class Meta:
        verbose_name = "Invitación a Familia"
        verbose_name_plural = "Invitaciones a Familias"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Invitación a {self.familia.nombre} - {self.codigo} ({self.get_estado_display()})"

    def esta_valido(self):
        """Verifica si el código de invitación es válido"""
        # Verificar si está expirado
        if timezone.now() > self.fecha_expiracion:
            if self.estado == 'PENDIENTE':
                self.estado = 'EXPIRADA'
                self.save()
            return False

        # Verificar estado
        if self.estado != 'PENDIENTE':
            return False

        # Verificar usos máximos
        if self.usos_maximos > 0 and self.usos_actuales >= self.usos_maximos:
            return False

        return True

    def usar_invitacion(self, user):
        """Marca la invitación como usada y agrega el usuario a la familia"""
        from django.db import transaction

        with transaction.atomic():
            # Agregar usuario a la familia
            self.familia.miembros.add(user)

            # Actualizar invitación
            self.usos_actuales += 1
            self.usado_por = user
            self.fecha_uso = timezone.now()

            # Si alcanzó el máximo de usos, marcar como aceptada
            if self.usos_maximos > 0 and self.usos_actuales >= self.usos_maximos:
                self.estado = 'ACEPTADA'

            self.save()

            return True

    def generar_codigo_unico():
        """Genera un código único de 8 caracteres"""
        import random
        import string

        while True:
            codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not InvitacionFamilia.objects.filter(codigo=codigo).exists():
                return codigo


class PreferenciasUsuario(models.Model):
    """Preferencias de privacidad y visualización del usuario"""
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='preferencias',
        verbose_name="Usuario"
    )
    ocultar_valores_monetarios = models.BooleanField(
        default=False,
        verbose_name="Ocultar Valores Monetarios",
        help_text="Cuando está activo, los valores se muestran como ****"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Preferencias de Usuario"
        verbose_name_plural = "Preferencias de Usuarios"

    def __str__(self):
        return f"Preferencias de {self.usuario.username}"


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
        return f"{self.nombre}"

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
        """Calcula el total de pagos que realizó este aportante en un mes (solo gastos compartidos)"""
        from django.db.models import Sum
        total_pagado = self.gastos_pagados.filter(
            fecha__month=mes,
            fecha__year=anio,
            tipo_gasto='COMPARTIDO'  # Solo gastos compartidos
        ).aggregate(total=Sum('monto'))['total'] or 0
        return total_pagado

    def calcular_gastos_asignados(self, mes, anio):
        """Calcula el total de gastos que le corresponden según su porcentaje en un mes (solo gastos compartidos)"""
        from django.db.models import Sum
        total_asignado = self.distribuciones.filter(
            gasto__fecha__month=mes,
            gasto__fecha__year=anio,
            gasto__tipo_gasto='COMPARTIDO'  # Solo gastos compartidos
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


class IngresoAportante(models.Model):
    """Modelo para registrar ingresos de cada aportante (salarios, bonos, etc.)"""
    TIPO_INGRESO_CHOICES = [
        ('SALARIO', 'Salario'),
        ('BONO', 'Bono/Prima'),
        ('COMISION', 'Comisión'),
        ('FREELANCE', 'Trabajo Freelance'),
        ('INVERSION', 'Rendimiento Inversión'),
        ('ARRIENDO', 'Arriendo'),
        ('PENSION', 'Pensión'),
        ('SUBSIDIO', 'Subsidio'),
        ('OTRO', 'Otro Ingreso'),
    ]

    aportante = models.ForeignKey(
        Aportante,
        on_delete=models.CASCADE,
        related_name='ingresos',
        verbose_name="Aportante"
    )
    tipo_ingreso = models.CharField(
        max_length=20,
        choices=TIPO_INGRESO_CHOICES,
        default='SALARIO',
        verbose_name="Tipo de Ingreso"
    )
    descripcion = models.CharField(
        max_length=200,
        verbose_name="Descripción",
        blank=True,
        help_text="Descripción adicional (opcional)"
    )
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Monto (COP)"
    )
    fecha = models.DateField(verbose_name="Fecha del Ingreso")
    recurrente = models.BooleanField(
        default=False,
        verbose_name="Recurrente",
        help_text="Marcar si es un ingreso mensual recurrente"
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Ingreso de Aportante"
        verbose_name_plural = "Ingresos de Aportantes"
        ordering = ['-fecha', '-fecha_registro']

    def __str__(self):
        if self.descripcion:
            return f"{self.get_tipo_ingreso_display()} - {self.descripcion} - ${self.monto:,.0f} ({self.fecha})"
        return f"{self.get_tipo_ingreso_display()} - ${self.monto:,.0f} ({self.fecha})"


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
    TIPO_GASTO_CHOICES = [
        ('COMPARTIDO', 'Gasto Compartido'),
        ('PERSONAL', 'Gasto Personal'),
    ]

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

    # Campos de Soft Delete
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Eliminación",
        help_text="Si tiene valor, el registro está eliminado (soft delete)"
    )
    deleted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gastos_eliminados',
        verbose_name="Eliminado por"
    )
    pagado_por = models.ForeignKey(
        Aportante,
        on_delete=models.PROTECT,
        related_name='gastos_pagados',
        verbose_name="Pagado por",
        help_text="Aportante que realizó el pago de este gasto"
    )
    tipo_gasto = models.CharField(
        max_length=20,
        choices=TIPO_GASTO_CHOICES,
        default='COMPARTIDO',
        verbose_name="Tipo de Gasto",
        help_text="Compartido: se distribuye entre aportantes. Personal: solo afecta al pagador"
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    pagado = models.BooleanField(default=False, verbose_name="Pagado")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    # Manager personalizado para soft delete
    objects = models.Manager()  # Manager por defecto (incluye eliminados)

    class ActiveManager(models.Manager):
        """Manager que solo devuelve registros no eliminados"""
        def get_queryset(self):
            return super().get_queryset().filter(deleted_at__isnull=True)

    active = ActiveManager()  # Manager para registros activos

    class DeletedManager(models.Manager):
        """Manager que solo devuelve registros eliminados"""
        def get_queryset(self):
            return super().get_queryset().filter(deleted_at__isnull=False)

    deleted = DeletedManager()  # Manager para registros eliminados

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

    def soft_delete(self, user):
        """Marca el gasto como eliminado (soft delete) sin borrarlo de la BD"""
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save()

        # Registrar en audit log
        from .models import AuditLog
        AuditLog.registrar(
            usuario=user,
            accion='DELETE',
            modelo='Gasto',
            objeto_id=self.id,
            descripcion=f'Gasto eliminado (soft delete): {self}',
            familia=self.subcategoria.categoria.familia
        )

    def restore(self, user):
        """Restaura un gasto eliminado"""
        self.deleted_at = None
        self.deleted_by = None
        self.save()

        # Registrar en audit log
        from .models import AuditLog
        AuditLog.registrar(
            usuario=user,
            accion='UPDATE',
            modelo='Gasto',
            objeto_id=self.id,
            descripcion=f'Gasto restaurado: {self}',
            familia=self.subcategoria.categoria.familia
        )

    @property
    def is_deleted(self):
        """Verifica si el gasto está eliminado"""
        return self.deleted_at is not None


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


# ==================== GAMIFICACIÓN ====================

class PerfilUsuario(models.Model):
    """Perfil extendido del usuario con gamificación"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_gamificacion')

    # Gamificación
    puntos_totales = models.IntegerField(default=0, verbose_name="Puntos Totales")
    nivel = models.IntegerField(default=1, verbose_name="Nivel")
    experiencia_nivel_actual = models.IntegerField(default=0, verbose_name="Experiencia en Nivel Actual")

    # Estadísticas
    dias_consecutivos = models.IntegerField(default=0, verbose_name="Días Consecutivos")
    ultima_actividad = models.DateField(auto_now=True, verbose_name="Última Actividad")
    fecha_registro_app = models.DateField(auto_now_add=True, verbose_name="Fecha de Registro")
    total_gastos_registrados = models.IntegerField(default=0, verbose_name="Total Gastos Registrados")
    total_ahorrado = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total Ahorrado")

    # Racha
    racha_actual = models.IntegerField(default=0, verbose_name="Racha Actual")
    mejor_racha = models.IntegerField(default=0, verbose_name="Mejor Racha")

    # Visitas
    visitas_dashboard = models.IntegerField(default=0, verbose_name="Visitas al Dashboard")

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"

    def __str__(self):
        return f"{self.user.username} - Nivel {self.nivel} ({self.puntos_totales} pts)"

    def calcular_nivel(self):
        """Calcula nivel basado en puntos"""
        niveles = {
            1: 0, 2: 100, 3: 300, 4: 600, 5: 1000,
            6: 1500, 7: 2100, 8: 2800, 9: 3600, 10: 5000
        }
        for nivel, puntos_req in sorted(niveles.items(), reverse=True):
            if self.puntos_totales >= puntos_req:
                return nivel
        return 1

    def agregar_puntos(self, puntos, razon):
        """Agrega puntos y registra el logro"""
        self.puntos_totales += puntos
        nivel_anterior = self.nivel
        self.nivel = self.calcular_nivel()
        self.save()

        # Registrar historial
        HistorialPuntos.objects.create(
            perfil=self,
            puntos=puntos,
            razon=razon
        )

        # Si subió de nivel, crear notificación
        if self.nivel > nivel_anterior:
            NotificacionLogro.objects.create(
                perfil=self,
                tipo='NIVEL',
                mensaje=f'¡Felicitaciones! Alcanzaste el nivel {self.nivel}'
            )

    def get_puntos_siguiente_nivel(self):
        """Retorna puntos necesarios para el siguiente nivel"""
        niveles = {
            1: 0, 2: 100, 3: 300, 4: 600, 5: 1000,
            6: 1500, 7: 2100, 8: 2800, 9: 3600, 10: 5000
        }
        siguiente = self.nivel + 1
        if siguiente in niveles:
            return niveles[siguiente] - self.puntos_totales
        return 0


class Logro(models.Model):
    """Catálogo de logros disponibles"""
    TIPO_LOGRO = [
        ('ACTIVIDAD', 'Actividad Diaria'),
        ('AHORRO', 'Ahorro'),
        ('DISCIPLINA', 'Disciplina Financiera'),
        ('SOCIAL', 'Social'),
        ('ESPECIAL', 'Especial'),
    ]

    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código")
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    descripcion = models.TextField(verbose_name="Descripción")
    tipo = models.CharField(max_length=20, choices=TIPO_LOGRO, verbose_name="Tipo")
    puntos_recompensa = models.IntegerField(default=10, verbose_name="Puntos de Recompensa")
    icono = models.CharField(max_length=50, default='🏆', verbose_name="Icono")
    requisito_numero = models.IntegerField(default=1, help_text="Ej: 7 días, 3 meses, $50000", verbose_name="Requisito Numérico")
    requisito_tipo = models.CharField(max_length=50, help_text="dias_consecutivos, meses_cumplidos, monto_ahorrado", verbose_name="Tipo de Requisito")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    es_secreto = models.BooleanField(default=False, verbose_name="Es Secreto")

    class Meta:
        verbose_name = "Logro"
        verbose_name_plural = "Logros"
        ordering = ['tipo', 'puntos_recompensa']

    def __str__(self):
        return f"{self.icono} {self.nombre} ({self.puntos_recompensa} pts)"


class LogroDesbloqueado(models.Model):
    """Logros que ha desbloqueado cada usuario"""
    perfil = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name='logros')
    logro = models.ForeignKey(Logro, on_delete=models.CASCADE)
    fecha_desbloqueo = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Desbloqueo")
    visto = models.BooleanField(default=False, verbose_name="Visto")

    class Meta:
        unique_together = ('perfil', 'logro')
        ordering = ['-fecha_desbloqueo']
        verbose_name = "Logro Desbloqueado"
        verbose_name_plural = "Logros Desbloqueados"

    def __str__(self):
        return f"{self.perfil.user.username} - {self.logro.nombre}"


class DesafioMensual(models.Model):
    """Desafíos especiales cada mes"""
    ESTADO = [
        ('ACTIVO', 'Activo'),
        ('FINALIZADO', 'Finalizado'),
        ('PROXIMO', 'Próximo'),
    ]

    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    descripcion = models.TextField(verbose_name="Descripción")
    mes = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], verbose_name="Mes")
    anio = models.IntegerField(verbose_name="Año")
    icono = models.CharField(max_length=50, default='🎯', verbose_name="Icono")
    puntos_premio = models.IntegerField(default=150, verbose_name="Puntos de Premio")

    # Requisitos
    meta_reduccion_categoria = models.CharField(max_length=50, blank=True, verbose_name="Categoría a Reducir")
    meta_porcentaje = models.IntegerField(default=0, verbose_name="Porcentaje de Reducción")
    meta_monto = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Monto Meta")

    estado = models.CharField(max_length=20, choices=ESTADO, default='PROXIMO', verbose_name="Estado")

    class Meta:
        verbose_name = "Desafío Mensual"
        verbose_name_plural = "Desafíos Mensuales"
        ordering = ['-anio', '-mes']

    def __str__(self):
        return f"{self.icono} {self.nombre} ({self.mes}/{self.anio})"


class ParticipacionDesafio(models.Model):
    """Participación de usuarios en desafíos"""
    perfil = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE)
    desafio = models.ForeignKey(DesafioMensual, on_delete=models.CASCADE)
    completado = models.BooleanField(default=False, verbose_name="Completado")
    progreso_porcentaje = models.IntegerField(default=0, verbose_name="Progreso (%)")
    fecha_inicio = models.DateField(auto_now_add=True, verbose_name="Fecha de Inicio")
    fecha_completado = models.DateField(null=True, blank=True, verbose_name="Fecha de Completado")

    class Meta:
        unique_together = ('perfil', 'desafio')
        verbose_name = "Participación en Desafío"
        verbose_name_plural = "Participaciones en Desafíos"

    def __str__(self):
        return f"{self.perfil.user.username} - {self.desafio.nombre}"


class HistorialPuntos(models.Model):
    """Historial de puntos ganados"""
    perfil = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name='historial_puntos')
    puntos = models.IntegerField(verbose_name="Puntos")
    razon = models.CharField(max_length=200, verbose_name="Razón")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    class Meta:
        ordering = ['-fecha']
        verbose_name = "Historial de Puntos"
        verbose_name_plural = "Historial de Puntos"

    def __str__(self):
        return f"{self.perfil.user.username} - {self.puntos} pts - {self.razon}"


class NotificacionLogro(models.Model):
    """Notificaciones de logros y niveles"""
    TIPO = [
        ('LOGRO', 'Logro Desbloqueado'),
        ('NIVEL', 'Subida de Nivel'),
        ('DESAFIO', 'Desafío Completado'),
        ('RACHA', 'Racha Alcanzada'),
    ]

    perfil = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name='notificaciones_logro')
    tipo = models.CharField(max_length=20, choices=TIPO, verbose_name="Tipo")
    mensaje = models.CharField(max_length=200, verbose_name="Mensaje")
    visto = models.BooleanField(default=False, verbose_name="Visto")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    class Meta:
        ordering = ['-fecha']
        verbose_name = "Notificación de Logro"
        verbose_name_plural = "Notificaciones de Logros"

    def __str__(self):
        return f"{self.perfil.user.username} - {self.tipo} - {self.mensaje[:30]}"


# ==================== CHATBOT IA ====================

class ConversacionChatbot(models.Model):
    """Conversaciones del chatbot con usuarios"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversaciones_chatbot')
    familia = models.ForeignKey(
        'Familia',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Familia"
    )
    titulo = models.CharField(max_length=200, verbose_name="Título de la Conversación")
    iniciada_en = models.DateTimeField(auto_now_add=True, verbose_name="Iniciada en")
    actualizada_en = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    activa = models.BooleanField(default=True, verbose_name="Conversación Activa")

    class Meta:
        verbose_name = "Conversación Chatbot"
        verbose_name_plural = "Conversaciones Chatbot"
        ordering = ['-actualizada_en']

    def __str__(self):
        return f"{self.user.username} - {self.titulo[:50]}"

    def get_contexto_reciente(self, limite=10):
        """Obtiene los últimos mensajes para contexto"""
        mensajes = self.mensajes.order_by('-fecha')[:limite]
        return reversed(list(mensajes))


class MensajeChatbot(models.Model):
    """Mensajes individuales en una conversación"""
    ROLE_CHOICES = [
        ('user', 'Usuario'),
        ('assistant', 'Asistente'),
        ('system', 'Sistema'),
    ]

    conversacion = models.ForeignKey(
        ConversacionChatbot,
        on_delete=models.CASCADE,
        related_name='mensajes',
        verbose_name="Conversación"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name="Rol")
    contenido = models.TextField(verbose_name="Contenido del Mensaje")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
    tokens_usados = models.IntegerField(default=0, verbose_name="Tokens Usados")

    class Meta:
        verbose_name = "Mensaje Chatbot"
        verbose_name_plural = "Mensajes Chatbot"
        ordering = ['fecha']

    def __str__(self):
        return f"{self.role} - {self.contenido[:50]}..."


class AnalisisIA(models.Model):
    """Análisis generados por IA para el usuario"""
    TIPO_ANALISIS = [
        ('AHORRO', 'Oportunidades de Ahorro'),
        ('PATRON', 'Patrones de Gasto'),
        ('PREDICCION', 'Predicción de Gastos'),
        ('RECOMENDACION', 'Recomendación Personalizada'),
        ('ALERTA', 'Alerta Financiera'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analisis_ia')
    familia = models.ForeignKey(
        'Familia',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Familia"
    )
    tipo = models.CharField(max_length=20, choices=TIPO_ANALISIS, verbose_name="Tipo de Análisis")
    titulo = models.CharField(max_length=200, verbose_name="Título")
    contenido = models.TextField(verbose_name="Contenido del Análisis")
    datos_json = models.JSONField(null=True, blank=True, verbose_name="Datos Adicionales")
    fecha_generacion = models.DateTimeField(auto_now_add=True, verbose_name="Generado en")
    visto = models.BooleanField(default=False, verbose_name="Visto por Usuario")
    relevancia = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Relevancia (1-10)"
    )

    class Meta:
        verbose_name = "Análisis IA"
        verbose_name_plural = "Análisis IA"
        ordering = ['-fecha_generacion']

    def __str__(self):
        return f"{self.user.username} - {self.tipo} - {self.titulo[:50]}"


class ConfiguracionCuentaPago(models.Model):
    """Configuración de cuentas bancarias para recibir pagos"""
    METODO_CHOICES = [
        ('BANCOLOMBIA', 'Bancolombia'),
        ('NEQUI', 'Nequi'),
        ('DAVIPLATA', 'Daviplata'),
        ('OTRO', 'Otro'),
    ]

    TIPO_CUENTA_CHOICES = [
        ('AHORROS', 'Ahorros'),
        ('CORRIENTE', 'Corriente'),
        ('NEQUI', 'Cuenta Nequi'),
        ('DAVIPLATA', 'Cuenta Daviplata'),
    ]

    metodo = models.CharField(
        max_length=20,
        choices=METODO_CHOICES,
        unique=True,
        verbose_name="Método de Pago"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    nombre_banco = models.CharField(
        max_length=100,
        verbose_name="Nombre del Banco/Entidad"
    )
    tipo_cuenta = models.CharField(
        max_length=20,
        choices=TIPO_CUENTA_CHOICES,
        verbose_name="Tipo de Cuenta"
    )
    numero_cuenta = models.CharField(
        max_length=50,
        verbose_name="Número de Cuenta/Celular",
        help_text="Para Bancolombia: número de cuenta. Para Nequi: número de celular"
    )
    titular = models.CharField(
        max_length=200,
        verbose_name="Titular de la Cuenta"
    )
    nit = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="NIT",
        help_text="Opcional, solo para empresas"
    )
    color = models.CharField(
        max_length=7,
        default='#3498db',
        verbose_name="Color del Botón",
        help_text="Código hexadecimal, ej: #FFDD00"
    )
    icono = models.CharField(
        max_length=10,
        default='💳',
        verbose_name="Emoji/Icono"
    )
    instrucciones = models.TextField(
        blank=True,
        verbose_name="Instrucciones para el Usuario",
        help_text="Una instrucción por línea"
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuración de Cuenta de Pago"
        verbose_name_plural = "Configuraciones de Cuentas de Pago"
        ordering = ['metodo']

    def __str__(self):
        return f"{self.nombre_banco} - {self.numero_cuenta}"

    def get_instrucciones_lista(self):
        """Retorna las instrucciones como lista"""
        if not self.instrucciones:
            return []
        return [linea.strip() for linea in self.instrucciones.split('\n') if linea.strip()]

    def to_dict(self):
        """Convierte la configuración a diccionario para usar en QR"""
        return {
            'nombre': self.nombre_banco,
            'tipo': self.get_tipo_cuenta_display(),
            'numero': self.numero_cuenta,
            'titular': self.titular,
            'nit': self.nit,
            'color': self.color,
            'icono': self.icono,
            'instrucciones': self.get_instrucciones_lista()
        }


class PasswordResetToken(models.Model):
    """Token para restablecer contraseña sin dependencia de email"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reset_tokens',
        verbose_name="Usuario"
    )
    token = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        verbose_name="Token"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    expires_at = models.DateTimeField(
        verbose_name="Fecha de Expiración"
    )
    used = models.BooleanField(
        default=False,
        verbose_name="Token Usado"
    )
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Uso"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP"
    )

    class Meta:
        verbose_name = "Token de Reseteo de Contraseña"
        verbose_name_plural = "Tokens de Reseteo de Contraseña"
        ordering = ['-created_at']

    def __str__(self):
        return f"Token para {self.user.username} - {'Usado' if self.used else 'Activo'}"

    def is_valid(self):
        """Verifica si el token es válido"""
        if self.used:
            return False
        if timezone.now() > self.expires_at:
            return False
        return True

    def mark_as_used(self):
        """Marca el token como usado"""
        self.used = True
        self.used_at = timezone.now()
        self.save()

    @classmethod
    def cleanup_expired(cls):
        """Elimina tokens expirados (tarea de mantenimiento)"""
        expired = cls.objects.filter(expires_at__lt=timezone.now())
        count = expired.count()
        expired.delete()
        return count


class AuditLog(models.Model):
    """Registro de auditoría para tracking de acciones importantes"""
    ACCION_CHOICES = [
        ('CREATE', 'Crear'),
        ('UPDATE', 'Actualizar'),
        ('DELETE', 'Eliminar'),
        ('VIEW', 'Ver'),
        ('EXPORT', 'Exportar'),
        ('LOGIN', 'Inicio de Sesión'),
        ('LOGOUT', 'Cierre de Sesión'),
        ('LOGIN_FAILED', 'Intento de Login Fallido'),
        ('PASSWORD_CHANGE', 'Cambio de Contraseña'),
        ('PAYMENT', 'Pago/Suscripción'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name="Usuario"
    )
    accion = models.CharField(
        max_length=20,
        choices=ACCION_CHOICES,
        verbose_name="Acción"
    )
    modelo = models.CharField(
        max_length=100,
        verbose_name="Modelo/Entidad",
        help_text="Nombre del modelo afectado (Gasto, Aportante, etc.)"
    )
    objeto_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="ID del Objeto"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP"
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name="User Agent"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y Hora"
    )
    datos_anteriores = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Datos Anteriores",
        help_text="Estado antes del cambio (JSON)"
    )
    datos_nuevos = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Datos Nuevos",
        help_text="Estado después del cambio (JSON)"
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción adicional de la acción"
    )
    familia = models.ForeignKey(
        'Familia',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name="Familia"
    )

    class Meta:
        verbose_name = "Registro de Auditoría"
        verbose_name_plural = "Registros de Auditoría"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['usuario', '-timestamp']),
            models.Index(fields=['accion', '-timestamp']),
            models.Index(fields=['familia', '-timestamp']),
        ]

    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else "Anónimo"
        return f"{usuario_str} - {self.get_accion_display()} {self.modelo} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    @staticmethod
    def registrar(usuario, accion, modelo, objeto_id=None, ip_address=None,
                  user_agent=None, datos_anteriores=None, datos_nuevos=None,
                  descripcion='', familia=None):
        """
        Método helper para registrar una acción de auditoría

        Ejemplo de uso:
        AuditLog.registrar(
            usuario=request.user,
            accion='CREATE',
            modelo='Gasto',
            objeto_id=gasto.id,
            ip_address=get_client_ip(request),
            descripcion=f'Gasto creado: {gasto.descripcion}'
        )
        """
        return AuditLog.objects.create(
            usuario=usuario,
            accion=accion,
            modelo=modelo,
            objeto_id=objeto_id,
            ip_address=ip_address,
            user_agent=user_agent,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos,
            descripcion=descripcion,
            familia=familia
        )

    @classmethod
    def obtener_historial_usuario(cls, usuario, limite=50):
        """Obtiene el historial de acciones de un usuario"""
        return cls.objects.filter(usuario=usuario).order_by('-timestamp')[:limite]

    @classmethod
    def obtener_historial_familia(cls, familia, limite=100):
        """Obtiene el historial de acciones de una familia"""
        return cls.objects.filter(familia=familia).order_by('-timestamp')[:limite]

    @classmethod
    def obtener_logins_recientes(cls, usuario, dias=30):
        """Obtiene los logins recientes de un usuario"""
        fecha_inicio = timezone.now() - timedelta(days=dias)
        return cls.objects.filter(
            usuario=usuario,
            accion='LOGIN',
            timestamp__gte=fecha_inicio
        ).order_by('-timestamp')

    @classmethod
    def cleanup_old_logs(cls, dias=90):
        """Elimina logs antiguos (tarea de mantenimiento)"""
        fecha_limite = timezone.now() - timedelta(days=dias)
        old_logs = cls.objects.filter(timestamp__lt=fecha_limite)
        count = old_logs.count()
        old_logs.delete()
        return count


