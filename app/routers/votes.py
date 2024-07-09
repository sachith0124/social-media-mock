from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import oauth2
import models

router = APIRouter(prefix="/posts/{post_id}/vote", tags=["Votes"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def upvote(post_id: int, 
                 db: Session = Depends(get_db),
                 current_user: models.User = Depends(oauth2.get_current_user)):
    
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} does not exist")
    
    vote = db.query(models.Vote).filter(models.Vote.post_id == post_id, models.Vote.user_id == current_user.id).first()
    if vote == None:
        new_vote = models.Vote(post_id=post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
    return
    # return {"new_vote_count": new_count}

@router.delete("/", status_code=status.HTTP_205_RESET_CONTENT)
async def remove_vote(post_id: int, 
                        db: Session = Depends(get_db),
                        current_user: models.User = Depends(oauth2.get_current_user)):

    vote_query = db.query(models.Vote).filter(models.Vote.post_id == post_id, models.Vote.user_id == current_user.id)
    if vote_query.first() != None:
        vote_query.delete(synchronize_session=False)
        db.commit()
    return
    # return {"new_vote_count": new_count}