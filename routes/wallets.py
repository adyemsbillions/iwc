from fastapi import APIRouter, Depends, HTTPException
from auth.dependencies import get_current_user

router = APIRouter(prefix="/wallets", tags=["Wallets"])

@router.post("/deposit-address")
def get_deposit_address(
    asset: str,
    user=Depends(get_current_user)
):
    """
    Asset values:
    - BTC
    - ETH
    - BNB
    - USDT

    Returns an existing wallet address or creates one.
    """

    asset = asset.upper()

    if asset not in ["BTC", "ETH", "BNB", "USDT"]:
        raise HTTPException(status_code=400, detail="Unsupported asset")

    # 1. Check if wallet already exists
    wallet = db.get_wallet(user.id, asset)

    if wallet:
        return {
            "asset": asset,
            "address": wallet["address"],
            "chain": wallet["chain"]
        }

    # 2. Generate wallet (logic implemented elsewhere)
    generated = wallet_service.generate_wallet(asset)

    # 3. Save wallet
    db.save_wallet(
        user_id=user.id,
        asset=asset,
        chain=generated["chain"],
        address=generated["address"],
        encrypted_private_key=generated["encrypted_private_key"]
    )

    return {
        "asset": asset,
        "address": generated["address"],
        "chain": generated["chain"]
    }
