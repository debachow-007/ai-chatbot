from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.admin.dependencies import admin_required
from app.models import DocumentChunk, PortfolioItem
from app.services.embeddings import get_query_embedding
from app.services.s3upload import upload_to_s3, delete_from_s3, extract_key_from_url  # if you want S3 upload

templates = Jinja2Templates(directory="app/admin/templates")

admin_router = APIRouter(prefix="/admin", tags=["admin"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------- DASHBOARD -----------------
@admin_router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, user=Depends(admin_required)):
    return templates.TemplateResponse("dashboard.html", {"request": request})


# ---------------- PORTFOLIO CRUD ----------------
@admin_router.get("/portfolio", response_class=HTMLResponse)
def portfolio_list(request: Request, db: Session = Depends(get_db), user=Depends(admin_required)):
    items = db.query(PortfolioItem).order_by(PortfolioItem.created_at.desc()).all()
    return templates.TemplateResponse("portfolio_list.html", {"request": request, "items": items})


@admin_router.get("/portfolio/create", response_class=HTMLResponse)
def create_page(request: Request, user=Depends(admin_required)):
    return templates.TemplateResponse("portfolio_form.html", {"request": request, "item": None})


@admin_router.post("/portfolio/create")
async def create_item(
    db: Session = Depends(get_db),
    user=Depends(admin_required),
    title: str = Form(...),
    description: str = Form(None),
    category: str = Form(None),
    project_url: str = Form(None),
    image_file: UploadFile = File(None)
):
    image_url = None
    if image_file:
        contents = await image_file.read()
        image_url = upload_to_s3(contents, image_file.filename)

    item = PortfolioItem(
        title=title,
        description=description,
        category=category,
        project_url=project_url,
        image_url=image_url
    )

    db.add(item)
    db.commit()
    return RedirectResponse("/admin/portfolio", status_code=302)


@admin_router.get("/portfolio/delete/{id}")
def delete_item(id: str, db: Session = Depends(get_db), user=Depends(admin_required)):
    item = db.query(PortfolioItem).filter(PortfolioItem.id == id).first()
    if item:
        if item.image_url:
            key = extract_key_from_url(item.image_url)
            delete_from_s3(key)

        db.delete(item)
        db.commit()

    return RedirectResponse("/admin/portfolio", status_code=302)


# ---------------- SITEMAP / DOCUMENT CHUNKS ----------------
@admin_router.get("/sitemap", response_class=HTMLResponse)
def sitemap_list(request: Request, db: Session = Depends(get_db), user=Depends(admin_required)):
    chunks = db.query(DocumentChunk).order_by(DocumentChunk.id.desc()).all()
    return templates.TemplateResponse("sitemap_list.html", {"request": request, "chunks": chunks})


@admin_router.get("/sitemap/embed-missing")
def regenerate_embeddings(db: Session = Depends(get_db), user=Depends(admin_required)):
    chunks = db.query(DocumentChunk).filter(DocumentChunk.embedding == None).all()

    for chunk in chunks:
        try:
            embedding = get_query_embedding(chunk.content)
            chunk.embedding = embedding
            db.add(chunk)
        except Exception as e:
            print("Embedding failed for chunk:", chunk.id, e)

    db.commit()
    return RedirectResponse("/admin/sitemap", status_code=302)
