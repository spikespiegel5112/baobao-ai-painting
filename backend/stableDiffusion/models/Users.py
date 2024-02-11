# from sqlalchemy import String
# from sqlalchemy.orm import Mapped
# from sqlalchemy.orm import mapped_column
#
# from stableDiffusion.models.Base import Base
#
#
# class Users(Base):
#     __tablename__ = "users"
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     userName: Mapped[str] = mapped_column(String(100))
#     welinkUserId: Mapped[str] = mapped_column(String(500))
#     welinkTenantId: Mapped[str] = mapped_column(String(500))
#     guestUserId: Mapped[str] = mapped_column(String(500))
#     role: Mapped[str] = mapped_column(String(100))
#
#     def __repr__(self) -> str:
#         return f"User(id={self.id!r})"
