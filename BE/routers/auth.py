from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models import Notification, User
from schemas.auth import LoginRequest, LoginResponse, UserResponse
from security import verify_password
from session import SESSION_COOKIE, SESSION_MAX_AGE_SECONDS, create_session_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> LoginResponse:
    user = db.scalar(select(User).where(User.username == payload.username, User.is_active.is_(True)))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    token = create_session_token(user.id)
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=SESSION_MAX_AGE_SECONDS,
    )

    unread_notifications = db.scalars(
        select(Notification)
        .where(Notification.user_id == user.id, Notification.read_at.is_(None))
        .order_by(Notification.created_at)
    ).all()

    return LoginResponse(
        user=UserResponse.model_validate(user),
        notifications=[notification.message for notification in unread_notifications],
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.post("/logout")
def logout(response: Response, current_user: User = Depends(get_current_user)) -> dict[str, str]:
    response.delete_cookie(key=SESSION_COOKIE)
    return {"message": "Logged out"}


@router.post("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    notification = db.scalar(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    notification.read_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Notification marked as read"}
