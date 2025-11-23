#!/bin/bash
# Script de inicio para Railway

# Railway asigna PORT automáticamente, si no existe usa 8000
PORT=${PORT:-8000}

echo "🚀 Iniciando ePriceFlo API en puerto $PORT..."

# Ejecutar uvicorn
exec uvicorn api:app --host 0.0.0.0 --port $PORT
