from fastapi import APIRouter , Depends , Request , Form 
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from database import get_data
from sqlalchemy import func
from models import Comment , User , Post , Like , Follow
from fastapi import File , UploadFile 
import shutil
from sqlalchemy import or_
from sqlalchemy.orm import joinedload 
import os
from datetime import datetime
from fastapi.responses import RedirectResponse

router = APIRouter ( )



templates = Jinja2Templates(directory="templates")
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER , exist_ok=True)
#Show all Post



def highlight_text (text:str , query:str):
    if not query :
        return text
    
    import re 
    pattern  = re.compile(re.escape(query),re.IGNORECASE)

    return pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>",text)






@router.get('/')
async def home (
    request:Request,
    db:Session =Depends(get_data)
): 
    user_id = request.session.get("user_id")

    if user_id:  
        # if logged in, go to posts page
        return RedirectResponse(url="/", status_code=303)  
    else:
        # if not logged in, show welcome page
        request.session.clear()
        return templates.TemplateResponse("new.html", {"request": request})

"""
@router.get('/home')
async def get_post(
    
    request:Request,
    db:Session = Depends(get_data)
):
    user_id = request.session.get('user_id')
    posts = db.query(Post).all()
   # images = db.query(Post).all()
    user = db.query(User).filter(User.id == user_id).first()

    return templates.TemplateResponse(
        'post.html',
        {'request':request,
        "posts":posts,"user":user}
    )
"""


@router.get('/home')
async def get_post(
    request: Request,
    db: Session = Depends(get_data)
):
    user_id = request.session.get('user_id')
    user = db.query(User).filter(User.id == user_id).first()
    search_query = request.query_params.get('q') # get search query
    posts_query = db.query(Post)
   

    if search_query:
        posts_query  = posts_query.filter(
            or_(
                Post.title.ilike(f"%{search_query}%"),
                Post.content.ilike(f"%{search_query}%"),
                #User.username.ilike(f"%{search_query}%")
            )
        )


    posts = posts_query.all()


    #followers_count = db.query(Follow).filter_by(following_id=post.owner_id).count()


    # प्रत्येक post साठी current user follow करतो का ते तपासा
    posts_with_status = []
    for post in posts:
        is_following = db.query(Follow).filter_by(
            follower_id=user_id,
            following_id=post.owner_id
        ).first() is not None

        followers_count = db.query(Follow).filter_by(following_id=post.owner_id).count()
        
        highlight_title = post.title
        highlight_content = post.content


        if search_query:
            highlight_title = highlight_text(post.title, search_query)
            highlight_content = highlight_text(post.content , search_query)
 
        




        posts_with_status.append({
            "post": post,
            "is_following": is_following,
            "followers_count":followers_count,
            "highlight_title":highlight_title,
            "highlight_content":highlight_content
            
        })
    user_followers_count = 0
    if user:
        user_followers_count = db.query(Follow).filter_by(following_id=user.id).count()
    

    
    if user:
        followers = (
            db.query(User.username)
            .join(Follow, Follow.follower_id == User.id)
            .filter(Follow.following_id == user.id)
            .all()
        )
        followers_list = [f[0] for f in followers]
    else:
     followers_list = [ ]

    
    return templates.TemplateResponse(
        "post.html",
        {"request": request, "posts": posts_with_status, "user": user,"followers_count":user_followers_count,
         "follow":followers_list}
    )


#show single or particultar post 

@router.get('/mypost')
async def my_post(
    request:Request,
    db:Session = Depends(get_data)
):
    if  not request.session.get('user_id'):
        request.session.clear()
        request.session['flash'] = "please login"
        return RedirectResponse(url='/home',status_code=303)

    posts = db.query(Post).filter(Post.owner_id == request.session['user_id']).all()
    
    user_id =request.session.get('user_id')
    user = db.query(User).filter(User.id == user_id).first()
    request.session['flash']= "Post  not found"
    return templates.TemplateResponse(
        'my_post.html',
        {'request':request , "posts":posts,'user':user}
    )

@router.post('/posts/{post_id}/like')
async def like_post(
    post_id:int,
    request:Request,
    db:Session = Depends(get_data)
):
    user_id = request.session.get('user_id')

    if not user_id:
        request.session.clear()
        request.session['flash'] = "Login First"
        return RedirectResponse(url="/login",status_code=303)
    
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post :
        request.session['flash'] = "Post not found"
        return RedirectResponse(url="/home",status_code=303)
    
    existing_like = db.query(Like).filter(
        Like.user_id == user_id , Like.post_id == post_id
    ).first()

    if existing_like :
        db.delete(existing_like)
        db.commit()
       # request.session['flash'] = "Unlike the post"
       # return RedirectResponse (url='/',status_code=303)
    else:
        new_like = Like(user_id = user_id , post_id = post_id)
        db.add(new_like)
        db.commit()
       # request.session['flash'] = "Liked"
    return RedirectResponse(url=f"/home#post-{post.id}",status_code=303)


@router.post('/follow/{user_id}')
async def follow_user(
    user_id:int,
    request:Request,
    db:Session = Depends(get_data)
):
    follower_id = request.session.get("user_id")

    if not follower_id:
        request.session.clear()
        return RedirectResponse(url="/login",status_code=303)
    
    if follower_id == user_id:
       return RedirectResponse(url="/home", status_code=303)
    

    existing = db.query(Follow).filter_by(follower_id=follower_id, following_id=user_id).first()
    if existing:
        db.delete(existing)
        db.commit()


    else :
        follow = Follow(follower_id=follower_id, following_id=user_id)
        db.add(follow)
        db.commit()
    

    return RedirectResponse(url=request.headers.get("referer"), status_code=303)  
    




@router.api_route('/post/create', methods=["GET","POST"])
async def  create_post(
    request:Request,
    title:str = Form(None),
    content:str = Form(None),
    image: UploadFile = File(None),
    db:Session =Depends(get_data)
):
    if 'user_id' not in request.session:
        request.session.clear()
        return RedirectResponse(url='/login',status_code=303)
    user_id = request.session.get('user_id')
    user = db.query(User).filter(User.id == user_id ).first()
    
    if request.method == "GET":
        return templates.TemplateResponse(
            'create_post.html',
            {'request':request,
             'user':user}
        )
    #if 'user_id' not in request.session:
     #   return RedirectResponse(url='/login',status_code=303)
    
    filename = None
    if image:
       # allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mov", ".avi"]
       # ext = os.path.splitext(image.filename)[1].lower()
        filename = f"{int(datetime.utcnow().timestamp())}_{image.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    new_post = Post(title = title , content = content , owner_id = request.session['user_id'],image = filename )
    db.add(new_post)
    db.commit()
    request.session['post_id'] = new_post.id
    request.session['flash']= "Post Create Successfull"
    return RedirectResponse(url='/home',status_code=303)


#EDIT POST


@router.api_route('/posts/{post_id}/edit', methods=["GET","POST"])
async def edit_post(
    post_id:int,
    request:Request,
    title:str = Form(None),
    content:str = Form(None),
    db:Session = Depends(get_data)
):
    
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        request.session.clear()
        return RedirectResponse(url='/home',status_code=303)
    
    if request.method == "GET":
        return templates.TemplateResponse(
            'edit.html',
            {'request':request,'post':post}
        )
    
    if post.owner_id != request.session.get('user_id'):
        request.session['flash']= "Not Authorized"
        return RedirectResponse(url='/home', status_code=303)
    
    post.title = title
    post.content = content
    db.commit()

    request.session['flash']= "update successfully...!"
    return RedirectResponse(url=f"/posts/{post_id}/edit", status_code=303)


@router.post('/posts/{post_id}/delet')
async def delete_post(
    post_id:int,
    request:Request,
    db:Session = Depends(get_data)
):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        request.session.clear()
        request.session['flash']="Post Not Found"
        return RedirectResponse(url='/home',status_code=303)
    
    if post.owner_id != request.session.get('user_id'):
        request.session['flash']="Not authorized...!"
        return RedirectResponse(url="/home",status_code=303)
    db.delete(post)
    db.commit()

    request.session['flash'] = "Post Deleted....!"
    return RedirectResponse(url=request.headers.get("referer"),status_code=303)


