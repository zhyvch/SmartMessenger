from datetime import timedelta
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    BackgroundTasks,
    Request,
)
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy import select, or_
from authlib.integrations.starlette_client import OAuth, OAuthError
from sqlalchemy.ext.asyncio import AsyncSession

from src.databases import get_async_db
from src.apps.users.models import User, RevokedToken
from src.apps.users.schemas import UserCreate, UserOut, Token, TokenRefresh, PasswordResetConfirm, EmailSchema
from src.apps.users.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    _create_token,
    decode_token,
    get_or_create_user,
)
from src.apps.users.utils import send_email, send_generic_email
from src.settings.config import settings

auth_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_db),
) -> User:
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise ValueError()
        user_id = int(payload["sub"] )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await session.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )
    return user


@auth_router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_db),
):
    if not any([data.email, data.phone_number, data.username]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide email, phone number, or username")

    # Check uniqueness
    if data.email:
        q = select(User).where(User.email == data.email)
        if (await session.execute(q)).scalars().first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    if data.phone_number:
        q = select(User).where(User.phone_number == data.phone_number)
        if (await session.execute(q)).scalars().first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number already registered")
    if data.username:
        q = select(User).where(User.username == data.username)
        if (await session.execute(q)).scalars().first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

    user = User(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        phone_number=data.phone_number,
        username=data.username,
        hashed_password=hash_password(data.password),
        is_active=True,
        email_verified=False,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    if data.email:
        token = _create_token(subject=user.id, token_type="verify", expires_delta=timedelta(hours=24))
        background_tasks.add_task(send_email, user.email, token)
    return user

@auth_router.get("/verify-email")
async def verify_email(
    token: str,
    session: AsyncSession = Depends(get_async_db),
):
    try:
        payload = decode_token(token)
        if payload.get("type") != "verify":
            raise ValueError()
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification token")

    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.email_verified:
        return {"message": "Email already verified"}

    user.email_verified = True
    await session.commit()
    return {"message": "Email verified successfully"}

@auth_router.post("/login", response_model=Token)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_db),
):
    identifier = form.username
    q = select(User).where(
        or_(User.email == identifier, User.phone_number == identifier, User.username == identifier)
    )
    user = (await session.execute(q)).scalars().first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})
    if not user.email_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not verified")

    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
    }

@auth_router.post("/refresh", response_model=Token)
async def refresh_token(
    payload: TokenRefresh,
    session: AsyncSession = Depends(get_async_db),
):
    try:
        data = decode_token(payload.refresh_token)
        if data.get("type") != "refresh":
            raise ValueError("Not a refresh token")
        jti = data["jti"]
        user_id = int(data["sub"])
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    result = await session.execute(
        select(RevokedToken).where(RevokedToken.jti == jti)
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    new_access = create_access_token(subject=user.id)
    new_refresh = create_refresh_token(subject=user.id)

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }

@auth_router.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
):
    await session.delete(current_user)
    await session.commit()


# 2) Відновлення пароля
@auth_router.post("/password-reset", status_code=status.HTTP_202_ACCEPTED)
async def password_reset_request(
    data: EmailSchema,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_db),
):
    q = select(User).where(User.email == data.email)
    user = (await session.execute(q)).scalars().first()
    if not user:
        return {"message": "If that email is registered, you will receive reset instructions."}

    from src.apps.users.security import _create_token
    token = _create_token(
        subject=user.id,
        token_type="reset",
        expires_delta=timedelta(hours=1),
    )
    link = f"{token}"
    background_tasks.add_task(
        send_generic_email,
        user.email,
        "Password Reset",
        f"Your token for password reset:\n\n{link}"
    )
    return {"message": "If that email is registered, you will receive reset instructions."}


@auth_router.post("/password-reset/confirm", status_code=status.HTTP_200_OK)
async def password_reset_confirm(
    data: PasswordResetConfirm,
    session: AsyncSession = Depends(get_async_db),
):
    try:
        payload = decode_token(data.token)
        if payload.get("type") != "reset":
            raise ValueError()
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.hashed_password = hash_password(data.new_password)
    await session.commit()
    return {"message": "Password has been reset successfully."}


oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

@auth_router.get("/oauth/google/login")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@auth_router.get("/oauth/google/callback", response_model=Token, name="google_callback")
async def google_callback(request: Request, session: AsyncSession = Depends(get_async_db)):
    # отримуємо токени від Google
    token = await oauth.google.authorize_access_token(request)

    userinfo_url = oauth.google.server_metadata.get("userinfo_endpoint")
    if not userinfo_url:
        raise HTTPException(500, "Google OIDC metadata missing userinfo_endpoint")

    resp = await oauth.google.get(userinfo_url, token=token)
    resp.raise_for_status()
    userinfo = resp.json()

    # дістати необхідні дані
    social_id = userinfo["sub"]
    email = userinfo.get("email")
    name = userinfo.get("name", "")

    user = await get_or_create_user(session, google_id=social_id, email=email, name=name)

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}