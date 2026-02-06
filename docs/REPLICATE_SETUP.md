# 🔁 Guía Completa de Configuración - Replicate API

**Fecha**: Enero 2026  
**Autor**: Edmundo Mori

---

## 📌 ¿Qué es Replicate?

Replicate es una plataforma que permite ejecutar modelos de ML/AI en la nube sin configurar infraestructura. Ofrece:

- **Inference endpoints** listos para usar
- **Métricas de uso** (run_count) que indican popularidad real
- **API REST bien documentada**
- Modelos de difusión, LLMs, visión, audio, y más

**Sitio oficial**: https://replicate.com

---

## 🎯 Requisitos

1. **Cuenta de Replicate** (gratuita)
2. **API Token** (gratis con límites generosos)
3. **Python 3.8+**

---

## 📝 Paso 1: Crear Cuenta en Replicate

### 1.1 Registrarse

1. Ir a https://replicate.com
2. Click en **"Sign up"** (esquina superior derecha)
3. Opciones de registro:
   - **GitHub** (recomendado - más rápido)
   - **Google**
   - **Email + Password**

4. Completar el registro siguiendo las instrucciones

### 1.2 Verificar cuenta

Si usaste email, verifica tu correo electrónico haciendo click en el enlace de confirmación.

---

## 🔑 Paso 2: Obtener API Token

### 2.1 Acceder a API Tokens

1. Una vez logueado, ir a: https://replicate.com/account/api-tokens
   
   **O navegar manualmente:**
   - Click en tu avatar (esquina superior derecha)
   - Click en **"Account settings"**
   - En el menú lateral izquierdo, click en **"API tokens"**

### 2.2 Crear un nuevo token

En la página de API tokens verás:

```
┌─────────────────────────────────────────┐
│  API tokens                              │
│                                          │
│  Use API tokens to authenticate your    │
│  requests to the Replicate API.         │
│                                          │
│  [ Create token ]                        │
│                                          │
│  No tokens yet                           │
└─────────────────────────────────────────┘
```

1. Click en **"Create token"**

2. (Opcional) Darle un nombre descriptivo al token:
   - Ejemplo: `ai-model-discovery`
   - Ejemplo: `dev-local`
   - Si lo dejas vacío, se genera un nombre automático

3. Click en **"Create"**

### 2.3 Copiar el token

⚠️ **IMPORTANTE**: El token se mostrará **UNA SOLA VEZ**

```
┌─────────────────────────────────────────────────┐
│  New API token created                           │
│                                                  │
│  This token will only be shown once.             │
│  Make sure to copy it now.                       │
│                                                  │
│  r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx        │
│                                                  │
│  [ Copy to clipboard ]    [ Done ]               │
└─────────────────────────────────────────────────┘
```

**Acción**: Click en **"Copy to clipboard"** o selecciona y copia el token manualmente.

**Formato del token**: Siempre comienza con `r8_` seguido de caracteres alfanuméricos.

---

## 💾 Paso 3: Configurar el Token en tu Sistema

### Opción A: Variable de Entorno (Recomendado)

#### En Linux/Mac

**Temporal (solo sesión actual):**

```bash
export REPLICATE_API_TOKEN="r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

**Permanente (añadir a tu shell config):**

```bash
# Para bash
echo 'export REPLICATE_API_TOKEN="r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"' >> ~/.bashrc
source ~/.bashrc

# Para zsh
echo 'export REPLICATE_API_TOKEN="r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"' >> ~/.zshrc
source ~/.zshrc
```

#### En Windows

**PowerShell:**

```powershell
$env:REPLICATE_API_TOKEN = "r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

**Permanente (System Properties):**

1. Buscar "Environment Variables" en el menú Start
2. Click en "Edit the system environment variables"
3. Click en "Environment Variables..."
4. En "User variables", click "New..."
5. Variable name: `REPLICATE_API_TOKEN`
6. Variable value: `r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
7. Click OK

### Opción B: Archivo .env

En el directorio de tu proyecto:

```bash
# Crear o editar archivo .env
echo 'REPLICATE_API_TOKEN=r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' >> .env
```

**Contenido del archivo `.env`:**

```bash
# Replicate API
REPLICATE_API_TOKEN=r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Otros tokens (opcional)
HF_TOKEN=hf_...
KAGGLE_USERNAME=...
KAGGLE_KEY=...
```

⚠️ **Seguridad**: Asegúrate de que `.env` esté en tu `.gitignore`:

```bash
echo '.env' >> .gitignore
```

---

## 🧪 Paso 4: Verificar la Configuración

### 4.1 Verificar variable de entorno

```bash
# En Linux/Mac/Windows (Git Bash)
echo $REPLICATE_API_TOKEN

# En Windows PowerShell
echo $env:REPLICATE_API_TOKEN
```

**Salida esperada**: `r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 4.2 Probar con Python

```python
import os

token = os.getenv('REPLICATE_API_TOKEN')

if token:
    print(f"✅ Token configurado correctamente")
    print(f"   Primeros 10 caracteres: {token[:10]}...")
else:
    print("❌ Token no encontrado")
    print("   Asegúrate de haber ejecutado:")
    print("   export REPLICATE_API_TOKEN='tu_token_aqui'")
```

### 4.3 Probar con requests

```python
import os
import requests

token = os.getenv('REPLICATE_API_TOKEN')
headers = {"Authorization": f"Bearer {token}"}

# Probar endpoint de cuenta
response = requests.get(
    "https://api.replicate.com/v1/account",
    headers=headers
)

if response.status_code == 200:
    data = response.json()
    print(f"✅ Autenticación exitosa")
    print(f"   Usuario: {data.get('username')}")
    print(f"   Tipo: {data.get('type')}")
else:
    print(f"❌ Error: {response.status_code}")
    print(f"   {response.text}")
```

---

## 📦 Paso 5: Instalar Dependencias

```bash
# SDK oficial de Replicate (opcional pero recomendado)
pip install replicate

# Solo requests (mínimo necesario)
pip install requests
```

---

## 🚀 Paso 6: Uso en el Proyecto

### Con el repositorio ReplicateRepository

```python
from utils.replicate_repository import ReplicateRepository

# El token se lee automáticamente de la variable de entorno
replicate_repo = ReplicateRepository()

# Obtener modelos
models = replicate_repo.fetch_models(limit=50)

print(f"✅ Descargados {len(models)} modelos de Replicate")
for model in models[:5]:
    print(f"  - {model.title} (runs: {model.extra_metadata.get('run_count', 0)})")
```

### Uso directo con la API

```python
import os
import requests

token = os.getenv('REPLICATE_API_TOKEN')
headers = {"Authorization": f"Bearer {token}"}

# Listar modelos públicos
response = requests.get(
    "https://api.replicate.com/v1/models",
    headers=headers
)

data = response.json()
print(f"Total modelos: {len(data['results'])}")
```

---

## 📊 Límites de Rate (Rate Limits)

Replicate tiene límites generosos:

| Endpoint | Límite |
|----------|--------|
| Crear predicción | **600 requests/minuto** |
| Otros endpoints | **3,000 requests/minuto** |

Si excedes los límites, recibirás HTTP 429:

```json
{
  "detail": "Request was throttled. Expected available in 1 second."
}
```

**Solución**: Implementar retry con backoff exponencial (ya incluido en el conector).

---

## 🔒 Seguridad del Token

### ✅ Buenas Prácticas

1. **Nunca commitear tokens a Git**
   ```bash
   # Verificar que .env está en .gitignore
   grep -q ".env" .gitignore || echo ".env" >> .gitignore
   ```

2. **Usar variables de entorno en producción**
   - En servidores: Variables de entorno del sistema
   - En CI/CD: Secrets del sistema (GitHub Secrets, GitLab Variables, etc.)

3. **Rotar tokens periódicamente**
   - Eliminar tokens viejos desde https://replicate.com/account/api-tokens
   - Crear nuevos tokens cada 3-6 meses

4. **Tokens diferentes por entorno**
   - `REPLICATE_API_TOKEN_DEV` para desarrollo
   - `REPLICATE_API_TOKEN_PROD` para producción

### ❌ NO hacer

- ❌ Hardcodear el token en el código:
  ```python
  # MAL - No hacer esto
  token = "r8_xxxxxxxxxxxxx"
  ```

- ❌ Commitear archivos con tokens:
  ```bash
  # MAL - No hacer esto
  git add config_with_token.py
  git commit -m "added config"
  ```

- ❌ Compartir tokens por email/chat sin encriptar

---

## 🐛 Troubleshooting

### Error: "Unauthenticated"

```json
{"title": "Unauthenticated", "detail": "You did not pass an authentication token", "status": 401}
```

**Solución:**
1. Verificar que `REPLICATE_API_TOKEN` está configurado
2. Verificar que no hay espacios extra en el token
3. Re-exportar la variable en la terminal actual

### Error: Token inválido

```json
{"title": "Unauthenticated", "detail": "Authentication token is invalid", "status": 401}
```

**Solución:**
1. Verificar que copiaste el token completo
2. Regenerar un nuevo token desde https://replicate.com/account/api-tokens
3. Verificar que el token comienza con `r8_`

### Error: Rate limit exceeded

```json
{"detail": "Request was throttled. Expected available in 5 seconds."}
```

**Solución:**
1. Esperar el tiempo indicado
2. Reducir el número de requests
3. El conector implementa retry automático

---

## 📚 Recursos Adicionales

- **Documentación oficial**: https://replicate.com/docs
- **API Reference**: https://replicate.com/docs/reference/http
- **Ejemplos**: https://replicate.com/docs/get-started
- **Status page**: https://replicatestatus.com
- **Support**: https://replicate.com/support

---

## ✅ Checklist de Configuración

- [ ] Cuenta de Replicate creada
- [ ] API Token generado
- [ ] Token copiado y guardado de forma segura
- [ ] Variable de entorno `REPLICATE_API_TOKEN` configurada
- [ ] Verificación con `echo $REPLICATE_API_TOKEN` exitosa
- [ ] Test de autenticación con Python exitoso
- [ ] SDK `replicate` instalado (opcional)
- [ ] Archivo `.env` en `.gitignore`
- [ ] Primer modelo descargado con éxito

---

## 🎉 ¡Listo!

Ya puedes usar Replicate en el proyecto AI Model Discovery.

**Próximo paso**: Ejecutar el notebook `02_multi_repository_validation.ipynb` con Replicate incluido.
