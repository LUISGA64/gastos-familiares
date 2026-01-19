# 🤖 Cómo Obtener tu GROQ API KEY (100% GRATIS)

## ¿Por qué Groq?
- ✅ **Completamente GRATIS** - Sin tarjeta de crédito
- ✅ **14,400 requests/día** - Más que suficiente
- ✅ **Llama 3.3 70B** - Modelo de IA de última generación
- ✅ **10x más rápido** que GPT-4
- ✅ **Sin límites de uso** en plan gratuito

---

## 📝 Paso a Paso para Obtener tu API Key

### 1️⃣ Ir a Groq Console
Abre tu navegador y ve a:
```
https://console.groq.com/
```

### 2️⃣ Crear Cuenta
- Click en "Sign Up" (Registrarse)
- Puedes usar:
  - Google (recomendado)
  - GitHub
  - Email

**NO necesitas tarjeta de crédito** ✅

### 3️⃣ Verificar Email (si usaste email)
- Revisa tu bandeja de entrada
- Click en el link de verificación
- Regresa a console.groq.com

### 4️⃣ Acceder al Dashboard
Una vez logeado, verás el dashboard de Groq.

### 5️⃣ Crear API Key
1. En el menú lateral izquierdo, busca **"API Keys"**
2. Click en **"Create API Key"**
3. Ponle un nombre descriptivo: `gastos-familiares-railway`
4. Click en **"Submit"**

### 6️⃣ COPIAR TU API KEY ⚠️
**IMPORTANTE:** La API key se mostrará UNA SOLA VEZ.

```
Ejemplo de API Key:
gsk_1234567890abcdefghijklmnopqrstuvwxyz1234567890
```

- ⚠️ **Cópiala AHORA** - No podrás verla de nuevo
- 📋 Pégala en un lugar seguro temporalmente
- 🔒 NO la compartas públicamente

### 7️⃣ Configurar en Railway
Cuando configures las variables de entorno en Railway:

```
Variable: GROQ_API_KEY
Valor: gsk_tu_api_key_aqui
```

---

## ✅ Verificar que Funciona

### Opción 1: En tu entorno local
1. Crea archivo `.env` en la raíz del proyecto:
   ```env
   AI_PROVIDER=groq
   GROQ_API_KEY=gsk_tu_api_key_aqui
   ```

2. Ejecuta el servidor:
   ```bash
   python manage.py runserver
   ```

3. Ve al chatbot en: `http://localhost:8000/chatbot/`

4. Escribe un mensaje de prueba

Si responde, ¡funciona! ✅

### Opción 2: Después del deploy en Railway
1. Una vez desplegado, ve a tu app
2. Login con tu usuario
3. Ve al chatbot
4. Envía un mensaje

---

## 📊 Límites del Plan Gratuito de Groq

| Característica | Límite Gratuito |
|----------------|-----------------|
| Requests/día | 14,400 |
| Requests/minuto | 30 |
| Tokens/minuto | 130,000 |
| Modelos disponibles | Llama 3.3 70B, Mixtral, etc. |
| Precio | $0 USD |
| Tarjeta requerida | NO ❌ |

**Suficiente para:**
- Aplicación con 50-100 usuarios
- ~480 conversaciones/día
- Uso personal y pruebas

---

## 🔄 ¿Qué pasa si se acaba el límite?

Si llegas al límite diario (14,400 requests):
1. Espera 24 horas para que se resetee
2. O considera el plan Pro de Groq (~$0.27 por 1M tokens)
3. O cambia a modo "demo" temporalmente

Para cambiar a modo demo (sin API):
```env
AI_PROVIDER=demo
```

---

## 🆘 Problemas Comunes

### Error: "Invalid API key"
**Solución:** 
- Verifica que copiaste la API key completa
- Asegúrate de que empiece con `gsk_`
- Revisa que no tenga espacios al inicio/final

### Error: "Rate limit exceeded"
**Solución:**
- Espera 1 minuto (límite por minuto)
- O espera 24h (límite diario)
- Verifica cuántas requests estás haciendo

### Error: "No API key found"
**Solución:**
- Verifica que la variable `GROQ_API_KEY` esté en Railway
- Asegúrate de que `AI_PROVIDER=groq`
- Redeploy la aplicación

---

## 🔐 Seguridad de la API Key

### ✅ HACER:
- Guardarla en variables de entorno
- Usar `.env` localmente (en `.gitignore`)
- Configurarla en Railway Variables
- Regenerarla si se expone

### ❌ NO HACER:
- Subirla a GitHub
- Compartirla públicamente
- Hardcodearla en el código
- Exponerla en frontend

---

## 🔄 Regenerar API Key (si se expone)

Si accidentalmente expones tu API key:

1. Ve a https://console.groq.com/
2. API Keys
3. Click en el ícono de basura 🗑️ junto a la key expuesta
4. Crear nueva API key
5. Actualizar en Railway Variables

---

## 📚 Recursos Adicionales

- 📖 Documentación Groq: https://console.groq.com/docs
- 🎯 Playground: https://console.groq.com/playground
- 💬 Comunidad: https://discord.gg/groq
- 📊 Dashboard de uso: https://console.groq.com/usage

---

## 💡 Tips Pro

### Monitorear uso
Ve a Groq Console > Usage para ver:
- Requests consumidos
- Límite restante
- Histórico de uso

### Múltiples API keys
Puedes crear varias API keys para:
- Desarrollo local
- Producción (Railway)
- Testing

### Fallback automático
Si Groq falla, la app automáticamente usa modo demo ✅

---

## ✨ ¡Listo!

Ya tienes tu GROQ API KEY gratis y lista para usar en Railway.

**Recuerda:**
- Copiarla en Railway Variables: `GROQ_API_KEY=gsk_tu_key`
- Configurar: `AI_PROVIDER=groq`
- ¡Disfrutar de 14,400 conversaciones IA gratis al día! 🎉

---

**¿Necesitas ayuda?**
- 📖 Ver: DEPLOY_RAILWAY.md
- 📋 Ver: RAILWAY_CHECKLIST.txt
- 🆘 Docs: https://console.groq.com/docs
