from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict

from app.db.supabase import get_supabase_client
from app.dependencies.auth import AuthenticatedUser, get_current_user
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    email: str
    password: str

    model_config = ConfigDict(extra="ignore")


class UserProfile(BaseModel):
    id: str
    email: str
    name: Optional[str] = None


class LoginResponseData(BaseModel):
    accessToken: str
    refreshToken: Optional[str] = None
    user: UserProfile


class MeResponseData(BaseModel):
    user: UserProfile


class SignupRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

    model_config = ConfigDict(extra="ignore")


@router.post(
    "/signup",
    summary="Register a new user via Supabase Auth",
)
def signup(data: SignupRequest):
    """Register a new user account in Supabase Auth."""
    supabase = get_supabase_client()
    try:
        credentials = {"email": data.email, "password": data.password}
        if data.full_name:
            credentials["options"] = {"data": {"full_name": data.full_name}}
        res = supabase.auth.sign_up(credentials)
        if not res or not res.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Signup failed",
            )
        return ApiResponse(
            data={
                "id": str(res.user.id),
                "email": res.user.email or data.email,
                "message": "User registered successfully",
            }
        )
    except HTTPException:
        raise
    except Exception as exc:
        msg = getattr(exc, "message", None) or str(exc) or "Signup failed"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg,
        )


@router.post(
    "/login",
    response_model=ApiResponse[LoginResponseData],
    summary="User login via Supabase Auth",
)
def login(data: LoginRequest):
    """Authenticate with email & password via Supabase Auth."""
    supabase = get_supabase_client()
    try:
        res = supabase.auth.sign_in_with_password(
            {"email": data.email, "password": data.password}
        )
        if not res or not res.session or not res.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        name = (
            res.user.user_metadata.get("full_name")
            or res.user.user_metadata.get("name")
            or (res.user.email.split("@")[0] if res.user.email else "")
        )

        return ApiResponse(
            data=LoginResponseData(
                accessToken=res.session.access_token,
                refreshToken=res.session.refresh_token,
                user=UserProfile(
                    id=str(res.user.id),
                    email=res.user.email or "",
                    name=name,
                ),
            )
        )
    except HTTPException:
        raise
    except Exception as exc:
        msg = getattr(exc, "message", None) or str(exc) or "Invalid email or password"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=msg,
        )


@router.post("/logout", summary="User logout")
def logout():
    """Logout current session."""
    try:
        supabase = get_supabase_client()
        supabase.auth.sign_out()
    except Exception:
        pass
    return ApiResponse(data={})


@router.get(
    "/me",
    response_model=ApiResponse[MeResponseData],
    summary="Get current authenticated user info",
)
def get_me(current_user: AuthenticatedUser = Depends(get_current_user)):
    """Fetch current user from verified bearer token."""
    name = current_user.email.split("@")[0] if current_user.email else ""
    return ApiResponse(
        data=MeResponseData(
            user=UserProfile(
                id=str(current_user.id),
                email=current_user.email,
                name=name,
            )
        )
    )
