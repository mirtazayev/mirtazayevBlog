import logging
import secrets

import redis.asyncio as redis
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBasic
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from markdown import markdown
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.sessions import SessionMiddleware

from configs import templates
from database.engine import get_db
from database.migration import run_migrations
from models.blog_model import Blog
from routers import todo_router, user_router, auth_router, blog_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Mirtazayev's Blog Todo API",
    description="API documentation for Mirtazayev's Blog Todos",
    version="1.0.0",
    openapi_url="/api/openapi.json",
)

app.mount("/static", StaticFiles(directory="static", html=True), name="static")
security = HTTPBasic()
app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex(32))
app.add_middleware(GZipMiddleware, minimum_size=500)

app.include_router(todo_router.router)
app.include_router(user_router.router)
app.include_router(auth_router.router)
app.include_router(blog_router.router)


@app.on_event("startup")
async def startup():
    try:
        get_db()
        run_migrations()
        redis_client = redis.Redis(host="localhost", port=6379, db=0)
        FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise HTTPException(status_code=500, detail=f"Startup failed: {str(e)}")


@app.get("/", tags=["index"])
@FastAPICache(expire=65)
async def root(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        articles = await db.execute(select(Blog).order_by(Blog.created_at.desc()).limit(3))
        articles = articles.scalars().all()

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
        logger.error(f"SQLAlchemy Error: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred.") from e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1, loop="uvloop", log_level="warning")
