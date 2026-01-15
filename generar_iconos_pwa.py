"""
Script para generar iconos para la PWA
Nota: Este es un placeholder. Para producción, usa herramientas como:
- https://realfavicongenerator.net/
- https://www.pwabuilder.com/imageGenerator
"""

print("""
📱 GENERACIÓN DE ICONOS PARA PWA

Para crear los iconos necesarios para tu PWA:

OPCIÓN 1 - Online (Recomendado):
================================
1. Visita: https://realfavicongenerator.net/
2. Sube tu logo (preferiblemente 512x512 px)
3. Descarga el paquete completo
4. Copia los iconos a: DjangoProject/static/icons/

OPCIÓN 2 - PWA Builder:
======================
1. Visita: https://www.pwabuilder.com/imageGenerator
2. Sube tu imagen
3. Descarga todos los tamaños
4. Organiza en: DjangoProject/static/icons/

OPCIÓN 3 - Crear placeholders manualmente:
==========================================
Puedes usar emojis o texto como placeholders temporales:

Tamaños necesarios:
- icon-72x72.png
- icon-96x96.png
- icon-128x128.png
- icon-144x144.png
- icon-152x152.png
- icon-192x192.png
- icon-384x384.png
- icon-512x512.png

OPCIÓN 4 - Usar Pillow (Python):
================================
pip install pillow

Luego ejecuta el siguiente código:
""")

codigo_ejemplo = '''
from PIL import Image, ImageDraw, ImageFont
import os

# Crear directorio
os.makedirs('static/icons', exist_ok=True)

tamaños = [72, 96, 128, 144, 152, 192, 384, 512]
colores = {
    'fondo': (52, 152, 219),  # Azul
    'texto': (255, 255, 255)   # Blanco
}

for tamaño in tamaños:
    # Crear imagen
    img = Image.new('RGB', (tamaño, tamaño), colores['fondo'])
    draw = ImageDraw.Draw(img)
    
    # Dibujar círculo
    margen = tamaño // 8
    draw.ellipse([margen, margen, tamaño-margen, tamaño-margen], 
                 fill=colores['texto'])
    
    # Agregar símbolo $ en el centro
    try:
        font_size = tamaño // 2
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    texto = "$"
    bbox = draw.textbbox((0, 0), texto, font=font)
    ancho_texto = bbox[2] - bbox[0]
    alto_texto = bbox[3] - bbox[1]
    
    x = (tamaño - ancho_texto) // 2
    y = (tamaño - alto_texto) // 2 - tamaño // 10
    
    draw.text((x, y), texto, fill=colores['fondo'], font=font)
    
    # Guardar
    img.save(f'static/icons/icon-{tamaño}x{tamaño}.png')
    print(f"✅ Creado: icon-{tamaño}x{tamaño}.png")

print("\\n✅ Todos los iconos creados!")
'''

print(codigo_ejemplo)

print("\n" + "="*60)
print("💡 RECOMENDACIÓN:")
print("="*60)
print("""
Para un resultado profesional:
1. Diseña un logo en 512x512 px
2. Usa realfavicongenerator.net
3. Descarga y copia a static/icons/

Para testing rápido:
1. Ejecuta el código Python de arriba
2. Tendrás iconos funcionales (no muy bonitos)
3. Reemplaza después con diseños profesionales
""")

