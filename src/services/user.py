from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models import User
from schemas.user import UserCreate
from services.security import hash_password, manager


@manager.user_loader
async def get_user(email: str, db: AsyncSession) -> Optional[User]:
    """
    Return the user with the corresponding email.
    """
    query = select(User).where(User.email == email)
    obj_url = (await db.scalars(query)).first()
    return obj_url


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """
    Create a new entry in the database user table.
    """
    user_data = user.model_dump()
    user_data['hashed_password'] = hash_password(user.password)
    user_data.pop('password')
    db_user = User(**user_data)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
