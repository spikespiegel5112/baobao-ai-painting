from sqlalchemy import String, Integer, Boolean, DateTime, Column
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


# from models import Images
# from models import Base


class Base(DeclarativeBase):
    pass


class Images(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fileName: Mapped[str] = mapped_column(String(100))
    customPositivePrompt: Mapped[str] = mapped_column(String(500))
    positivePrompt: Mapped[str] = mapped_column(String(2000))
    customNegativePrompt: Mapped[str] = mapped_column(String(500), nullable=True)
    negativePrompt: Mapped[str] = mapped_column(String(2000), nullable=True)
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    seed: Mapped[int] = mapped_column(Integer)
    otherSettings: Mapped[str] = mapped_column(String(500), nullable=True)
    userId: Mapped[int] = mapped_column(String(100), nullable=False)
    userComesFrom: Mapped[int] = mapped_column(String(100), nullable=False)
    welinkUserId: Mapped[int] = mapped_column(String(500), nullable=True)
    guestUserId: Mapped[str] = mapped_column(String(500), nullable=True)
    isPublic: Mapped[bool] = mapped_column(Boolean(False), nullable=True)
    createdAt: Mapped[DateTime] = mapped_column(DateTime(),
                                                nullable=False)

    def to_json(self):
        return {
            'id': self.id,
            'fileName': self.fileName,
            'customPositivePrompt': self.customPositivePrompt,
            'positivePrompt': self.positivePrompt,
            'customNegativePrompt': self.customNegativePrompt,
            'negativePrompt': self.negativePrompt,
            'width': self.width,
            'height': self.height,
            'seed': self.seed,
            'otherSettings': self.otherSettings,
            'welinkUserId': self.welinkUserId,
            'guestUserId': self.guestUserId,
            'userId': self.userId,
            'isPublic': self.isPublic,
            'createdAt': self.createdAt,
        }

    def __repr__(self) -> str:
        return f"Images(id={self.id!r})"


class Prompts(Base):
    __tablename__ = "prompts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(50))
    value: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(50), nullable=True)
    direction: Mapped[str] = mapped_column(String(50))

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'value': self.value,
            'category': self.category,
            'direction': self.direction,
        }

    def __repr__(self) -> str:
        return f"Prompts(id={self.id!r})"


class PromptCategories(Base):
    __tablename__ = "prompt_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(50))
    value: Mapped[str] = mapped_column(String(100))

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'value': self.value,
        }

    def __repr__(self) -> str:
        return f"Prompts(id={self.id!r})"


class Models(Base):
    __tablename__ = "models"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[int] = mapped_column(String(200))
    repoName: Mapped[int] = mapped_column(String(200))
    envPath: Mapped[str] = mapped_column(String(200))
    useCuda: Mapped[bool] = mapped_column(Boolean(True))
    defaultSettings: Mapped[str] = mapped_column(String(2000))

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'repoName': self.repoName,
            'envPath': self.envPath,
            'useCuda': self.useCuda,
            'defaultSettings': self.defaultSettings,
        }

    def __repr__(self) -> str:
        return f"Prompts(id={self.id!r})"


class DictionaryTypes(Base):
    __tablename__ = "dictionaryTypes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(50))
    value: Mapped[str] = mapped_column(String(100))

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'value': self.value,
        }

    def __repr__(self) -> str:
        return f"DictionaryTypes(id={self.id!r})"


class Dictionaries(Base):
    __tablename__ = "dictionaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(50))
    value: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(50))

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'value': self.value,
            'category': self.category,
        }

    def __repr__(self) -> str:
        return f"Dictionaries(id={self.id!r})"


class Users(Base):
    guest_user_id = None
    welink_user_id = None
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    userNameCn = Column(String(100), nullable=True)
    userNameEn = Column(String(100), nullable=True)
    welinkUserId = Column(String(500), nullable=True)
    welinkTenantId = Column(String(500), nullable=True)
    guestUserId = Column(String(500), nullable=True)
    role = Column(String(100), nullable=True)
    settings = Column(String(500), nullable=True)

    def to_json(self):
        return {
            'id': self.id,
            'userNameCn': self.userNameCn,
            'userNameEn': self.userNameEn,
            'welinkUserId': self.welinkUserId,
            'welinkTenantId': self.welinkTenantId,
            'guestUserId': self.guestUserId,
            'role': self.role,
            'settings': self.settings,
        }

    def __repr__(self) -> str:
        return f"Users(id={self.id!r})"


class Queue(Base):
    __tablename__ = "queue"

    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, nullable=False)
    sessionId = Column(String(255), nullable=True)
    userComesFrom = Column(String(100), nullable=False)
    welinkUserId = Column(String(500), nullable=True)
    guestUserId = Column(String(500), nullable=True)
    customPositivePrompt = Column(String(2000), nullable=True)
    positivePrompt = Column(String(2000), nullable=True)
    customNegativePrompt = Column(String(2000), nullable=True)
    negativePrompt = Column(String(2000), nullable=True)
    numInferenceSteps = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    seed = Column(String(100), nullable=True)

    lifeCycle = Column(String(50), nullable=True)

    otherSettings = Column(String(2000), nullable=True)
    createdAt = Column(DateTime, nullable=False)

    def to_json(self):
        return {
            'id': self.id,
            'userId': self.userId,
            'sessionId': self.sessionId,
            'userComesFrom': self.userComesFrom,
            'welinkUserId': self.welinkUserId,
            'guestUserId': self.guestUserId,
            'customPositivePrompt': self.customPositivePrompt,
            'positivePrompt': self.positivePrompt,
            'customNegativePrompt': self.customNegativePrompt,
            'negativePrompt': self.negativePrompt,
            'numInferenceSteps': self.numInferenceSteps,
            'width': self.width,
            'height': self.height,
            'lifeCycle': self.lifeCycle,
            'otherSettings': self.otherSettings,
            'seed': self.seed,
            'createdAt': self.createdAt,
        }

    def __repr__(self) -> str:
        return f"Queue(id={self.id!r})"


engine = create_engine(
    'mysql+pymysql://chat-sd:xxxxxxxxxxxxxx@baobaojs.com/chat-sd?charset=utf8',
    echo=True, pool_size=100)


def initDatabase():
    # 调用create_all来创建表结构，已经存在的表将被忽略
    Base.metadata.create_all(engine)
