import os

from src.utils.types import nn
from src.utils.env import load_dotenvs


load_dotenvs()

ENVIRONMENT = nn(os.getenv("ENVIRONMENT"))
assert ENVIRONMENT


PASSWORD_SHA256_SALT = nn(os.getenv("PASSWORD_SHA256_SALT"))

JWT_PRIVATE_KEY = str.encode(nn(os.getenv("JWT_PRIVATE_KEY")))
JWT_PUBLIC_KEY = str.encode(nn(os.getenv("JWT_PUBLIC_KEY")))
