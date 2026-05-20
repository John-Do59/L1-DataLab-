# 🎙️ Pitch de Soutenance - Ligue 1 Predictive Analytics

Ce document contient la structure narrative pour présenter le projet au jury RNCP.

## 🌟 1. L'Accroche (30 secondes)
"Le football est souvent perçu comme imprévisible. Pourtant, derrière chaque match se cachent des millions de données : performances historiques, valorisations financières, cotes du marché. Mon projet, **Ligue 1 DataLab**, transforme ce chaos de données en un système de prédiction industriel capable d'identifier les victoires à domicile avec plus de 80% de fiabilité."

## 🛠️ 2. Le Défi Technique (1 minute)
"Le défi n'était pas seulement de faire du Machine Learning, mais de construire une **architecture micro-services robuste** :
- **Multi-sources** : Ingestion asynchrone et résolution d'entités.
- **Double Persistance** : Séparation des données ML (`l1_ml`) et Applicatives (`l1_app`).
- **APIs découplées** : Une API spécialisée ML (XGBoost) et une API Produit servant de Gateway.
- **Conteneurisation** : Déploiement complet via Docker Compose."

## 🧠 3. Les "Wow Factors" (2 minutes)
Voici les trois piliers qui font la force du projet :
1. **L'Elo Rating** : "J'ai implémenté l'algorithme Elo (utilisé aux échecs) pour quantifier la puissance réelle des équipes, ce qui a été le moteur principal de notre performance."
2. **Double Sécurité de Nettoyage** : "Le système filtre les doublons dès le scraping (Scrapy Pipeline) et garantit l'intégrité en base de données (SQL ON CONFLICT)."
3. **Analyse Critique** : "Je ne vends pas un modèle parfait. Je présente un modèle audité, dont je connais précisément les zones d'incertitude (le match nul)."

## 📈 4. Résultats & Impact (1 minute)
- **Accuracy** : ~48-52% (Performance significative en prédiction sportive).
- **Recall Home** : 81% (Expertise sur les victoires à domicile).
- **Inférence Live** : "Le système est opérationnel sur la saison actuelle 2025/2026."

## 🏁 5. Conclusion (30 secondes)
"Plus qu'un modèle de prédiction, ce projet démontre une maîtrise complète de la chaîne de valeur de la donnée : de la capture brute au produit fini, audité et prêt pour la production."

---

### 💡 Conseils pour les questions du Jury :
- **Si on vous demande pourquoi l'accuracy n'est pas plus haute ?**
  > "Le football contient une part de hasard (hasard structurel). Même les bookmakers professionnels plafonnent. L'important est d'avoir un modèle calibré et stable."
- **Si on vous demande comment vous gérez les nouvelles équipes ?**
  > "Le système Elo attribue une note par défaut de 1500 points et s'ajuste dynamiquement dès les premiers matchs."
