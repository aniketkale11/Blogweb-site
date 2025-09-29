from fastapi import Depends ,Form , Request,APIRouter
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from models import User , Post ,Comment
from database import get_data

router = APIRouter()
templates = Jinja2Templates(directory="templates")
# ADD COMMENT
@router.post("/posts/{post_id}/comments")
async def  create_comment(
    post_id:int,
    request:Request,
    content:str = Form(...),
    db:Session = Depends(get_data)
):
    if "user_id" not in request.session:
        request.session.clear()
        request.session['flash']="plz login for comment"
        return RedirectResponse(url='/login',status_code=303)
    
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        request.session.clear()
        request.session['flash']="Post not Found"
        return RedirectResponse(url="/home",status_code=303)
    

    new_comment = Comment(content = content , post_id = post_id , user_id =request.session.get('user_id'))
    db.add(new_comment)
    db.commit()
    request.session['comment_id']=new_comment.id
    request.session['flash'] = "Comment added"
    return RedirectResponse(url=f"/home#comment--{new_comment.id}",status_code=303)



@router.api_route('/comments/{comment_id}/edit', methods=["GET", "POST"])
async def edit_post(
    comment_id: int,
    request: Request,
    content: str = Form(None),
    db: Session = Depends(get_data)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    # Check comment existence early
    if not comment:
        request.session.clear()
        request.session['flash'] = "Comment not found"
        return RedirectResponse(url="/home", status_code=303)

    # Only logged in users can edit
    user_id = request.session.get('user_id')
    if not user_id:
        request.session.clear()
        request.session['flash'] = "Please login to edit"
        return RedirectResponse(url='/login', status_code=303)

    # Only owner can edit
    if comment.user_id != user_id:
        request.session['flash'] = "Not authorized"
        return RedirectResponse(url=f"/home#comment--{comment.id}", status_code=303)

    # Handle GET (show edit form)
    if request.method == "GET":
        return templates.TemplateResponse(
            "edit_comment.html",
            {"request": request, "comment": comment}
        )

    # Handle POST (update comment)
    if request.method == "POST":
        if content:
            comment.content = content
            db.commit()
            request.session['flash'] = "Comment updated successfully"
        return RedirectResponse(url=f"/home#comment--{comment.id}", status_code=303)

    

    comment.content = content
    db.commit()

    request.session['flash']= "Edit Successfully"
    return RedirectResponse(
        url=f"/#comment--{comment.id}",
        status_code=303
    ) 


@router.post('/comments/{comment_id}/delete')
async def delete_comment(
    comment_id:int ,
    request:Request,
    db:Session = Depends(get_data)
):
    if "user_id" not in request.session:
        request.session.clear()
        request.session['flash']= "Please login to delete Comments..!"
        return RedirectResponse(url='/login',status_code=303)
    
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        request.session.clear()
        request.session['flash']= 'Comment not found'
        return RedirectResponse(url='/home',status_code=303)
    
    if comment.user_id != request.session.get('user_id'):
        request.session['flash'] = "Not authorized"
        return RedirectResponse (url="/home",status_code=303)
    id = request.session.get('post_id') 
    db.delete(comment)
    db.commit()
    request.session['flash']= "comment deleted....!"
    return RedirectResponse(url="/home",status_code=303)

