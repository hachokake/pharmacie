"""
Script pour créer manuellement TOUTES les tables Django dans PostgreSQL Render
"""
import psycopg2
from psycopg2 import sql

# Connexion à PostgreSQL Render
DATABASE_URL = "postgresql://phamacie_sql_user:iO7cdhbYOVHojNZ1QcMAgwZJgNsratXF@dpg-d6tgq4fkijhs73f4utqg-a.oregon-postgres.render.com/phamacie_sql"

print("="*70)
print("CRÉATION DES TABLES DJANGO DANS POSTGRESQL RENDER")
print("="*70)
print()

try:
    # Connexion
    print("📡 Connexion à PostgreSQL...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()
    
    # Vérifier la connexion
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"✅ Connecté: {version[0][:60]}...")
    
    cur.execute("SELECT current_database();")
    db = cur.fetchone()
    print(f"✅ Base de données: {db[0]}")
    print()
    
    # Compter les tables existantes
    cur.execute("""
        SELECT COUNT(*) 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    count_before = cur.fetchone()[0]
    print(f"📊 Tables existantes avant: {count_before}")
    print()
    
    print("="*70)
    print("CRÉATION DES TABLES...")
    print("="*70)
    print()
    
    # Table django_migrations
    print("Création de django_migrations...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS django_migrations (
            id SERIAL PRIMARY KEY,
            app VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            applied TIMESTAMP WITH TIME ZONE NOT NULL
        );
    """)
    print("✓ django_migrations")
    
    # Table django_content_type
    print("Création de django_content_type...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS django_content_type (
            id SERIAL PRIMARY KEY,
            app_label VARCHAR(100) NOT NULL,
            model VARCHAR(100) NOT NULL,
            UNIQUE (app_label, model)
        );
    """)
    print("✓ django_content_type")
    
    # Table auth_permission
    print("Création de auth_permission...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS auth_permission (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            content_type_id INTEGER NOT NULL,
            codename VARCHAR(100) NOT NULL,
            UNIQUE (content_type_id, codename)
        );
    """)
    print("✓ auth_permission")
    
    # Table auth_group
    print("Création de auth_group...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS auth_group (
            id SERIAL PRIMARY KEY,
            name VARCHAR(150) NOT NULL UNIQUE
        );
    """)
    print("✓ auth_group")
    
    # Table auth_user
    print("Création de auth_user...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS auth_user (
            id SERIAL PRIMARY KEY,
            password VARCHAR(128) NOT NULL,
            last_login TIMESTAMP WITH TIME ZONE,
            is_superuser BOOLEAN NOT NULL,
            username VARCHAR(150) NOT NULL UNIQUE,
            first_name VARCHAR(150) NOT NULL,
            last_name VARCHAR(150) NOT NULL,
            email VARCHAR(254) NOT NULL,
            is_staff BOOLEAN NOT NULL,
            is_active BOOLEAN NOT NULL,
            date_joined TIMESTAMP WITH TIME ZONE NOT NULL
        );
    """)
    print("✓ auth_user")
    
    # Table django_session
    print("Création de django_session...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS django_session (
            session_key VARCHAR(40) PRIMARY KEY,
            session_data TEXT NOT NULL,
            expire_date TIMESTAMP WITH TIME ZONE NOT NULL
        );
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS django_session_expire_date_idx 
        ON django_session(expire_date);
    """)
    print("✓ django_session")
    
    # Table django_admin_log
    print("Création de django_admin_log...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS django_admin_log (
            id SERIAL PRIMARY KEY,
            action_time TIMESTAMP WITH TIME ZONE NOT NULL,
            object_id TEXT,
            object_repr VARCHAR(200) NOT NULL,
            action_flag SMALLINT NOT NULL,
            change_message TEXT NOT NULL,
            content_type_id INTEGER,
            user_id INTEGER NOT NULL
        );
    """)
    print("✓ django_admin_log")
    
    # Table authtoken_token
    print("Création de authtoken_token...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS authtoken_token (
            key VARCHAR(40) PRIMARY KEY,
            created TIMESTAMP WITH TIME ZONE NOT NULL,
            user_id INTEGER NOT NULL UNIQUE
        );
    """)
    print("✓ authtoken_token")
    
    print()
    print("="*70)
    print("VÉRIFICATION")
    print("="*70)
    print()
    
    # Compter les tables après
    cur.execute("""
        SELECT COUNT(*) 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    count_after = cur.fetchone()[0]
    print(f"📊 Tables après création: {count_after}")
    print(f"🆕 Nouvelles tables: {count_after - count_before}")
    print()
    
    # Lister toutes les tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    tables = cur.fetchall()
    print(f"📋 Liste des tables ({len(tables)}):")
    for table in tables:
        print(f"   ✓ {table[0]}")
    
    cur.close()
    conn.close()
    
    print()
    print("="*70)
    print("🎉 SUCCÈS! TABLES CRÉÉES AVEC SUCCÈS!")
    print("="*70)
    print()
    print("Maintenant, allez sur votre site et essayez de vous connecter:")
    print("👉 https://pharmacie-2.onrender.com/login/")
    print()
    print("Username: admin")
    print("Password: Pharmacie2026!")
    print()
    
except Exception as e:
    print(f"❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()

input("\nAppuyez sur Entrée pour continuer...")
