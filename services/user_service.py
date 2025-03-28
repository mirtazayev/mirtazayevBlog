import secrets

from fastapi import Depends, Request, status, HTTPException
from sqlalchemy.orm import Session

from database.engine import get_db
from models.user_model import UserModel


def get_current_user(request: Request):
    user_id = request.session.get('user_id')
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/auth"}
        )
    return user_id


def create_user(telegram_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == telegram_id).first()
    if not user:
        user = UserModel(id=telegram_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def generate_session_token():
    return secrets.token_hex(16)
