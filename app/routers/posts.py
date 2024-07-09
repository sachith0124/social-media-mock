from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
import models
import schemas
from database import get_db
from typing import List
import oauth2

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.get("/", response_model=List[schemas.PostResponseSchema])
async def get_posts(db: Session = Depends(get_db), 
                    current_user: models.User = Depends(oauth2.get_current_user), 
                    limit: int = 10,
                    skip: int = 0,
                    search_key: str = ""):
    posts = db.query(
            models.Post.id,
            models.Post.title,
            models.Post.content,
            models.Post.published,
            models.Post.created_at,
            func.count(models.Vote.post_id).label("votes"),
            models.Post.owner_id,
            models.User.username.label("owner_username"),
            models.User.email.label("owner_email")
        ) \
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True) \
        .join(models.User, models.User.id == models.Post.owner_id) \
        .group_by(
            models.Post.id,
            models.User.id
        ) \
        .filter(
            models.Post.owner_id == current_user.id,
            models.Post.title.contains(search_key)
        ) \
        .limit(limit).offset(skip).all()
    
    return posts

@router.get("/{id}", response_model=schemas.PostResponseSchema)
async def get_post_with_id(id: int, db: Session = Depends(get_db)):
    post = db.query(
            models.Post.id,
            models.Post.title,
            models.Post.content,
            models.Post.published,
            models.Post.created_at,
            func.count(models.Vote.post_id).label("votes"),
            models.Post.owner_id,
            models.User.username.label("owner_username"),
            models.User.email.label("owner_email")
        ) \
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True) \
        .join(models.User, models.User.id == models.Post.owner_id) \
        .group_by(
            models.Post.id,
            models.User.id
        ) \
        .filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id:{id} not found")
    return post

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostDBSchema)
async def create_post(post: schemas.PostSchema, 
                      db: Session = Depends(get_db), 
                      current_user: int = Depends(oauth2.get_current_user)):
    new_post = models.Post(owner_id = current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, 
                      db: Session = Depends(get_db), 
                      current_user: int = Depends(oauth2.get_current_user)):
    post_from_db = db.query(models.Post).filter(models.Post.id == id)
    if post_from_db.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id:{id} does not exist")
    
    if post_from_db.first().owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"not authorized to delete post")
    
    post_from_db.delete(synchronize_session=False)
    db.commit()

@router.put("/{id}", response_model=schemas.PostDBSchema)
async def update_post(id: int, 
                      updated_post: schemas.PostSchema,
                      db: Session = Depends(get_db), 
                      current_user: int = Depends(oauth2.get_current_user)):
    post_from_db = db.query(models.Post).filter(models.Post.id == id)
    if post_from_db.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id:{id} does not exist")
    
    if post_from_db.first().owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"not authorized to delete post")
    post_from_db.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()
    return post_from_db.first()