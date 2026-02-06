#!/usr/bin/env python3
"""
Script de inicio rápido para la aplicación Streamlit

Uso:
    python run_app.py
    
    # O con configuración personalizada
    python run_app.py --port 8501 --host localhost

Autor: Edmundo Mori
Fecha: 2026-02-04
"""

import subprocess
import sys
from pathlib import Path
import argparse


def check_dependencies():
    """Verificar dependencias necesarias"""
    required = [
        "streamlit",
        "rdflib",
        "langchain",
        "chromadb",
        "pandas",
        "plotly"
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("❌ Faltan dependencias:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\n💡 Instala con: pip install streamlit rdflib langchain chromadb pandas plotly")
        return False
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Iniciar aplicación Streamlit")
    parser.add_argument("--port", type=int, default=8501, help="Puerto (default: 8501)")
    parser.add_argument("--host", default="localhost", help="Host (default: localhost)")
    parser.add_argument("--no-browser", action="store_true", help="No abrir navegador")
    
    args = parser.parse_args()
    
    print("🚀 Iniciando AI Model Discovery...")
    print("=" * 70)
    
    # Verificar dependencias
    if not check_dependencies():
        return 1
    
    print("✅ Dependencias verificadas")
    
    # Ruta a la app
    app_path = Path(__file__).parent / "app" / "main.py"
    
    if not app_path.exists():
        print(f"❌ No se encontró {app_path}")
        return 1
    
    print(f"📁 App: {app_path}")
    print(f"🌐 URL: http://{args.host}:{args.port}")
    print("=" * 70)
    
    # Comando streamlit
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.port",
        str(args.port),
        "--server.address",
        args.host
    ]
    
    if args.no_browser:
        cmd.extend(["--server.headless", "true"])
    
    # Ejecutar
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n\n✅ Aplicación cerrada")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
