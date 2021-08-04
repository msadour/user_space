"""Schemas."""

from pydantic import BaseModel


class UserDataSchema(BaseModel):
    """Class UserDataSchema."""

    email: str
    password: str
    phone_number: str


class UserAuthentication(BaseModel):
    """Class UserAuthentication."""

    email: str
    password: str


class UserOTPSchema(BaseModel):
    """Class UserOTPSchema."""

    otp_secret: str


class UserPhoneValidation(BaseModel):
    """Class UserPhoneValidation."""

    phone: str
    code: str


class UserPhone(BaseModel):
    """Class UserPhone."""

    phone: str


class SupplyPassword(BaseModel):
    """Class SupplyPassword."""

    password: str
    password_again: str
