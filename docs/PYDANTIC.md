# Pydantic V2 Validation

Le projet s'appuie sur **Pydantic v2** pour la validation des entrées (Request Body) et la sérialisation des sorties (Response Body).

## Pourquoi Pydantic ?
1. **Sécurité**: Empêche l'injection de données malformées.
2. **Documentation**: Génère automatiquement le Swagger UI (`/docs`).
3. **Performance**: V2 est écrit en Rust, offrant une validation ultra-rapide.

## Modèles Clés

### Schéma de création (`UserCreate`)
Assure que l'email est valide et que le mot de passe respecte les contraintes.

```python
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
```

### Schéma de réponse (`UserResponse`)
Filtre les données sensibles (comme le hash du mot de passe) avant l'envoi au client.

```python
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    
    class Config:
        from_attributes = True # Permet la conversion auto depuis SQLAlchemy
```

## Validation ML
Toutes les caractéristiques (features) envoyées au modèle XGBoost sont validées par le schéma `MatchFeatures` dans la ML API.
