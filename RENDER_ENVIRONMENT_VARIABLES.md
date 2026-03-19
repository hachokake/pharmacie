# 🔧 VARIABLES D'ENVIRONNEMENT POUR RENDER

## ⚠️ PROBLÈME ACTUEL
Votre site charge indéfiniment car les **variables d'environnement ne sont pas configurées sur Render**.

---

## ✅ CONFIGURATION À FAIRE SUR RENDER (5 MINUTES)

### 📍 **OÙ LES AJOUTER:**
1. Allez sur: https://dashboard.render.com
2. Cliquez sur votre service **"pharmacie-2"**
3. Cliquez sur **"Environment"** dans le menu de gauche (ou "Settings" puis cherchez "Environment Variables")
4. Cliquez sur **"Add Environment Variable"** pour chaque variable ci-dessous

---

## 🔑 **VARIABLES À AJOUTER (COPIEZ-COLLEZ):**

### 1️⃣ SECRET_KEY (OBLIGATOIRE)
```
Key: SECRET_KEY
Value: h^3k)@w!rgl=ki0ny73+ox+ww=23wwk)t=2wl*!3smq%a#0upj
```
⚠️ **IMPORTANT:** Cette clé est unique et sécurisée pour votre production!

### 2️⃣ DEBUG (OBLIGATOIRE)
```
Key: DEBUG
Value: False
```
⚠️ DOIT être False en production!

### 3️⃣ DATABASE_URL (OBLIGATOIRE)
```
Key: DATABASE_URL
Value: postgresql://phamacie_sql_user:iO7cdhbYOVHojNZ1QcMAgwZJgNsratXF@dpg-d6tgq4fkijhs73f4utqg-a.oregon-postgres.render.com/phamacie_sql
```

### 4️⃣ ALLOWED_HOSTS (OBLIGATOIRE)
```
Key: ALLOWED_HOSTS
Value: pharmacie-2.onrender.com,*.onrender.com,*
```

### 5️⃣ RENDER (OBLIGATOIRE)
```
Key: RENDER
Value: True
```

### 6️⃣ PYTHON_VERSION (RECOMMANDÉ)
```
Key: PYTHON_VERSION
Value: 3.13.0
```

---

## 🎯 APRÈS AVOIR AJOUTÉ TOUTES LES VARIABLES:

1. **Cliquez sur "Save Changes"** (en bas)
2. Render va **redémarrer automatiquement** votre service
3. Attendez **2-3 minutes** que le redémarrage finisse
4. Testez votre site: https://pharmacie-2.onrender.com

---

## 📌 RÉSUMÉ VISUEL:

```
Environment Variables (6 variables)
┌─────────────────────────────────────────────┐
│ SECRET_KEY = django-prod-pharmacie-2026...  │
│ DEBUG = False                               │
│ DATABASE_URL = postgresql://phamacie_sql... │
│ ALLOWED_HOSTS = pharmacie-2.onrender.com... │
│ RENDER = True                               │
│ PYTHON_VERSION = 3.13.0                     │
└─────────────────────────────────────────────┘
```

---

## 🚨 SI LE SITE CHARGE ENCORE:

Après 3 minutes, si ça charge toujours:
1. Allez dans **"Events"** (onglet en haut)
2. Cherchez le dernier événement "Deploy succeeded"
3. Copiez-moi l'heure du déploiement réussi
4. Si vous voyez "Deploy failed", copiez-moi l'erreur

---

## ✅ SUCCÈS = SITE S'OUVRE EN 2-5 SECONDES
