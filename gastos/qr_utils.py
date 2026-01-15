"""
Utilidades para generar códigos QR de pago
MÉTODOS ACTIVOS: Bancolombia y Nequi
PRÓXIMAMENTE: Tarjetas de Crédito, PSE, DaviPlata
"""
import qrcode
from io import BytesIO
from decimal import Decimal
import base64
from django.core.files.base import ContentFile
from django.utils import timezone
import uuid


class GeneradorQRPago:
    """Clase para generar códigos QR de pago"""

    # Configuración de cuentas de destino (CAMBIAR POR LAS REALES)
    CUENTAS = {
        'BANCOLOMBIA': {
            'numero_cuenta': '12345678901',
            'tipo_cuenta': 'Ahorros',
            'titular': 'Gestor Gastos Familiares SAS',
            'nit': '900123456-7',
            'banco': 'Bancolombia'
        },
        'NEQUI': {
            'numero': '3001234567',
            'nombre': 'Gestor Gastos Familiares'
        }
    }

    @staticmethod
    def generar_referencia_unica():
        """Genera una referencia única para el pago"""
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        uuid_corto = str(uuid.uuid4())[:8].upper()
        return f"GGF-{timestamp}-{uuid_corto}"

    @staticmethod
    def generar_qr_bancolombia(monto, referencia, concepto="Suscripción Premium"):
        """
        Genera QR para transferencia Bancolombia

        Args:
            monto (Decimal): Monto a pagar
            referencia (str): Referencia del pago
            concepto (str): Concepto del pago

        Returns:
            tuple: (imagen_qr_base64, datos_qr)
        """
        cuenta_info = GeneradorQRPago.CUENTAS['BANCOLOMBIA']

        # Datos para el QR (formato simplificado para transferencias)
        # En producción, usar el formato oficial de Bancolombia
        datos_qr = {
            'banco': cuenta_info['banco'],
            'numero_cuenta': cuenta_info['numero_cuenta'],
            'tipo_cuenta': cuenta_info['tipo_cuenta'],
            'titular': cuenta_info['titular'],
            'nit': cuenta_info['nit'],
            'monto': str(monto),
            'referencia': referencia,
            'concepto': concepto
        }

        # Crear string para el QR
        # Formato: BANCO|CUENTA|TIPO|MONTO|REFERENCIA|CONCEPTO
        qr_string = (
            f"BANCOLOMBIA|"
            f"{cuenta_info['numero_cuenta']}|"
            f"{cuenta_info['tipo_cuenta']}|"
            f"{monto}|"
            f"{referencia}|"
            f"{concepto}"
        )

        # Generar QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_string)
        qr.make(fit=True)

        # Crear imagen
        img = qr.make_image(fill_color="#FFDD00", back_color="white")  # Colores Bancolombia

        # Convertir a base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()

        return img_base64, datos_qr

    @staticmethod
    def generar_qr_nequi(monto, referencia, concepto="Suscripción Premium"):
        """
        Genera QR para pago Nequi

        Args:
            monto (Decimal): Monto a pagar
            referencia (str): Referencia del pago
            concepto (str): Concepto del pago

        Returns:
            tuple: (imagen_qr_base64, datos_qr)
        """
        cuenta_info = GeneradorQRPago.CUENTAS['NEQUI']

        # Datos para el QR
        datos_qr = {
            'metodo': 'Nequi',
            'numero': cuenta_info['numero'],
            'nombre': cuenta_info['nombre'],
            'monto': str(monto),
            'referencia': referencia,
            'concepto': concepto
        }

        # Crear string para el QR
        # Formato Nequi simplificado
        qr_string = (
            f"NEQUI|"
            f"{cuenta_info['numero']}|"
            f"{monto}|"
            f"{referencia}|"
            f"{concepto}"
        )

        # Generar QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_string)
        qr.make(fit=True)

        # Crear imagen con colores de Nequi
        img = qr.make_image(fill_color="#FF006B", back_color="white")  # Color Nequi

        # Convertir a base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()

        return img_base64, datos_qr

    @staticmethod
    def generar_qr_generico(datos_pago):
        """
        Genera QR genérico con datos de pago

        Args:
            datos_pago (dict): Diccionario con datos del pago

        Returns:
            str: Imagen QR en base64
        """
        # Convertir datos a string
        qr_string = "|".join([f"{k}:{v}" for k, v in datos_pago.items()])

        # Generar QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_string)
        qr.make(fit=True)

        img = qr.make_image(fill_color="#2c3e50", back_color="white")

        # Convertir a base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()

        return img_base64

    @staticmethod
    def validar_comprobante(imagen):
        """
        Valida que el archivo sea una imagen válida

        Args:
            imagen: Archivo de imagen

        Returns:
            tuple: (es_valido, mensaje_error)
        """
        # Validar tamaño (máximo 5MB)
        if imagen.size > 5 * 1024 * 1024:
            return False, "El archivo es muy grande. Máximo 5MB."

        # Validar extensión
        extensiones_permitidas = ['.jpg', '.jpeg', '.png', '.pdf']
        nombre = imagen.name.lower()
        if not any(nombre.endswith(ext) for ext in extensiones_permitidas):
            return False, "Formato no permitido. Use JPG, PNG o PDF."

        return True, None


class VerificadorPagos:
    """Clase para verificar pagos pendientes"""

    @staticmethod
    def verificar_pago(pago, usuario_verificador):
        """
        Marca un pago como verificado y lo aprueba

        Args:
            pago: Instancia del modelo Pago
            usuario_verificador: Usuario que verifica

        Returns:
            bool: True si se aprobó correctamente
        """
        if pago.estado == 'VERIFICANDO':
            pago.aprobar_pago(verificado_por=usuario_verificador)
            pago.save()
            pago.familia.save()
            return True
        return False

    @staticmethod
    def rechazar_pago(pago, motivo, usuario_verificador):
        """
        Rechaza un pago

        Args:
            pago: Instancia del modelo Pago
            motivo: Motivo del rechazo
            usuario_verificador: Usuario que rechaza
        """
        pago.estado = 'RECHAZADO'
        pago.verificado_por = usuario_verificador
        pago.notas = f"Rechazado: {motivo}"
        pago.save()

    @staticmethod
    def obtener_pagos_pendientes():
        """
        Obtiene todos los pagos pendientes de verificación

        Returns:
            QuerySet: Pagos en estado VERIFICANDO
        """
        from .models import Pago
        return Pago.objects.filter(estado='VERIFICANDO').order_by('-fecha_pago')


# Información de cuentas para mostrar al usuario
INFO_CUENTAS_COLOMBIA = {
    'bancolombia': {
        'nombre': 'Bancolombia',
        'tipo': 'Ahorros',
        'numero': '12345678901',
        'titular': 'Gestor Gastos Familiares SAS',
        'nit': '900.123.456-7',
        'color': '#FFDD00',
        'icono': '🏦',
        'instrucciones': [
            'Abre la app de Bancolombia',
            'Ve a "Transferencias"',
            'Escanea el código QR o ingresa los datos manualmente',
            'Confirma el monto y la referencia',
            'Completa la transferencia',
            'Sube el comprobante aquí'
        ]
    },
    'nequi': {
        'nombre': 'Nequi',
        'tipo': 'Cuenta Nequi',
        'numero': '300 123 4567',
        'titular': 'Gestor Gastos Familiares',
        'color': '#FF006B',
        'icono': '💰',
        'instrucciones': [
            'Abre la app de Nequi',
            'Ve a "Enviar plata"',
            'Escanea el código QR',
            'Confirma el monto',
            'Ingresa tu clave',
            'Sube el comprobante aquí'
        ]
    },
    # DaviPlata - PRÓXIMAMENTE
    # 'daviplata': {
    #     'nombre': 'DaviPlata',
    #     'tipo': 'Bolsillo',
    #     'numero': '300 765 4321',
    #     'titular': 'Gestor Gastos Familiares',
    #     'color': '#ED1C24',
    #     'icono': '📱',
    #     'instrucciones': [
    #         'Abre la app DaviPlata',
    #         'Ve a "Enviar plata"',
    #         'Ingresa el número destino',
    #         'Confirma el monto y referencia',
    #         'Sube el comprobante aquí'
    #     ]
    # }
}

