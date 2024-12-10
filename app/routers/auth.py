from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from datetime import timedelta
from jwt.exceptions import InvalidTokenError

from ..dependencies.auth import (
    Token,
    authenticate_user,
    ACCESS_TOKEN_EXPIRE_HOURS,
    create_access_token,
    create_refresh_token,
    REFRESH_TOKEN_EXPIRE_DAYS,
    verify_token,
    oauth2_scheme,
    blacklist_token,
)
from ..dependencies.db import SessionDep

router = APIRouter(tags=["auth"])


@router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
    response: Response,
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    refresh_token = create_refresh_token(data={"sub": user.email})
    max_age = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=max_age,
    )

    return Token(access_token=access_token, token_type="bearer")


@router.post("/refresh")
async def refresh_access_token(request: Request, session: SessionDep):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=403, detail="Refresh token missing")

    user_data = verify_token(refresh_token, session)
    if not user_data:
        raise HTTPException(status_code=403, detail="Invalid refresh token")

    new_access_token = create_access_token(data={"sub": user_data.email})
    return Token(access_token=new_access_token, token_type="bearer")


@router.post("/logout")
async def logout(
    response: Response,
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
):
    try:
        blacklist_token(token, session)
        response.delete_cookie(key="refresh_token")

        return {"message": "Logged out successfully"}

    except InvalidTokenError:
        raise HTTPException(status_code=403, detail="Invalid token")
