# 📊 Tableaux de Bord Grafana - L1 DataLab

Ce document détaille la configuration de **Grafana** pour la visualisation premium de nos télémétries et la supervision de nos modèles en production.

---

## 🚀 Premier Démarrage & Identifiants

Grafana démarre automatiquement en tant que service conteneurisé (`l1-grafana`).
* **Adresse d'accès locale** : 👉 **[http://localhost:3000](http://localhost:3000)**
* **Identifiants de connexion** :
  * **Utilisateur** : `admin`
  * **Mot de passe par défaut** : `admin` (il vous sera demandé de le modifier lors du premier accès).

---

## 🔌 Raccordement de la Source de Données (Prometheus)

Pour lier Grafana à Prometheus au sein du réseau isolé de Docker :

1. Cliquez sur l'icône **Menu** (en haut à gauche) $\to$ **Connections** $\to$ **Data sources**.
2. Cliquez sur **Add data source** et sélectionnez **Prometheus**.
3. Remplissez le champ **Connection URL** avec l'adresse du conteneur interne :
   ```
   http://prometheus:9090
   ```
4. Descendez en bas de page et cliquez sur **Save & test**. Un message vert *"Data source is working"* doit apparaître !

---

## 🛠️ Création du Tableau de Bord "MLOps AI Insights"

Voici les configurations recommandées pour concevoir un dashboard MLOps premium devant le jury :

### 1. Panel "Statut de Dérive (Concept Drift)" (Jauge Lumineuse)
* **Visualisation** : `Gauge` ou `Stat`.
* **Requête PromQL** : `l1_ml_concept_drift_status`
* **Mise en forme (Thresholds)** :
  * `0` $\to$ Vert (Stable, inférence saine).
  * `1` $\to$ Orange (Dérive suspectée, retrain suggéré).
  * `2` $\to$ Rouge (Drift critique, retrain urgent !).

### 2. Panel "Calibration probabiliste (Brier Score)" (Série Temporelle)
* **Visualisation** : `Time series`.
* **Requête PromQL** : `l1_ml_active_model_brier_score`
* **Objectif de Production** : Plus la courbe est proche de `0`, plus le modèle est performant et calibré.

### 3. Panel "Précision de Prédiction (Accuracy)" (Série Temporelle)
* **Visualisation** : `Time series` ou `Gauge`.
* **Requête PromQL** : `l1_ml_active_model_accuracy * 100`
* **Unité de valeur** : Pourcentage (`%`).

### 4. Panel "Volume de Prédictions par Issue" (Diagramme Circulaire)
* **Visualisation** : `Pie chart`.
* **Requête PromQL** : `sum by (outcome) (l1_ml_predictions_total)`
* **Usage** : Analyser si le modèle a un biais en faveur des victoires à domicile (`H`) ou s'il prédit fidèlement la réalité.

---

## 💾 Sauvegarde Persistante
Toutes vos modifications de tableaux de bord, dossiers et sources de données sont sauvegardées de manière persistante sur votre machine hôte grâce au volume Docker nommé `grafana_data` défini à la base de `docker-compose.yml`. Aucun risque de perte de données en arrêtant la stack !
