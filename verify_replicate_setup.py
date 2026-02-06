#!/usr/bin/env python3
"""
Script de verificación de configuración de Replicate API.

Verifica que el token de Replicate esté configurado correctamente
y puede comunicarse con la API.

Uso:
    python verify_replicate_setup.py

Autor: Edmundo Mori
Fecha: Enero 2026
"""

import os
import sys
import requests


def print_header():
    """Imprime el encabezado del script."""
    print("=" * 60)
    print("🔁 VERIFICACIÓN DE REPLICATE API")
    print("=" * 60)
    print()


def check_token_env():
    """Verifica que la variable de entorno REPLICATE_API_TOKEN esté configurada."""
    print("📝 Paso 1: Verificando variable de entorno...")
    
    token = os.getenv('REPLICATE_API_TOKEN')
    
    if not token:
        print("❌ REPLICATE_API_TOKEN no está configurada")
        print()
        print("💡 Soluciones:")
        print("   1. Exportar la variable:")
        print("      export REPLICATE_API_TOKEN='r8_tu_token_aqui'")
        print()
        print("   2. O crear archivo .env con:")
        print("      REPLICATE_API_TOKEN=r8_tu_token_aqui")
        print()
        print("   3. Obtener token en: https://replicate.com/account/api-tokens")
        print()
        return None
    
    # Verificar formato del token
    if not token.startswith('r8_'):
        print(f"⚠️  El token no comienza con 'r8_' (comienza con '{token[:3]}')")
        print("   Verifica que hayas copiado el token completo")
        print()
        return None
    
    print(f"✅ Variable de entorno configurada")
    print(f"   Primeros 15 caracteres: {token[:15]}...")
    print(f"   Longitud: {len(token)} caracteres")
    print()
    
    return token


def test_authentication(token):
    """Prueba la autenticación con la API de Replicate."""
    print("🔐 Paso 2: Probando autenticación con API...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            "https://api.replicate.com/v1/account",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Autenticación exitosa!")
            print(f"   Usuario: {data.get('username', 'N/A')}")
            print(f"   Tipo de cuenta: {data.get('type', 'N/A')}")
            print()
            return True
        elif response.status_code == 401:
            print("❌ Autenticación fallida - Token inválido")
            print(f"   Respuesta: {response.text}")
            print()
            print("💡 Soluciones:")
            print("   1. Verificar que copiaste el token completo")
            print("   2. Generar un nuevo token en: https://replicate.com/account/api-tokens")
            print()
            return False
        else:
            print(f"⚠️  Error inesperado: HTTP {response.status_code}")
            print(f"   Respuesta: {response.text}")
            print()
            return False
            
    except requests.exceptions.Timeout:
        print("⏱️  Timeout - No se pudo conectar a la API")
        print("   Verifica tu conexión a internet")
        print()
        return False
    except requests.exceptions.ConnectionError:
        print("🌐 Error de conexión - No se pudo alcanzar api.replicate.com")
        print("   Verifica tu conexión a internet o proxy")
        print()
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {type(e).__name__}: {e}")
        print()
        return False


def test_models_endpoint(token):
    """Prueba el endpoint de listado de modelos."""
    print("📚 Paso 3: Probando endpoint de modelos...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            "https://api.replicate.com/v1/models?sort_by=model_created_at&sort_direction=desc",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            print(f"✅ Endpoint de modelos funcional")
            print(f"   Modelos en respuesta: {len(results)}")
            
            if results:
                model = results[0]
                print(f"   Ejemplo de modelo:")
                print(f"     - Nombre: {model.get('owner')}/{model.get('name')}")
                print(f"     - Runs: {model.get('run_count', 0):,}")
                print(f"     - URL: {model.get('url')}")
            print()
            return True
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}")
            print()
            return False
            
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        print()
        return False


def check_dependencies():
    """Verifica que las dependencias necesarias estén instaladas."""
    print("📦 Paso 4: Verificando dependencias...")
    
    # Verificar requests
    try:
        import requests
        print(f"✅ requests instalado (v{requests.__version__})")
    except ImportError:
        print("❌ requests no instalado")
        print("   pip install requests")
        return False
    
    # Verificar replicate SDK (opcional)
    try:
        import replicate
        print(f"✅ replicate SDK instalado (opcional)")
    except ImportError:
        print("⚠️  replicate SDK no instalado (opcional)")
        print("   pip install replicate")
    
    print()
    return True


def print_summary(success):
    """Imprime el resumen final."""
    print("=" * 60)
    if success:
        print("🎉 CONFIGURACIÓN COMPLETA Y FUNCIONAL")
        print()
        print("Ya puedes usar Replicate en tu proyecto:")
        print()
        print("  from utils.replicate_repository import ReplicateRepository")
        print("  ")
        print("  repo = ReplicateRepository()")
        print("  models = repo.fetch_models(limit=50)")
    else:
        print("⚠️  CONFIGURACIÓN INCOMPLETA")
        print()
        print("Por favor, corrige los errores anteriores.")
        print()
        print("Documentación completa:")
        print("  docs/REPLICATE_SETUP.md")
    print("=" * 60)


def main():
    """Función principal."""
    print_header()
    
    # Paso 1: Verificar token
    token = check_token_env()
    if not token:
        print_summary(False)
        sys.exit(1)
    
    # Paso 2: Verificar autenticación
    auth_ok = test_authentication(token)
    if not auth_ok:
        print_summary(False)
        sys.exit(1)
    
    # Paso 3: Probar endpoint de modelos
    models_ok = test_models_endpoint(token)
    if not models_ok:
        print_summary(False)
        sys.exit(1)
    
    # Paso 4: Verificar dependencias
    deps_ok = check_dependencies()
    
    # Resumen final
    success = auth_ok and models_ok and deps_ok
    print_summary(success)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
