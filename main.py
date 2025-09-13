from fastapi import FastAPI
import uvicorn
from starlette.middleware.sessions import SessionMiddleware
from blog import router as blog_router
from comment import router as comment_router
from database import Base , engine
from auth import router as auth_router

app = FastAPI()

app.add_middleware(SessionMiddleware,secret_key = "rinki",session_cookie = "session",max_age=None)


app.include_router(blog_router , tags=['Blog'])
app.include_router(comment_router, tags=['comment'])
app.include_router(auth_router , tags=["authentication"]) 
#Base.metadata.drop_all(bind=engine)        
Base.metadata.create_all(bind=engine ) 

if __name__ == '__main__':
    uvicorn.run("main:app",host="localhost",port=8000)   