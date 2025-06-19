from typing import Annotated

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.databases import Base

int_pk = Annotated[int, mapped_column(Integer, primary_key=True, index=True)]


class User(Base):
    __tablename__ = "users"

    id: Mapped[int_pk]
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(
        String(255), unique=True, index=True, nullable=True
    )
    phone_number: Mapped[str | None] = mapped_column(
        String(20), unique=True, index=True, nullable=True
    )
    username: Mapped[str | None] = mapped_column(
        String(255), unique=True, index=True, nullable=True
    )
    hashed_password: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # OAuth identifiers
    google_id: Mapped[str | None] = mapped_column(
        String, unique=True, index=True, nullable=True
    )

    # Relationship to revoked tokens (logout)
    revoked_tokens = relationship(
        "RevokedToken",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # friends relationship
    sent_friend_requests = relationship(
        "FriendRequest",
        foreign_keys="FriendRequest.from_user_id",
        back_populates="from_user",
        cascade="all, delete-orphan",
    )
    received_friend_requests = relationship(
        "FriendRequest",
        foreign_keys="FriendRequest.to_user_id",
        back_populates="to_user",
        cascade="all, delete-orphan",
    )


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id: Mapped[int_pk]
    jti: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    expires_at: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    user = relationship("User", back_populates="revoked_tokens")
