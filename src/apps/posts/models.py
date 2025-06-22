from datetime import datetime, timezone
from typing import Annotated

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.apps.users.models import User
from src.databases import Base

int_pk = Annotated[int, mapped_column(Integer, primary_key=True, index=True)]
created_at = Annotated[
    datetime,
    mapped_column(DateTime(timezone=True), default=datetime.now(tz=timezone.utc)),
]
updated_at = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        default=datetime.now(tz=timezone.utc),
        onupdate=datetime.now(tz=timezone.utc),
    ),
]


class PostModel(Base):
    __tablename__ = "posts"

    id: Mapped[int_pk]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    user: Mapped["User"] = relationship(
        backref="posts",
    )
    comments: Mapped[list["CommentModel"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
    )
    likes: Mapped[list["LikeModel"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
    )


class LikeModel(Base):
    __tablename__ = "likes"

    id: Mapped[int_pk]
    created_at: Mapped[created_at]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )

    user: Mapped["User"] = relationship(backref="likes")
    post: Mapped["PostModel"] = relationship(back_populates="likes")

    __table_args__ = (UniqueConstraint("user_id", "post_id", name="uq_user_post_like"),)


class CommentModel(Base):
    __tablename__ = "comments"

    id: Mapped[int_pk]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    content: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )

    user: Mapped["User"] = relationship(backref="comments")
    post: Mapped["PostModel"] = relationship(back_populates="comments")
