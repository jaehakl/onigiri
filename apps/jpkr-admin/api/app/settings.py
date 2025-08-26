import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    db_url: str = os.getenv("ONIGIRI_DB_URL", "") if os.getenv("ONIGIRI_DB_URL", "") else "sqlite:///./../../db.sqlite3"
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    google_redirect_uri: str = os.getenv("GOOGLE_REDIRECT_URI", "")

    app_base_url: str = os.getenv("APP_BASE_URL", "http://localhost:5173")

    session_cookie_name: str = os.getenv("SESSION_COOKIE_NAME", "sid")
    session_cookie_secure: bool = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    session_max_age: int = int(os.getenv("SESSION_MAX_AGE_SECONDS", "1209600"))  # 14d

settings = Settings()