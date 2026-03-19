"""
Script pour forcer les migrations sur PostgreSQL de Render
"""
import os
import sys
import django

# FORCER l'utilisation de PostgreSQL de Render
os.environ['DATABASE_URL'] = 'postgresql://phamacie_sql_user:iO7cdhbYOVHojNZ1QcMAgwZJgNsratXF@dpg-d6tgq4fkijhs73f4utqg-a.oregon-postgres.render.com/phamacie_sql'
os.environ['DJANGO_SETTINGS_MODULE'] = 'pharmacy_project.settings'

# Setup Django
django.setup()

from django.core.management import call_command
from django.db import connection

print("="*70)
print("VÉRIFICATION DE LA CONNEXION À POSTGRESQL RENDER")
print("="*70)

# Vérifier la connexion
with connection.cursor() as cursor:
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"✅ Connecté à PostgreSQL: {version[0][:50]}...")
    
    cursor.execute("SELECT current_database();")
    db_name = cursor.fetchone()
    print(f"✅ Base de données: {db_name[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
    table_count = cursor.fetchone()
    print(f"📊 Nombre de tables existantes: {table_count[0]}")

print("\n" + "="*70)
print("EXÉCUTION DES MIGRATIONS")
print("="*70)

# Exécuter les migrations
try:
    call_command('migrate', verbosity=2, interactive=False)
    print("\n✅ MIGRATIONS RÉUSSIES!")
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    sys.exit(1)

print("\n" + "="*70)
print("VÉRIFICATION DES TABLES CRÉÉES")
print("="*70)

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        ORDER BY tablename;
    """)
    tables = cursor.fetchall()
    print(f"\n📋 Tables dans la base ({len(tables)} tables):")
    for table in tables:
        print(f"   ✓ {table[0]}")

print("\n" + "="*70)
print("TERMINÉ!")
print("="*70)
