# 🎯 Guía Rápida Visual: Obtener Token de Replicate

## En 3 minutos ⏱️

---

### 📍 PASO 1: Ir a la página de API Tokens

```
🌐 URL: https://replicate.com/account/api-tokens
```

O navegar manualmente:
1. Login en https://replicate.com
2. Click en tu avatar (arriba a la derecha)
3. Click en "Account settings"
4. En el menú lateral: "API tokens"

---

### 🔑 PASO 2: Crear nuevo token

**Lo que verás:**

```
┌────────────────────────────────────────────────────┐
│                                                     │
│  🔐 API tokens                                      │
│                                                     │
│  Use API tokens to authenticate your requests      │
│  to the Replicate API.                             │
│                                                     │
│  ┌──────────────────┐                              │
│  │  Create token   │                               │
│  └──────────────────┘                              │
│                                                     │
│  📝 No tokens yet                                   │
│                                                     │
└────────────────────────────────────────────────────┘
```

**Acción:**
- Click en el botón azul **"Create token"**

---

### 📝 PASO 3: Darle un nombre (opcional)

**Aparecerá un modal:**

```
┌────────────────────────────────────────────────────┐
│  Create API token                                   │
│                                                     │
│  Name (optional)                                    │
│  ┌──────────────────────────────────────────────┐  │
│  │ ai-model-discovery                           │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  ┌─────────┐  ┌────────┐                           │
│  │ Cancel │  │ Create │                            │
│  └─────────┘  └────────┘                           │
└────────────────────────────────────────────────────┘
```

**Acción:**
- Opcional: Escribir un nombre descriptivo
- Click en **"Create"**

---

### 💾 PASO 4: COPIAR EL TOKEN ⚠️

**IMPORTANTE:** El token se mostrará **UNA SOLA VEZ**

```
┌────────────────────────────────────────────────────┐
│  ✅ New API token created                           │
│                                                     │
│  ⚠️  This token will only be shown once.            │
│      Make sure to copy it now.                     │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │ r8_YourActualTokenWillAppearHere          │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  ┌─────────────────────────┐  ┌──────┐             │
│  │ 📋 Copy to clipboard    │  │ Done │            │
│  └─────────────────────────┘  └──────┘             │
└────────────────────────────────────────────────────┘
```

**Acciones:**
1. Click en **"📋 Copy to clipboard"**
2. O seleccionar todo el texto y Ctrl+C
3. Guardar en un lugar seguro (editor de texto, password manager)

**Formato del token:** Siempre comienza con `r8_`

---

### 🖥️ PASO 5: Configurar en tu terminal

#### Linux / Mac:

```bash
# En la terminal
export REPLICATE_API_TOKEN="r8_tu_token_aqui"

# Verificar
echo $REPLICATE_API_TOKEN
```

#### Windows (PowerShell):

```powershell
# En PowerShell
$env:REPLICATE_API_TOKEN = "r8_tu_token_aqui"

# Verificar
echo $env:REPLICATE_API_TOKEN
```

---

### ✅ PASO 6: Verificar que funciona

```bash
# Ejecutar script de verificación
python verify_replicate_setup.py
```

**Salida esperada:**

```
============================================================
🔁 VERIFICACIÓN DE REPLICATE API
============================================================

📝 Paso 1: Verificando variable de entorno...
✅ Variable de entorno configurada
   Primeros 15 caracteres: r8_Hw9j8K2Pq4R...
   Longitud: 40 caracteres

🔐 Paso 2: Probando autenticación con API...
✅ Autenticación exitosa!
   Usuario: tu_username
   Tipo de cuenta: user

📚 Paso 3: Probando endpoint de modelos...
✅ Endpoint de modelos funcional
   Modelos en respuesta: 20
   Ejemplo de modelo:
     - Nombre: stability-ai/sdxl
     - Runs: 45,234,567
     - URL: https://replicate.com/stability-ai/sdxl

📦 Paso 4: Verificando dependencias...
✅ requests instalado (v2.31.0)
✅ replicate SDK instalado (opcional)

============================================================
🎉 CONFIGURACIÓN COMPLETA Y FUNCIONAL
============================================================
```

---

## 🚨 Problemas Comunes

### ❌ Error: "REPLICATE_API_TOKEN no está configurada"

**Solución:**
```bash
export REPLICATE_API_TOKEN="r8_tu_token_aqui"
```

### ❌ Error: "Token inválido"

**Causas posibles:**
1. Token mal copiado (faltan caracteres)
2. Token con espacios extra
3. Token expirado

**Solución:**
1. Generar nuevo token en https://replicate.com/account/api-tokens
2. Copiar **TODO** el token
3. Configurar nuevamente

### ❌ Error: "Timeout"

**Solución:**
- Verificar conexión a internet
- Desactivar VPN si está activo
- Verificar firewall

---

## 📚 Siguiente Paso

Una vez verificado, ya puedes usar Replicate:

```python
from utils.replicate_repository import ReplicateRepository

repo = ReplicateRepository()
models = repo.fetch_models(limit=50)

print(f"✅ {len(models)} modelos descargados")
```

---

## 🔗 Enlaces Útiles

- **Crear token**: https://replicate.com/account/api-tokens
- **Documentación**: https://replicate.com/docs
- **API Reference**: https://replicate.com/docs/reference/http
- **Guía completa**: `docs/REPLICATE_SETUP.md`
- **Script verificación**: `verify_replicate_setup.py`

---

**¿Dudas?** Revisa la guía completa en `docs/REPLICATE_SETUP.md`
