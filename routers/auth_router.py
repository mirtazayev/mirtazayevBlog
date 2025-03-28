from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from configs import templates
from database.engine import get_db
from models.user_model import UserModel
from services.user_service import generate_session_token

router = APIRouter(
    tags=["Authentication"],
    prefix="/auth"
)


@router.get("/")
async def auth(request: Request):
    return templates.TemplateResponse("/auth/auth.html", {"request": request})


@router.post("/verify")
async def authenticate_user(request: Request,
                            telegram_id: int = Form(...),
                            db: Session = Depends(get_db)
                            ):
    stored_user = db.query(UserModel).filter(UserModel.id == telegram_id).first()

    if stored_user:
        session_token = generate_session_token()
        request.session['user_id'] = stored_user.id

        return RedirectResponse(url="/todo", status_code=303)

    return templates.TemplateResponse("/auth/auth_error.html", {"request": request})
