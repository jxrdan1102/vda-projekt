from http.client import HTTPException

from sqlalchemy.exc import SQLAlchemyError


def handle_exceptions(default_status_code=500, default_detail="Interner Serverfehler"):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                raise  # Weitergeben
            except SQLAlchemyError as e:
                raise HTTPException(
                    status_code=500, detail=f"Datenbankfehler: {str(e)}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=default_status_code, detail=str(e) or default_detail
                )

        return wrapper

    return decorator
