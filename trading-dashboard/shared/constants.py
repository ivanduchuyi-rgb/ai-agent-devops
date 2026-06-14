import os
from typing import Optional

# Supabase Configuration
SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

# Cloudflare R2 Configuration
R2_ACCOUNT_ID: str = os.getenv("R2_ACCOUNT_ID", "")
R2_ACCESS_KEY_ID: str = os.getenv("R2_ACCESS_KEY_ID", "")
R2_SECRET_ACCESS_KEY: str = os.getenv("R2_SECRET_ACCESS_KEY", "")
R2_BUCKET: str = os.getenv("R2_BUCKET", "trading-screenshots")
R2_PUBLIC_URL: str = os.getenv("R2_PUBLIC_URL", "")  # Optional custom domain

# Upload Authentication
UPLOAD_KEY: str = os.getenv("UPLOAD_KEY", "NUOCh2o#mC2#")

# Presigned URL Settings
PRESIGNED_URL_EXPIRY: int = 300  # 5 minutes
PRESIGNED_URL_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB

# Allowed Extensions
ALLOWED_EXTENSIONS: set = {".png", ".jpg", ".jpeg", ".gif", ".webp"}

# Vercel Function Settings
MAX_DURATION: int = 30  # seconds
CSV_CHUNK_SIZE: int = 1000

# Table Names
TRADES_TABLE: str = "trades"
UPLOADS_PREFIX: str = "screenshots/"
STATE_KEY: str = "state/upload_state.json"

def validate_env() -> list:
    """Validate required environment variables are set."""
    missing = []
    required = [
        ("SUPABASE_URL", SUPABASE_URL),
        ("SUPABASE_KEY", SUPABASE_KEY),
        ("R2_ACCOUNT_ID", R2_ACCOUNT_ID),
        ("R2_ACCESS_KEY_ID", R2_ACCESS_KEY_ID),
        ("R2_SECRET_ACCESS_KEY", R2_SECRET_ACCESS_KEY),
        ("R2_BUCKET", R2_BUCKET),
    ]
    for name, value in required:
        if not value:
            missing.append(name)
    return missing