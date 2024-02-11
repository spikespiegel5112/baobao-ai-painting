from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from stableDiffusion.models import Base


class Images(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fileName: Mapped[str] = mapped_column(String(100))
    positivePrompt: Mapped[str] = mapped_column(String(2000))
    negativePrompt: Mapped[str] = mapped_column(String(2000))
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    welinkUserId: Mapped[int] = mapped_column(String(500))
    guestUserId: Mapped[str] = mapped_column(String(500))
    role: Mapped[str] = mapped_column(String(100))

    def __repr__(self) -> str:
        return f"User(id={self.id!r})"
