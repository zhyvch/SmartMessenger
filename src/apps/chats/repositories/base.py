from abc import ABC, abstractmethod
from uuid import UUID

from src.apps.chats.entities import Chat, ChatPermissions, Message
from src.apps.chats.schemas import Order, UpdateChatPermissionsSchema


class BaseChatRepository(ABC):
    @abstractmethod
    async def add_chat(self, chat: Chat) -> None: ...

    @abstractmethod
    async def get_chat(self, chat_id: UUID) -> Chat: ...

    @abstractmethod
    async def get_user_chats(self, user_id: int) -> list[Chat]: ...

    @abstractmethod
    async def delete_chat(self, chat_id: UUID) -> None: ...

    @abstractmethod
    async def get_private_chat_by_member_ids(
        self, member_1_id: int, member_2_id: int
    ) -> Chat | None: ...


class BaseMessageRepository(ABC):
    @abstractmethod
    async def add_message(self, message: Message) -> None: ...

    @abstractmethod
    async def get_message(self, message_id: UUID) -> Message: ...

    @abstractmethod
    async def get_chat_messages(
        self, chat_id: UUID, offset: int, limit: int, ordering: Order
    ) -> list[Message]: ...

    @abstractmethod
    async def mark_message_as_read(self, message_id: UUID, user_id: int) -> None: ...

    @abstractmethod
    async def delete_message(self, message_id: UUID) -> None: ...

    @abstractmethod
    async def delete_chat_messages(self, chat_id: UUID) -> None: ...


class BaseChatPermissionsRepository(ABC):
    @abstractmethod
    async def get_user_chat_permissions(
        self, chat_id: UUID, user_id: int
    ) -> ChatPermissions: ...

    @abstractmethod
    async def add_user_chat_permissions(
        self, chat_permissions: ChatPermissions
    ) -> None: ...

    @abstractmethod
    async def delete_all_user_chat_permissions(self, chat_id: UUID) -> None: ...

    @abstractmethod
    async def delete_user_chat_permissions(
        self, chat_id: UUID, user_id: int
    ) -> None: ...

    @abstractmethod
    async def update_user_chat_permissions(
        self,
        chat_id: UUID,
        user_id: int,
        new_chat_permissions: UpdateChatPermissionsSchema,
    ) -> None: ...
