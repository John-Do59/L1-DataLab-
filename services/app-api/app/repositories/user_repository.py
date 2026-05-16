from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.models import User
from ..schemas.schemas import UserCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str):
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, user_in: UserCreate):
        hashed_pw = pwd_context.hash(user_in.password)
        db_user = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed_pw
        )
        self.session.add(db_user)
        await self.session.flush() # Pour récupérer l'ID
        return db_user
