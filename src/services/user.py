from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.db import get_session
from models import User
from schemas.user import UserCreate
from services.security import hash_password, manager


@manager.user_loader(session_provider=get_session)
async def get_user(email: str,
                   db: Optional[AsyncSession] = None,
                   session_provider: Optional[AsyncSession] = None
) -> Optional[User]:
    """
    Return the user with the corresponding email.
    """
    if db is None:
        db = await anext(session_provider())
    query = select(User).where(User.email == email)
    user = (await db.scalars(query)).first()
    return user


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
