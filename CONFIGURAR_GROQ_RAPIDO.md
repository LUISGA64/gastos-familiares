# 🎯 CONFIGURACIÓN RÁPIDA DE GROQ

## Método 1: Edición Manual (RECOMENDADO)

### Paso 1: Abre el archivo .env
```
Ruta: C:\Users\luisg\PycharmProjects\DjangoProject\.env
```

### Paso 2: Cambia estas 2 líneas:

**ANTES**:
```env
AI_PROVIDER=demo
GROQ_API_KEY=
```

**DESPUÉS**:
```env
AI_PROVIDER=groq
GROQ_API_KEY=gsk_tu_api_key_real_aqui
```

### Paso 3: Guarda (Ctrl+S)

### Paso 4: Reinicia servidor
```bash
# En la terminal:
Ctrl+C
python manage.py runserver
```

### Paso 5: Prueba
```
http://127.0.0.1:8000/chatbot/conversacion/
```

---

## Método 2: Usando PowerShell

Si prefieres hacerlo desde terminal:

```powershell
# Detener servidor (Ctrl+C primero)

# Configurar
$env:AI_PROVIDER="groq"
$env:GROQ_API_KEY="gsk_tu_api_key_aqui"

# O editar .env directamente:
(Get-Content .env) -replace 'AI_PROVIDER=demo', 'AI_PROVIDER=groq' | Set-Content .env
(Get-Content .env) -replace 'GROQ_API_KEY=', 'GROQ_API_KEY=gsk_tu_key_aqui' | Set-Content .env

# Reiniciar
python manage.py runserver
```

---

## ✅ Verificar que Funcione

### 1. Ve al chatbot:
```
http://127.0.0.1:8000/chatbot/conversacion/
```

### 2. Escribe:
```
"¿Cuánto gasté este mes?"
```

### 3. Si funciona verás:
```
✅ Respuesta de IA real (más elaborada que modo demo)
✅ En la consola: "Usando Groq API..."
✅ Respuesta en ~1-2 segundos
```

### 4. Si hay error verás:
```
❌ "Groq API key no configurada"
❌ Revisa que pegaste bien la key
```

---

## 🎯 Tu API Key

Debe verse así:
```
gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

- Empieza con `gsk_`
- Tiene ~50 caracteres
- Solo letras, números y guiones bajos

---

¡Configúralo y pruébalo! 🚀
