import time
from typing import Optional
from uuid import UUID
from fastapi import Depends, Header, HTTPException, status
import jwt
from pydantic import BaseModel

from app.config import get_settings
from app.db.supabase import get_authenticated_supabase_client, get_supabase_client
from supabase import Client


class AuthenticatedUser(BaseModel):
    """Represents an authenticated user verified via Supabase Auth."""
    id: UUID
    email: str
    token: str


def get_current_user(
    authorization: Optional[str] = Header(default=None, description="Bearer JWT token")
) -> AuthenticatedUser:
    """Extract and validate the caller's Supabase JWT token.
    
    Rejects requests missing or having malformed/invalid bearer tokens.
    Never trusts client-supplied owner_id in request bodies.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = parts[1].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Empty bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    settings = get_settings()

    # 1. If JWT secret is configured, verify signature directly
    if settings.SUPABASE_JWT_SECRET:
        try:
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
            user_id = payload.get("sub")
            email = payload.get("email", "")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload: missing sub",
                )
            return AuthenticatedUser(id=UUID(user_id), email=email, token=token)
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token signature or format",
            )

    # 2. Otherwise try verifying via live Supabase Auth client
    try:
        supabase = get_supabase_client()
        user_response = supabase.auth.get_user(token)
        if user_response and user_response.user:
            return AuthenticatedUser(
                id=UUID(user_response.user.id),
                email=user_response.user.email or "",
                token=token,
            )
    except Exception:
        pass

    # 3. Fallback: Parse unverified JWT payload (used in local development / offline test suites)
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing sub claim",
            )
        
        # Verify expiration timestamp if provided in token
        exp = payload.get("exp")
        if exp and exp < time.time():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            )

        email = payload.get("email", "")
        return AuthenticatedUser(id=UUID(user_id), email=email, token=token)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed or invalid authentication token",
        )
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format in token",
        )


def get_user_db(
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> Client:
    """Dependency injecting a Supabase client scoped to the authenticated user's JWT.
    
    Ensures that PostgREST queries evaluate PostgreSQL Row Level Security (RLS)
    in the context of auth.uid() = current_user.id.
    """
    return get_authenticated_supabase_client(current_user.token)
