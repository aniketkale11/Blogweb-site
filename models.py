from sqlalchemy import Column , Integer ,String , Boolean , ForeignKey  , DateTime , UniqueConstraint
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class User (Base):
    __tablename__ = "users"

    id = Column(Integer , primary_key=True, index=True)
    username = Column(String , nullable=False)
    password = Column (String , nullable= False)
    gmail = Column(String , nullable=True , unique=True)
    #created_at = Column(DateTime, default=datetime.utcnow)
    #profile_photo = Column(String , nullable=True)
    # Relationship


    posts = relationship("Post", back_populates="auther")
    comments =  relationship("Comment", back_populates="user")
    likes = relationship("Like" , back_populates="user")
    following = relationship("Follow", foreign_keys="Follow.follower_id", back_populates="follower")
    followers = relationship("Follow", foreign_keys="Follow.following_id", back_populates="following")

class Post(Base):
    __tablename__= "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String , nullable=False)
    content = Column(String , nullable=False)
    owner_id = Column(Integer , ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow) 
    image = Column(String, nullable=True)
    #Relationship
    auther = relationship("User", back_populates="posts")
    comments = relationship("Comment" , back_populates="post")
    likes = relationship('Like',back_populates="post")
   # follower = relationship('Follow', back_populates="post")
class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer , primary_key=True, index=True)
    content = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer , ForeignKey("posts.id"))
    created_at = Column(DateTime, default=datetime.utcnow) 
    #Relationship
    post = relationship('Post', back_populates="comments")
    user= relationship ('User' , back_populates="comments") 
    

class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer , primary_key=True , index = True)

    user_id = Column (Integer , ForeignKey("users.id"))
    post_id = Column(Integer , ForeignKey('posts.id'))


    #relationship 
    user = relationship("User",back_populates="likes")
    post = relationship("Post",back_populates="likes")

    __table_args__ = (UniqueConstraint("user_id","post_id",name="unique_user_post"),)




class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer , primary_key=True, index=True)
    follower_id = Column(Integer , ForeignKey("users.id" , ondelete="CASCADE"))
    following_id = Column(Integer , ForeignKey("users.id", ondelete="CASCADE"))
    
    #relationship
    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    following = relationship("User", foreign_keys=[following_id], back_populates="followers")
    #post = relationship('Post',back_populates='follower')

    __table_args__ = (UniqueConstraint("follower_id","following_id" , name="unique_follow"),)