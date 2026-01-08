from fastapi import APIRouter, Depends, HTTPException
from database import get_db_connection
from auth import get_current_user

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("")
def get_profile(email: str = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    id,
                    username,
                    email,
                    user_type,
                    is_verified
                FROM users
                WHERE email = %s
            """, (email,))
            user = cur.fetchone()

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            return {
                "username": user["username"],
                "user_type": user["user_type"],     
                "verified": bool(user["is_verified"]),
                "user_id": str(user["id"]),
                "email": user["email"],
                "features": {
                    "transfer": True,
                    "buy_crypto": True,
                    "fiat_deposit": True,
                    "crypto_deposit": True,
                    "swap": True,
                    "iwc_pay": True,
                    "pos_services": True,
                    "web3": True
                }
            }
    finally:
        conn.close()
