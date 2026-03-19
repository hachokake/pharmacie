#!/usr/bin/env bash
set -o errexit

echo "==================== INSTALLATION DES DÉPENDANCES ===================="
pip install -r requirements.txt

echo "==================== COLLECTE DES FICHIERS STATIQUES ===================="
python manage.py collectstatic --no-input

echo "==================== EXÉCUTION DES MIGRATIONS ===================="
python manage.py migrate --no-input --verbosity 2

echo "==================== BUILD TERMINÉ AVEC SUCCÈS ===================="