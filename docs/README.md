# SenStat-AI : Assistant Conversationnel Data

SenStat-AI est un prototype de chatbot conçu pour interroger et analyser les données statistiques de 14 régions du Sénégal (2020-2024). 
Ce projet a été réalisé dans le cadre d'un laboratoire d'évaluation, avec une contrainte stricte d'optimisation (8 Go RAM).

⚠️ **Avertissement :** Les données utilisées par cet assistant sont des *données pédagogiques fictives* et ne reflètent pas les statistiques réelles de l'ANSD.

---

## 📸 Aperçu de l'Interface

*(Les captures d'écran finales seront insérées ici lors de la démo)*
- **Mode Clair**
- **Mode Sombre**
- **Graphique interactif (Chart.js)**
- **Tableau de données généré dynamiquement**

---

## 🚀 Fonctionnalités Clés

- **Compréhension du Langage Naturel (NLP) :** Détection d'intentions (`QueryIntent`), entités (Régions, Années, Indicateurs), avec ou sans IA Générative (fallback déterministe inclus).
- **Opérations Data Supportées :**
  - Valeur simple (ex: Taux de pauvreté à Dakar)
  - Comparaison (ex: Dakar vs Thiès)
  - Évolution / Tendance temporelle
  - Classement / Top N
  - Agrégations (Moyenne, Somme)
- **Sécurité et Robustesse :**
  - Validation stricte des données importées (CSV idempotent).
  - Whitelist SQL stricte : aucune génération de requêtes libres par l'IA.
- **Interface Avancée :**
  - Intégration de Chart.js avec destruction/recréation propre des canevas.
  - Explicabilité : Le bloc "Comment j'ai compris votre question" montre le JSON d'intention analysé.
  - Support natif du Mode Sombre.

---

## 🛠️ Stack Technique

- **Backend :** Python 3.13, Django 5, Django REST Framework (DRF), PostgreSQL
- **Frontend :** HTML5, Bootstrap 5, Vanilla JS (`chat.js`), Chart.js
- **Architecture :** MVC Django avec Service Layer pour séparer la logique métier (`QuestionService`, `StatistiqueService`).

---

## 👥 Équipe & Répartition

Conformément aux directives du TP, le travail a été effectué en binôme :

- **El Hadji Massogui Diop (Backend / Django) :** Modèles, Imports CSV, Moteur ORM, API REST, Intégration Gemini & Repli déterministe.
- **Serigne Mbacke Faye (Frontend / JS) :** Interface Bootstrap 5, Mode Sombre, Parsing JSON, Gestion Graphique Chart.js, Mocks de test.

---

## ⚙️ Installation & Démarrage (Local)

1. Cloner le dépôt et créer un environnement virtuel.
2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Configurer les variables d'environnement (`.env`) en vous basant sur `.env.example`.
4. Appliquer les migrations :
   ```bash
   python manage.py migrate
   ```
5. Importer les données fictives :
   ```bash
   python manage.py importer_statistiques data/donnees_statistiques_senegal_fictives.csv
   ```
6. Lancer le serveur de développement :
   ```bash
   python manage.py runserver
   ```
