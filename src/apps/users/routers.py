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
from sqlalchemy import or_
from authlib.integrations.starlette_client import OAuth, OAuthError

from src.apps.users.models import User, RevokedToken

from src.apps.users.dependencies import SessionDep
from src.apps.users.schemas import (
    UserCreate,
    UserOut,
    Token,
    TokenRefresh,
)
from src.apps.users.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    _create_token,
    decode_token,
)
from src.apps.users.utils import send_email
from src.settings.config import settings


auth_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f'{settings.API_V1_PREFIX}/auth/login')


async def get_current_user(
    session: SessionDep,
    token: str = Depends(oauth2_scheme),
) -> User:
    try:
        payload = decode_token(token)
        if payload.get('type') != 'access':
            raise ValueError()
        user_id = int(payload['sub'])
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authentication credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    user = await session.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Inactive user',
        )
    return user


# ─── Google OAuth ───────────────────────────────────────────────────────────────
oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid'},
)


# ─── Registration ──────────────────────────────────────────────────────────────
@auth_router.post(
    '/register',
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserCreate,
    background_tasks: BackgroundTasks,
    session: SessionDep,
):
    if not any([data.email, data.phone_number, data.username]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Provide email, phone number, or username',
        )
    if data.email and await session.query(User).filter_by(email=data.email).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Email already registered')
    if data.phone_number and await session.query(User).filter_by(phone_number=data.phone_number).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Phone number already registered')
    if data.username and await session.query(User).filter_by(username=data.username).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Username already taken')

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
    await session.add(user)
    await session.commit()
    await session.refresh(user)

    if data.email:
        token = _create_token(
            subject=user.id,
            token_type='verify',
            expires_delta=timedelta(hours=24),
        )
        link = f'{settings.APP_URL}/auth/verify-email?token={token}'
        background_tasks.add_task(
            send_email,
            user.email,
            'Verify your email',
            f'Click here to verify your address:\n{link}'
        )

    return user


# ─── Email verification ────────────────────────────────────────────────────────
@auth_router.get('/verify-email')
async def verify_email(
    token: str,
    session: SessionDep,
):
    try:
        payload = decode_token(token)
        if payload.get('type') != 'verify':
            raise ValueError()
        user_id = int(payload['sub'])
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid or expired verification token',
        )
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'User not found')
    if user.email_verified:
        return {'message': 'Email already verified'}
    user.email_verified = True
    await session.commit()
    return {'message': 'Email verified successfully'}


# ─── Login ──────────────────────────────────────────────────────────────────────
@auth_router.post('/login', response_model=Token)
async def login(
    session: SessionDep,
    form: OAuth2PasswordRequestForm = Depends(),
):
    identifier = form.username
    user = await session.query(User).filter(
        or_(
            User.email == identifier,
            User.phone_number == identifier,
            User.username == identifier,
        )
    ).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email not verified',
        )
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    return Token(access_token=access, refresh_token=refresh, token_type='bearer')


# ─── Refresh JWTs ───────────────────────────────────────────────────────────────
@auth_router.post('/refresh', response_model=Token)
async def refresh_token(
    payload: TokenRefresh,
    session: SessionDep,
):
    try:
        data = decode_token(payload.refresh_token)
        if data.get('type') != 'refresh':
            raise ValueError()
        jti = data.get('jti')
        user_id = int(data['sub'])
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid refresh token',
        )
    if await session.query(RevokedToken).filter_by(jti=jti).first():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token has been revoked',
        )
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'User not found')
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    return Token(access_token=access, refresh_token=refresh, token_type='bearer')


# ─── Logout ─────────────────────────────────────────────────────────────────────
@auth_router.post('/logout', status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    payload: TokenRefresh,
    session: SessionDep,
):
    try:
        data = decode_token(payload.refresh_token)
        if data.get('type') != 'refresh':
            raise ValueError()
        jti = data.get('jti')
        user_id = int(data.get('sub'))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid refresh token',
        )

    revoked = RevokedToken(
        jti=jti,
        expires_at=data.get('exp'),
        user_id=user_id,
    )
    await session.add(revoked)
    await session.commit()


# ─── Delete account ────────────────────────────────────────────────────────────
@auth_router.delete('/users/me', status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    session: SessionDep,
    user: User = Depends(get_current_user),
):
    await session.delete(user)
    await session.commit()


# ─── Google OAuth login/callback ────────────────────────────────────────────────
@auth_router.get('/oauth/google/login')
async def oauth_google_login(
    request: Request
):
    redirect_uri = request.url_for('oauth_google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@auth_router.get('/oauth/google/callback', response_model=Token)
async def oauth_google_callback(
    request: Request,
    session: SessionDep,
):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f'OAuth error: {e.error}')

    if 'id_token' in token:
        user_info = await oauth.google.parse_id_token(request, token)
    else:
        resp = await oauth.google.get('userinfo', token=token)
        resp.raise_for_status()
        user_info = resp.json()

    social_id = user_info['sub']
    email = user_info.get('email')
    name = user_info.get('name', '')
    first_name, *rest = name.split(' ')
    last_name = ' '.join(rest) if rest else ''

    user = await session.query(User).filter_by(google_id=social_id).first()
    if not user and email:
        user = await session.query(User).filter_by(email=email).first()
        if user:
            user.google_id = social_id
            await session.commit()
            await session.refresh(user)
    if not user:
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=None,
            username=None,
            hashed_password=None,
            is_active=True,
            email_verified=True,
            google_id=social_id,
        )
        await session.add(user)
        await session.commit()
        await session.refresh(user)

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    return Token(access_token=access, refresh_token=refresh, token_type='bearer')
