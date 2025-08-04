from typing import Dict, Optional
from app.user.user_schema import User
from sqlalchemy import Column, String
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from database.mysql_connection import SessionLocal, engine

Base = declarative_base()

class UserModel(Base):
    __tablename__ = "users"
    email = Column(String(255), primary_key=True, index=True)
    username = Column(String(100))
    password = Column(String(255))

class UserRepository:
    """
    사용자 정보를 MySQL 데이터베이스에서 CRUD하는 레포지토리 클래스
    """ 

    def __init__(self, db: Session) -> None:
        """
        데이터베이스 세션을 받아 UserRepository 인스턴스를 초기화하는 메서드

        Parameters:
        - db (Session): SQLAlchemy 데이터베이스 세션
        """
        self.db = db

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        이메일을 기준으로 사용자를 조회하는 메서드

        Parameters:
        - email (str): 조회할 사용자의 이메일

        Returns:
        - Optional[User]: 조회된 사용자 정보 (없으면 None)
        """
        user_model = self.db.query(UserModel).filter(UserModel.email == email).first()
        return User(**user_model.__dict__) if user_model else None

    def save_user(self, user: User) -> User: 
        """
        사용자 정보를 저장하거나, 이미 존재할 경우 업데이트하는 메서드

        Parameters:
        - user (User): 저장 또는 업데이트할 사용자 객체

        Returns:
        - User: 저장된 사용자 객체
        """
        existing = self.db.query(UserModel).filter(UserModel.email == user.email).first()
        if existing:
            existing.username = user.username
            existing.password = user.password
        else:
            new_user = UserModel(**user.dict())
            self.db.add(new_user)
        self.db.commit()
        return user

    def delete_user(self, user: User) -> User:
        """
        사용자 정보를 데이터베이스에서 삭제하는 메서드

        Parameters:
        - user (User): 삭제할 사용자 객체

        Returns:
        - User: 삭제한 사용자 객체 (존재하지 않아도 반환됨)
        """
        user_model = self.db.query(UserModel).filter(UserModel.email == user.email).first()
        if user_model:
            self.db.delete(user_model)
            self.db.commit()
        return user