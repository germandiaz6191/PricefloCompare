"""
Script simple para iniciar la API REST
"""
import uvicorn
from api import app

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Iniciando PricefloCompare API")
    print("=" * 70)
    print()
    print("📖 Documentación interactiva:")
    print("   http://localhost:8000/docs")
    print()
    print("🔍 Endpoints principales:")
    print("   http://localhost:8000/products          - Lista de productos")
    print("   http://localhost:8000/products/1        - Detalle producto 1")
    print("   http://localhost:8000/products/1/prices - Precios de producto 1")
    print("   http://localhost:8000/stats             - Estadísticas")
    print("   http://localhost:8000/health            - Health check")
    print()
    print("⏹️  Para detener: Ctrl+C")
    print("=" * 70)
    print()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
