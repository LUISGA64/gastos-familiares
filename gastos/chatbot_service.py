"""
Servicio de Chatbot IA Multi-Proveedor
Asistente financiero inteligente para análisis de gastos
Soporta: GPT-4, Groq (gratis), y modo demo
"""
import os
import json
import requests
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Avg, Count, Q
from django.conf import settings
from .models import (
    Gasto, Aportante, CategoriaGasto, ConversacionChatbot,
    MensajeChatbot, AnalisisIA, MetaAhorro
)


class ChatbotIAService:
    """Servicio principal del chatbot con IA multi-proveedor"""

    def __init__(self):
        # Determinar proveedor de IA a usar
        self.provider = getattr(settings, 'AI_PROVIDER', 'demo')  # demo, groq, openai

        # Inicializar según proveedor
        if self.provider == 'openai':
            from openai import OpenAI
            api_key = getattr(settings, 'OPENAI_API_KEY', 'tu-api-key-aqui')
            self.client = OpenAI(api_key=api_key) if api_key != 'tu-api-key-aqui' else None
            self.model = "gpt-4-turbo-preview"
        elif self.provider == 'groq':
            # Groq es GRATIS y muy rápido (usa modelos open source)
            self.groq_api_key = getattr(settings, 'GROQ_API_KEY', None)
            self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
            self.model = "llama-3.3-70b-versatile"  # Modelo más reciente de Groq (Llama 3.3)
        else:
            # Modo demo - respuestas predefinidas inteligentes
            self.client = None
            self.model = "demo"

    def obtener_o_crear_conversacion(self, user, familia=None):
        """Obtiene la conversación activa o crea una nueva"""
        conversacion = ConversacionChatbot.objects.filter(
            user=user,
            familia=familia,
            activa=True
        ).first()

        if not conversacion:
            conversacion = ConversacionChatbot.objects.create(
                user=user,
                familia=familia,
                titulo=f"Conversación {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            )

        return conversacion

    def obtener_contexto_financiero(self, user, familia):
        """Genera contexto financiero del usuario para la IA"""
        mes_actual = timezone.now().month
        anio_actual = timezone.now().year

        # Ingresos totales
        ingresos = Aportante.objects.filter(
            familia=familia,
            activo=True
        ).aggregate(total=Sum('ingreso_mensual'))['total'] or 0

        # Gastos del mes
        gastos_mes = Gasto.objects.filter(
            subcategoria__categoria__familia=familia,
            fecha__month=mes_actual,
            fecha__year=anio_actual
        )

        total_gastos = gastos_mes.aggregate(total=Sum('monto'))['total'] or 0

        # Gastos por categoría
        gastos_por_cat = CategoriaGasto.objects.filter(
            familia=familia
        ).annotate(
            total=Sum('subcategorias__gastos__monto',
                     filter=Q(subcategorias__gastos__fecha__month=mes_actual,
                            subcategorias__gastos__fecha__year=anio_actual))
        ).exclude(total=None).order_by('-total')[:5]

        categorias_texto = "\n".join([
            f"- {cat.nombre}: ${cat.total:,.0f}"
            for cat in gastos_por_cat
        ])

        # Ahorro
        ahorro_mes = ingresos - total_gastos

        # Metas de ahorro
        metas_activas = MetaAhorro.objects.filter(
            familia=familia,
            estado='ACTIVA'
        ).count()

        # Histórico (3 meses)
        meses_anteriores = []
        for i in range(1, 4):
            fecha = timezone.now() - timedelta(days=30*i)
            gastos_mes_ant = Gasto.objects.filter(
                subcategoria__categoria__familia=familia,
                fecha__month=fecha.month,
                fecha__year=fecha.year
            ).aggregate(total=Sum('monto'))['total'] or 0
            meses_anteriores.append(f"{fecha.strftime('%B')}: ${gastos_mes_ant:,.0f}")

        historico_texto = "\n".join(meses_anteriores)

        contexto = f"""
INFORMACIÓN FINANCIERA DEL USUARIO:

📊 RESUMEN ACTUAL ({timezone.now().strftime('%B %Y')}):
- Ingresos mensuales: ${ingresos:,.0f}
- Gastos totales: ${total_gastos:,.0f}
- Ahorro/Balance: ${ahorro_mes:,.0f}
- Porcentaje gastado: {(total_gastos/ingresos*100) if ingresos > 0 else 0:.1f}%

💰 PRINCIPALES CATEGORÍAS DE GASTO:
{categorias_texto}

📈 HISTÓRICO (3 MESES):
{historico_texto}

🎯 METAS DE AHORRO:
- Metas activas: {metas_activas}

INSTRUCCIONES PARA LA IA:
- Sé amigable, profesional y motivador
- Habla en español colombiano (COP = pesos colombianos)
- Usa emojis relevantes
- Da consejos prácticos y accionables
- Si te preguntan sobre análisis específico, usa estos datos
- Si no tienes la información exacta, di que puedes ayudar con otra cosa
- Sé conciso pero completo (máximo 200 palabras por respuesta)
"""
        return contexto

    def enviar_mensaje(self, user, familia, mensaje_usuario):
        """Envía un mensaje al chatbot y obtiene respuesta"""

        try:
            # Obtener o crear conversación
            conversacion = self.obtener_o_crear_conversacion(user, familia)

            # Guardar mensaje del usuario
            MensajeChatbot.objects.create(
                conversacion=conversacion,
                role='user',
                contenido=mensaje_usuario
            )

            # Obtener contexto financiero
            contexto = self.obtener_contexto_financiero(user, familia)

            # Obtener respuesta según proveedor
            if self.provider == 'groq':
                resultado = self._enviar_groq(conversacion, mensaje_usuario, contexto)
            elif self.provider == 'openai':
                resultado = self._enviar_openai(conversacion, mensaje_usuario, contexto)
            else:
                resultado = self._enviar_demo(conversacion, mensaje_usuario, contexto)

            if resultado['success']:
                # Guardar respuesta del asistente
                MensajeChatbot.objects.create(
                    conversacion=conversacion,
                    role='assistant',
                    contenido=resultado['respuesta'],
                    tokens_usados=resultado.get('tokens_usados', 0)
                )

                return {
                    'success': True,
                    'respuesta': resultado['respuesta'],
                    'conversacion_id': conversacion.id,
                    'tokens_usados': resultado.get('tokens_usados', 0)
                }
            else:
                return resultado

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'respuesta': f'Lo siento, ocurrió un error: {str(e)}'
            }

    def _enviar_groq(self, conversacion, mensaje_usuario, contexto):
        """Enviar mensaje usando Groq (GRATIS)"""
        if not self.groq_api_key:
            return {
                'success': False,
                'respuesta': '⚠️ Groq API key no configurada. Configura GROQ_API_KEY en .env'
            }

        try:
            # Preparar mensajes - solo user y assistant en el historial
            mensajes_historial = list(conversacion.get_contexto_reciente(limite=6))

            # Sistema de instrucciones simplificado
            system_prompt = """Eres FinanBot, un asistente financiero experto.
Ayudas a las personas con sus finanzas familiares.
Sé amigable, práctico y motivador. Usa emojis relevantes.
Responde en máximo 150 palabras."""

            mensajes_api = [
                {
                    "role": "system",
                    "content": system_prompt
                }
            ]

            # Agregar contexto financiero como primer mensaje user si no hay historial
            if len(mensajes_historial) == 0:
                # Extraer solo datos clave del contexto
                import re
                ingresos_match = re.search(r'Ingresos mensuales: \$([0-9,]+)', contexto)
                gastos_match = re.search(r'Gastos totales: \$([0-9,]+)', contexto)
                ahorro_match = re.search(r'Ahorro/Balance: \$([0-9,]+)', contexto)

                contexto_resumen = f"""Datos del usuario:
- Ingresos: ${ingresos_match.group(1) if ingresos_match else '0'}
- Gastos: ${gastos_match.group(1) if gastos_match else '0'}
- Balance: ${ahorro_match.group(1) if ahorro_match else '0'}"""

                mensajes_api.append({
                    "role": "user",
                    "content": f"Contexto: {contexto_resumen}\n\nPregunta: {mensaje_usuario}"
                })
            else:
                # Agregar historial (solo user y assistant, no system)
                for msg in mensajes_historial:
                    if msg.role in ['user', 'assistant']:
                        mensajes_api.append({
                            "role": msg.role,
                            "content": msg.contenido[:500]  # Limitar longitud
                        })

                # Agregar mensaje actual
                mensajes_api.append({
                    "role": "user",
                    "content": mensaje_usuario
                })

            # Llamar a Groq API
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.model,
                "messages": mensajes_api,
                "temperature": 0.7,
                "max_tokens": 400,
                "top_p": 1,
                "stream": False
            }

            response = requests.post(self.groq_url, headers=headers, json=data, timeout=30)

            # Verificar respuesta
            if response.status_code != 200:
                error_detail = response.text
                return {
                    'success': False,
                    'respuesta': f'⚠️ Error de Groq API ({response.status_code}): {error_detail[:200]}'
                }

            resultado = response.json()
            respuesta_ia = resultado['choices'][0]['message']['content']
            tokens_usados = resultado.get('usage', {}).get('total_tokens', 0)

            return {
                'success': True,
                'respuesta': respuesta_ia,
                'tokens_usados': tokens_usados
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'respuesta': f'⚠️ Error de conexión con Groq: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'respuesta': f'⚠️ Error con Groq: {str(e)}'
            }

    def _enviar_openai(self, conversacion, mensaje_usuario, contexto):
        """Enviar mensaje usando OpenAI GPT-4"""
        if not self.client:
            return {
                'success': False,
                'respuesta': '⚠️ OpenAI API key no configurada. Configura OPENAI_API_KEY en .env'
            }

        try:
            from openai import OpenAI

            # Preparar mensajes
            mensajes_historial = list(conversacion.get_contexto_reciente(limite=10))

            mensajes_api = [
                {
                    "role": "system",
                    "content": f"""Eres un asistente financiero experto llamado 'FinanBot'. 
Tu trabajo es ayudar a las personas a administrar mejor su dinero familiar.

{contexto}

Personalidad:
- Amigable y motivador
- Práctico y directo
- Usa ejemplos concretos
- Celebra logros financieros
- Da recomendaciones específicas basadas en los datos"""
                }
            ]

            # Agregar historial
            for msg in mensajes_historial:
                mensajes_api.append({
                    "role": msg.role,
                    "content": msg.contenido
                })

            # Agregar mensaje actual
            mensajes_api.append({
                "role": "user",
                "content": mensaje_usuario
            })

            # Llamar a GPT-4
            response = self.client.chat.completions.create(
                model=self.model,
                messages=mensajes_api,
                temperature=0.7,
                max_tokens=500
            )

            respuesta_ia = response.choices[0].message.content
            tokens_usados = response.usage.total_tokens

            return {
                'success': True,
                'respuesta': respuesta_ia,
                'tokens_usados': tokens_usados
            }

        except Exception as e:
            return {
                'success': False,
                'respuesta': f'Error con OpenAI: {str(e)}'
            }

    def _enviar_demo(self, conversacion, mensaje_usuario, contexto):
        """Modo demo con respuestas inteligentes basadas en patrones"""
        # Analizar el mensaje del usuario
        mensaje_lower = mensaje_usuario.lower()

        # Extraer datos del contexto para respuestas dinámicas
        import re
        ingresos_match = re.search(r'Ingresos mensuales: \$([0-9,]+)', contexto)
        gastos_match = re.search(r'Gastos totales: \$([0-9,]+)', contexto)
        ahorro_match = re.search(r'Ahorro/Balance: \$([0-9,]+)', contexto)

        ingresos = ingresos_match.group(1) if ingresos_match else "0"
        gastos = gastos_match.group(1) if gastos_match else "0"
        ahorro = ahorro_match.group(1) if ahorro_match else "0"

        # Patrones de respuesta inteligentes
        if any(word in mensaje_lower for word in ['cuánto gast', 'total gast', 'gasté']):
            respuesta = f"""💰 Análisis de Gastos del Mes:

📊 Has gastado **${gastos}** hasta ahora
💵 Tus ingresos son: **${ingresos}**
{'✅' if '-' not in ahorro else '⚠️'} Balance actual: **${ahorro}**

💡 **Consejo**: {'¡Vas muy bien! Sigue así.' if '-' not in ahorro else 'Considera reducir gastos variables para mejorar tu ahorro.'}

¿Quieres que analice alguna categoría específica?"""

        elif any(word in mensaje_lower for word in ['ahorr', 'ahorrar', 'ahorro']):
            respuesta = f"""💎 Oportunidades de Ahorro Detectadas:

Basado en tu situación actual:
- 💰 Ahorro actual: **${ahorro}**

🎯 **3 Recomendaciones Clave**:

1. 🍔 **Delivery/Restaurantes**: Reduce un 30% cocinando en casa
   → Ahorro estimado: ~$150,000/mes

2. 📱 **Servicios duplicados**: Revisa suscripciones
   → Ahorro estimado: ~$45,000/mes

3. 🚕 **Transporte**: Usa transporte público 3 días/semana
   → Ahorro estimado: ~$80,000/mes

💡 **Ahorro total potencial: ~$275,000/mes**

¿Quieres que te ayude a crear un plan específico?"""

        elif any(word in mensaje_lower for word in ['comprar', 'puedo comprar', 'alcanza']):
            respuesta = f"""🎯 Análisis de Capacidad de Compra:

Tu situación financiera actual:
- 💵 Ahorro mensual: **${ahorro}**
- 📊 Gastos promedio: **${gastos}**

💡 **Recomendación**:
Para compras grandes, te sugiero:

1. 📅 **Define el monto**: ¿Cuánto cuesta lo que quieres?
2. ⏱️ **Calcula tiempo**: Divide entre tu ahorro mensual
3. 🎯 **Crea una meta**: Usa la sección "Metas de Ahorro"

Ejemplo: 
- Producto: $2,000,000
- Ahorro mensual: ${ahorro}
- Tiempo estimado: {round(2000000 / (float(ahorro.replace(',', '')) if ahorro != '0' else 1))} meses

¿Quieres que cree una meta específica para ti?"""

        elif any(word in mensaje_lower for word in ['consejo', 'tip', 'recomend', 'ayud']):
            respuesta = f"""🌟 Consejos Financieros Personalizados:

Basado en tu perfil:

📈 **Nivel Financiero**: Intermedio
💰 **Ingresos**: ${ingresos}
📊 **Gastos**: ${gastos}

🎯 **Top 5 Consejos**:

1. 📝 **Regla 50/30/20**
   - 50% necesidades
   - 30% deseos
   - 20% ahorro

2. 🔥 **Mantén tu racha**
   - Registra gastos diariamente
   - Desbloquea logros
   - Gana puntos

3. 📊 **Revisa categorías**
   - Identifica gastos excesivos
   - Establece límites
   - Ajusta mensualmente

4. 🎯 **Define metas claras**
   - Metas a corto plazo (1-3 meses)
   - Metas a mediano plazo (3-12 meses)
   - Celebra cada logro

5. 💳 **Fondo de emergencia**
   - Ahorra 3-6 meses de gastos
   - Comienza con $500,000
   - Aumenta gradualmente

¿Sobre cuál quieres más detalles?"""

        elif any(word in mensaje_lower for word in ['presupuesto', 'cómo voy', 'como voy']):
            respuesta = f"""📊 Estado de tu Presupuesto:

**Resumen del Mes**:
- 💵 Ingresos: ${ingresos}
- 💰 Gastos: ${gastos}
- ✨ Balance: ${ahorro}

{'✅ **¡Excelente!** Estás dentro del presupuesto' if '-' not in ahorro else '⚠️ **Atención**: Gastos superan ingresos'}

📈 **Distribución Ideal**:
- Necesidades: 50% → ${int(float(ingresos.replace(',','')) * 0.5):,}
- Deseos: 30% → ${int(float(ingresos.replace(',','')) * 0.3):,}
- Ahorro: 20% → ${int(float(ingresos.replace(',','')) * 0.2):,}

💡 {'Sigue así, vas por buen camino' if '-' not in ahorro else 'Te recomiendo revisar gastos variables'}

¿Quieres ver el detalle por categorías?"""

        elif any(word in mensaje_lower for word in ['hola', 'hi', 'buenas', 'hey']):
            respuesta = """👋 ¡Hola! Soy **FinanBot**, tu asistente financiero personal.

Puedo ayudarte con:
- 💰 Análisis de gastos
- 📊 Oportunidades de ahorro
- 🎯 Planificación financiera
- 💡 Consejos personalizados
- 📈 Estado de presupuesto

**Pregúntame cosas como**:
- "¿Cuánto gasté este mes?"
- "¿En qué puedo ahorrar?"
- "¿Puedo comprar un iPhone?"
- "Dame consejos financieros"

¿En qué te ayudo hoy? 😊"""

        else:
            respuesta = f"""🤖 Entiendo tu consulta sobre: "{mensaje_usuario}"

Actualmente estoy en **modo demo** (sin conexión a IA en la nube).

📊 **Datos de tu situación**:
- Ingresos: ${ingresos}
- Gastos: ${gastos}
- Balance: ${ahorro}

💡 **Puedo ayudarte con**:
- Análisis de gastos
- Oportunidades de ahorro
- Planificación de compras
- Consejos financieros
- Estado de presupuesto

**Para activar IA completa**:
1. Configura Groq (GRATIS) o OpenAI
2. Reinicia el servidor
3. ¡Respuestas más inteligentes!

¿Quieres que analice algo específico con los datos actuales?"""

        return {
            'success': True,
            'respuesta': respuesta,
            'tokens_usados': 0
        }

        try:
            # Obtener o crear conversación
            conversacion = self.obtener_o_crear_conversacion(user, familia)

            # Guardar mensaje del usuario
            MensajeChatbot.objects.create(
                conversacion=conversacion,
                role='user',
                contenido=mensaje_usuario
            )

            # Obtener contexto financiero
            contexto = self.obtener_contexto_financiero(user, familia)

            # Preparar mensajes para la API
            mensajes_historial = list(conversacion.get_contexto_reciente(limite=10))

            mensajes_api = [
                {
                    "role": "system",
                    "content": f"""Eres un asistente financiero experto llamado 'FinanBot'. 
Tu trabajo es ayudar a las personas a administrar mejor su dinero familiar.

{contexto}

Personalidad:
- Amigable y motivador
- Práctico y directo
- Usa ejemplos concretos
- Celebra logros financieros
- Da recomendaciones específicas basadas en los datos"""
                }
            ]

            # Agregar historial
            for msg in mensajes_historial:
                mensajes_api.append({
                    "role": msg.role,
                    "content": msg.contenido
                })

            # Agregar mensaje actual
            mensajes_api.append({
                "role": "user",
                "content": mensaje_usuario
            })

            # Llamar a GPT-4
            response = self.client.chat.completions.create(
                model=self.model,
                messages=mensajes_api,
                temperature=0.7,
                max_tokens=500
            )

            respuesta_ia = response.choices[0].message.content
            tokens_usados = response.usage.total_tokens

            # Guardar respuesta del asistente
            MensajeChatbot.objects.create(
                conversacion=conversacion,
                role='assistant',
                contenido=respuesta_ia,
                tokens_usados=tokens_usados
            )

            return {
                'success': True,
                'respuesta': respuesta_ia,
                'conversacion_id': conversacion.id,
                'tokens_usados': tokens_usados
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'respuesta': f'Lo siento, ocurrió un error: {str(e)}'
            }

    def generar_analisis_automatico(self, user, familia):
        """Genera análisis automático de oportunidades de ahorro"""

        if not self.client:
            return None

        try:
            contexto = self.obtener_contexto_financiero(user, familia)

            prompt = f"""Basándote en esta información financiera:

{contexto}

Genera un análisis conciso (máximo 150 palabras) con:
1. Las 3 principales oportunidades de ahorro
2. Un monto estimado de ahorro potencial
3. Una recomendación prioritaria

Formato: Texto directo, usa emojis, sé específico con montos."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un asesor financiero experto."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )

            analisis_texto = response.choices[0].message.content

            # Guardar análisis
            analisis = AnalisisIA.objects.create(
                user=user,
                familia=familia,
                tipo='AHORRO',
                titulo='Oportunidades de Ahorro Detectadas',
                contenido=analisis_texto,
                relevancia=8
            )

            return analisis

        except Exception as e:
            print(f"Error generando análisis: {e}")
            return None

    def generar_prediccion_mes(self, user, familia):
        """Genera predicción de gastos para el próximo mes"""

        if not self.client:
            return None

        try:
            # Obtener histórico de 3 meses
            meses_data = []
            for i in range(1, 4):
                fecha = timezone.now() - timedelta(days=30*i)
                gastos = Gasto.objects.filter(
                    subcategoria__categoria__familia=familia,
                    fecha__month=fecha.month,
                    fecha__year=fecha.year
                ).aggregate(total=Sum('monto'))['total'] or 0
                meses_data.append({
                    'mes': fecha.strftime('%B'),
                    'total': float(gastos)
                })

            prompt = f"""Basándote en este histórico de gastos:

{chr(10).join([f"- {m['mes']}: ${m['total']:,.0f}" for m in meses_data])}

Predice el gasto total del próximo mes y explica por qué (máximo 100 palabras).
Incluye:
1. Monto predicho
2. Rango de confianza
3. Factores a considerar"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un analista financiero predictivo."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=200
            )

            prediccion_texto = response.choices[0].message.content

            # Guardar predicción
            prediccion = AnalisisIA.objects.create(
                user=user,
                familia=familia,
                tipo='PREDICCION',
                titulo='Predicción de Gastos Próximo Mes',
                contenido=prediccion_texto,
                datos_json={'historico': meses_data},
                relevancia=7
            )

            return prediccion

        except Exception as e:
            print(f"Error generando predicción: {e}")
            return None

    def cerrar_conversacion(self, conversacion_id):
        """Cierra una conversación"""
        try:
            conversacion = ConversacionChatbot.objects.get(id=conversacion_id)
            conversacion.activa = False
            conversacion.save()
            return True
        except:
            return False

    def obtener_conversaciones_usuario(self, user, familia=None):
        """Obtiene el historial de conversaciones"""
        query = ConversacionChatbot.objects.filter(user=user)
        if familia:
            query = query.filter(familia=familia)
        return query.order_by('-actualizada_en')[:10]
