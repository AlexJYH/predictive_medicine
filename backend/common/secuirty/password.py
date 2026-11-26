from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError

_password_hasher = PasswordHasher()


def hash_password(password):
    return _password_hasher.hash(password)


def verify_password(plain_password, hashed_password):
    try:
        return _password_hasher.verify(hashed_password, plain_password, )
    except (VerificationError, InvalidHashError):
        return False
