#!/usr/bin/env python
"""
Script pour créer un superutilisateur pour le système de pharmacie
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_project.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import IntegrityError

def create_superuser():
    """Créer un superutilisateur pour l'administration"""
    
    print("=" * 60)
    print("🔐 CRÉATION DU SUPERUTILISATEUR")
    print("=" * 60)
    
    # Demander les informations
    username = input("\n👤 Nom d'utilisateur (admin): ").strip() or "admin"
    email = input("📧 Email (admin@pharmacie.com): ").strip() or "admin@pharmacie.com"
    
    # Vérifier si l'utilisateur existe déjà
    if User.objects.filter(username=username).exists():
        print(f"\n⚠️  L'utilisateur '{username}' existe déjà!")
        print("Voulez-vous le supprimer et en créer un nouveau? (o/n): ", end="")
        response = input().strip().lower()
        if response == 'o' or response == 'oui':
            User.objects.filter(username=username).delete()
            print(f"✅ Utilisateur '{username}' supprimé")
        else:
            print("❌ Opération annulée")
            return
    
    # Demander le mot de passe
    import getpass
    while True:
        password = getpass.getpass("🔒 Mot de passe: ")
        password2 = getpass.getpass("🔒 Confirmer le mot de passe: ")
        
        if password != password2:
            print("❌ Les mots de passe ne correspondent pas. Réessayez.")
            continue
        
        if len(password) < 8:
            print("❌ Le mot de passe doit contenir au moins 8 caractères. Réessayez.")
            continue
        
        break
    
    # Créer le superutilisateur
    try:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        print("\n" + "=" * 60)
        print("✅ SUPERUTILISATEUR CRÉÉ AVEC SUCCÈS!")
        print("=" * 60)
        print(f"\n👤 Nom d'utilisateur: {username}")
        print(f"📧 Email: {email}")
        print(f"🔑 Statut: Superutilisateur")
        print("\n🌐 Vous pouvez maintenant vous connecter à:")
        print("   - Interface web: http://localhost:8000/login")
        print("   - Admin Django: http://localhost:8000/admin")
        print("=" * 60)
        
    except IntegrityError as e:
        print(f"\n❌ Erreur lors de la création: {e}")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")

if __name__ == '__main__':
    try:
        create_superuser()
    except KeyboardInterrupt:
        print("\n\n❌ Opération annulée par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
