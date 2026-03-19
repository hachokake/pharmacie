#!/usr/bin/env python
"""
Script de vérification de configuration pour Railway
Vérifie que toutes les variables d'environnement nécessaires sont définies
"""

import os
import sys

def check_config():
    """Vérifie la configuration de l'application"""
    
    print("🔍 Vérification de la configuration Railway...\n")
    
    errors = []
    warnings = []
    
    # Variables obligatoires
    required_vars = {
        'SECRET_KEY': 'Clé secrète Django',
        'DEBUG': 'Mode debug (doit être False en production)',
    }
    
    # Variables optionnelles mais recommandées
    optional_vars = {
        'DATABASE_URL': 'URL de connexion PostgreSQL',
        'ALLOWED_HOSTS': 'Domaines autorisés',
        'EMAIL_HOST': 'Serveur email',
        'PHARMACY_NAME': 'Nom de la pharmacie',
    }
    
    # Vérifier les variables obligatoires
    print("📋 Variables OBLIGATOIRES:")
    for var, description in required_vars.items():
        value = os.environ.get(var)
        if value:
            # Masquer les valeurs sensibles
            display_value = '***' if 'KEY' in var or 'PASSWORD' in var else value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: NON DÉFINIE")
            errors.append(f"{var} ({description})")
    
    # Vérifier les variables optionnelles
    print("\n📋 Variables OPTIONNELLES:")
    for var, description in optional_vars.items():
        value = os.environ.get(var)
        if value:
            display_value = '***' if 'PASSWORD' in var or 'URL' in var else value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ⚠️  {var}: Non définie")
            warnings.append(f"{var} ({description})")
    
    # Détection de l'environnement
    print("\n🌍 Environnement:")
    is_railway = os.environ.get('RAILWAY_ENVIRONMENT')
    is_render = os.environ.get('RENDER')
    
    if is_railway:
        print(f"  ✅ Railway détecté: {is_railway}")
    elif is_render:
        print(f"  ✅ Render détecté")
    else:
        print(f"  ℹ️  Environnement local")
    
    # Vérifications spécifiques
    print("\n🔒 Vérifications de sécurité:")
    
    # DEBUG doit être False en production
    debug_value = os.environ.get('DEBUG', 'False')
    if (is_railway or is_render) and debug_value.lower() != 'false':
        print(f"  ⚠️  DEBUG devrait être False en production (actuellement: {debug_value})")
        warnings.append("DEBUG devrait être False en production")
    else:
        print(f"  ✅ DEBUG: {debug_value}")
    
    # SECRET_KEY doit être longue
    secret_key = os.environ.get('SECRET_KEY', '')
    if len(secret_key) < 50:
        print(f"  ⚠️  SECRET_KEY semble trop courte ({len(secret_key)} caractères, recommandé: 50+)")
        warnings.append("SECRET_KEY devrait contenir au moins 50 caractères")
    else:
        print(f"  ✅ SECRET_KEY: {len(secret_key)} caractères")
    
    # Résumé
    print("\n" + "="*60)
    if errors:
        print(f"\n❌ ERREURS ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
        print("\n⚠️  L'application ne pourra pas démarrer correctement!")
        return False
    
    if warnings:
        print(f"\n⚠️  AVERTISSEMENTS ({len(warnings)}):")
        for warning in warnings:
            print(f"  - {warning}")
        print("\n✅ L'application devrait fonctionner, mais certaines fonctionnalités peuvent être limitées.")
    else:
        print("\n✅ Toutes les vérifications sont OK!")
    
    return True

if __name__ == '__main__':
    try:
        success = check_config()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Erreur lors de la vérification: {e}")
        sys.exit(1)
