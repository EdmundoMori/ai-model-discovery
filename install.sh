#!/bin/bash

# Script de instalación rápida para AI Model Discovery
# Autor: Edmundo Mori

set -e  # Exit on error

echo "=================================================="
echo "AI Model Discovery - Instalación"
echo "=================================================="
echo ""

# Verificar Python 3.10+
echo "🐍 Verificando Python..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Versión encontrada: $python_version"

# Verificar Poetry
echo ""
echo "📦 Verificando Poetry..."
if ! command -v poetry &> /dev/null; then
    echo "   ⚠️  Poetry no encontrado. Instalando..."
    curl -sSL https://install.python-poetry.org | python3 -
    echo "   ✅ Poetry instalado"
else
    poetry_version=$(poetry --version 2>&1 | awk '{print $3}')
    echo "   ✅ Poetry encontrado: $poetry_version"
fi

# Instalar dependencias
echo ""
echo "📚 Instalando dependencias..."
poetry install

echo ""
echo "✅ Instalación completada exitosamente"
echo ""
echo "=================================================="
echo "Próximos pasos:"
echo "=================================================="
echo ""
echo "1. Activar el entorno virtual:"
echo "   poetry shell"
echo ""
echo "2. Configurar API keys:"
echo "   cp .env.example .env"
echo "   nano .env  # Editar con tus keys"
echo ""
echo "3. Ejecutar validación:"
echo "   poetry run jupyter notebook notebooks/01_validation.ipynb"
echo ""
echo "Ver QUICKSTART.md para más detalles."
echo ""
