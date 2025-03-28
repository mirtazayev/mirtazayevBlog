from datetime import datetime

from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session

from configs import templates
from database.engine import get_db
from models.todo_model import TodoModel
from services.todo_service import get_todos
from services.user_service import get_current_user

router = APIRouter(
    tags=["Todos"],
    prefix="/todo"
)


@router.get("/create")
async def create(request: Request, current_user: int = Depends(get_current_user)):
    if isinstance(current_user, RedirectResponse):
        return current_user

    return templates.TemplateResponse("/todo/create.html", {"request": request})


@router.post("/create")
async def create_todo(
        title: str = Form(...),
        description: str = Form(""),
        status: str = Form("Not Started"),
        due_date: str = Form(None),
        current_user: int = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    due_date_obj = datetime.strptime(due_date, "%Y-%m-%d") if due_date else None

    new_todo = TodoModel(
        title=title,
        description=description,
        status=status,
        due_date=due_date_obj,
        user_id=current_user
    )
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

    return RedirectResponse(url="/todo", status_code=303)


@router.get("/", )
async def todos_main(request: Request, current_user: int = Depends(get_current_user), db: Session = Depends(get_db)):
    todos = await get_todos(current_user, db)
    return templates.TemplateResponse("/todo/todo.html", {"request": request, "todos": todos})


@router.get("/update/{todo_id}")
async def update_todo_page(request: Request, todo_id: int, db: Session = Depends(get_db),
                           current_user: int = Depends(get_current_user)):
    if isinstance(current_user, RedirectResponse):
        return current_user

    todo = db.query(TodoModel).filter(TodoModel.id == todo_id, TodoModel.user_id == current_user).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found or unauthorized")

    return templates.TemplateResponse("/todo/update.html", {"request": request, "todo": todo})


@router.post("/update/{todo_id}")
async def update_todo(
        todo_id: int,
        title: str = Form(...),
        description: str = Form(...),
        status: str = Form(...),
        due_date: str = Form(None),
        db: Session = Depends(get_db),
        current_user: int = Depends(get_current_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    todo = db.query(TodoModel).filter(TodoModel.id == todo_id, TodoModel.user_id == current_user).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found or unauthorized")

    todo.title = title
    todo.description = description
    todo.status = status
    todo.due_date = datetime.strptime(due_date, "%Y-%m-%d") if due_date else None
    db.commit()

    return RedirectResponse(url="/todo", status_code=303)


@router.delete("/delete/{todo_id}")
async def delete_todo(
        todo_id: int,
        current_user: int = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    todo_to_delete = db.query(TodoModel).filter(TodoModel.id == todo_id, TodoModel.user_id == current_user).first()

    if not todo_to_delete:
        raise HTTPException(status_code=404, detail="Todo not found or not authorized to delete")

    db.delete(todo_to_delete)
    db.commit()

    return JSONResponse(content={"detail": "Todo deleted successfully"}, status_code=200)
