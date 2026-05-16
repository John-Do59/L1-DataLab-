# Sécurité et Authentification JWT

## Architecture de Sécurité
L'application **L1 DataLab** utilise désormais une architecture de sécurité robuste basée sur les standards de l'industrie :
- **Hashage des mots de passe** : Utilisation native de `bcrypt` (contournement du bug passlib/bcrypt pour Python 3.12+).
- **Tokens** : JSON Web Tokens (JWT) signés avec l'algorithme `HS256`.
- **Validation** : Protection des routes via l'injection de dépendances FastAPI (`OAuth2PasswordBearer`).

## Endpoints Implémentés

### 1. Inscription (`POST /users`)
Permet la création d'un utilisateur.
- **Entrée** : `username`, `email`, `password` (clair).
- **Traitement** : Le mot de passe est haché via un salt généré par `bcrypt` avant stockage en base de données.
- **Sortie** : Modèle utilisateur (sans le mot de passe).

### 2. Connexion (`POST /auth/login`)
Point d'entrée pour récupérer le token d'accès.
- **Entrée** : Formulaire `OAuth2PasswordRequestForm` (champs `username` et `password`).
- **Traitement** : Vérification stricte via `bcrypt.checkpw()`.
- **Sortie** : 
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1...",
    "token_type": "bearer"
  }
  ```

### 3. Route Protégée (`POST /predict`)
Le "cœur métier" de l'application est protégé. L'utilisateur doit fournir le token dans les en-têtes HTTP.
- **Header requis** : `Authorization: Bearer <access_token>`
- **Comportement** : La dépendance `get_current_user` décode le JWT, vérifie son expiration (`exp`), valide l'identité (`sub`), et injecte l'objet `User` directement dans le contexte de la route.

## Historique et Traçabilité
Grâce à cette authentification, chaque appel à `/predict` est enregistré dans la table `prediction_history` avec l'ID de l'utilisateur (`current_user.id`), permettant ainsi de :
- Créer un dashboard personnalisé pour chaque utilisateur.
- Calculer le taux de réussite des prédictions (Brier Score individuel).
