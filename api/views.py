"""Views."""

from datetime import datetime, timedelta

import jwt
import pyotp

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import and_
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import Response

from api.hasher import Hasher
from api.models import User, SessionLocal, PhoneValidationUser, OTPUser
from api.schemas import (
    UserDataSchema,
    UserPhoneValidation,
    UserPhone,
    SupplyPassword,
    UserAuthentication,
)
from api.settings import Settings
from api.utils import (
    perform_create_user,
    get_user_by_email,
    perform_authentication,
    perform_send_sms_to_user,
    get_payload_from_token,
)

router = APIRouter()
settings = Settings()
SECRET = settings.secret


def get_db() -> None:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/api/auth")
def auth(info_user: UserAuthentication) -> Response:
    """View for authentication of user (email / password).

    Args:
        info_user:

    Returns:
        Response from the view.
    """
    user = perform_authentication(info_user)
    token = jwt.encode(
        {"email": user.email, "password": user.password}, settings.jwt_secret
    )
    return Response(status_code=status.HTTP_200_OK, content=str({"token": token}))


@router.get("/api/verify-otp/{otp_secret}/{to_email}")
def verify_otp(otp_secret, to_email, db: Session = Depends(get_db)) -> Response:
    """View for verify the One Time Password.

    Args:
        otp_secret:
        to_email:
        db:

    Returns:
        Response from the view.
    """
    user = get_user_by_email(to_email)

    totp = pyotp.TOTP(otp_secret)
    token_valid = totp.verify(totp.now())

    otp_user = OTPUser.query.filter(OTPUser.user_id == user.id).first()

    if (
        datetime.now() > otp_user.date_expired
        or not token_valid
        or otp_user.is_already_open is True
    ):
        return Response(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=str({"error": "FMA expired"}),
        )

    user.is_opt_verified = True
    otp_user.is_already_open = True

    db.commit()

    token = jwt.encode(
        {"email": user.email, "password": user.password}, settings.jwt_secret
    )
    return Response(status_code=status.HTTP_200_OK, content=str({"token": token}))


@router.post("/api/refresh-otp")
def refresh_otp(info_user: UserAuthentication, db: Session = Depends(get_db)) -> None:
    """View for refresh the link of OTP.

    Args:
        info_user:
        db:

    Returns:
        Response from the view.
    """
    user = perform_authentication(info_user)
    otp_user = OTPUser.query.filter(OTPUser.user_id == user.id).first()
    otp_user.date_expired = datetime.now() + timedelta(minutes=30)
    otp_user.is_already_open = False
    db.commit()


@router.post("/api/supply-password")
def supply_password(
    data: SupplyPassword, request: Request, db: Session = Depends(get_db)
) -> Response:
    """View for supplied password.

    Args:
        data:
        request:
        db:

    Returns:
        Response from the view.
    """
    token = request.headers.get("token")
    payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    user = User.query.filter(User.email == payload["email"]).first()

    if (
        Hasher.verify_password(data.password, user.password)
        and data.password == data.password_again
    ):
        user.is_password_supplied = True
        db.commit()
        return Response(
            status_code=status.HTTP_200_OK,
            content=str({"success": "password supplied"}),
        )
    else:
        return Response(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=str({"error": "Passwords don't match or are wrong."}),
        )


@router.post("/api/send-sms")
def send_sms(user_phone: UserPhone, db: Session = Depends(get_db)) -> Response:
    """View for sending sms.

    Args:
        user_phone:
        db:

    Returns:
        Response from the view.
    """
    user = User.query.filter(User.phone_number == user_phone.phone).first()
    if user:
        perform_send_sms_to_user(user, user_phone.phone, db)
        return Response(status_code=status.HTTP_200_OK)
    else:
        return Response(
            status_code=status.HTTP_404_NOT_FOUND,
            content=str({"error": "User not found."}),
        )


@router.post("/api/auth-sms")
def auth_sms(info_user: UserPhoneValidation) -> Response:
    """View for authenticate a user through a code receive by sms.

    Args:
        info_user:

    Returns:
        Response from the view.
    """
    user = User.query.filter(User.phone_number == info_user.phone).first()
    code_user_object = PhoneValidationUser.query.filter(
        PhoneValidationUser.user_id == user.id
    ).first()
    if code_user_object and code_user_object.code == info_user.code:
        PhoneValidationUser.query.filter(
            PhoneValidationUser.user_id == user.id
        ).delete()
        token = jwt.encode(
            {"email": user.email, "password": user.password}, settings.jwt_secret
        )
        return Response(status_code=status.HTTP_200_OK, content=str({"token": token}))
    else:
        return Response(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=str({"error": "The code provided is wrong"}),
        )


@router.post("/api/registration")
def registration(info_user: UserDataSchema, db: Session = Depends(get_db)) -> Response:
    """View for create a user.

    Args:
        info_user:
        db:

    Returns:
        Response from the view.
    """
    check_user_exist = get_user_by_email(email=info_user.email)
    if check_user_exist:
        raise HTTPException(status_code=400, detail="Email already registered")
    perform_create_user(db, info_user)
    return Response(status_code=status.HTTP_201_CREATED)


@router.delete("/api/delete_account")
def delete_account(request: Request) -> Response:
    """View for account deletion.

    Args:
        request:

    Returns:
        Response from the view.
    """
    try:
        payload = get_payload_from_token(request)
        User.query.filter(
            and_(User.email == payload["email"], User.password == payload["password"])
        ).delete()
        return Response(status_code=204)
    except Exception:
        return Response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=str({"error": "User cannot be delete."}),
        )


@router.get("/api/access_profile")
def access_profile(request: Request) -> User:
    """View for user information access.

    Returns:
        Response from the view.
    """
    payload = get_payload_from_token(request)
    user = User.query.filter(User.email == payload["email"]).first()

    return user.info_without_password()


@router.get("/api/all_profile")
def all_profile():
    """View for all users access.

    Returns:
        Response from the view.
    """
    return [user.info_without_password() for user in User.query.all()]
