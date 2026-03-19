import os
os.environ.setdefault('DATABASE_URL', 'postgresql://phamacie_sql_user:iO7cdhbYOVHojNZ1QcMAgwZJgNsratXF@dpg-d6tgq4fkijhs73f4utqg-a.oregon-postgres.render.com/phamacie_sql')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_project.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Créer ou mettre à jour l'admin
try:
    user = User.objects.get(username='admin')
    print(f"✅ Utilisateur 'admin' trouvé: {user.email}")
except User.DoesNotExist:
    user = User.objects.create_superuser(
        username='admin',
        email='admin@pharmacie.com',
        password='Pharmacie2026!'
    )
    print("✅ Superuser 'admin' créé!")

# Définir le mot de passe
user.set_password('Pharmacie2026!')
user.save()

print("\n" + "="*50)
print("🎉 MOT DE PASSE DÉFINI AVEC SUCCÈS !")
print("="*50)
print("\n📋 IDENTIFI ANTS DE CONNEXION:")
print(f"   URL: https://pharmacie-2.onrender.com/admin")
print(f"   Username: admin")
print(f"   Password: Pharmacie2026!")
print("\n" + "="*50)
