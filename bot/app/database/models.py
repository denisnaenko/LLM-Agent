from sqlalchemy import BigInteger, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from typing import List

engine = create_async_engine(url="sqlite+aiosqlite:///db.sqlite3")
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase): ...

class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=False)
    skin_type: Mapped[str] = mapped_column(String(50), nullable=True)
    features: Mapped[str] = mapped_column(String, nullable=True)
    risks: Mapped[str] = mapped_column(String, nullable=True)

    def set_features(self, features: List[str]):
        """Устанавливает особенности как строку, разделённую запятыми"""
        self.features = ",".join(features)

    def get_features(self) -> List[str]:
        """Возвращает особенности как список строк"""
        return self.features.split(",") if self.features else []

    def set_risks(self, risks: List[str]):
        """Устанавливает риски как стрку, разделённую запятыми"""
        self.risks = ",".join(risks)

    def get_risks(self) -> List[str]:
        """Возвращает риски как список строк."""
        return self.risks.split(",") if self.risks else []

# Асинхронная функция для создания таблицы
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)