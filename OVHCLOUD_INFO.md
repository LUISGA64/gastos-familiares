# 🌐 INFORMACIÓN ESPECÍFICA - OVHCLOUD

## ✅ ¿Por qué OVHcloud?

OVHcloud es uno de los **mayores proveedores de hosting de Europa** y ofrece una excelente relación calidad-precio.

### Ventajas de OVHcloud
- ✅ **Precio excelente:** Desde €4/mes
- ✅ **Rendimiento:** Hardware de alta calidad
- ✅ **Datacenters globales:** Europa, América, Asia, África
- ✅ **Empresa europea:** Cumple RGPD/GDPR
- ✅ **Soporte 24/7:** En español
- ✅ **Red propia:** Anti-DDoS incluido
- ✅ **Sin cargos ocultos:** Precio fijo mensual
- ✅ **Ancho de banda ilimitado:** En la mayoría de planes

---

## 💰 PLANES VPS DE OVHCLOUD

### VPS Starter - €4.80/mes
- **RAM:** 2GB
- **vCPU:** 1
- **Almacenamiento:** 20GB SSD
- **Ancho de banda:** 100 Mbps
- **Ideal para:** Desarrollo, testing, apps pequeñas

### VPS Value - €8.40/mes ⭐ RECOMENDADO
- **RAM:** 4GB
- **vCPU:** 2
- **Almacenamiento:** 40GB SSD
- **Ancho de banda:** 250 Mbps
- **Ideal para:** Producción, apps medianas (100-500 usuarios)

### VPS Essential - €14.40/mes
- **RAM:** 8GB
- **vCPU:** 4
- **Almacenamiento:** 80GB SSD
- **Ancho de banda:** 500 Mbps
- **Ideal para:** Apps grandes (500-2000 usuarios)

### VPS Comfort - €23.00/mes
- **RAM:** 16GB
- **vCPU:** 8
- **Almacenamiento:** 160GB SSD
- **Ancho de banda:** 1 Gbps
- **Ideal para:** Apps enterprise

---

## 🌍 DATACENTERS DISPONIBLES

OVHcloud tiene datacenters en:

### Europa
- 🇫🇷 **Francia (Gravelines, Roubaix, Estrasburgo)**
- 🇬🇧 **Reino Unido (Londres)**
- 🇩🇪 **Alemania (Frankfurt, Limburg)**
- 🇵🇱 **Polonia (Varsovia)**
- 🇮🇹 **Italia**

### América
- 🇨🇦 **Canadá (Beauharnois, Toronto)**
- 🇺🇸 **USA (Oregon, Virginia)**

### Asia-Pacífico
- 🇸🇬 **Singapur**
- 🇦🇺 **Australia (Sídney)**

**Recomendación para tu proyecto:**
- **España/Europa:** Francia (Gravelines) - Mejor latencia
- **LATAM:** Canadá (Beauharnois) - Más cercano
- **USA:** Oregon o Virginia

---

## 🚀 PASOS PARA CREAR VPS EN OVHCLOUD

### 1. Crear cuenta
1. Ve a https://www.ovhcloud.com/es/
2. Click en **"Crear cuenta"** o **"Sign up"**
3. Completa tus datos
4. Verifica tu email

### 2. Pedir VPS
1. Ir a https://www.ovhcloud.com/es/vps/
2. Click en **"Pedir"**
3. Selecciona el plan (Value €8.40/mes recomendado)
4. Configura:
   - **Distribución:** Ubuntu 22.04 LTS
   - **Datacenter:** Elige según tu ubicación
   - **Periodo:** Mensual (puedes cambiar después)
5. Añade al carrito
6. Procede al pago
7. Completa el pedido

### 3. Acceder a tu VPS
**Importante:** OVHcloud te enviará las credenciales por email:
- **Subject:** "Instalación de su VPS" o "Your VPS installation"
- **Contenido:** IP, usuario (root), contraseña temporal

**Email puede tardar:** 5-15 minutos después del pedido

### 4. Conectar por SSH
```powershell
# Desde PowerShell o CMD
ssh root@TU_IP_AQUI

# Ingresa la contraseña temporal del email
# OVHcloud te pedirá cambiar la contraseña en el primer login:
# 1. Ingresa contraseña actual
# 2. Ingresa nueva contraseña
# 3. Confirma nueva contraseña
```

### 5. Verificar sistema
```bash
# Verificar versión de Ubuntu
lsb_release -a
# Debería mostrar: Ubuntu 22.04.x LTS

# Verificar Python
python3 --version
# Debería mostrar: Python 3.10.x o superior

# Actualizar sistema
apt update && apt upgrade -y
```

---

## 🔧 PANEL DE CONTROL DE OVHCLOUD

### Acceder al panel
1. Ve a https://www.ovh.com/manager/
2. Inicia sesión con tu cuenta
3. Click en **"Servidores"** > **"VPS"**
4. Selecciona tu VPS

### Funciones útiles del panel
- **Reiniciar VPS:** En caso de problemas
- **Modo rescue:** Para recuperación
- **Reinstalar SO:** Si necesitas empezar de cero
- **Estadísticas:** CPU, RAM, disco, red
- **Reverse DNS:** Configurar PTR para email
- **Snapshot/Backup:** Copias de seguridad (adicional)

---

## 💳 MÉTODOS DE PAGO

OVHcloud acepta:
- ✅ Tarjeta de crédito/débito (Visa, Mastercard)
- ✅ PayPal
- ✅ Transferencia bancaria
- ✅ Domiciliación bancaria (SEPA)

**Facturación:**
- Mensual por defecto
- Puedes cambiar a anual (descuento ~10%)
- Sin compromiso de permanencia

---

## 🆘 SOPORTE DE OVHCLOUD

### Canales de soporte
- **Ticket system:** Desde el panel de control
- **Teléfono:** Disponible según plan
- **Comunidad:** https://community.ovh.com/
- **Guías:** https://help.ovhcloud.com/

### Horarios
- Soporte técnico: 24/7
- Soporte comercial: Horario laboral

### Idiomas
- ✅ Español
- ✅ Inglés
- ✅ Francés
- ✅ Y más...

---

## 📊 COMPARACIÓN CON OTROS PROVEEDORES

| Característica | OVHcloud | Digital Ocean | Hetzner |
|----------------|----------|---------------|---------|
| **Precio (4GB)** | €8.40/mes | $24/mes (~€22) | €4.50/mes |
| **Ancho de banda** | 250 Mbps | 4TB/mes | 20TB/mes |
| **Datacenters** | Global | Global | Europa/USA |
| **Anti-DDoS** | ✅ Incluido | ❌ Adicional | ✅ Incluido |
| **Soporte español** | ✅ SÍ | ❌ Solo inglés | ❌ Solo inglés/alemán |
| **Empresa europea** | ✅ Francia | ❌ USA | ✅ Alemania |
| **RGPD/GDPR** | ✅ Nativo | ⚠️ Adaptado | ✅ Nativo |

**Conclusión:** OVHcloud ofrece excelente precio y es ideal si prefieres un proveedor europeo con soporte en español.

---

## 🔒 SEGURIDAD

### Anti-DDoS incluido
OVHcloud incluye protección Anti-DDoS en todos los planes:
- Protección de red
- Mitigación automática
- Sin costo adicional

### Firewall
- Firewall de red configurable desde panel
- Puedes combinar con UFW en el servidor

### Backups
- **Snapshot manual:** Gratis (1 snapshot a la vez)
- **Backup automático:** Servicio adicional (~€2-4/mes)
- **Recomendación:** Usar backups de PostgreSQL + snapshot ocasional

---

## 🎯 RECOMENDACIÓN PARA TU PROYECTO DJANGO

### Plan recomendado
**VPS Value - €8.40/mes**
- Suficiente para 100-500 usuarios concurrentes
- 4GB RAM para Django + PostgreSQL + Nginx
- 2 vCPUs para procesar requests
- 40GB para código + base de datos + logs

### Datacenter recomendado
- **Si estás en España/Europa:** Francia (Gravelines)
- **Si tus usuarios son LATAM:** Canadá (Beauharnois)
- **Si tus usuarios son USA:** Oregon o Virginia

### Escalabilidad
Puedes upgradear fácilmente desde el panel:
- Value (€8.40) → Essential (€14.40) → Comfort (€23)
- Reinicio requerido (downtime ~5 minutos)

---

## 📝 CHECKLIST OVHCLOUD

Antes de empezar el deploy:

- [ ] Cuenta de OVHcloud creada
- [ ] Email verificado
- [ ] Método de pago agregado
- [ ] VPS pedido (Value recomendado)
- [ ] Email con credenciales recibido
- [ ] IP pública anotada
- [ ] Contraseña cambiada en primer login
- [ ] SSH funcionando
- [ ] Sistema actualizado

---

## 🚀 SIGUIENTE PASO

Una vez que tengas tu VPS de OVHcloud creado y acceso SSH:

👉 **Sigue la guía:** `DEPLOY_RAPIDO.md`

O si prefieres una guía más general:

👉 **Sigue la guía:** `DEPLOY_VPS_UNIVERSAL.md`

---

## 📚 ENLACES ÚTILES

- **Web oficial:** https://www.ovhcloud.com/es/
- **VPS:** https://www.ovhcloud.com/es/vps/
- **Panel de control:** https://www.ovh.com/manager/
- **Guías:** https://help.ovhcloud.com/
- **Comunidad:** https://community.ovh.com/
- **Status:** https://www.status-ovhcloud.com/

---

**OVHcloud es una excelente opción para tu proyecto Django! 🎉**

**Fecha:** 2026-01-21  
**Estado:** ✅ Información actualizada
