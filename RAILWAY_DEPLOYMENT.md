# 🚂 Guide de Déploiement sur Railway

## ✅ Préparation Effectuée

Votre projet est maintenant configuré pour Railway. Les modifications suivantes ont été apportées :

### 1. **Configuration Django (`settings.py`)**
- ✅ Détection automatique de Railway via `RAILWAY_ENVIRONMENT`
- ✅ Configuration de base de données PostgreSQL automatique
- ✅ CSRF_TRUSTED_ORIGINS configuré pour `*.railway.app`
- ✅ CORS configuré pour autoriser les requêtes en production
- ✅ Sécurité SSL activée automatiquement en production
- ✅ Gestion des fichiers statiques avec WhiteNoise
- ✅ Erreurs de variables non définies corrigées

### 2. **Fichiers de Configuration Créés**
- ✅ `railway.json` - Configuration de build Railway
- ✅ `Procfile` - Commandes de démarrage
- ✅ `RAILWAY_DEPLOYMENT.md` - Ce guide

---

## 📋 Étapes de Déploiement

### **Étape 1 : Créer un compte Railway**
1. Allez sur [railway.app](https://railway.app)
2. Créez un compte (vous pouvez utiliser GitHub)
3. Vous avez 5$ de crédit gratuit pour commencer

### **Étape 2 : Créer un Nouveau Projet**
1. Cliquez sur **"New Project"**
2. Sélectionnez **"Deploy from GitHub repo"**
3. Connectez votre compte GitHub si ce n'est pas déjà fait
4. Sélectionnez votre dépôt `PHARMACIE-APK`

> **Note:** Si vous n'avez pas encore poussé votre code sur GitHub, faites-le d'abord :
> ```bash
> git init
> git add .
> git commit -m "Initial commit for Railway deployment"
> git remote add origin <YOUR_GITHUB_REPO_URL>
> git push -u origin main
> ```

### **Étape 3 : Ajouter une Base de Données PostgreSQL**
1. Dans votre projet Railway, cliquez sur **"New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway créera automatiquement la base de données
3. La variable `DATABASE_URL` sera automatiquement disponible ✅

### **Étape 4 : Configurer les Variables d'Environnement**

Allez dans l'onglet **"Variables"** de votre service Django et ajoutez :

#### **Variables Obligatoires**
```
SECRET_KEY=votre-clé-secrète-django-très-longue-et-aléatoire
DEBUG=False
ALLOWED_HOSTS=*
```

#### **Variables Optionnelles** (selon vos besoins)
```
# Email (si vous utilisez l'envoi d'emails)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app

# Informations de la pharmacie
PHARMACY_NAME=Pharmacie XYZ
PHARMACY_ADDRESS=123 Rue Exemple, Kinshasa
PHARMACY_PHONE=+243 XX XXX XXXX
PHARMACY_EMAIL=contact@pharmacie.com

# Domaine personnalisé (si vous en avez un)
CUSTOM_DOMAIN=pharmacie.votredomaine.com
```

> **💡 Conseil:** Pour générer une SECRET_KEY sécurisée, utilisez :
> ```python
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

### **Étape 5 : Déploiement Automatique**
1. Railway va détecter votre projet Django automatiquement
2. Il installera les dépendances depuis `requirements.txt`
3. Il exécutera les migrations et collectera les fichiers statiques
4. L'application sera déployée automatiquement ! 🎉

### **Étape 6 : Accéder à votre Application**
1. Dans Railway, cliquez sur votre service Django
2. Allez dans l'onglet **"Settings"**
3. Section **"Networking"** → Cliquez sur **"Generate Domain"**
4. Votre URL sera quelque chose comme : `votre-app.railway.app`

### **Étape 7 : Créer un Superutilisateur**
1. Dans Railway, allez dans l'onglet **"Deployments"**
2. Cliquez sur les **3 points** du dernier déploiement → **"View Logs"**
3. En haut à droite, cliquez sur **"Shell"** (icône de terminal)
4. Exécutez :
```bash
python manage.py createsuperuser
```

---

## 🔧 Commandes Utiles via Railway Shell

### Accéder au Shell Django
```bash
python manage.py shell
```

### Voir les Migrations
```bash
python manage.py showmigrations
```

### Collecter les Fichiers Statiques
```bash
python manage.py collectstatic --noinput
```

### Vider le Cache
```bash
python manage.py clear_cache
```

---

## 🌐 Configuration d'un Domaine Personnalisé

Si vous avez votre propre domaine (ex: `pharmacie.com`):

1. Dans Railway, allez dans **"Settings"** → **"Networking"** → **"Custom Domain"**
2. Entrez votre domaine (ex: `www.pharmacie.com`)
3. Railway vous donnera un enregistrement CNAME à ajouter chez votre registrar
4. Ajoutez la variable d'environnement :
   ```
   CUSTOM_DOMAIN=www.pharmacie.com
   ```

---

## 📊 Monitoring et Logs

### **Voir les Logs**
- Dans Railway, onglet **"Deployments"** → Cliquez sur un déploiement → **"View Logs"**
- Les logs Django s'affichent en temps réel

### **Métriques**
- Railway montre automatiquement :
  - Utilisation CPU
  - Utilisation Mémoire
  - Nombre de requêtes
  - Temps de réponse

---

## 💾 Sauvegarde de la Base de Données

### **Créer une Sauvegarde**
Via Railway CLI :
```bash
# Installer Railway CLI
npm i -g @railway/cli

# Se connecter
railway login

# Créer un backup
railway run pg_dump $DATABASE_URL > backup.sql
```

### **Restaurer une Sauvegarde**
```bash
railway run psql $DATABASE_URL < backup.sql
```

---

## 🚨 Dépannage

### **Erreur 500 - Internal Server Error**
1. Vérifiez les logs dans Railway
2. Assurez-vous que `DEBUG=False`
3. Vérifiez que `SECRET_KEY` est définie
4. Vérifiez que les migrations sont appliquées

### **Erreur de Base de Données**
1. Vérifiez que PostgreSQL est bien ajouté
2. Vérifiez que `DATABASE_URL` existe dans les variables
3. Essayez de relancer les migrations via Shell

### **Fichiers Statiques Non Trouvés**
```bash
# Dans le Shell Railway
python manage.py collectstatic --noinput
```

### **Redéployer l'Application**
1. Allez dans **"Settings"** → **"Service"**
2. Cliquez sur **"Redeploy"**

---

## 💰 Coûts

Railway offre :
- **5$ de crédit gratuit** pour commencer
- Ensuite, environ **5$ par mois** pour une petite application
- Tarification basée sur l'utilisation réelle

**Estimation pour cette application :**
- Django + PostgreSQL : ~5-10$/mois
- Si peu de trafic : peut rester dans le crédit gratuit

---

## 📞 Support

### Documentation Railway
- [Docs Railway](https://docs.railway.app/)
- [Déployer Django sur Railway](https://docs.railway.app/guides/django)

### Community
- [Discord Railway](https://discord.gg/railway)
- [Forum Railway](https://help.railway.app/)

---

## ✅ Checklist de Déploiement

- [ ] Code poussé sur GitHub
- [ ] Projet créé sur Railway
- [ ] PostgreSQL ajouté
- [ ] Variables d'environnement configurées
- [ ] Domaine généré
- [ ] Application déployée avec succès
- [ ] Superutilisateur créé
- [ ] Tests effectués (login, ajout médicament, etc.)
- [ ] Logs vérifiés (pas d'erreurs)

---

## 🎯 Prochaines Étapes

Une fois déployé, vous pouvez :
1. ✅ Tester tous les modules (médicaments, ventes, inventaire)
2. 🌐 Configurer un domaine personnalisé
3. 📊 Monitorer les performances
4. 🔒 Configurer des backups automatiques
5. 📱 Connecter votre APK Android à l'API Railway

---

**Bon déploiement ! 🚀**
