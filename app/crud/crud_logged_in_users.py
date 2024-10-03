from sqlalchemy import delete, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.base import CRUDBase
from app.models.logged_in_users import LoggedInUsers
from app.schemas import logged_in_users
from jose import jwt
from fastapi import Request
import time


def isTokenExpired(exp):
    current_timestamp = int(time.time())
    return exp < current_timestamp


def insertRefreshToken(refreshToken: str, user_id: int, db: Session):
    db_obj = LoggedInUsers(user_id=user_id, refresh_token=refreshToken)
    db.add(db_obj)
    try:
        db.commit()
    except Exception as e:
        print(e)


class LoggedInUserCRUD(CRUDBase[LoggedInUsers, logged_in_users.LoggedInUserCreate, logged_in_users.LoggedInUserUpdate]):

    def check_login(db: Session, *, user_id: int, refresh_token: str) -> bool:
        check_is_session_created = db.query(LoggedInUsers).filter(LoggedInUsers.user_id == user_id).first()
        if check_is_session_created is not None:
            delete_previous_token = delete(LoggedInUsers).where(LoggedInUsers.user_id == user_id)
            db.execute(delete_previous_token)
            try:
                db.commit()
            except Exception as e:
                print(e)
            insertRefreshToken(refreshToken=refresh_token, user_id=user_id, db=db)
        else:
            insertRefreshToken(refreshToken=refresh_token, user_id=user_id, db=db)

    def checkForActiveSession(db: Session, *, user_id: int, request: Request):
        refresh_token = request.headers.get('Refreshtoken')
        check_token = db.query(LoggedInUsers)\
            .filter(LoggedInUsers.user_id == user_id)\
            .filter(LoggedInUsers.refresh_token == refresh_token).first()

        if check_token is not None:
            return True
        else:
            return False

    def logout(db: Session, *, user_id: int):
        delete_obj = delete(LoggedInUsers).where(LoggedInUsers.user_id == user_id)
        db.execute(delete_obj)
        try:
            db.commit()
        except Exception as e:
            db.rollback()


