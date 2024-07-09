from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
import models
import utils
import oauth2

router = APIRouter()

@router.post("/login", status_code=status.HTTP_202_ACCEPTED)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials!")
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN , detail="Invalid Credentials!")
    
    access_token = oauth2.create_access_token({"user_id": user.email})
    return {"access_token": access_token, "token_type": "bearer"}