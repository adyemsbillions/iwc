from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
import pymysql

from database import get_db_connection
from auth import create_access_token
from routes.dashboard import router as dashboard_router
from routes.profile import router as profile_router

app = FastAPI(title="IWC Exchange")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =========================
# MODELS
# =========================
class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str


# =========================
# PUBLIC ROUTES
# =========================
@app.get("/")
def root():
    return {"status": "IWC Exchange API running"}


@app.post("/signup")
async def signup(request: SignupRequest):
    if request.password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    hashed_password = pwd_context.hash(request.password)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (email, password_hash)
                VALUES (%s, %s)
                """,
                (request.email, hashed_password)
            )
        conn.commit()
        return {"message": "Signup successful"}
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
                "SELECT email, password_hash FROM users WHERE email = %s",
                (form_data.username,)
            )
            user = cur.fetchone()
    finally:
        conn.close()

    if not user or not pwd_context.verify(form_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(user["email"])
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# =========================
# PROTECTED ROUTES
# =========================
app.include_router(dashboard_router)
app.include_router(profile_router)
