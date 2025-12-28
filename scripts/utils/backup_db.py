"""
Script de backup automático de la base de datos SQLite
Crea copias de seguridad con timestamp y gestiona rotación
"""
import os
import shutil
from datetime import datetime
from pathlib import Path

# Configuración
DATABASE_PATH = "data/prices.db"
BACKUP_DIR = "backups"
MAX_BACKUPS = 30  # Mantener últimos 30 backups


def create_backup():
    """Crea un backup de la base de datos con timestamp"""

    # Verificar que la BD existe
    if not os.path.exists(DATABASE_PATH):
        print(f"❌ Base de datos no encontrada: {DATABASE_PATH}")
        return False

    # Crear directorio de backups si no existe
    os.makedirs(BACKUP_DIR, exist_ok=True)

    # Generar nombre de backup con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"prices_backup_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    try:
        # Copiar archivo de BD
        shutil.copy2(DATABASE_PATH, backup_path)

        # Verificar tamaño
        original_size = os.path.getsize(DATABASE_PATH)
        backup_size = os.path.getsize(backup_path)

        if original_size != backup_size:
            print(f"⚠️  Advertencia: Tamaños no coinciden")
            print(f"   Original: {original_size} bytes")
            print(f"   Backup: {backup_size} bytes")

        print(f"✅ Backup creado: {backup_filename}")
        print(f"   Tamaño: {backup_size / 1024:.2f} KB")
        print(f"   Ruta: {backup_path}")

        return True

    except Exception as e:
        print(f"❌ Error al crear backup: {e}")
        return False


def rotate_backups():
    """Elimina backups antiguos manteniendo solo los MAX_BACKUPS más recientes"""

    if not os.path.exists(BACKUP_DIR):
        return

    # Listar todos los backups ordenados por fecha (más reciente primero)
    backups = sorted(
        [f for f in os.listdir(BACKUP_DIR) if f.startswith("prices_backup_") and f.endswith(".db")],
        reverse=True
    )

    if len(backups) <= MAX_BACKUPS:
        print(f"📦 Total de backups: {len(backups)}/{MAX_BACKUPS}")
        return

    # Eliminar backups excedentes
    backups_to_delete = backups[MAX_BACKUPS:]
    deleted_count = 0

    for backup in backups_to_delete:
        try:
            backup_path = os.path.join(BACKUP_DIR, backup)
            os.remove(backup_path)
            deleted_count += 1
        except Exception as e:
            print(f"⚠️  Error eliminando {backup}: {e}")

    print(f"🗑️  Backups eliminados: {deleted_count}")
    print(f"📦 Backups restantes: {len(backups) - deleted_count}")


def list_backups():
    """Lista todos los backups disponibles"""

    if not os.path.exists(BACKUP_DIR):
        print("📦 No hay backups disponibles")
        return

    backups = sorted(
        [f for f in os.listdir(BACKUP_DIR) if f.startswith("prices_backup_") and f.endswith(".db")],
        reverse=True
    )

    if not backups:
        print("📦 No hay backups disponibles")
        return

    print(f"\n📦 Backups disponibles ({len(backups)}):")
    print("=" * 70)

    for i, backup in enumerate(backups, 1):
        backup_path = os.path.join(BACKUP_DIR, backup)
        size = os.path.getsize(backup_path)
        modified = datetime.fromtimestamp(os.path.getmtime(backup_path))

        print(f"{i:2}. {backup}")
        print(f"    Tamaño: {size / 1024:.2f} KB")
        print(f"    Fecha: {modified.strftime('%Y-%m-%d %H:%M:%S')}")

    print("=" * 70)


def restore_backup(backup_filename: str):
    """
    Restaura la base de datos desde un backup

    Args:
        backup_filename: Nombre del archivo de backup a restaurar
    """
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    if not os.path.exists(backup_path):
        print(f"❌ Backup no encontrado: {backup_filename}")
        return False

    try:
        # Crear backup del estado actual antes de restaurar
        if os.path.exists(DATABASE_PATH):
            print("📋 Creando backup del estado actual antes de restaurar...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safety_backup = f"data/prices_before_restore_{timestamp}.db"
            shutil.copy2(DATABASE_PATH, safety_backup)
            print(f"✅ Backup de seguridad: {safety_backup}")

        # Restaurar desde backup
        shutil.copy2(backup_path, DATABASE_PATH)

        print(f"✅ Base de datos restaurada desde: {backup_filename}")
        return True

    except Exception as e:
        print(f"❌ Error al restaurar backup: {e}")
        return False


def main():
    """Ejecuta backup con rotación automática"""
    print("🔄 Iniciando proceso de backup...")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Crear backup
    success = create_backup()

    if success:
        # Rotar backups antiguos
        rotate_backups()

        print()
        list_backups()

    print("\n✨ Proceso completado")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "list":
            list_backups()
        elif command == "restore" and len(sys.argv) > 2:
            restore_backup(sys.argv[2])
        else:
            print("Uso:")
            print("  python backup_db.py           - Crear nuevo backup")
            print("  python backup_db.py list      - Listar backups disponibles")
            print("  python backup_db.py restore <archivo> - Restaurar desde backup")
    else:
        main()
