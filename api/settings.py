"""Settings."""

from decouple import config


class Settings:
    """Class Settings."""

    twilio_account_sid = config("TWILIO_ACCOUNT_SID")
    twilio_auth_token = config("TWILIO_AUTH_TOKEN")
    twilio_phone_number = config("TWILIO_PHONE_NUMBER")
    messaging_service_sid = config("MESSAGING_SERVICE_SID")
    sendgrid_api_key = config("SENDGRID_API_KEY")
    jwt_secret = config("JWT_SECRET")
    secret = config("SECRET")
