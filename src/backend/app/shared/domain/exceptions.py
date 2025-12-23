"""共通例外クラス"""

from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    """リソースが見つからない"""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found: {identifier}",
        )


class ConflictError(HTTPException):
    """リソースの競合"""

    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=message,
        )


class ValidationError(HTTPException):
    """バリデーションエラー"""

    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


class ExternalServiceError(HTTPException):
    """外部サービスエラー"""

    def __init__(self, service: str, message: str):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"{service}: {message}",
        )
