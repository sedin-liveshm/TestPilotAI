from functools import lru_cache
from supabase import create_client, Client
from app.config import get_settings


@lru_cache()
def get_supabase_client() -> Client:
    """Initialize and return a cached Supabase client instance.
    
    Uses settings provided by app.config.get_settings().
    Never logs or exposes secret credentials.
    """
    settings = get_settings()
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
