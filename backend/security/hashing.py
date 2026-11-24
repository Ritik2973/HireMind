from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

# Initialize the password hasher using the modern Argon2 algorithm
password_hash = PasswordHash((Argon2Hasher(),))

def get_password_hash(password: str) -> str:
    """Hashes a plaintext password securely."""
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against the hash."""
    return password_hash.verify(plain_password, hashed_password)
