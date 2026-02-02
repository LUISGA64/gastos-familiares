from django import forms
from .models import Aportante, CategoriaGasto, SubcategoriaGasto, Gasto, DistribucionGasto, MetaAhorro


class AportanteForm(forms.ModelForm):
    class Meta:
        model = Aportante
        fields = ['nombre', 'email', 'ingreso_mensual', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del aportante'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.com'}),
            'ingreso_mensual': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nombre': 'Nombre',
            'email': 'Email',
            'ingreso_mensual': 'Ingreso Mensual (COP)',
            'activo': 'Activo',
        }
        help_texts = {
            'email': 'Email para recibir códigos de confirmación de conciliaciones',
        }


class CategoriaGastoForm(forms.ModelForm):
    class Meta:
        model = CategoriaGasto
        fields = ['nombre', 'descripcion', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Servicios Públicos'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción opcional'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SubcategoriaGastoForm(forms.ModelForm):
    class Meta:
        model = SubcategoriaGasto
        fields = ['categoria', 'nombre', 'tipo', 'monto_estimado', 'descripcion', 'activo']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Servicio de Internet'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'monto_estimado': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Descripción opcional'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'categoria': 'Categoría Principal',
            'nombre': 'Nombre del Gasto',
            'tipo': 'Tipo de Gasto',
            'monto_estimado': 'Monto Estimado Mensual (COP)',
            'descripcion': 'Descripción',
            'activo': 'Activo',
        }


class GastoForm(forms.ModelForm):
    distribuir_automaticamente = forms.BooleanField(
        required=False,
        initial=True,
        label='Distribuir automáticamente según ingresos',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    # Campo adicional para filtrar subcategorías por categoría
    categoria_filter = forms.ModelChoiceField(
        queryset=CategoriaGasto.objects.filter(activo=True),
        required=False,
        label='Filtrar por categoría',
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Todas las categorías"
    )

    class Meta:
        model = Gasto
        fields = ['subcategoria', 'tipo_gasto', 'descripcion', 'monto', 'fecha', 'pagado_por', 'observaciones', 'pagado']
        widgets = {
            'subcategoria': forms.Select(attrs={'class': 'form-select'}),
            'tipo_gasto': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Factura de enero (opcional)'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'pagado_por': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones opcionales'}),
            'pagado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'subcategoria': 'Tipo de Gasto',
            'tipo_gasto': 'Compartido o Personal',
            'descripcion': 'Descripción Adicional (Opcional)',
            'monto': 'Monto (COP)',
            'fecha': 'Fecha',
            'pagado_por': 'Pagado por',
            'observaciones': 'Observaciones',
            'pagado': 'Pagado',
        }

    def __init__(self, *args, **kwargs):
        familia_id = kwargs.pop('familia_id', None)
        super().__init__(*args, **kwargs)

        # Filtrar subcategorías y aportantes por familia si se proporciona
        if familia_id:
            self.fields['subcategoria'].queryset = SubcategoriaGasto.objects.filter(
                categoria__familia_id=familia_id,
                activo=True
            ).select_related('categoria').order_by('categoria__nombre', 'nombre')

            self.fields['pagado_por'].queryset = Aportante.objects.filter(
                familia_id=familia_id,
                activo=True
            )

            self.fields['categoria_filter'].queryset = CategoriaGasto.objects.filter(
                familia_id=familia_id,
                activo=True
            )
        else:
            # Sin familia_id, mostrar todas (compatibilidad)
            self.fields['subcategoria'].queryset = SubcategoriaGasto.objects.filter(
                activo=True
            ).select_related('categoria').order_by('categoria__nombre', 'nombre')

            self.fields['pagado_por'].queryset = Aportante.objects.filter(activo=True)

        # Personalizar el label de subcategoría para mostrar la jerarquía
        self.fields['subcategoria'].label_from_instance = lambda obj: f"{obj.categoria.nombre} → {obj.nombre} ({obj.get_tipo_display()})"


class GastoPersonalForm(forms.ModelForm):
    """Formulario para gastos personales - sin distribución automática"""

    # Campo adicional para filtrar subcategorías por categoría
    categoria_filter = forms.ModelChoiceField(
        queryset=CategoriaGasto.objects.filter(activo=True),
        required=False,
        label='Filtrar por categoría',
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Todas las categorías"
    )

    class Meta:
        model = Gasto
        fields = ['subcategoria', 'descripcion', 'monto', 'fecha', 'pagado_por', 'observaciones', 'pagado']
        widgets = {
            'subcategoria': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Compra personal (opcional)'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'pagado_por': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones opcionales'}),
            'pagado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'subcategoria': 'Tipo de Gasto',
            'descripcion': 'Descripción Adicional (Opcional)',
            'monto': 'Monto (COP)',
            'fecha': 'Fecha',
            'pagado_por': 'Pagado por',
            'observaciones': 'Observaciones',
            'pagado': 'Pagado',
        }

    def __init__(self, *args, **kwargs):
        familia_id = kwargs.pop('familia_id', None)
        super().__init__(*args, **kwargs)

        # Establecer tipo_gasto como PERSONAL por defecto
        self.instance.tipo_gasto = 'PERSONAL'

        # Filtrar subcategorías y aportantes por familia si se proporciona
        if familia_id:
            self.fields['subcategoria'].queryset = SubcategoriaGasto.objects.filter(
                categoria__familia_id=familia_id,
                activo=True
            ).select_related('categoria').order_by('categoria__nombre', 'nombre')

            self.fields['pagado_por'].queryset = Aportante.objects.filter(
                familia_id=familia_id,
                activo=True
            )

            self.fields['categoria_filter'].queryset = CategoriaGasto.objects.filter(
                familia_id=familia_id,
                activo=True
            )
        else:
            # Sin familia_id, mostrar todas (compatibilidad)
            self.fields['subcategoria'].queryset = SubcategoriaGasto.objects.filter(
                activo=True
            ).select_related('categoria').order_by('categoria__nombre', 'nombre')

            self.fields['pagado_por'].queryset = Aportante.objects.filter(activo=True)

        # Personalizar el label de subcategoría para mostrar la jerarquía
        self.fields['subcategoria'].label_from_instance = lambda obj: f"{obj.categoria.nombre} → {obj.nombre} ({obj.get_tipo_display()})"



class DistribucionGastoForm(forms.ModelForm):
    class Meta:
        model = DistribucionGasto
        fields = ['aportante', 'porcentaje']
        widgets = {
            'aportante': forms.Select(attrs={'class': 'form-select'}),
            'porcentaje': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
        }


# FormSet para manejar múltiples distribuciones
DistribucionGastoFormSet = forms.inlineformset_factory(
    Gasto,
    DistribucionGasto,
    form=DistribucionGastoForm,
    extra=0,
    can_delete=True
)


class MetaAhorroForm(forms.ModelForm):
    """Formulario para crear y editar metas de ahorro"""

    class Meta:
        model = MetaAhorro
        fields = ['nombre', 'descripcion', 'monto_objetivo', 'fecha_objetivo', 'prioridad', 'icono']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Vacaciones en Cartagena',
                'maxlength': 200
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe tu meta de ahorro (opcional)'
            }),
            'monto_objetivo': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'fecha_objetivo': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'prioridad': forms.Select(attrs={
                'class': 'form-select'
            }),
            'icono': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[
                ('piggy-bank', '🐷 Alcancía - Ahorro general'),
                ('airplane', '✈️ Avión - Viajes/Vacaciones'),
                ('house', '🏠 Casa - Vivienda'),
                ('car-front', '🚗 Carro - Vehículo'),
                ('mortarboard', '🎓 Graduación - Educación'),
                ('heart-pulse', '❤️ Salud - Gastos médicos'),
                ('shield-check', '🛡️ Escudo - Fondo de emergencia'),
                ('gift', '🎁 Regalo - Ocasión especial'),
                ('laptop', '💻 Laptop - Tecnología'),
                ('bicycle', '🚲 Bicicleta - Deportes'),
                ('tree', '🌳 Árbol - Inversión'),
                ('star', '⭐ Estrella - Meta importante'),
            ]),
        }
        labels = {
            'nombre': 'Nombre de la Meta',
            'descripcion': 'Descripción',
            'monto_objetivo': 'Monto Objetivo (COP)',
            'fecha_objetivo': 'Fecha Objetivo',
            'prioridad': 'Prioridad',
            'icono': 'Ícono',
        }
        help_texts = {
            'monto_objetivo': 'Cantidad total que deseas ahorrar',
            'fecha_objetivo': 'Fecha en la que deseas alcanzar esta meta',
            'prioridad': 'Qué tan importante es esta meta para ti',
        }


class AgregarAhorroForm(forms.Form):
    """Formulario para agregar ahorro a una meta existente"""

    monto = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0.01'
        }),
        label='Monto a Agregar (COP)',
        help_text='Cantidad que deseas agregar a esta meta'
    )

    nota = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Ahorro de enero'
        }),
        label='Nota (Opcional)',
        help_text='Descripción de este aporte'
    )


class IngresoAportanteForm(forms.ModelForm):
    """Formulario para registrar ingresos de aportantes"""

    class Meta:
        from .models import IngresoAportante
        model = IngresoAportante
        fields = ['aportante', 'tipo_ingreso', 'descripcion', 'monto', 'fecha', 'recurrente', 'observaciones']
        widgets = {
            'aportante': forms.Select(attrs={'class': 'form-select'}),
            'tipo_ingreso': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Salario de enero (opcional)'
            }),
            'monto': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'recurrente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones opcionales'
            }),
        }
        labels = {
            'aportante': 'Aportante',
            'tipo_ingreso': 'Tipo de Ingreso',
            'descripcion': 'Descripción Adicional (Opcional)',
            'monto': 'Monto (COP)',
            'fecha': 'Fecha del Ingreso',
            'recurrente': 'Ingreso Recurrente Mensual',
            'observaciones': 'Observaciones',
        }
        help_texts = {
            'recurrente': 'Marcar si este ingreso se repite mensualmente (ej: salario)',
            'tipo_ingreso': 'Tipo de ingreso recibido',
        }

    def __init__(self, *args, **kwargs):
        familia_id = kwargs.pop('familia_id', None)
        super().__init__(*args, **kwargs)

        # Filtrar aportantes por familia si se proporciona
        if familia_id:
            from .models import Aportante
            self.fields['aportante'].queryset = Aportante.objects.filter(
                familia_id=familia_id,
                activo=True
            )
        else:
            from .models import Aportante
            self.fields['aportante'].queryset = Aportante.objects.filter(activo=True)


