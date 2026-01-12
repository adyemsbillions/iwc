from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from database import get_db_connection
from models import UserSignup, Token
from email_utils import send_verification_email


SECRET_KEY = "iwc-exchange-super-secret-key-2025-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
EMAIL_TOKEN_EXPIRE_HOURS = 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": email, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_email_verification_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=EMAIL_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": email,
        "type": "email_verification",
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return email

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def signup_user(user: UserSignup):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE email=%s", (user.email,))
    if cursor.fetchone():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = get_password_hash(user.password)
    verification_token = create_email_verification_token(user.email)

    cursor.execute("""
        INSERT INTO users (email, password, is_verified, verification_token)
        VALUES (%s, %s, %s, %s)
    """, (user.email, hashed_password, 0, verification_token))

    conn.commit()
    conn.close()

    send_verification_email(user.email, verification_token)

    return {
        "message": "Registration successful. Please check your email to verify your account."
    }


def login_user(form_data: OAuth2PasswordRequestForm):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT email, password, is_verified
        FROM users WHERE email=%s
    """, (form_data.username,))

    user = cursor.fetchone()
    conn.close()

    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if user["is_verified"] == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in"
        )

    access_token = create_access_token(user["email"])

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


def verify_email(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "email_verification":
            raise HTTPException(status_code=400, detail="Invalid token")

        email = payload.get("sub")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users
            SET is_verified = 1, verification_token = NULL
            WHERE email = %s AND verification_token = %s
        """, (email, token))

        conn.commit()
        conn.close()

        return {"message": "Email verified successfully. You can now log in."}

    except JWTError:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification token"
        )
