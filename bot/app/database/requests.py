from app.database.models import async_session
from app.database.models import User
from sqlalchemy import select, update, delete

async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()

async def set_skin_type(tg_id, skin_type):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if user: 
            user.skin_type = skin_type
            await session.commit()
        
        