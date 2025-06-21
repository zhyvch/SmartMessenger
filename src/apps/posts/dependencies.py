from typing import Annotated

from fastapi import Depends

from src.apps.users.models import User
from src.apps.users.routers.auth import get_current_user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
