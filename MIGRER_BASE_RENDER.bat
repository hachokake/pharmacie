@echo off
echo ========================================
echo MIGRATION DE LA BASE DE DONNEES RENDER
echo ========================================
echo.
echo Ce script va creer les tables dans PostgreSQL sur Render
echo.

REM Définir l'URL de la base de données Render
set DATABASE_URL=postgresql://phamacie_sql_user:iO7cdhbYOVHojNZ1QcMAgwZJgNsratXF@dpg-d6tgq4fkijhs73f4utqg-a.oregon-postgres.render.com/phamacie_sql

echo Connexion a PostgreSQL sur Render...
echo.

REM Exécuter les migrations
python manage.py migrate

echo.
echo ========================================
echo MIGRATION TERMINEE !
echo ========================================
echo.
echo Les tables ont ete creees dans PostgreSQL.
echo Votre site devrait maintenant fonctionner !
echo.
pause
