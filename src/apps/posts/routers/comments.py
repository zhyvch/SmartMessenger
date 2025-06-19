from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.posts.dependencies import CurrentUserDep
from src.apps.posts.models import CommentModel
from src.apps.posts.schemas import Comment, CommentUpdate
from src.databases import get_async_db

comments_router = APIRouter()


@comments_router.get("/{comment_id}")
async def get_comment_by_id(
    comment_id: int,
    user: CurrentUserDep,
    session: AsyncSession = Depends(get_async_db),
) -> Comment:
    comment = await session.get(CommentModel, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    return Comment.model_validate(comment)


@comments_router.patch("/{comment_id}")
async def update_comment(
    comment_id: int,
    schema: CommentUpdate,
    user: CurrentUserDep,
    session: AsyncSession = Depends(get_async_db),
) -> Comment:
    comment = await session.get(CommentModel, comment_id)
    if not comment or comment.user_id != user.id:
        raise HTTPException(
            status_code=404, detail="Comment not found or access denied"
        )

    if schema.content:
        comment.content = schema.content

    await session.commit()
    await session.refresh(comment)

    return Comment.model_validate(comment)


@comments_router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    user: CurrentUserDep,
    session: AsyncSession = Depends(get_async_db),
):
    comment = await session.get(CommentModel, comment_id)
    if not comment or comment.user_id != user.id:
        raise HTTPException(
            status_code=404, detail="Comment not found or access denied"
        )

    await session.delete(comment)
    await session.commit()
    return {"detail": "Comment deleted successfully"}
