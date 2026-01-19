"""
Vistas para exportar datos del dashboard a PDF y Excel
"""
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime
from decimal import Decimal
import io

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.pdfgen import canvas

import xlsxwriter

from .models import Aportante, CategoriaGasto, Gasto, MetaAhorro, Familia


@login_required
def exportar_dashboard_pdf(request):
    """Exportar dashboard completo a PDF"""
    # Verificar permisos
    familia_id = request.session.get('familia_id')
    if not familia_id:
        return JsonResponse({'error': 'No hay familia seleccionada'}, status=400)

    familia = get_object_or_404(Familia, id=familia_id)

    # Verificar si tiene permiso para exportar
    if not familia.tiene_exportar_datos():
        return JsonResponse({
            'error': 'Esta función requiere Plan Premium o superior'
        }, status=403)

    # Crear buffer para PDF
    buffer = io.BytesIO()

    # Crear PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)

    # Contenedor para elementos
    elements = []
    styles = getSampleStyleSheet()

    # Estilo personalizado para título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=30,
        alignment=1  # Center
    )

    # Estilo para subtítulos
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#34495E'),
        spaceAfter=12,
    )

    # Obtener datos del mes actual
    mes_actual = timezone.now().month
    anio_actual = timezone.now().year
    nombre_mes = timezone.now().strftime('%B %Y')

    # Título
    elements.append(Paragraph(f"📊 Reporte Financiero", title_style))
    elements.append(Paragraph(f"Familia: {familia.nombre}", styles['Heading3']))
    elements.append(Paragraph(f"Período: {nombre_mes}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))

    # Obtener datos
    aportantes = Aportante.objects.filter(familia_id=familia_id, activo=True)
    total_ingresos = aportantes.aggregate(total=Sum('ingreso_mensual'))['total'] or Decimal('0')

    gastos_mes = Gasto.objects.filter(
        subcategoria__categoria__familia_id=familia_id,
        fecha__month=mes_actual,
        fecha__year=anio_actual
    )

    total_gastos_mes = gastos_mes.aggregate(total=Sum('monto'))['total'] or Decimal('0')
    gastos_fijos_mes = gastos_mes.filter(subcategoria__tipo='FIJO').aggregate(total=Sum('monto'))['total'] or Decimal('0')
    gastos_variables_mes = gastos_mes.filter(subcategoria__tipo='VARIABLE').aggregate(total=Sum('monto'))['total'] or Decimal('0')
    balance = total_ingresos - total_gastos_mes

    # Resumen ejecutivo
    elements.append(Paragraph("💰 Resumen Ejecutivo", subtitle_style))

    data_resumen = [
        ['Concepto', 'Monto'],
        ['Ingresos Totales', f'${total_ingresos:,.0f}'],
        ['Gastos del Mes', f'${total_gastos_mes:,.0f}'],
        ['  - Gastos Fijos', f'${gastos_fijos_mes:,.0f}'],
        ['  - Gastos Variables', f'${gastos_variables_mes:,.0f}'],
        ['Balance', f'${balance:,.0f}'],
    ]

    table_resumen = Table(data_resumen, colWidths=[3.5*inch, 2*inch])
    table_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ECF0F1')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))

    elements.append(table_resumen)
    elements.append(Spacer(1, 0.3*inch))

    # Aportantes
    elements.append(Paragraph("👥 Aportantes", subtitle_style))

    data_aportantes = [['Nombre', 'Ingreso Mensual', '% Total']]
    for aportante in aportantes:
        porcentaje = (float(aportante.ingreso_mensual) / float(total_ingresos) * 100) if total_ingresos > 0 else 0
        data_aportantes.append([
            aportante.nombre,
            f'${aportante.ingreso_mensual:,.0f}',
            f'{porcentaje:.1f}%'
        ])

    table_aportantes = Table(data_aportantes, colWidths=[2.5*inch, 2*inch, 1*inch])
    table_aportantes.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ECC71')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))

    elements.append(table_aportantes)
    elements.append(Spacer(1, 0.3*inch))

    # Gastos por categoría
    elements.append(Paragraph("📊 Gastos por Categoría", subtitle_style))

    gastos_por_categoria = CategoriaGasto.objects.filter(
        familia_id=familia_id,
        subcategorias__gastos__fecha__month=mes_actual,
        subcategorias__gastos__fecha__year=anio_actual
    ).annotate(
        total_gastado=Sum('subcategorias__gastos__monto')
    ).order_by('-total_gastado')

    data_categorias = [['Categoría', 'Tipo', 'Total Gastado', '% Total']]
    for categoria in gastos_por_categoria:
        porcentaje = (float(categoria.total_gastado) / float(total_gastos_mes) * 100) if total_gastos_mes > 0 else 0
        tipo = dict(CategoriaGasto.TIPO_CHOICES).get(categoria.tipo_principal, categoria.tipo_principal)
        data_categorias.append([
            categoria.nombre,
            tipo,
            f'${categoria.total_gastado:,.0f}',
            f'{porcentaje:.1f}%'
        ])

    if len(data_categorias) > 1:
        table_categorias = Table(data_categorias, colWidths=[2*inch, 1.3*inch, 1.5*inch, 0.7*inch])
        table_categorias.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E74C3C')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(table_categorias)
    else:
        elements.append(Paragraph("No hay gastos registrados en este período.", styles['Normal']))

    elements.append(Spacer(1, 0.3*inch))

    # Metas de ahorro
    metas = MetaAhorro.objects.filter(familia_id=familia_id, activa=True)
    if metas.exists():
        elements.append(Paragraph("🎯 Metas de Ahorro", subtitle_style))

        data_metas = [['Meta', 'Objetivo', 'Ahorrado', 'Progreso']]
        for meta in metas:
            porcentaje = (float(meta.monto_actual) / float(meta.monto_objetivo) * 100) if meta.monto_objetivo > 0 else 0
            data_metas.append([
                meta.nombre,
                f'${meta.monto_objetivo:,.0f}',
                f'${meta.monto_actual:,.0f}',
                f'{porcentaje:.1f}%'
            ])

        table_metas = Table(data_metas, colWidths=[2*inch, 1.5*inch, 1.5*inch, 0.5*inch])
        table_metas.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9B59B6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))

        elements.append(table_metas)

    # Pie de página
    elements.append(Spacer(1, 0.5*inch))
    footer_text = f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} | Gastos Familiares Pro"
    elements.append(Paragraph(footer_text, styles['Normal']))

    # Construir PDF
    doc.build(elements)

    # Obtener el valor del buffer y retornar
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_dashboard_{nombre_mes.replace(" ", "_")}.pdf"'
    response.write(pdf)

    return response


@login_required
def exportar_dashboard_excel(request):
    """Exportar dashboard completo a Excel"""
    # Verificar permisos
    familia_id = request.session.get('familia_id')
    if not familia_id:
        return JsonResponse({'error': 'No hay familia seleccionada'}, status=400)

    familia = get_object_or_404(Familia, id=familia_id)

    # Verificar si tiene permiso para exportar
    if not familia.tiene_exportar_datos():
        return JsonResponse({
            'error': 'Esta función requiere Plan Premium o superior'
        }, status=403)

    # Crear buffer para Excel
    output = io.BytesIO()

    # Crear workbook
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})

    # Formatos
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 18,
        'font_color': '#2C3E50',
        'align': 'center',
        'valign': 'vcenter',
    })

    header_format = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'bg_color': '#3498DB',
        'font_color': 'white',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
    })

    money_format = workbook.add_format({
        'num_format': '$#,##0',
        'align': 'right',
    })

    percent_format = workbook.add_format({
        'num_format': '0.0%',
        'align': 'right',
    })

    cell_format = workbook.add_format({
        'align': 'left',
        'valign': 'vcenter',
        'border': 1,
    })

    # Obtener datos
    mes_actual = timezone.now().month
    anio_actual = timezone.now().year
    nombre_mes = timezone.now().strftime('%B %Y')

    # HOJA 1: Resumen
    worksheet_resumen = workbook.add_worksheet('Resumen')
    worksheet_resumen.set_column('A:A', 30)
    worksheet_resumen.set_column('B:B', 20)

    # Título
    worksheet_resumen.merge_range('A1:B1', f'📊 Reporte Financiero - {familia.nombre}', title_format)
    worksheet_resumen.write('A2', f'Período: {nombre_mes}')

    # Obtener datos
    aportantes = Aportante.objects.filter(familia_id=familia_id, activo=True)
    total_ingresos = aportantes.aggregate(total=Sum('ingreso_mensual'))['total'] or Decimal('0')

    gastos_mes = Gasto.objects.filter(
        subcategoria__categoria__familia_id=familia_id,
        fecha__month=mes_actual,
        fecha__year=anio_actual
    )

    total_gastos_mes = gastos_mes.aggregate(total=Sum('monto'))['total'] or Decimal('0')
    gastos_fijos_mes = gastos_mes.filter(subcategoria__tipo='FIJO').aggregate(total=Sum('monto'))['total'] or Decimal('0')
    gastos_variables_mes = gastos_mes.filter(subcategoria__tipo='VARIABLE').aggregate(total=Sum('monto'))['total'] or Decimal('0')
    balance = total_ingresos - total_gastos_mes

    # Resumen ejecutivo
    row = 4
    worksheet_resumen.write(row, 0, 'Concepto', header_format)
    worksheet_resumen.write(row, 1, 'Monto', header_format)

    row += 1
    worksheet_resumen.write(row, 0, 'Ingresos Totales', cell_format)
    worksheet_resumen.write(row, 1, float(total_ingresos), money_format)

    row += 1
    worksheet_resumen.write(row, 0, 'Gastos del Mes', cell_format)
    worksheet_resumen.write(row, 1, float(total_gastos_mes), money_format)

    row += 1
    worksheet_resumen.write(row, 0, '  - Gastos Fijos', cell_format)
    worksheet_resumen.write(row, 1, float(gastos_fijos_mes), money_format)

    row += 1
    worksheet_resumen.write(row, 0, '  - Gastos Variables', cell_format)
    worksheet_resumen.write(row, 1, float(gastos_variables_mes), money_format)

    row += 1
    balance_format = workbook.add_format({
        'num_format': '$#,##0',
        'align': 'right',
        'bold': True,
        'bg_color': '#2ECC71' if balance >= 0 else '#E74C3C',
        'font_color': 'white',
        'border': 1,
    })
    worksheet_resumen.write(row, 0, 'Balance', header_format)
    worksheet_resumen.write(row, 1, float(balance), balance_format)

    # HOJA 2: Aportantes
    worksheet_aportantes = workbook.add_worksheet('Aportantes')
    worksheet_aportantes.set_column('A:A', 30)
    worksheet_aportantes.set_column('B:B', 20)
    worksheet_aportantes.set_column('C:C', 15)

    worksheet_aportantes.merge_range('A1:C1', '👥 Aportantes', title_format)

    row = 3
    worksheet_aportantes.write(row, 0, 'Nombre', header_format)
    worksheet_aportantes.write(row, 1, 'Ingreso Mensual', header_format)
    worksheet_aportantes.write(row, 2, '% Total', header_format)

    for aportante in aportantes:
        row += 1
        porcentaje = (float(aportante.ingreso_mensual) / float(total_ingresos)) if total_ingresos > 0 else 0
        worksheet_aportantes.write(row, 0, aportante.nombre, cell_format)
        worksheet_aportantes.write(row, 1, float(aportante.ingreso_mensual), money_format)
        worksheet_aportantes.write(row, 2, porcentaje, percent_format)

    # HOJA 3: Gastos por Categoría
    worksheet_categorias = workbook.add_worksheet('Gastos por Categoría')
    worksheet_categorias.set_column('A:A', 30)
    worksheet_categorias.set_column('B:B', 15)
    worksheet_categorias.set_column('C:C', 20)
    worksheet_categorias.set_column('D:D', 15)

    worksheet_categorias.merge_range('A1:D1', '📊 Gastos por Categoría', title_format)

    row = 3
    worksheet_categorias.write(row, 0, 'Categoría', header_format)
    worksheet_categorias.write(row, 1, 'Tipo', header_format)
    worksheet_categorias.write(row, 2, 'Total Gastado', header_format)
    worksheet_categorias.write(row, 3, '% Total', header_format)

    gastos_por_categoria = CategoriaGasto.objects.filter(
        familia_id=familia_id,
        subcategorias__gastos__fecha__month=mes_actual,
        subcategorias__gastos__fecha__year=anio_actual
    ).annotate(
        total_gastado=Sum('subcategorias__gastos__monto')
    ).order_by('-total_gastado')

    for categoria in gastos_por_categoria:
        row += 1
        porcentaje = (float(categoria.total_gastado) / float(total_gastos_mes)) if total_gastos_mes > 0 else 0
        tipo = dict(CategoriaGasto.TIPO_CHOICES).get(categoria.tipo_principal, categoria.tipo_principal)
        worksheet_categorias.write(row, 0, categoria.nombre, cell_format)
        worksheet_categorias.write(row, 1, tipo, cell_format)
        worksheet_categorias.write(row, 2, float(categoria.total_gastado), money_format)
        worksheet_categorias.write(row, 3, porcentaje, percent_format)

    # HOJA 4: Metas de Ahorro
    metas = MetaAhorro.objects.filter(familia_id=familia_id, activa=True)
    if metas.exists():
        worksheet_metas = workbook.add_worksheet('Metas de Ahorro')
        worksheet_metas.set_column('A:A', 30)
        worksheet_metas.set_column('B:B', 20)
        worksheet_metas.set_column('C:C', 20)
        worksheet_metas.set_column('D:D', 15)

        worksheet_metas.merge_range('A1:D1', '🎯 Metas de Ahorro', title_format)

        row = 3
        worksheet_metas.write(row, 0, 'Meta', header_format)
        worksheet_metas.write(row, 1, 'Objetivo', header_format)
        worksheet_metas.write(row, 2, 'Ahorrado', header_format)
        worksheet_metas.write(row, 3, 'Progreso', header_format)

        for meta in metas:
            row += 1
            porcentaje = (float(meta.monto_actual) / float(meta.monto_objetivo)) if meta.monto_objetivo > 0 else 0
            worksheet_metas.write(row, 0, meta.nombre, cell_format)
            worksheet_metas.write(row, 1, float(meta.monto_objetivo), money_format)
            worksheet_metas.write(row, 2, float(meta.monto_actual), money_format)
            worksheet_metas.write(row, 3, porcentaje, percent_format)

    # HOJA 5: Detalle de Gastos
    worksheet_detalle = workbook.add_worksheet('Detalle de Gastos')
    worksheet_detalle.set_column('A:A', 15)
    worksheet_detalle.set_column('B:B', 25)
    worksheet_detalle.set_column('C:C', 25)
    worksheet_detalle.set_column('D:D', 30)
    worksheet_detalle.set_column('E:E', 20)

    worksheet_detalle.merge_range('A1:E1', '📝 Detalle de Gastos del Mes', title_format)

    row = 3
    worksheet_detalle.write(row, 0, 'Fecha', header_format)
    worksheet_detalle.write(row, 1, 'Categoría', header_format)
    worksheet_detalle.write(row, 2, 'Subcategoría', header_format)
    worksheet_detalle.write(row, 3, 'Descripción', header_format)
    worksheet_detalle.write(row, 4, 'Monto', header_format)

    gastos_detalle = gastos_mes.select_related('subcategoria__categoria').order_by('-fecha')

    for gasto in gastos_detalle:
        row += 1
        worksheet_detalle.write(row, 0, gasto.fecha.strftime('%d/%m/%Y'), cell_format)
        worksheet_detalle.write(row, 1, gasto.subcategoria.categoria.nombre, cell_format)
        worksheet_detalle.write(row, 2, gasto.subcategoria.nombre, cell_format)
        worksheet_detalle.write(row, 3, gasto.descripcion or '', cell_format)
        worksheet_detalle.write(row, 4, float(gasto.monto), money_format)

    # Cerrar workbook
    workbook.close()

    # Obtener el valor del buffer
    output.seek(0)

    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="reporte_dashboard_{nombre_mes.replace(" ", "_")}.xlsx"'

    return response
