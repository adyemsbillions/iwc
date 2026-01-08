from fastapi import APIRouter, Depends
from auth.dependencies import get_current_user

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("/")
def get_alerts(user=Depends(get_current_user)):
    """
    Returns system-generated alerts.
    """

    return db.get_alerts_by_user(user.id)


@router.post("/mark-read/{alert_id}")
def mark_alert_read(alert_id: int, user=Depends(get_current_user)):
    """
    Marks an alert as read.
    """

    db.mark_alert_as_read(alert_id, user.id)

    return {"status": "ok"}
