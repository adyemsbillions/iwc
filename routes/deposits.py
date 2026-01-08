from fastapi import APIRouter, Depends
from auth.dependencies import get_current_user

router = APIRouter(prefix="/deposits", tags=["Deposits"])

@router.get("/")
def list_user_deposits(user=Depends(get_current_user)):
    """
    Returns deposits detected for the user.
    """

    deposits = db.get_deposits_by_user(user.id)

    return deposits
