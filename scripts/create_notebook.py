import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

# Markdown introduction
md_intro = """# Baseline Model: Logistic Regression
L'objectif de ce notebook est d'établir un modèle de référence (baseline) simple et interprétable pour la prédiction des résultats des matchs de Ligue 1 (H: Domicile, D: Nul, A: Extérieur).
Nous utiliserons une **Régression Logistique** sur notre dataset `ml_dataset.csv`.

Étapes :
1. Chargement des données
2. Nettoyage et encodage
3. Split temporel (Train sur les saisons passées, Test sur la saison actuelle)
4. Entraînement du modèle
5. Évaluation (Accuracy, Matrice de Confusion, Rapport de Classification)
"""

# Import code
code_imports = """import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler
import os

# Configuration de base
plt.style.use('ggplot')
sns.set_palette("husl")
"""

# Load Data code
code_load = """# 1. Chargement du dataset
DATA_PATH = '../features/ml_dataset.csv'
df = pd.read_csv(DATA_PATH)

print(f"Shape: {df.shape}")
df.head()
"""

# Data Prep code
code_prep = """# 2. Préparation des données
# On retire les matchs qui n'ont pas de résultat (ex: matchs futurs)
df = df.dropna(subset=['result'])

# Features sélectionnées pour la baseline
features = [
    'home_form_5', 'away_form_5',
    'home_offensive_str', 'away_offensive_str',
    'home_defensive_str', 'away_defensive_str',
    'home_avg_overall', 'away_avg_overall',
    'home_squad_value', 'away_squad_value'
]

# Gestion des valeurs manquantes simples
df[features] = df[features].fillna(df[features].median())

X = df[features]
y = df['result']
"""

# Temporal Split code
code_split = """# 3. Split Temporel
# On utilise la saison 2018/19 pour tester, et tout le reste pour entraîner.
test_season = '2018/19'

train_mask = df['season'] != test_season
test_mask = df['season'] == test_season

X_train, y_train = X[train_mask], y[train_mask]
X_test, y_test = X[test_mask], y[test_mask]

print(f"Train size: {len(X_train)} matchs")
print(f"Test size: {len(X_test)} matchs")

# Standardisation
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
"""

# Training code
code_train = """# 4. Entraînement de la Régression Logistique
model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X_train_scaled, y_train)

print("Modèle entraîné avec succès !")
"""

# Evaluation code
code_eval = """# 5. Évaluation du modèle
y_pred = model.predict(X_test_scaled)

accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy sur la saison test ({test_season}) : {accuracy:.2%}")

print("\\nClassification Report:")
print(classification_report(y_test, y_pred))
"""

# Confusion Matrix
code_cm = """# Affichage de la matrice de confusion
labels = ['H', 'D', 'A']
cm = confusion_matrix(y_test, y_pred, labels=labels)

plt.figure(figsize=(6,5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
plt.xlabel('Prédiction')
plt.ylabel('Réalité')
plt.title(f'Matrice de Confusion - Baseline Logistic ({test_season})')
plt.show()
"""

# Add cells to notebook
nb['cells'] = [
    nbf.v4.new_markdown_cell(md_intro),
    nbf.v4.new_code_cell(code_imports),
    nbf.v4.new_code_cell(code_load),
    nbf.v4.new_code_cell(code_prep),
    nbf.v4.new_code_cell(code_split),
    nbf.v4.new_code_cell(code_train),
    nbf.v4.new_code_cell(code_eval),
    nbf.v4.new_code_cell(code_cm)
]

# Write out the notebook
with open('ml/notebooks/03_baseline_logistic.ipynb', 'w') as f:
    nbf.write(nb, f)
