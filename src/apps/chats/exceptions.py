from dataclasses import dataclass
from uuid import UUID
from src.apps.chats.entities import Chat as ChatEntity, Message as MessageEntity
from src.apps.chats.models import ChatModel, MessageModel


@dataclass
class ChatNotFoundException(Exception):
    chat_id: UUID

    @property
    def message(self):
        return f'Chat with id {self.chat_id} not found'


@dataclass
class MessageNotFoundException(Exception):
    message_id: UUID

    @property
    def message(self):
        return f'Message with id {self.message_id} not found'


@dataclass
class WrongTypeException(Exception):
    expected_type: str
    gotten_type: str

    @property
    def message(self):
        return f'Wrong type. Expected {self.expected_type}, got {self.gotten_type}'


class IsNotChatEntityException(WrongTypeException):
    def __init__(self, gotten_type: str):
        super().__init__(type(ChatEntity).__name__, gotten_type)


class IsNotChatModelException(WrongTypeException):
    def __init__(self, gotten_type: str):
        super().__init__(type(ChatModel).__name__, gotten_type)


class IsNotMessageEntityException(WrongTypeException):
    def __init__(self, gotten_type: str):
        super().__init__(type(MessageEntity).__name__, gotten_type)


class IsNotMessageModelException(WrongTypeException):
    def __init__(self, gotten_type: str):
        super().__init__(type(MessageModel).__name__, gotten_type)
