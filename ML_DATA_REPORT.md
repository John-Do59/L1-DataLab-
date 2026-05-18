# Rapport Pipeline Machine Learning (L1 DataLab)

Ce document explique de manière transparente comment les données sont utilisées pour entraîner notre modèle de prédiction des résultats de Ligue 1 (Victoire Domicile, Nul, Victoire Extérieur).

## 1. Sources de Données (Sources Brutes)

L'intelligence de l'algorithme repose sur une convergence de plusieurs sources hétérogènes :

- **API Ligue 1 (LFP)** : Historique des scores, compositions des équipes, et informations officielles sur les clubs (logos, identifiants).
- **Scraping FC24** : Données statistiques et attributs des joueurs (Offense, Défense, Overall) pour quantifier le niveau intrinsèque d'un effectif sur une saison.
- **Transfermarkt** : Valeur marchande des joueurs et des effectifs, un excellent proxy pour évaluer la qualité d'une équipe et son budget.
- **Bookmakers (Boutique Parquet)** : Cotes et probabilités implicites historiques. L'intégration de la sagesse des foules (marché des paris) est souvent le prédicteur le plus performant.

## 2. Nettoyage et Consolidation (Data Cleaning)

Avant de devenir des "Features", les données brutes ont subi plusieurs étapes de nettoyage (dans `scripts/etl_*`) :

- **Gestion des valeurs manquantes** : Remplacement par la médiane globale pour éviter la perte de données (ex: si une donnée FC24 manque pour un joueur précis).
- **Suppression des doublons** : Le scraping peut générer des doublons (plusieurs passages sur une même page). Le script ETL fusionne les données en s'assurant de garder l'observation la plus récente.
- **Alignement temporel (Time Travel)** : Il est crucial d'éviter la *fuite de données (data leakage)*. Toutes les statistiques (forme, Elo, moyenne de buts) sont calculées **avant** le coup d'envoi du match cible.

## 3. Ingénierie des Caractéristiques (Feature Engineering)

Les modèles simples ne "comprennent" pas le football, ils comprennent les chiffres. Nous avons transformé l'historique brut en 16 caractéristiques (features) puissantes (voir `ml/features/create_ml_dataset.py`) :

### A. Classement Dynamique (Elo Rating)
- `home_elo`, `away_elo`, `elo_diff` : Un système d'évaluation continu similaire aux échecs. Une victoire contre une équipe forte rapporte plus de points qu'une victoire contre une équipe faible.

### B. Dynamique d'Équipe (Forme)
- `home_form_5`, `away_form_5` : Moyenne des points pris (3 pour V, 1 pour N, 0 pour D) sur les 5 derniers matchs.
- `offensive_str` / `defensive_str` : Buts moyens marqués et encaissés sur ces mêmes 5 derniers matchs.

### C. Puissance Intrinsèque (Squad Value)
- `home_avg_overall`, `away_avg_overall` : Note moyenne des joueurs (issue de FC24).
- `home_squad_value`, `away_squad_value` : Valeur financière totale du 11 de départ.

### D. Sagesse des Bookmakers
- `odds_prob_home`, `odds_prob_draw`, `odds_prob_away` : La probabilité implicite calculée à partir de la cote moyenne des bookmakers.

## 4. Modélisation : Vers la Simplicité (Random Forest)

Lors de notre validation croisée, nous avons remarqué qu'un **Random Forest Classifier** (Forêt Aléatoire) performe remarquablement bien avec ces features soigneusement sélectionnées, atteignant environ **57% d'Accuracy**.

### Pourquoi le Random Forest est-il adapté ?
1. **Résistance à l'Overfitting** : Dans le football, la part d'aléatoire est énorme (cartons rouges, poteaux rentrants). Les modèles très complexes comme XGBoost ont tendance à sur-apprendre cet aléa (overfitting). Les forêts aléatoires lissent cette variance.
2. **Interprétabilité** : Nous pouvons facilement extraire quelles variables sont les plus importantes (généralement les cotes et le Elo Diff).
3. **Gestion non-linéaire** : Le modèle comprend que si la différence de Elo est faible, la forme sur les 5 derniers matchs devient le critère décisif.

---
*Rapport généré par l'Analyste IA — L1 DataLab*
