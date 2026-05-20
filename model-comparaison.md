# 🏆 Rapport de Comparaison des Modèles Prédictifs (L1 DataLab)

Ce document synthétise la démarche scientifique, l'évaluation et les choix techniques qui ont conduit à la sélection du modèle de production pour motoriser la plateforme L1 DataLab.

---

## 1. Cadre Méthodologique de Modélisation

Prédire l'issue d'un match de football (Victoire Domicile `H`, Nul `D`, Victoire Extérieur `A`) est un problème stochastique à forte variance. Pour assurer la crédibilité de notre travail auprès d'un jury ou de professionnels de la Data Science, nous avons appliqué deux principes stricts :

### A. Le Split Temporel (Chronologique)
*   **Le problème du split standard** : Utiliser un `train_test_split(shuffle=True)` classique provoque du *Data Leakage*. On utilise des informations du futur (ex: forme des équipes en mai 2025) pour évaluer des matchs du passé (ex: août 2024).
*   **Notre solution** : Nous avons trié le dataset chronologiquement et séparé strictement les données : **80% passés pour l'entraînement (Train)** et **20% futurs/récents pour la validation (Test)**.

### B. La Calibration des Probabilités
*   En sport, prédire uniquement la classe la plus probable (ex: victoire à domicile) est insuffisant. Il est indispensable d'obtenir une **probabilité précise et réaliste** (ex: 62% de victoire, 20% de nul, 18% de défaite).
*   Nous avons appliqué la méthode **Platt Scaling** (`CalibratedClassifierCV` avec une sigmoïde) sur le Random Forest afin de lisser ses probabilités de sortie et de les aligner sur la fréquence réelle des événements.

---

## 2. Tableau de Comparaison des Performances (Validation Set)

Voici le benchmark officiel obtenu sur les **12 features dynamiques** réellement stockées en production :

| Métrique d'Évaluation | 🌲 Random Forest Calibré | 🚀 XGBoost Classifier | Analyse du Score |
|---|---|---|---|
| **Accuracy (Exactitude)** | **60.53%** | **51.95%** | RF surpasse largement XGBoost (+8.58%) |
| **Log Loss (Entropie Croisée)** | **0.8323** | **0.9595** | RF est beaucoup plus fiable et calibré |
| **F1-Score (Macro)** | **53.30%** | **49.88%** | RF gère mieux le déséquilibre des classes |
| **Precision (Macro)** | **54.91%** | **49.46%** | RF commet beaucoup moins de faux positifs |
| **Recall (Macro)** | **52.28%** | **50.31%** | RF capture plus fidèlement les surprises |
| **ROC-AUC (Macro OVR)** | **73.19%** | **70.12%** | RF sépare mieux les issues possibles |

---

## 3. Analyse Critique des Modèles

### 🌲 Random Forest Calibré (Sélectionné pour la Production)
*   **Pourquoi il performe si bien (60.53%)** : Le Random Forest est un modèle basé sur le *Bagging* (entraînement de plusieurs arbres indépendants en parallèle). Il est naturellement robuste au sur-apprentissage. Combiné avec une **calibration Platt Scaling**, le modèle évite les prédictions trop confiantes erronées. C'est le modèle parfait pour notre API en direct.

### 🚀 XGBoost Classifier (Rejeté)
*   **Pourquoi il sous-performe (51.95%)** : Le boosting (XGBoost) entraîne les arbres de manière séquentielle pour corriger les erreurs des précédents. Sur un dataset de taille modérée comme l'historique de Ligue 1, le boosting a tendance à **sur-apprendre (overfitting) la variance historique** et les anomalies d'une saison donnée, ce qui dégrade sa capacité à généraliser sur les saisons futures.

---

## 4. Décision & Architecture de Production

Le modèle **Random Forest Calibré (v1)** est officiellement déployé en production. 

L'API ML [services/ml-api/main.py](file:///Users/amaury/L1-DataLab-/services/ml-api/main.py) charge désormais ce modèle avec `joblib` et expose les métadonnées de prédiction. 
L'API applicative [services/app-api/app/main.py](file:///Users/amaury/L1-DataLab-/services/app-api/app/main.py) relaie automatiquement le nom et la version du modèle pour une transparence totale de l'orbite prédictif.
