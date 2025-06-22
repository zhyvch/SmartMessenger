from fastapi import HTTPException, status


class AIServiceException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


class OpenAIServiceException(AIServiceException):
    def __init__(self, detail: str = 'OpenAI service is currently unavailable'):
        super().__init__(detail=detail)


class UnsplashServiceException(AIServiceException):
    def __init__(self, detail: str = 'Unsplash service is currently unavailable'):
        super().__init__(detail=detail)
