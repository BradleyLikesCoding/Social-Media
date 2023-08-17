from datetime import datetime, timezone
import hashlib
import random
from types import GeneratorType
import sqlalchemy
from sqlalchemy import Column, Float, Integer, String, delete, text
import sqlalchemy.orm

SALT = "giuavoerhmcgiuerhougeaiuvhgeaf"

engine = sqlalchemy.create_engine("sqlite:///tictac.db", echo=False)
Base = sqlalchemy.orm.declarative_base()
Session = sqlalchemy.orm.sessionmaker(engine)
session = None

def init():
    global session
    Base.metadata.create_all(engine)
    session = Session()

def hash_password(password):
    return hashlib.sha256((password+SALT).encode("utf-8")).hexdigest()

def generate_id():
    return int(datetime.now(timezone.utc).timestamp() * 10000) * 1000 + random.randint(0, 9999)


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    display_name = Column(String(32), nullable=False)
    username = Column(String(32), nullable=False, unique=True)
    password = Column(String(32), nullable=False)

    @classmethod
    def new(cls, display_name, username, unhashed_password):
        return cls(generate_id(), display_name, username, hash_password(unhashed_password))

    def __init__(self, id, display_name, username, password):
        self.id = id
        self.display_name = display_name
        self.username = username
        self.password = password


class Post(Base):
    __tablename__ = "posts"

    post_id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, nullable=False)
    title = Column(String(128), nullable=False)
    body = Column(String(512), nullable=False)

    @classmethod
    def new(cls, owner, title, body):
        return cls(generate_id(), owner.id if isinstance(owner, Account) else owner, title, body)

    def __init__(self, post_id, owner_id, title, body):
        self.post_id = post_id
        self.owner_id = owner_id
        self.title = title
        self.body = body

class Comment(Base):
    __tablename__ = "comments"

    commenter_id = Column(Integer, nullable=False)
    comment_id = Column(Integer, primary_key=True)
    post_id = Column(Integer, nullable=False)
    text = Column(String(256))

    @classmethod
    def new(cls, commenter_id, post_id, text):
        return cls(generate_id(), commenter_id, post_id, text)

    def __init__(self, comment_id, commenter_id, post_id, text):
        self.commenter_id = commenter_id
        self.comment_id = comment_id
        self.post_id = post_id
        self.text = text


class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    following_id = Column(Integer, nullable=False)

    @classmethod
    def new(cls, user_id, following_id):
        return cls(generate_id(), user_id, following_id)

    def __init__(self, id, user_id, following_id):
        self.id = id
        self.user_id = user_id
        self.following_id = following_id