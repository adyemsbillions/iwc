from fastapi import APIRouter, Depends
from auth.dependencies import get_current_user

router = APIRouter(prefix="/balances", tags=["Balances"])

@router.get("/")
def get_user_balances(user=Depends(get_current_user)):
    """
    Returns internal balances.
    Not real-time blockchain balances.
    """

    return {
        "BTC": user.btc_balance,
        "ETH": user.eth_balance,
        "BNB": user.bnb_balance,
        "USDT": user.usdt_balance
    }
