# SenStat AI — Backend (API & NLP)

Bienvenue dans le dépôt du projet **SenStat AI**. Ce projet est un assistant conversationnel intelligent spécialisé dans l'analyse des données statistiques régionales du Sénégal (2020-2024).

Ce README documente spécifiquement **l'architecture et les fonctionnalités Backend**, développées par **El Hadji Massogui Diop**.

---

## 🏗️ Architecture du Backend

L'application est construite avec **Django 5** et **Django REST Framework (DRF)**, en respectant rigoureusement une architecture découplée (Séparation des préoccupations).

### 1. Application `statistics` (Couche Données)
- **Modèles** : Conception du modèle `StatistiqueRegionale` avec contrainte d'unicité (`UniqueConstraint` sur `region` et `annee`).
- **Commande d'import** : Script idempotent de chargement du fichier CSV (`update_or_create`) avec validation rigoureuse des types et des bornes (pourcentages de 0 à 100).
- **Service ORM** : Le `StatistiqueService` centralise les requêtes base de données en garantissant la sécurité (Whitelist en `frozenset` avec lookup $O(1)$) pour prévenir toute injection SQL.

### 2. Application `chatbot` (Couche Intelligence)
- **NLP Déterministe** : Un moteur robuste codé en pur Python pour parser les questions (extraction d'indicateurs, années, régions, et déduction d'opérations comme `trend`, `compare`, `ranking`).
- **IA Générative (Gemini)** : Un client léger (`urllib.request`) intégré sans dépendance lourde, agissant comme bonus avec un mécanisme de **repli garanti** (fallback) vers le NLP local en cas de timeout ou de réponse invalide.

### 3. Application `api` (Couche Exposition)
- **Vue Fine** : L'API (`/api/question/`) ne gère que la validation du JSON (via serializers) et délègue toute la logique métier au `QuestionService`.
- **Contrat strict** : Renvoie systématiquement la réponse sous forme de texte, données tabulaires, configuration graphique Chart.js, et métadonnées.

---

## 🔒 Sécurité et Qualité du Code

- **Zéro Injection** : Aucune requête utilisateur ne génère de SQL direct. Tout passe par un mapping strict (Whitelist `WHITELIST_FIELDS`).
- **Typage et PEP 8** : Code entièrement typé, avec des docstrings sur chaque module, classe et méthode métier.
- **Logging** : Mise en place de `application.log` et `errors.log` pour la traçabilité.
- **Tests Automatisés** : 16 tests unitaires et d'intégration validant les bornes, les synonymes complexes, les erreurs d'ambiguïté et le contrat API (`python manage.py test`).

---

## 🚀 Installation & Lancement

### Prérequis
- Python 3.13
- Git

### Étapes d'installation

1. **Cloner le dépôt et activer l'environnement**
   ```bash
   git clone <url_du_depot>
   cd "SenStat AI"
   python -m venv env
   .\env\Scripts\activate
   ```

2. **Installer les dépendances strictes** (optimisées pour 8 Go de RAM)
   ```bash
   pip install django djangorestframework django-cors-headers drf-spectacular python-dotenv
   ```

3. **Configurer les variables d'environnement**
   - Copiez `.env.example` en `.env`.
   - Modifiez les clés si nécessaire (la clé Gemini est optionnelle).

4. **Préparer la base de données**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Importer les données (Idempotent)**
   ```bash
   python manage.py importer_statistiques chemin/vers/donnees.csv
   ```

6. **Lancer le serveur**
   ```bash
   python manage.py runserver
   ```

---

## 📚 Documentation API (Swagger)

Une documentation interactive est disponible grâce à `drf-spectacular`.
Une fois le serveur lancé, visitez :
- **Swagger UI** : [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)

---
*Développé dans le cadre du TP Architecte Logiciel Senior.*
