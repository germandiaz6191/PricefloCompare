"""
Script para activar Amazon con código de afiliado

Uso: python activate_amazon_affiliate.py TU_CODIGO_AQUI

Ejemplo: python activate_amazon_affiliate.py priceflo-20
"""
import sys
from database import get_db

def activate_amazon_affiliate(affiliate_code: str, also_activate_store: bool = False):
    """
    Activa afiliados de Amazon con el código proporcionado

    Args:
        affiliate_code: Tu código de Amazon Associates (ej: 'priceflo-20')
        also_activate_store: Si también activar Amazon para scraping
    """

    if not affiliate_code or len(affiliate_code) < 3:
        print("❌ Código de afiliado inválido")
        print("Debe ser algo como: priceflo-20")
        return False

    with get_db() as conn:
        # Verificar que Amazon existe
        store = conn.execute(
            "SELECT id, active, affiliate_enabled FROM stores WHERE name = 'Amazon'"
        ).fetchone()

        if not store:
            print("❌ Amazon no existe en la base de datos")
            print("💡 Primero ejecuta: python add_amazon_store.py")
            return False

        # Actualizar código de afiliado
        conn.execute("""
            UPDATE stores
            SET affiliate_enabled = 1,
                affiliate_code = ?,
                active = ?
            WHERE name = 'Amazon'
        """, (
            affiliate_code,
            1 if also_activate_store else store['active']
        ))

        conn.commit()

        print("✅ Afiliado de Amazon activado exitosamente")
        print(f"\n📊 Configuración:")
        print(f"   Código de afiliado: {affiliate_code}")
        print(f"   Patrón de URL: https://amazon.com/...?tag={affiliate_code}")
        print(f"   Amazon activa para scraping: {'Sí' if (also_activate_store or store['active']) else 'No'}")

        if not also_activate_store and not store['active']:
            print(f"\n💡 Amazon NO está activa para scraping")
            print(f"   Los productos de Éxito/Homecenter seguirán funcionando normal")
            print(f"   Cuando agregues productos de Amazon, se mostrarán con link de afiliado")

        print(f"\n🎉 ¡Listo! Ahora todos los links a Amazon tendrán tu código de afiliado")
        print(f"   Cuando alguien compre a través de tu link → recibes comisión")

        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Falta el código de afiliado")
        print("\nUso:")
        print("   python activate_amazon_affiliate.py TU_CODIGO")
        print("\nEjemplo:")
        print("   python activate_amazon_affiliate.py priceflo-20")
        print("\n💡 Para activar Amazon también para scraping:")
        print("   python activate_amazon_affiliate.py priceflo-20 --activate-store")
        sys.exit(1)

    code = sys.argv[1]
    activate_store = '--activate-store' in sys.argv

    activate_amazon_affiliate(code, activate_store)
