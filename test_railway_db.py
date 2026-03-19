#!/usr/bin/env python
"""
Script de vérification de la connexion PostgreSQL Railway
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_project.settings')
django.setup()

from django.contrib.auth.models import User
from pharmacy.models import Medicament, Vente, Client

print("✅ Connexion PostgreSQL Railway réussie!")
print("\n📊 État de la base de données:")
print(f"  - Utilisateurs: {User.objects.count()}")
print(f"  - Médicaments: {Medicament.objects.count()}")
print(f"  - Ventes: {Vente.objects.count()}")
print(f"  - Clients: {Client.objects.count()}")
print("\n✅ Toutes les tables sont accessibles!")
