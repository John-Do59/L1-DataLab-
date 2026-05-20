# 🔥 Supervision Prometheus - L1 DataLab

Ce document détaille la configuration, l'intégration réseau et les métriques supervisées par **Prometheus** pour la surveillance en temps réel de notre API de Machine Learning.

---

## 🏗️ Architecture du Grattage (Scraping)

Prometheus est configuré comme un service conteneurisé indépendant (`l1-prometheus`) connecté au réseau interne de Docker.
* **Intervalle de collecte (`scrape_interval`)** : Réglé sur **5 secondes** (`5s`) pour permettre une réactivité maximale sur les indicateurs de prédiction lors des soutenances et démonstrations.
* **Cible (Target)** : Lit le endpoint de télémétrie `/metrics` exposé sur le conteneur de l'API ML : `ml-api:8000`.

---

## 📊 Métriques MLOps Supervisées

L'API ML expose des indicateurs métier et techniques indispensables pour le maintien en conditions opérationnelles de l'intelligence artificielle :

### 1. Compteurs de Prédictions (`l1_ml_predictions_total`)
* **Type** : `Counter` (incrémenté à chaque appel).
* **Labels** :
  * `outcome` : L'issue prédite (`H` pour victoire à domicile, `D` pour match nul, `A` pour victoire à l'extérieur).
  * `model_version` : Identifiant unique de la version de modèle championne active en production (ex : `v_20260519_030117`).
* **Usage** : Analyser le volume d'appels et la distribution des décisions prises par le modèle.

### 2. Histogramme de Certitude (`l1_ml_prediction_confidence`)
* **Type** : `Histogram` (répartition par seaux / bins).
* **Usage** : Visualiser si les prédictions émises par l'IA ont une certitude élevée (proche de 1.0) ou incertaine (proche de 0.33), révélant un éventuel fléchissement de la confiance du modèle.

### 3. Statut du Concept Drift (`l1_ml_concept_drift_status`)
* **Type** : `Gauge` (valeur instantanée).
* **Codes de statut** :
  * `0` : **Stable**. Le modèle a une confiance moyenne glissante conforme aux distributions d'entraînement.
  * `1` : **Déviation suspectée**. La certitude moyenne glissante a chuté de plus de 15%. Un réentraînement est conseillé.
  * `2` : **Drift critique**. La confiance glissante s'est écroulée sous 38%. Un réentraînement immédiat est déclenché/requis.

### 4. Gauges de Performances du Champion Actif
* `l1_ml_active_model_accuracy` : Taux de prédiction correcte du modèle sur le jeu de validation temporel.
* `l1_ml_active_model_brier_score` : Mesure de calibration probabiliste multi-classes (proche de `0.0` = parfaite).
* `l1_ml_active_model_log_loss` : Indice de surprise du modèle lors des tests temporels.

---

## 📈 Exemples de Requêtes PromQL Utiles

Saisissez ces expressions directement dans la barre de recherche sur l'interface de Prometheus (`http://localhost:9090`) pour tracer des graphiques en direct :

* **Taux d'appels à la seconde (toutes versions confondues)** :
  ```promql
  sum(rate(l1_ml_predictions_total[1m]))
  ```
* **Distribution des prédictions par issue et version** :
  ```promql
  l1_ml_predictions_total
  ```
* **Surveillance en direct de la dérive (Concept Drift)** :
  ```promql
  l1_ml_concept_drift_status
  ```
* **Évolution de la calibration (Brier Score)** :
  ```promql
  l1_ml_active_model_brier_score
  ```

---

## 🌐 Accès à la Console
Dès que la stack Docker est démarrée, accédez à la console de diagnostic Prometheus à l'adresse suivante :
👉 **[http://localhost:9090](http://localhost:9090)**
