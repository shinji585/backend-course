from fastapi_users.password import PasswordHelper
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

password_hash = PasswordHash((Argon2Hasher(), BcryptHasher()))


password_helper = PasswordHelper(password_hash=password_hash)
