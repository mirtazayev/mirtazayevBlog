import asyncio
import logging
import secrets

from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.security import HTTPBasic
from markdown import markdown
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from bot import dp, bot
from configs import templates
from database.engine import init_db, get_db
from database.migration import run_migrations
from models.blog_model import Blog
from routers import todo_router, user_router, auth_router, blog_router

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
app = FastAPI(
    title="Mirtazayev's Blog Todo API",
    description="API documentation for Mirtazayev's Blog Todos",
    version="1.0.0",
    openapi_url="/api/openapi.json",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
security = HTTPBasic()
app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex(32))


@app.get("/", tags=["index"])
async def root(request: Request, db: Session = Depends(get_db)):
    try:
        articles = db.query(Blog).order_by(Blog.created_at.desc()).limit(3).all()
        html_content = [markdown(article.content, extensions=["fenced_code", "tables", "codehilite"]) for article in
                        articles]

        articles_and_content = zip(articles, html_content)

        return templates.TemplateResponse(
            "main/index.html",
            {
                "request": request,
                "articles_and_content": articles_and_content
            }
        )

    except SQLAlchemyError as e:
        print(f"SQLAlchemy Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching articles."
        ) from e
    except Exception as e:
        print(f"General Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process request."
        ) from e


app.include_router(todo_router.router)
app.include_router(user_router.router)
app.include_router(auth_router.router)
app.include_router(blog_router.router)


async def run_telegram_bot():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


#
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("/main/404.html", {"request": request}, status_code=404)


@app.get("/meta.json")
async def get_metadata():
    return {
        "name": "Mirtazayev's Blog",
        "description": "Technical blog and portfolio",
        "version": "1.0.1",
        "repository": "https://github.com/mirtazayev/mirtazayevBlog",
        "author": "Asadbek Mirtazayev",
        "license": "MIT",
    }


@app.on_event("startup")
async def startup():
    try:
        init_db()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection failed: {str(e)}"
        )

    run_migrations()

    asyncio.create_task(run_telegram_bot())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
