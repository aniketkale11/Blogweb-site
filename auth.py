from fastapi import HTTPException , templating ,Request , Depends  ,Form , APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from database import get_data
from sqlalchemy.orm import  Session
from models import User , Post, Comment
from database import Base


router = APIRouter()

templates = Jinja2Templates(directory='templates')

@router.api_route('/reg' ,methods=["GET","POST"])
async def registration (
    request:Request,
    username:str = Form(None),
    password:str = Form(None),
    gmail:str = Form(None),
    db:Session = Depends(get_data)
):
    
    if request.method =="GET":
        return templates.TemplateResponse(
            "register.html",
            {'request':request}
        )
    
    existing_user = db.query(User).filter(User.gmail == gmail).first()

    if existing_user :
        request.session['flash'] = "User have alrady account....!"
        return RedirectResponse(url='/reg',status_code=303)
    
    
    new_user = User(username = username , password = password , gmail = gmail)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    request.session['user_id'] = new_user.id
    request.session['flash'] = "Registration successfully...!"
    return RedirectResponse(url="/home",status_code=303) 



@router.api_route('/login', methods=["GET","POST"])
async def login(
    request:Request,
    username:str = Form(None),
    password:str = Form(None),
    db:Session =Depends(get_data)

):
    if request.method == "GET":
        return templates.TemplateResponse(
            'login.html',
            {'request':request}
        )
    
    user = db.query(User).filter(User.username == username , User.password == password).first()

    if user :
        request.session['flash'] = "Login Successfully....!"
        request.session['user_id']= user.id
        return RedirectResponse(url="/home", status_code=303)
    

    request.session['flash'] = "Inavlide Password"
    return RedirectResponse(url="/login", status_code=303)



@router.api_route('/logout',methods=["GET","POST"])
async def logout(
    request:Request,
    db:Session = Depends(get_data)
):
    request.session.clear()
    request.session['flash']= "Logout Succsessgully"
    return RedirectResponse(url="/",status_code=303)  # Add welcome Page




@router.api_route('/forget',methods=["GET","POST"])
async def forget(
    request:Request,
    gmail:str = Form(None),
    db:Session =Depends(get_data)
):
    if request.method == "GET":
        return templates.TemplateResponse(
            'forget.html',
            {'request':request}
        )
    
    user = db.query(User).filter(User.gmail == gmail).first()

    if not user:
        request.session['flash'] = "User not registerd"
        return RedirectResponse(url='/login',status_code=303)
    

    request.session['reset_gmail'] = gmail
    return RedirectResponse(url="/reset",status_code=303)



@router.api_route('/reset',methods=["GET","POST"])
async def reset(
    request:Request,
    password:str = Form(None),
    db:Session =Depends(get_data)
):
    if request.method == "GET":
        return templates.TemplateResponse(
            'reset.html',
            {'request':request}
        )
    
    if not password:
        request.session['flash'] = 'Password Requird'
        return RedirectResponse (url="/reset",status_code=303)
    


    gmail = request.session.get('reset_gmail')


    if not gmail:
        request.session['flash'] = "Session expaired"
        return RedirectResponse(url="/forget",status_code=303)
    

    user = db.query(User).filter(User.gmail == gmail).first()


    if user:
        user.password = password
        db.commit()
        request.session['flash'] = "Password reset Successfully"
        return RedirectResponse(url='/login')
    
    request.session["flash"] = "Something Went wrong"
    return RedirectResponse(url='/login',status_code=303)

    

