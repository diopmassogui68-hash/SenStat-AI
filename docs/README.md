# SenStat AI - Agent IA Statistique Django

**Projet de Laboratoire** (Version optimisée 8 Go RAM)
**Membres du groupe (Trinôme) :** 
- **El Hadji Massogui Diop** (Backend / Django ORM / NLP)
- **Serigne Mbacke Faye** (Cœur Frontend / JS / Chart.js)
- **Sanor Mangane** (Habillage / UX Premium / CSS)

---

## 📌 Présentation du Projet
SenStat AI est un prototype d'assistant conversationnel spécialisé dans l'interrogation de données statistiques régionales sénégalaises (2020-2024). L'objectif est de fournir une interface intuitive en langage naturel permettant d'extraire des valeurs, comparer des régions, afficher des évolutions temporelles ou générer des classements.

**Avertissement :** *Toutes les données utilisées dans cette application sont strictement fictives et à vocation pédagogique.*

## 🚀 Guide d'Installation et de Lancement

### 1. Prérequis
- Python 3.13
- Git

### 2. Installation
```bash
# Cloner le dépôt et entrer dans le dossier
git clone <url_du_repo>
cd SenStat-AI

# Créer et activer l'environnement virtuel
python -m venv .venv
# Sur Windows :
.\.venv\Scripts\activate
# Sur Linux/Mac :
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration et Base de Données
```bash
# Générer la base de données
python manage.py makemigrations statistics
python manage.py migrate

# Importer le jeu de données (Idempotent)
python manage.py importer_statistiques donnees_statistiques_senegal_fictives.csv
```

### 4. Lancement du Serveur
```bash
python manage.py runserver
```
Rendez-vous sur [http://127.0.0.1:8000](http://127.0.0.1:8000) pour utiliser l'application.

---

## 💡 Exemples de questions pour la Démonstration (Soutenance)

1. **Valeur simple** : *"Quelle est la population de Dakar en 2024 ?"*
2. **Comparaison (Graphique Barre)** : *"Compare le taux de chômage entre Thiès, Diourbel et Kaolack en 2023."*
3. **Évolution (Graphique Ligne)** : *"Montre-moi l'évolution de l'accès internet à Ziguinchor entre 2020 et 2024."*
4. **Classement (Top N)** : *"Quels sont les 3 meilleurs élèves pour le taux de scolarisation ?"*
5. **Hors sujet / Ambigu (Sécurité)** : *"Quel est le score du match de foot d'hier ?"* (Doit être refusé poliment).

---

## 🏗️ Architecture et Choix Techniques

Notre approche s'est concentrée sur l'efficacité et la sécurité (pas de sur-ingénierie, empreinte RAM minimale).

1. **Sécurité ORM (Whitelist)** : Toute intention utilisateur est confrontée à une liste blanche stricte (`ALLOWED_INDICATORS`). Aucune requête SQL issue de l'utilisateur ou générée par une IA n'est directement exécutée.
2. **Double Moteur NLP** :
   - **Moteur Primaire (Optionnel)** : IA Générative (Gemini 1.5 Flash via `GEMINI_API_KEY` dans `.env`) bridée avec une température à `0.1` pour renvoyer exclusivement un JSON.
   - **Moteur de Repli (Garantie de service)** : Un algorithme déterministe puissant (regex + dictionnaires de synonymes) prend le relais silencieusement si l'IA échoue, si le réseau coupe, ou si aucune clé n'est fournie.
3. **Interface Glassmorphism** : Le frontend utilise des variables CSS pures et Bootstrap 5 pour un mode sombre/clair ultra-léger et un design "Premium" (pas de frameworks lourds).

---

## 📊 Note de synthèse : Limites & Améliorations Possibles

Dans le cadre strict des contraintes matérielles imposées (8 Go RAM, temps limité), nous avons privilégié la robustesse et l'exactitude des données à l'ajout massif de fonctionnalités. Voici une analyse critique de notre propre solution :

### Limites actuelles
1. **Compréhension NLP déterministe stricte** : Si le moteur de repli est utilisé (sans IA), il exige que l'utilisateur utilise des mots-clés proches de ceux définis dans `synonyms.py`. Une phrase trop complexe ou une faute d'orthographe majeure non prévue pourrait générer une "ambiguïté".
2. **Scalabilité des entités** : Les 14 régions sont codées en dur pour l'extraction. Si le Sénégal crée une 15ème région, il faudra modifier le code source du NLP (en mode déterministe).
3. **Persistance de l'historique** : L'historique du chat est géré purement côté client (`chat.js`). Un rafraîchissement de la page (F5) efface la conversation.

### Améliorations futures (Si mis en production)
1. **Base de données vectorielle légère** : Pour améliorer le NLP sans dépendre d'une API externe (Gemini), nous pourrions intégrer `ChromaDB` (très léger en local) ou `pgvector` avec un petit modèle d'embeddings (ex: `all-MiniLM-L6-v2`) pour comprendre le sens sémantique des questions sans dictionnaire codé en dur.
2. **Tableau de Bord / Dashboard global** : Actuellement l'outil est purement conversationnel. Ajouter une page "Vue d'ensemble" avec une carte choroplèthe du Sénégal utilisant `Folium` ou `Leaflet` apporterait une plus-value décisionnelle.
3. **Mise en cache** : Bien que la base actuelle soit minuscule (70 lignes), sur une vraie base nationale à des millions de lignes, intégrer Redis (ou le cache Django natif en mémoire) sur les requêtes fréquentes (ex: "population globale") réduirait le temps de latence.

---

## ✅ Tableau de Conformité (Grille d'évaluation)

| Exigence du Cahier des Charges | Statut | Emplacement / Justification |
|--------------------------------|--------|-----------------------------|
| Modèle exact avec les 11 champs | ✅ | `apps/statistics/models.py` (StatistiqueRegionale) |
| Contrainte d'unicité (region+annee) | ✅ | `Meta.constraints` (UniqueConstraint) |
| Import idempotent (update_or_create) | ✅ | `importer_statistiques.py` |
| Validation stricte des données (0-100) | ✅ | `apps/statistics/validators.py` |
| NLP : Extraction indicateurs/régions/années | ✅ | `apps/chatbot/nlp/entities.py` |
| NLP : Détection d'ambiguïté | ✅ | `intent_parser.py` (_resolve_ambiguity) |
| ORM Sûr : Whitelist de champs | ✅ | `apps/statistics/services.py` (ALLOWED_INDICATORS) |
| Opérations couvertes (val, comp, trend, rank, sum, avg)| ✅ | `StatistiqueService._handle_*` |
| API : Contrat JSON exact et stable | ✅ | `apps/api/views.py` et `services.py` |
| Interface : Zone saisie, Chat, Tableau, Loader | ✅ | `templates/chatbot/index.html` |
| Graphiques Chart.js cohérents avec tableau | ✅ | `static/js/chat.js` (updateChart) |
| Destruction du graphique précédent (règle lab) | ✅ | `chat.js` (chartInstance.destroy()) |
| Mention "données fictives" visible | ✅ | Navbar + `models.py` docstring |
| Tests (8 minimum) couvrant nominaux/limites | ✅ | `apps/statistics/tests/` et `apps/chatbot/tests/` (9 tests au total) |
| Architecture sans sur-ingénierie | ✅ | Pas de Kubernetes, Celery, etc. |
| Bonus : Bloc "Analyse / Comment j'ai compris" | ✅ | Frontend (badge sous les messages IA) |
| Bonus : Suggestions contextuelles & Mode Sombre | ✅ | Frontend (CSS pur, JS léger) |
| Bonus : Repli déterministe silencieux si échec IA | ✅ | `apps/chatbot/services.py` (QuestionService) |
