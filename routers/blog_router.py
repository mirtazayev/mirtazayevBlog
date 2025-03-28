import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Request, HTTPException, status, UploadFile, File
from markdown import markdown
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse, HTMLResponse

from configs import templates
from database.engine import get_db
from models.blog_model import Blog, create_slug
from services.user_service import get_current_user

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
router = APIRouter(
    tags=["Blog"],
    prefix="/blog"
)


@router.get("/")
def read_articles(request: Request, db: Session = Depends(get_db)):
    articles = db.query(Blog).all()
    return templates.TemplateResponse("/blog/blog.html", {"request": request, "articles": articles})


@router.get("/{slug}")
async def get_article(request: Request, slug: str, db: Session = Depends(get_db)):
    article = db.query(Blog).filter(Blog.slug == slug).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found.")

    html_content = markdown(article.content, extensions=["fenced_code", "tables", "codehilite"])

    return templates.TemplateResponse(
        "/blog/article.html",
        {"request": request, "article": article, "content": html_content}
    )


def check_user_permission(user_id: int) -> bool:
    return user_id == 1622920687


@router.get("/create/article", response_class=HTMLResponse)
async def show_create_form(request: Request, current_user: int = Depends(get_current_user)):
    if check_user_permission(current_user):
        success = request.query_params.get("success", None)
        return templates.TemplateResponse("/blog/upload-md.html", {"request": request, "success": success})
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied!")


@router.post("/create/article")
async def create_article(
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    try:
        logger.debug(f"Received file: {file.filename}")

        if not file.filename.endswith('.md'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only Markdown (.md) files are allowed."
            )

        content = await file.read()
        content_str = content.decode('utf-8')

        title = file.filename.rsplit('.', 1)[0].strip()
        logger.debug(f"Extracted title: {title}")

        if not title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename must contain a valid title before the .md extension."
            )

        slug = create_slug(db, title)
        logger.debug(f"Generated slug: {slug}")

        if db.query(Blog).filter(Blog.slug == slug).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An article with this title already exists."
            )

        new_article = Blog(
            title=title,
            content=content_str,
            slug=slug,
            created_at=datetime.utcnow()
        )

        db.add(new_article)
        db.commit()
        db.refresh(new_article)

        logger.debug(f"Article created with ID: {new_article.id}")

        return RedirectResponse(url=f"/blog/{slug}", status_code=status.HTTP_303_SEE_OTHER)

    except UnicodeDecodeError:
        logger.error("File encoding issue.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file encoding. Please upload a UTF-8 encoded file."
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while saving article."
        ) from e
    except HTTPException:
        logger.error("HTTP exception occurred.")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process the article."
        ) from e
