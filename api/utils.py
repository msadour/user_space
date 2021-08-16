"""Utils."""

from datetime import datetime, timedelta
import random
from typing import Any, Dict
import jwt

import pyotp
import sendgrid
from jwt import DecodeError
from sendgrid.helpers.mail import Mail, Email, To, Content
from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session
from starlette.requests import Request
from twilio.rest import Client

from api.hasher import Hasher
from api.models import User, PhoneValidationUser, OTPUser
from api.schemas import UserDataSchema, UserAuthentication
from api.settings import Settings


settings = Settings()


def get_user_by_email(email: str) -> User:
    """Get a user via his email.

    Args:
        email:

    Returns:
        User object.
    """
    return User.query.filter(User.email == email).first()


def send_email(to_email_user: str, otp_secret: str) -> None:
    """Send an email to the user in order to verify it.

    Args:
        to_email_user:
        otp_secret
    """
    sg = sendgrid.SendGridAPIClient(api_key=settings.sendgrid_api_key)
    from_email = Email("sadour.mehdi@gmail.com")
    to_email = To(to_email_user)
    link = "0.0.0.0:8000/api/verify-otp/{0}/{1}".format(otp_secret, to_email_user)

    subject = "Verify your account"

    content = Content("text/plain", "Click on the following link : {0}".format(link))
    mail = Mail(from_email, to_email, subject, content)

    mail_json = mail.get()

    sg.client.mail.send.post(request_body=mail_json)


def get_payload_from_token(request: Request) -> Dict:
    """get information of a user regarding the token sent.

    Args:
        request:

    Returns:
        payload.
    """
    token = request.headers.get("token")
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return payload
    except DecodeError:
        raise Exception("Token not valid")


def perform_authentication(user: UserAuthentication) -> User:
    """Authenticate a user.

    Args:
        user:

    Returns:
        User authenticated.
    """
    user_db = User.query.filter(and_(User.email == user.email)).first()

    if user_db is None:
        raise HTTPException(status_code=404, detail="User not found")

    if not Hasher.verify_password(user.password, user_db.password):
        raise HTTPException(status_code=404, detail="Wrong password")

    if not user_db.is_opt_verified:
        raise HTTPException(status_code=404, detail="Account not verified")

    if not user_db.is_password_supplied:
        raise HTTPException(status_code=404, detail="Password not supplied")

    return user_db


def perform_create_user(db: Session, user: UserDataSchema) -> User:
    """Create a new user.

    Args:
        db:
        user:

    Returns:
        User created.
    """
    hashed_password = Hasher.get_password_hash(user.password)
    user = User(
        email=user.email, password=hashed_password, phone_number=user.phone_number
    )
    db.add(user)
    db.commit()

    otp = OTPUser(
        user_id=user.id,
        otp_secret=pyotp.random_base32(),
        date_expired=datetime.now() + timedelta(minutes=30),
    )
    db.add(otp)
    db.commit()

    send_email(user.email, otp.otp_secret)

    return user


def perform_send_sms_to_user(user: User, to_number: str, db: Session) -> Any:
    """Send sms to user for validation.

    Args:
        user:
        to_number:
        db:

    Returns:
        A sms sent.
    """
    code = "".join([str(random.randint(1, 10)) for _ in range(6)])
    validation = PhoneValidationUser(user_id=user.id, code=code)
    db.add(validation)
    db.commit()
    db.refresh(validation)

    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

    return client.messages.create(
        from_=settings.twilio_phone_number,
        to=to_number,
        body="Your code authentication is " + code,
        messaging_service_sid=settings.messaging_service_sid,
    )
