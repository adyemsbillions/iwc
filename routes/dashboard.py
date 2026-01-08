from fastapi import APIRouter, Depends, HTTPException
from database import get_db_connection
from auth import get_current_user

router = APIRouter()

@router.get("/dashboard")
async def dashboard(email: str = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT email FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
    finally:
        conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

  
    name = email.split("@")[0].replace(".", " ").title()

    return {
        "greeting": "Good morning!",
        "name": name,
        "email": email,
        "total_balance": "14874.39",
        "currency": "USD"
    }