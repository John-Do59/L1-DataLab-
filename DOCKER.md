# 🐳 Guide Infrastructure Docker - L1 DataLab

Ce document détaille l'implémentation, l'optimisation et la gestion de l'infrastructure conteneurisée.

---

## 🏗️ Architecture Multi-Services

L'architecture de production repose sur une orchestration conteneurisée découplée en microservices :

* **Bases de données isolées (PostgreSQL 15)** :
  * `db-ml` (port local `5433`) : Contient les données d'entraînement historique, les variables ingérées et les scores Elo.
  * `db-app` (port local `5434`) : Logique métier, historique prédictions, **pgvector** pour RAG sémantique (image `pgvector/pgvector:pg15`).
* **Cache de performance (Redis 7)** : Port local `6379`, gérant les caches de calcul et les sessions.
* **Moteur d'intelligence (ml-api)** : Port local `8001`. Service d'inférence en charge du chargement dynamique à chaud et à chaud du modèle champion RandomForestCalibrated.
* **Passerelle Applicative (app-api)** : Port local `8002`. Gère les flux métiers et l'authentification.
* **Client Léger (frontend)** : Port local `8080`. Interface Vue.js 3 premium et minimaliste.
* **Supervision MLOps (Prometheus & Grafana)** :
  * Prometheus (port local `9090`) : Gratte la télémétrie de l'API ML toutes les 5 secondes.
  * Grafana (port local `3000`) : Visualise les courbes d'apprentissage et de drift.

---

## 🚀 Tableau de Distribution des Ports Réseau

Voici l'inventaire des accès réseaux de la stack :

| Conteneur | Service | Port Interne | Port Hôte Exposé | Usage |
| :--- | :--- | :--- | :--- | :--- |
| `l1-db-ml` | PostgreSQL (ML) | `5432` | `5433` | Stockage des features et modèles |
| `l1-db-app` | PostgreSQL (App) | `5432` | `5434` | Données métiers de l'application |
| `l1-redis` | Cache Redis | `6379` | `6379` | Cache de performances |
| `l1-ml-api` | FastAPI (Moteur ML) | `8000` | `8001` | Inférence et pipeline MLOps |
| `l1-app-api` | FastAPI (Gateway) | `8000` | `8002` | Logique métier et relais |
| `l1-frontend` | Nginx (Client Vue) | `80` | `8080` | Interface utilisateur |
| `l1-prometheus` | Prometheus | `9090` | `9090` | Collecte des métriques d'inférence |
| `l1-grafana` | Grafana Dashboard | `3000` | `3000` | Tableaux de bord de production |

---

## 🛠️ Commandes Utiles de Maintenance

### 1. Cycle de vie de la Stack
* **Démarrer avec recompilation** : `docker compose up --build -d`
* **Arrêter tous les conteneurs** : `docker compose down`
* **Nettoyer les volumes de données** : `docker compose down -v`

### 2. Diagnostics des API
* **Santé de l'API ML** : `curl http://localhost:8001/`
* **Santé du monitoring Prometheus** : `curl http://localhost:9090/-/healthy`
* **Consulter les logs à chaud** : `docker compose logs -f ml-api`

### 3. Connexions directes PostgreSQL
* **Accéder à la base ML** : `docker exec -it l1-db-ml psql -U postgres -d l1_ml`
* **Accéder à la base App** : `docker exec -it l1-db-app psql -U postgres -d l1_app`

---

## 🔒 Persistance des Modèles & Sécurité

* **Volume de Montage (`./ml/models:/app/ml/models`)** : Ce dossier est partagé en lecture/écriture entre votre machine hôte et le conteneur `l1-ml-api`. Dès que le pipeline MLOps génère un nouveau modèle champion ou met à jour `metadata.json`, l'API ML le charge instantanément à chaud (en <10ms), garantissant un déploiement continu à zéro-downtime.
* **Sécurité Réseau** : Les conteneurs communiquent sur un sous-réseau privé isolé. Seules les APIs et les serveurs web de visualisation (Nginx, Grafana) sont accessibles via votre machine hôte, protégeant vos bases de données contre toute intrusion externe directe.

---

## 🔄 Stratégie de Mise à Jour des Images Docker

Pour garantir la sécurité et les performances, les images Docker sont maintenues avec la politique suivante :

* **Grafana & Prometheus** : Mises à jour régulières (Versions courantes : Grafana `11.1.0`, Prometheus `v2.54.1`).
* **PostgreSQL** : Verrouillé sur la version `15` pour éviter les conflits de données lors des upgrades majeurs. 
* **Python** : Verrouillé sur `3.11` (stabilité et compatibilité Data Science).
* **Node.js** : Verrouillé sur `20` LTS.
* **Redis** : Verrouillé sur `7`.

### Procédure de Mise à Jour

1. **Modifier les versions** dans le fichier `docker-compose.yml`.
2. **Rebuild complet** de la stack (sans utiliser le cache) :

   ```bash
   docker compose build --no-cache
   docker compose up -d
   ```

3. **Vérifications post-déploiement** :
   * Les dashboards Grafana s'affichent correctement.
   * Les métriques Prometheus remontent.
   * Les alertes (Discord/Telegram) et exporters sont fonctionnels.
4. **Attention PostgreSQL** : Ne JAMAIS mettre à jour la version majeure sans :
   * Avoir créé un **Tag Git** de l'état fonctionnel.
   * Avoir fait un dump (export complet) des bases de données au préalable.

### 🛡️ Sécurité & Vulnérabilités (CVE)

Avant tout déploiement sur une infrastructure Cloud (GCP, Kubernetes), il est fortement recommandé d'analyser les images Docker pour détecter d'éventuelles vulnérabilités :

```bash
# Avec Docker Scout
docker scout quickview

# Avec Trivy
trivy image <nom_de_l_image>
```
