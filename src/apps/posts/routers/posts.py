from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.apps.posts.dependencies import CurrentUserDep
from src.apps.posts.models import CommentModel, LikeModel, PostModel
from src.apps.posts.schemas import (
    Comment,
    CommentCreate,
    Like,
    Post,
    PostCreate,
    PostUpdate,
)
from src.databases import get_async_db

posts_router = APIRouter()


@posts_router.get("/")
async def get_current_user_posts(
    user: CurrentUserDep,
    session: AsyncSession = Depends(get_async_db),
):
    query = await session.execute(select(PostModel).where(PostModel.user_id == user.id))
    posts = query.scalars().all()
    return [Post.model_validate(post) for post in posts]


@posts_router.get("/{post_id}")
async def get_post_by_id(
    post_id: int,
    user: CurrentUserDep,
    session: AsyncSession = Depends(get_async_db),
) -> Post:
    post = await session.get(PostModel, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return Post.model_validate(post)


@posts_router.post("/")
async def create_post(
    user: CurrentUserDep,
    schema: PostCreate,
    session: AsyncSession = Depends(get_async_db),
) -> Post:
    post = PostModel(
        title=schema.title,
        content=schema.content,
        user_id=user.id,
    )
    session.add(post)
    await session.commit()
    await session.refresh(post)

    return Post.model_validate(post)


@posts_router.patch("/{post_id}")
async def update_post(
    post_id: int,
    schema: PostUpdate,
    user: CurrentUserDep,
    session: AsyncSession = Depends(get_async_db),
) -> Post:
    post = await session.get(PostModel, post_id)
    if not post or post.user_id != user.id:
        raise HTTPException(status_code=404, detail="Post not found or access denied")

    if schema.title:
        post.title = schema.title

    if schema.content:
        post.content = schema.content

    await session.commit()
    await session.refresh(post)

    return Post.model_validate(post)


@posts_router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    user: CurrentUserDep,
    session: AsyncSession = Depends(get_async_db),
):
    post = await session.get(PostModel, post_id)
    if not post or post.user_id != user.id:
        raise HTTPException(status_code=404, detail="Post not found or access denied")

    await session.delete(post)
    await session.commit()
    return {"detail": "Post deleted successfully"}


@posts_router.get("/{post_id}/comments")
async def get_post_comments(
    post_id: int,
    user: CurrentUserDep,
    session: AsyncSession = Depends(get_async_db),
) -> list[Comment]:
    query = (
        select(PostModel)
        .options(selectinload(PostModel.comments))
        .where(PostModel.id == post_id)
    )
    post = (await session.execute(query)).scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return [Comment.model_validate(comment) for comment in post.comments]


@posts_router.post("/{post_id}/comments")
async def create_comment(
    post_id: int,
    schema: CommentCreate,
    user: CurrentUserDep,
    session: AsyncSession = Depends(get_async_db),
) -> Comment:
    post = await session.get(PostModel, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment = CommentModel(
        content=schema.content,
        user_id=user.id,
        post_id=post_id,
    )
    session.add(comment)
    await session.commit()
    await session.refresh(comment)

    return Comment.model_validate(comment)


@posts_router.get("/{post_id}/likes")
async def get_post_likes(
    post_id: int,
    user: CurrentUserDep,
    session: AsyncSession = Depends(get_async_db),
) -> list[Like]:
    post = await session.get(PostModel, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    likes = await session.execute(select(LikeModel).where(LikeModel.post_id == post_id))
    return [Like.model_validate(like) for like in likes.scalars().all()]


@posts_router.post("/{post_id}/likes")
async def like_post(
    post_id: int,
    user: CurrentUserDep,
    session: AsyncSession = Depends(get_async_db),
) -> Like:
    query = (
        select(PostModel)
        .options(selectinload(PostModel.likes))
        .where(PostModel.id == post_id)
    )
    post = (await session.execute(query)).scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    for like in post.likes:
        if like.user_id == user.id:
            raise HTTPException(status_code=400, detail="You already liked this post")

    like = LikeModel(user_id=user.id, post_id=post_id)
    session.add(like)
    await session.commit()
    await session.refresh(like)

    return Like.model_validate(like)


@posts_router.delete("/{post_id}/likes")
async def unlike_post(
    post_id: int,
    user: CurrentUserDep,
    session: AsyncSession = Depends(get_async_db),
):
    post = await session.get(PostModel, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    like = await session.execute(
        select(LikeModel).where(
            LikeModel.user_id == user.id, LikeModel.post_id == post_id
        )
    )
    like = like.scalar_one_or_none()

    if not like:
        raise HTTPException(status_code=404, detail="Like not found")

    await session.delete(like)
    await session.commit()

    return {"detail": "Post unliked successfully"}
