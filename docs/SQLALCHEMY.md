# SQLAlchemy 2.0 Async Guide

Cette plateforme utilise **SQLAlchemy 2.0** en mode asynchrone pour garantir des performances optimales sous haute charge (FastAPI).

## Architecture
- **Engine**: `create_async_engine` avec le driver `postgresql+asyncpg`.
- **Session**: `async_sessionmaker` pour une gestion thread-safe.
- **Pattern**: Repository Pattern pour isoler la logique de persistance.

## Exemple d'utilisation (Service/Repository)

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import User

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str):
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalars().first()
```

## Injection de Dépendance (FastAPI)
La session est injectée automatiquement dans les endpoints :

```python
@app.post("/users")
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # ...
```

## Commandes Utiles
- Vérifier la connexion : `docker compose logs db-app`
- Voir le schéma : `docker exec -it l1-db-app psql -U postgres -d l1_app -c "\dt"`
