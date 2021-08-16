"""Hasher class file."""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hasher:
    """Class Hasher."""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify the password supplied by the user.

        Args:
            plain_password:
            hashed_password:

        Returns:
            Password verified or not.
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Get a hashed password.

        Args:
            password:

        Returns:
            Password hashed..
        """
        return pwd_context.hash(password)
