"""Models."""

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    UniqueConstraint,
    Boolean,
    DateTime,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:qwertz@database:5432/user_space"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = scoped_session(SessionLocal)
Base = declarative_base()
Base.query = session.query_property()


class User(Base):
    """Class User."""

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)
    phone_number = Column(String)
    is_opt_verified = Column(Boolean, default=False)
    is_password_supplied = Column(Boolean, default=False)


class TokenValidation(Base):
    """Class TokenValidation."""

    __tablename__ = "token"

    id = Column(Integer, primary_key=True)
    token = Column(String)
    date_expiration = Column(DateTime)
    is_valid = Column(Boolean)


class UserTokenValidation(Base):
    """Class UserTokenValidation."""

    __tablename__ = "user_token"

    __table_args__ = (
        UniqueConstraint("user_id", "token_id", name="_user_id_token_id"),
    )

    user_id = Column(Integer, primary_key=True)
    token_id = Column(Integer, primary_key=True)


class PhoneValidationUser(Base):
    """Class PhoneValidationUser."""

    __tablename__ = "phone_validation_user"

    user_id = Column(Integer, primary_key=True)
    code = Column(String)


class OTPUser(Base):
    """Class OTPUser."""

    __tablename__ = "top_user"

    user_id = Column(Integer, primary_key=True)
    otp_secret = Column(String, unique=True)
    date_expired = Column(DateTime)
    is_already_open = Column(Boolean, default=False)
