# app/config.py
import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()  # Lädt .env-Datei

PRIVATE_KEY_FILE = os.getenv("PRIVATE_KEY_FILE", "private_key.pem")
PUBLIC_KEY_FILE = os.getenv("PUBLIC_KEY_FILE", "public_key.pem")
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-key")
ALGORITHM = os.getenv("ALGORITHM", "EdDSA")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 5))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", 5))
LOCKOUT_TIME = timedelta(minutes=int(os.getenv("LOCKOUT_TIME_MINUTES", 15)))