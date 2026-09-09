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


def get_authenticated_supabase_client(access_token: str) -> Client:
    """Initialize a Supabase client scoped to an authenticated user's JWT.
    
    Attaches the Bearer access token to PostgREST headers so that PostgreSQL
    Row Level Security (RLS) evaluates auth.uid() in the context of the user.
    """
    settings = get_settings()
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    if access_token:
        client.postgrest.auth(access_token)
        client.postgrest.session.headers["Authorization"] = f"Bearer {access_token}"
    return client
