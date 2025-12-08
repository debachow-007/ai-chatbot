from fastapi import APIRouter, Request, Depends, Form, Response
from app.services.auth_service import authenticate_admin, create_access_token
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.auth_service import authenticate_admin, create_access_token

templates = Jinja2Templates(directory="app/admin/templates")
auth_router = APIRouter(prefix="/admin/auth", tags=["admin-auth"])

@auth_router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@auth_router.post("/login")
def login(response: Response, username: str = Form(...), password: str = Form(...)):
    if authenticate_admin(username, password):
        token = create_access_token({"sub": username})
        response = RedirectResponse("/admin", status_code=302)
        response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
        return response
    return RedirectResponse("/admin/auth/login?error=1", status_code=302)

@auth_router.get("/logout")
def logout(response: Response):
    response = RedirectResponse("/admin/auth/login", status_code=302)
    response.delete_cookie("access_token")
    return response
