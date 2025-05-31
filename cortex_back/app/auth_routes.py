from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app import auth_models, auth_schemas, security
from app.auth_database import get_auth_db

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/register", response_model=auth_schemas.UserOut)
def register(user_in: auth_schemas.UserCreate, db: Session = Depends(get_auth_db)):
    existing = db.query(auth_models.User).filter(auth_models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    new_user = auth_models.User(
        email=user_in.email,
        hashed_password=security.hash_password(user_in.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=auth_schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_auth_db)):
    user = db.query(auth_models.User).filter(auth_models.User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"}
        )
    token = security.create_access_token({"user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}

# Dependencia para rutas protegidas
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_auth_db)):
    creds_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise creds_exc
    except JWTError:
        raise creds_exc
    user = db.query(auth_models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user