"""FastAPI application bootstrap, error handling, and route registration."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .storage import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="AI Analytics Tool", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global error handler
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "internal_error", "message": str(exc), "details": []}},
    )


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Route registration
# ---------------------------------------------------------------------------
from . import analytics, operators, tenants  # noqa: E402
from .auth import (  # noqa: E402
    create_token,
    current_user,
    hash_password,
    pwd_context,
    validate_password_policy,
    verify_password,
)
from .models import User  # noqa: E402
from .storage import get_db  # noqa: E402
from pydantic import BaseModel, EmailStr  # noqa: E402
from fastapi import Depends, HTTPException, status  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

app.include_router(tenants.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(operators.router, prefix="/api")


# ---------------------------------------------------------------------------
# Auth endpoints
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


@app.post("/api/auth/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is inactive")
    token = create_token(user.id, {"type": "tenant_user"})
    return {
        "user": {"id": user.id, "email": user.email},
        "token": token,
        "message": "logged_in",
    }


@app.post("/api/auth/logout")
def logout():
    return {"message": "logged_out"}


@app.get("/api/me")
def me(user: User = Depends(current_user), db: Session = Depends(get_db)):
    from .models import TenantMembership
    membership = db.query(TenantMembership).filter(
        TenantMembership.tenant_id == user.tenant_id,
        TenantMembership.user_id == user.id,
    ).first()
    return {
        "id": user.id,
        "email": user.email,
        "role": membership.role if membership else "user",
        "tenant_id": user.tenant_id,
        "is_active": user.is_active,
    }


@app.patch("/api/me/password")
def change_password(body: PasswordChangeRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if not verify_password(body.current_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    validate_password_policy(body.new_password)
    user.password_hash = hash_password(body.new_password)
    from datetime import datetime, timezone
    user.password_changed_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "password_updated"}