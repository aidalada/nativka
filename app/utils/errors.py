from fastapi import HTTPException, status


def http_error(status_code: int, code: str, message: str, details: dict | None = None) -> HTTPException:
    payload: dict = {"code": code, "message": message}
    if details is not None:
        payload["details"] = details
    return HTTPException(status_code=status_code, detail=payload)


def not_found(entity: str = "resource") -> HTTPException:
    return http_error(status.HTTP_404_NOT_FOUND, f"{entity}_not_found", f"{entity.capitalize()} not found")


def bad_request(code: str, message: str, details: dict | None = None) -> HTTPException:
    return http_error(status.HTTP_400_BAD_REQUEST, code, message, details)


def conflict(code: str, message: str) -> HTTPException:
    return http_error(status.HTTP_409_CONFLICT, code, message)



