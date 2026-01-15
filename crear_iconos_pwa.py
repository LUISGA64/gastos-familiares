"""
Script para generar iconos PWA placeholder
"""
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("❌ Pillow no está instalado")
    print("Instalando Pillow...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    from PIL import Image, ImageDraw, ImageFont
    print("✅ Pillow instalado correctamente")

import os

# Crear directorio si no existe
os.makedirs('static/icons', exist_ok=True)

print("🎨 GENERANDO ICONOS PWA")
print("="*60)

# Tamaños necesarios para PWA
tamaños = [72, 96, 128, 144, 152, 192, 384, 512]

# Colores del tema (mismo que en la app)
color_fondo = (52, 152, 219)  # #3498db - Azul
color_acento = (255, 255, 255)  # Blanco
color_texto = (44, 62, 80)  # #2c3e50 - Azul oscuro

for tamaño in tamaños:
    print(f"Generando icon-{tamaño}x{tamaño}.png...", end=" ")

    # Crear imagen con fondo azul
    img = Image.new('RGB', (tamaño, tamaño), color_fondo)
    draw = ImageDraw.Draw(img)

    # Dibujar círculo blanco en el centro
    margen = tamaño // 6
    draw.ellipse(
        [margen, margen, tamaño - margen, tamaño - margen],
        fill=color_acento,
        outline=color_acento
    )

    # Agregar símbolo $ en el centro
    try:
        # Intentar usar fuente del sistema
        font_size = tamaño // 2
        try:
            # Windows
            font = ImageFont.truetype("C:/Windows/Fonts/Arial.ttf", font_size)
        except:
            try:
                # Otra ubicación común
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                # Fuente por defecto
                font = ImageFont.load_default()
    except Exception as e:
        font = ImageFont.load_default()

    # Dibujar el símbolo $
    texto = "$"

    # Calcular posición centrada
    try:
        bbox = draw.textbbox((0, 0), texto, font=font)
        ancho_texto = bbox[2] - bbox[0]
        alto_texto = bbox[3] - bbox[1]
    except:
        # Fallback para versiones antiguas de Pillow
        ancho_texto = font_size // 2
        alto_texto = font_size

    x = (tamaño - ancho_texto) // 2
    y = (tamaño - alto_texto) // 2 - tamaño // 20

    # Dibujar texto
    draw.text((x, y), texto, fill=color_texto, font=font)

    # Guardar imagen
    ruta = f'static/icons/icon-{tamaño}x{tamaño}.png'
    img.save(ruta, 'PNG', optimize=True)

    # Verificar tamaño del archivo
    tamaño_kb = os.path.getsize(ruta) / 1024
    print(f"✅ ({tamaño_kb:.1f} KB)")

print("\n" + "="*60)
print("✅ TODOS LOS ICONOS GENERADOS CORRECTAMENTE")
print("="*60)

# Listar archivos creados
print("\n📁 Archivos creados en static/icons/:")
for archivo in sorted(os.listdir('static/icons')):
    if archivo.endswith('.png'):
        ruta = os.path.join('static/icons', archivo)
        tamaño = os.path.getsize(ruta) / 1024
        print(f"   ✅ {archivo} ({tamaño:.1f} KB)")

print("\n" + "="*60)
print("💡 SIGUIENTE PASO:")
print("="*60)
print("""
1. ✅ Iconos placeholder creados
2. ⏳ Reinicia el servidor si está corriendo
3. ⏳ Recarga la página (Ctrl+Shift+R)
4. ✅ Los errores 404 de iconos desaparecerán

OPCIONAL - Para iconos profesionales:
- Visita: https://realfavicongenerator.net/
- Sube un logo de 512x512 px
- Descarga y reemplaza los iconos en static/icons/
""")

print("\n🎨 Los iconos actuales son placeholders funcionales")
print("   Puedes reemplazarlos después con diseños profesionales")
print("")

