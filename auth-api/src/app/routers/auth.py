from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import LoginRequest, RegisterRequest, TokenOut, UpdateProfileRequest, UserOut
from app.services.auth_service import (
    create_access_token,
    decode_token,
    get_user_by_id,
    login,
    register,
    update_profile,
)

router = APIRouter(prefix="/auth", tags=["auth"])
bearer = HTTPBearer()


def _current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> int:
    return decode_token(credentials.credentials)


@router.post("/register", response_model=TokenOut, status_code=201)
def register_user(body: RegisterRequest, db: Session = Depends(get_db)):
    user = register(db, body.name, body.email, body.password)
    token = create_access_token(user.id)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenOut)
def login_user(body: LoginRequest, db: Session = Depends(get_db)):
    user = login(db, body.email, body.password)
    token = create_access_token(user.id)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def get_profile(
    user_id: int = Depends(_current_user_id),
    db: Session = Depends(get_db),
):
    return UserOut.model_validate(get_user_by_id(db, user_id))


@router.patch("/me", response_model=UserOut)
def update_my_profile(
    body: UpdateProfileRequest,
    user_id: int = Depends(_current_user_id),
    db: Session = Depends(get_db),
):
    return UserOut.model_validate(update_profile(db, user_id, body.name))
