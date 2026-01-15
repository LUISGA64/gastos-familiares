from django import forms
from .models import Aportante, CategoriaGasto, SubcategoriaGasto, Gasto, DistribucionGasto


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
        fields = ['subcategoria', 'descripcion', 'monto', 'fecha', 'pagado_por', 'observaciones', 'pagado']
        widgets = {
            'subcategoria': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Factura de enero (opcional)'}),
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
        super().__init__(*args, **kwargs)
        # Ordenar subcategorías por categoría y nombre
        self.fields['subcategoria'].queryset = SubcategoriaGasto.objects.filter(
            activo=True
        ).select_related('categoria').order_by('categoria__nombre', 'nombre')

        # Personalizar el label de subcategoría para mostrar la jerarquía
        self.fields['subcategoria'].label_from_instance = lambda obj: f"{obj.categoria.nombre} → {obj.nombre} ({obj.get_tipo_display()})"

        # Solo mostrar aportantes activos
        self.fields['pagado_por'].queryset = Aportante.objects.filter(activo=True)


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

