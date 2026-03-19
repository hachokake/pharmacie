@echo off
echo ========================================
echo CONNEXION POSTGRESQL RENDER
echo ========================================
echo.

REM Vérifier si psql est installé
where psql >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] psql n'est pas installe sur votre systeme.
    echo.
    echo Pour installer PostgreSQL client:
    echo 1. Telechargez PostgreSQL depuis: https://www.postgresql.org/download/windows/
    echo 2. Ou installez via Chocolatey: choco install postgresql
    echo.
    pause
    exit /b 1
)

echo [INFO] Connection a PostgreSQL sur Render...
echo.

set PGPASSWORD=iO7cdhbYOVHojNZ1QcMAgwZJgNsratXF
psql -h dpg-d6tgq4fkijhs73f4utqg-a.oregon-postgres.render.com -U phamacie_sql_user -d phamacie_sql

pause
