#!/bin/bash
# Script de gestión de PricefloCompare

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funciones de utilidad
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Comando: setup
setup() {
    print_info "Configurando PricefloCompare..."

    # Instalar dependencias
    if [ ! -d "venv" ]; then
        print_info "Creando entorno virtual..."
        python3 -m venv venv
        print_success "Entorno virtual creado"
    fi

    print_info "Activando entorno virtual e instalando dependencias..."
    source venv/bin/activate
    pip install -r requirements.txt
    print_success "Dependencias instaladas"

    # Crear directorios
    mkdir -p data backups logs
    print_success "Directorios creados"

    # Migrar datos si existen configs JSON
    if [ -f "config_sitios.json" ] && [ -f "config_productos.json" ]; then
        print_info "Migrando configuraciones a base de datos..."
        python migrate_to_db.py
        print_success "Migración completada"
    fi

    print_success "Setup completado"
}

# Comando: migrate
migrate() {
    print_info "Ejecutando migración de JSON a SQLite..."
    python migrate_to_db.py
}

# Comando: scrape
scrape() {
    print_info "Ejecutando scraping de precios..."
    python job_scraper.py
}

# Comando: api
api() {
    print_info "Iniciando API REST..."
    print_info "Documentación disponible en: http://localhost:8000/docs"
    python api.py
}

# Comando: backup
backup() {
    print_info "Creando backup de base de datos..."
    python backup_db.py
}

# Comando: stats
stats() {
    print_info "Estadísticas del sistema:"
    python -c "from database import get_stats; import json; print(json.dumps(get_stats(), indent=2, default=str))"
}

# Comando: docker-up
docker_up() {
    print_info "Iniciando contenedores Docker..."
    docker-compose up -d
    print_success "Contenedores iniciados"
    print_info "API disponible en: http://localhost:8000"
    print_info "Ver logs: docker-compose logs -f"
}

# Comando: docker-down
docker_down() {
    print_info "Deteniendo contenedores Docker..."
    docker-compose down
    print_success "Contenedores detenidos"
}

# Comando: docker-logs
docker_logs() {
    docker-compose logs -f
}

# Comando: test
test_api() {
    print_info "Probando API..."

    # Verificar que la API esté corriendo
    if ! curl -s http://localhost:8000/health > /dev/null; then
        print_error "API no está corriendo. Ejecuta: ./manage.sh api"
        exit 1
    fi

    print_success "API está corriendo"

    # Test básico de endpoints
    print_info "Probando endpoint /products..."
    curl -s http://localhost:8000/products | python -m json.tool | head -20

    print_info "Probando endpoint /stats..."
    curl -s http://localhost:8000/stats | python -m json.tool
}

# Comando: help
show_help() {
    cat << EOF
PricefloCompare - Gestión de Sistema

COMANDOS:

  setup         Configuración inicial (crear venv, instalar deps, migrar)
  migrate       Migrar configuraciones JSON a base de datos
  scrape        Ejecutar scraping de precios manualmente
  api           Iniciar API REST en modo desarrollo
  backup        Crear backup de la base de datos
  stats         Mostrar estadísticas del sistema

DOCKER:

  docker-up     Iniciar todos los servicios con Docker
  docker-down   Detener todos los servicios Docker
  docker-logs   Ver logs de contenedores en tiempo real

TESTING:

  test          Probar endpoints de la API

EJEMPLOS:

  # Setup inicial
  ./manage.sh setup

  # Ejecutar sin Docker
  ./manage.sh api          # Terminal 1: API
  ./manage.sh scrape       # Terminal 2: Scrape manual

  # Ejecutar con Docker
  ./manage.sh docker-up
  ./manage.sh docker-logs

  # Verificar estado
  ./manage.sh stats
  ./manage.sh test

EOF
}

# Parsear comando
case "$1" in
    setup)
        setup
        ;;
    migrate)
        migrate
        ;;
    scrape)
        scrape
        ;;
    api)
        api
        ;;
    backup)
        backup
        ;;
    stats)
        stats
        ;;
    docker-up)
        docker_up
        ;;
    docker-down)
        docker_down
        ;;
    docker-logs)
        docker_logs
        ;;
    test)
        test_api
        ;;
    help|--help|-h|"")
        show_help
        ;;
    *)
        print_error "Comando desconocido: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
