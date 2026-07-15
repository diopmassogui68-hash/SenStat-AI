# 🎤 Script de Démonstration — Soutenance Backend (Massogui)

*Ce document est ton "antisèche" pour la présentation devant le jury. Suis ces étapes dans l'ordre pour impressionner le professeur et lui prouver que tous les critères de la grille sont validés à 100%.*

---

## ⏱️ Préparation avant la démo (En coulisses)
1. Ouvre ton terminal dans le dossier du projet.
2. Active l'environnement virtuel : `.\env\Scripts\activate`
3. Vérifie que ton `.env` est bien configuré (pas besoin de la clé Gemini au début pour prouver le fonctionnement NLP).

---

## 🎬 Étape 1 : Le Modèle et la Sécurité (Montrer le code)
**Ce que tu dis :** *"Pour respecter les contraintes de RAM (8 Go), j'ai opté pour une architecture monolithique découplée sous Django, sans Celery ni Redis."*

1. **Ouvre `apps/statistics/models.py`**
   - Montre les validateurs (`MinValueValidator(0.0)`).
   - Montre `UniqueConstraint` en expliquant que c'est la norme Django moderne pour éviter les doublons métier.

2. **Ouvre `apps/statistics/services.py`**
   - Pointe la ligne `WHITELIST_FIELDS: frozenset`.
   - **L'argument qui tue :** *"Plutôt qu'une liste, j'ai utilisé un `frozenset`. C'est immutable, et la recherche se fait en temps constant O(1), ce qui sécurise instantanément l'API contre toute attaque d'injection SQL."*

---

## 🎬 Étape 2 : L'Importation Idempotente et le Logging
**Ce que tu dis :** *"Le script d'import a été conçu pour être robuste, loggué, et idempotent (barème 15 points)."*

1. **Dans le terminal**, lance l'import (assure-toi d'avoir un fichier CSV sous la main, par exemple `dataset.csv`) :
   ```bash
   python manage.py importer_statistiques dataset.csv
   ```
2. **Montre le résultat terminal** (succès).
3. **L'argument qui tue :** Relance exactement **la même commande**. Le terminal va afficher `Mis à jour : X` ou `Créés : 0`.
   - *"Comme vous le voyez, le script utilise `update_or_create`. Aucun doublon n'est créé si on importe 10 fois le même fichier."*
4. **Ouvre le dossier `logs/`** et montre `application.log` pour prouver que tout est tracé en temps réel.

---

## 🎬 Étape 3 : Le Moteur NLP Déterministe et l'API
**Ce que tu dis :** *"Conformément aux exigences, le système doit fonctionner SANS Intelligence Artificielle. J'ai donc codé un moteur NLP local."*

1. **Lance le serveur :**
   ```bash
   python manage.py runserver
   ```
2. **Ouvre Swagger** dans ton navigateur : [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
   - Montre que l'API est magnifiquement documentée grâce à `drf-spectacular`.

3. **Fais un test en direct dans Swagger** (Endpoint POST `/api/question/`) :
   - *Test 1 (Question simple)* : `{"question": "Quel est le chômage à Dakar en 2024 ?"}`
     - Fais remarquer que "chômage" est reconnu malgré l'absence d'accent.
   - *Test 2 (Déduction / Trend)* : `{"question": "Évolution de la population de Dakar de 2020 à 2023"}`
     - Montre le JSON de retour : le `chart_type` est devenu `"line"`, et l'opération `"trend"` a été déduite automatiquement.
   - *Test 3 (Sécurité / Ambiguïté)* : `{"question": "Compare la pauvreté à Dakar."}`
     - Montre le message d'erreur poli expliquant qu'il faut au moins 2 régions pour comparer.

---

## 🎬 Étape 4 : Les Tests Automatisés (La cerise sur le gâteau)
**Ce que tu dis :** *"Pour garantir la stabilité du code avant de passer le relais au Frontend, j'ai implémenté une suite de tests unitaires couvrant tous les cas limites."*

1. **Dans le terminal**, lance les tests :
   ```bash
   python manage.py test --verbosity=2
   ```
2. Laisse le jury apprécier la vitesse d'exécution et le message **`Ran 16 tests in 0.xxx s - OK`**.

---
*Fin de ta partie. Tu peux céder la parole avec fierté : "Le backend est solide, sécurisé et documenté. Je passe la main à mon collègue Serigne pour vous montrer comment cette API a été consommée par l'interface Frontend."*
