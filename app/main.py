from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from . import models, schemas, auth, database
from .routers import tasks_router
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from dotenv import load_dotenv
from datetime import timedelta
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks_router)

@app.get("/", response_class=HTMLResponse)
def read_home(request: Request, db: Session = Depends(database.get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return templates.TemplateResponse("index.html", {"request": request, "user": None})
    try:
        payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return templates.TemplateResponse("index.html", {"request": request, "user": None})
        user = auth.get_user(db, username=username)
        return templates.TemplateResponse("index.html", {"request": request, "user": user})
    except JWTError:
        return templates.TemplateResponse("index.html", {"request": request, "user": None})

@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
def register_user(request: Request, form_data: schemas.UserCreate = Depends(schemas.UserCreate.as_form), db: Session = Depends(database.get_db)):
    db_user = auth.get_user(db, username=form_data.username)
    if db_user:
        return templates.TemplateResponse("register.html", {"request": request, "message": "Пользователь уже существует"})
    hashed_password = auth.get_password_hash(form_data.password)
    new_user = models.User(username=form_data.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    response = RedirectResponse(url="/login", status_code=303)
    return response

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "message": "Неверные учетные данные"})
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax"
    )
    return response

@app.get("/logout", response_class=HTMLResponse)
def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response