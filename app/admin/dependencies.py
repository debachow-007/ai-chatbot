from fastapi import Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
import jwt
from app.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

def admin_required(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse("/admin/auth/login", status_code=302)

    try:
        scheme, token = token.split(" ")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return RedirectResponse("/admin/auth/login", status_code=302)
