from sqlalchemy.orm import Session

from models.todo_model import TodoModel


async def get_todos(current_user, db: Session):
    return db.query(TodoModel).filter(TodoModel.user_id == current_user).order_by(TodoModel.created_at.desc()).all()
