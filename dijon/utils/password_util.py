from passlib.context import CryptContext


crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(input: str):
    return crypt_context.hash(input)


def verify(password: str, password_hash: str) -> bool:
    return bool(crypt_context.verify(password, password_hash))
