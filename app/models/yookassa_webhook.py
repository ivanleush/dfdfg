from pydantic import BaseModel
from typing import Optional

class YooKassaWebhook(BaseModel):
    event: str
    object: dict
    test: Optional[bool] = None
    type: Optional[str] = None
    id: Optional[str] = None
    status: Optional[str] = None
    payment_id: Optional[str] = None
    amount: Optional[dict] = None
    created_at: Optional[str] = None
    paid_at: Optional[str] = None
    metadata: Optional[dict] = None
    confirmation_url: Optional[str] = None
    payment_method: Optional[dict] = None
    description: Optional[str] = None
    receipt: Optional[dict] = None
