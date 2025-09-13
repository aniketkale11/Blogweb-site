from fastapi import APIRouter , Depends , Request , Form 
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from database import get_data
from models import Comment , User , Post , Like
from fastapi.responses import RedirectResponse

router = APIRouter ( )



templates = Jinja2Templates(directory="templates")

#Show all Post

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


@router.get('/home')
async def get_post(
    request:Request,
    db:Session = Depends(get_data)
):
    user_id = request.session.get('user_id')
    posts = db.query(Post).all()
    user = db.query(User).filter(User.id == user_id).first()
    return templates.TemplateResponse(
        'post.html',
        {'request':request,
        "posts":posts,"user":user}
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







@router.api_route('/post/create', methods=["GET","POST"])
async def  create_post(
    request:Request,
    title:str = Form(None),
    content:str = Form(None),
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
    

    new_post = Post(title = title , content = content , owner_id = request.session['user_id'])
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


