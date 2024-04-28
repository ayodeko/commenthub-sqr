from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from api import database, crud
from api.settings import SETTINGS

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SETTINGS.SECRET_KEY, algorithms=[SETTINGS.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            print(1)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        print(2)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = crud.user.get_by_email(db, email=email)
    if user is None or user.is_verified is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
