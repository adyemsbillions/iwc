from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
import pymysql

from database import get_db_connection
from auth import (
    create_access_token,
    create_email_verification_token,
    verify_email,
)
from email_utils import send_verification_email
from routes.dashboard import router as dashboard_router
from routes.profile import router as profile_router

app = FastAPI(title="IWC Exchange")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str


@app.get("/")
def root():
    return {"status": "IWC Exchange API running"}


@app.post("/signup")
async def signup(request: SignupRequest):
    if request.password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    hashed_password = pwd_context.hash(request.password)
    verification_token = create_email_verification_token(request.email)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (email, password_hash, is_verified, verification_token)
                VALUES (%s, %s, %s, %s)
                """,
                (request.email, hashed_password, 0, verification_token)
            )
        conn.commit()
        send_verification_email(request.email, verification_token)
        return {"message": "Signup successful. Please verify your email."}
    except pymysql.err.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already registered")
    except Exception:
        raise HTTPException(status_code=500, detail="Server error")
    finally:
        conn.close()


@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT email, password_hash, is_verified
                FROM users WHERE email = %s
                """,
                (form_data.username,)
            )
            user = cur.fetchone()
    finally:
        conn.close()

    if not user or not pwd_context.verify(form_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user["is_verified"] == 0:
        raise HTTPException(status_code=403, detail="Please verify your email")

    access_token = create_access_token(user["email"])
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/verify-email")
def verify(token: str):
    return verify_email(token)


app.include_router(dashboard_router)
app.include_router(profile_router)
