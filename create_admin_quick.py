#!/usr/bin/env python
"""
Script pour créer rapidement un superutilisateur admin
Username: admin
Password: admin123
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_project.settings')
django.setup()

from django.contrib.auth.models import User

# Supprimer l'ancien admin s'il existe
if User.objects.filter(username='admin').exists():
    User.objects.filter(username='admin').delete()
    print("ℹ️  Ancien utilisateur 'admin' supprimé")

# Créer le nouveau superutilisateur
user = User.objects.create_superuser(
    username='admin',
    email='admin@pharmacie.com',
    password='admin123'
)

print("\n" + "=" * 60)
print("✅ SUPERUTILISATEUR CRÉÉ AVEC SUCCÈS!")
print("=" * 60)
print("\n📋 INFORMATIONS DE CONNEXION:")
print("   👤 Nom d'utilisateur: admin")
print("   🔒 Mot de passe: admin123")
print("   📧 Email: admin@pharmacie.com")
print("\n🌐 ACCÈS À L'APPLICATION:")
print("   • Interface web: http://localhost:8000/login")
print("   • Admin Django: http://localhost:8000/admin")
print("\n⚠️  IMPORTANT: Changez le mot de passe après la première connexion!")
print("=" * 60)
