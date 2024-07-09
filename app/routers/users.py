from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db
from typing import List
import utils

router = APIRouter(tags=["Users"])

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.UserDBSchema)
async def register_user(user: schemas.UserSchema, db: Session = Depends(get_db)):
    new_user = models.User(**user.model_dump())
    
    hashed_password = utils.hash(new_user.password)
    new_user.password = hashed_password

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/users", response_model=List[schemas.UserDBSchema])
async def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

@router.get("/users/{id}", response_model=schemas.UserDBSchema)
async def get_user(db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id:{id} does not exist!")
    return user