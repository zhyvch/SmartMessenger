from datetime import datetime

from pydantic import BaseModel


class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class Post(PostBase):
    id: int
    created_at: datetime
    updated_at: datetime
    user_id: int

    class Config:
        from_attributes = True


class Like(BaseModel):
    id: int
    user_id: int
    post_id: int

    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    content: str | None = None


class Comment(CommentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    user_id: int
    post_id: int

    class Config:
        from_attributes = True
