import logging

from fastapi import FastAPI, Request, status, HTTPException, WebSocketException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from pymongo.errors import PyMongoError
from sqlalchemy.exc import SQLAlchemyError

from src.apps.chats.exceptions import ChatNotFoundException, MessageNotFoundException, WrongTypeException, \
    ChatPermissionsNotFoundException

logger = logging.getLogger(__name__)


def exception_registry(app: FastAPI) -> None:
    @app.exception_handler(ChatNotFoundException)
    def handle_chat_not_found_exception(request: Request, exc: ChatNotFoundException):
        logger.error('%s: %s', exc.__class__.__name__, exc.message)

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'message': f'{exc.message}'
            }
        )

    @app.exception_handler(MessageNotFoundException)
    def handle_message_not_found_exception(request: Request, exc: MessageNotFoundException):
        logger.error('%s: %s', exc.__class__.__name__, exc.message)

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'message': f'{exc.message}'
            }
        )

    @app.exception_handler(ChatPermissionsNotFoundException)
    def handle_chat_permissions_not_found_exception(request: Request, exc: ChatPermissionsNotFoundException):
        logger.error('%s: %s', exc.__class__.__name__, exc.message)

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'message': f'{exc.message}'
            }
        )

    @app.exception_handler(WrongTypeException)
    def handle_wrong_type_exception(request: Request, exc: WrongTypeException):
        logger.error('%s: %s', exc.__class__.__name__, exc.message)

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                'message': f'{exc.message}'
            }
        )

    @app.exception_handler(ValidationError)
    def handle_validation_error_exception(request: Request, exc: ValidationError):
        errors = [f"{error['loc'][0]}: {error['msg']}" for error in exc.errors()]
        message = '\n'.join(errors)

        logger.error('%s: %s', exc.__class__.__name__, message)

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                'message': message
            }
        )

    @app.exception_handler(PyMongoError)
    def handle_pymongo_error_exception(request: Request, exc: PyMongoError):
        logger.error('%s: %s', exc.__class__.__name__, str(exc))

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'message': 'PyMongo error'
            }
        )

    @app.exception_handler(SQLAlchemyError)
    def handle_sqlalchemy_error_exception(request: Request, exc: SQLAlchemyError):
        logger.error('%s: %s', exc.__class__.__name__, str(exc))

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'message': 'SQLAlchemy error'
            }
        )

    @app.exception_handler(HTTPException)
    def handle_http_exception(request: Request, exc: HTTPException):
        logger.error('%s: %s', exc.__class__.__name__, exc.detail)

        return JSONResponse(
            status_code=exc.status_code,
            content={
                'message': f'{exc.detail}'
            }
        )

    @app.exception_handler(WebSocketException)
    def handle_websocket_exception(request: Request, exc: WebSocketException):
        logger.error('%s: %s', exc.__class__.__name__, str(exc))

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'message': f'{exc}'
            }
        )

    @app.exception_handler(Exception)
    def handle_general_exception(request: Request, exc: Exception):
        logger.error("Unhandled exception (%s): %s", exc.__class__.__name__, str(exc))

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'message': 'Internal server error'}
        )
