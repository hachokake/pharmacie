@echo off
cls
echo ========================================
echo MIGRATION POSTGRESQL RENDER
echo ========================================
echo.

set DATABASE_URL=postgresql://phamacie_sql_user:iO7cdhbYOVHojNZ1QcMAgwZJgNsratXF@dpg-d6tgq4fkijhs73f4utqg-a.oregon-postgres.render.com/phamacie_sql

echo Connexion a PostgreSQL sur Render...
echo Base: phamacie_sql
echo.

echo ========================================
echo ETAPE 1: Verification de la connexion
echo ========================================
python -c "import os; os.environ['DATABASE_URL']='%DATABASE_URL%'; import django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_project.settings'); django.setup(); from django.db import connection; c = connection.cursor(); c.execute('SELECT current_database()'); print(f'Base connectee: {c.fetchone()[0]}'); c.execute('SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=''public'''); print(f'Tables actuelles: {c.fetchone()[0]}'); c.close()"

echo.
echo ========================================
echo ETAPE 2: Execution des migrations
echo ========================================
python manage.py migrate --verbosity 2

echo.
echo ========================================
echo ETAPE 3: Verification des tables
echo ========================================
python -c "import os; os.environ['DATABASE_URL']='%DATABASE_URL%'; import django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_project.settings'); django.setup(); from django.db import connection; c = connection.cursor(); c.execute('SELECT tablename FROM pg_tables WHERE schemaname=''public'' ORDER BY tablename'); tables = c.fetchall(); print(f'\nTables créées ({len(tables)} tables):'); [print(f'  - {t[0]}') for t in tables]; c.close()"

echo.
echo ========================================
echo ETAPE 4: Creation du compte admin
echo ========================================
python create_admin.py

echo.
echo ========================================
echo TERMINE!
echo ========================================
echo.
echo Votre site devrait maintenant fonctionner!
echo URL: https://pharmacie-2.onrender.com/login
echo.
pause
