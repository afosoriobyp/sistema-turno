"""
Generador de SECRET_KEY para Flask

Este script genera una clave secreta segura para usar en producción.
Ejecutar cada vez que necesites una nueva SECRET_KEY.

Uso:
    python generate_secret_key.py
"""

import secrets

def generate_secret_key():
    """Genera una SECRET_KEY segura de 64 caracteres hexadecimales"""
    return secrets.token_hex(32)

def generate_multiple_keys(count=5):
    """Genera múltiples claves para elegir"""
    return [generate_secret_key() for _ in range(count)]

if __name__ == '__main__':
    print("\n" + "="*70)
    print("GENERADOR DE SECRET_KEY PARA FLASK")
    print("="*70)
    print("\n✨ Clave secreta generada:\n")
    
    key = generate_secret_key()
    print(f"   {key}\n")
    
    print("📋 Cómo usar esta clave:")
    print("\n1. Copia la clave generada arriba")
    print("2. En tu archivo .env, añade/modifica:")
    print(f"   SECRET_KEY={key}")
    print("\n⚠️  IMPORTANTE:")
    print("   - NO compartas esta clave con nadie")
    print("   - NO la subas a Git")
    print("   - Usa una clave diferente para cada entorno")
    print("   - Guárdala en un lugar seguro\n")
    
    # Generar claves adicionales
    response = input("¿Deseas generar más claves para elegir? (s/n): ").lower()
    if response == 's':
        print("\n🔑 Claves adicionales generadas:\n")
        additional_keys = generate_multiple_keys(4)
        for i, k in enumerate(additional_keys, 1):
            print(f"{i}. {k}")
        print()
    
    print("="*70)
    print("✅ Listo! Copia tu clave favorita y úsala en .env\n")
