from app.database.models import async_session
from app.database.models import User
from typing import List
from sqlalchemy import text

async def upsert_user(tg_id: int, skin_type: str, features: List[str], risks: List[str]):
    """Добавляет пользователя или обновляет данные, если запись уже существует"""
    
    async with async_session() as session:
        async with session.begin():
            # Пытаемся получить пользователя по tg_id
            query = text("SELECT * FROM users WHERE tg_id = :tg_id")
            existing_user = await session.execute(query, {"tg_id": tg_id})
            user = existing_user.fetchone()

            if user:
                # Если пользователь существует, обновляем его данные
                user_obj = await session.get(User, user.user_id)
                user_obj.skin_type = skin_type
                user_obj.set_features(features)
                user_obj.set_risks(risks)
            else:
                # Если пользователь не найден, добавляем новую запись
                user_obj = User(tg_id=tg_id, skin_type=skin_type)
                user_obj.set_features(features)
                user_obj.set_risks(risks)
                session.add(user_obj)