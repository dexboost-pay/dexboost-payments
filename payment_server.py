import os
import uuid
import hmac
import json
import hashlib
from typing import Optional

import requests
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv

load_dotenv()

NOWPAY_API_KEY = os.getenv("NOWPAY_API_KEY", "").strip()
NOWPAY_IPN_SECRET = os.getenv("NOWPAY_IPN_SECRET", "").strip()
NOWPAY_BASE_URL = os.getenv("NOWPAY_BASE_URL", "https://api.nowpayments.io/v1").strip()
APP_BASE_URL = os.getenv("APP_BASE_URL", "").strip()

if not NOWPAY_API_KEY:
    raise ValueError("NOWPAY_API_KEY missing in .env")

app = FastAPI()

# Временное хранилище депозитов в памяти
# Потом перенесем в базу
deposits = {}


def nowpay_headers():
    return {
        "x-api-key": NOWPAY_API_KEY,
        "Content-Type": "application/json",
    }


@app.get("/")
def root():
    return {"ok": True, "message": "payment server is running"}


@app.post("/create-deposit")
async def create_deposit(payload: dict):
    """
    Принимает:
    {
      "user_id": 123,
      "amount_usd": 100
    }
    """
    user_id = payload.get("user_id")
    amount_usd = payload.get("amount_usd")

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    try:
        amount_usd = float(amount_usd)
    except Exception:
        raise HTTPException(status_code=400, detail="amount_usd must be a number")

    if amount_usd < 10:
        raise HTTPException(status_code=400, detail="minimum deposit is 10 USD")

    deposit_id = str(uuid.uuid4())[:8].upper()
    order_id = f"DEP-{deposit_id}"

    if not APP_BASE_URL:
        raise HTTPException(status_code=500, detail="APP_BASE_URL is empty in .env")

    ipn_callback_url = f"{APP_BASE_URL}/nowpayments-ipn"

    # Используем invoice endpoint
    request_payload = {
        "price_amount": amount_usd,
        "price_currency": "usd",
        "order_id": order_id,
        "order_description": f"Deposit for Telegram user {user_id}",
        "ipn_callback_url": ipn_callback_url,
        "success_url": "https://t.me",
        "cancel_url": "https://t.me",
        "is_fixed_rate": False,
        "is_fee_paid_by_user": True
    }

    response = requests.post(
        f"{NOWPAY_BASE_URL}/invoice",
        headers=nowpay_headers(),
        json=request_payload,
        timeout=30
    )

    try:
        result = response.json()
    except Exception:
        raise HTTPException(status_code=500, detail=f"NOWPayments bad response: {response.text}")

    if response.status_code not in (200, 201):
        raise HTTPException(status_code=response.status_code, detail=result)

    invoice_id = result.get("id")
    invoice_url = result.get("invoice_url") or result.get("invoice_url")

    deposits[deposit_id] = {
        "deposit_id": deposit_id,
        "user_id": user_id,
        "amount_usd": amount_usd,
        "order_id": order_id,
        "invoice_id": invoice_id,
        "invoice_url": invoice_url,
        "status": "waiting_payment",
        "raw_create_response": result,
    }

    return {
        "success": True,
        "deposit_id": deposit_id,
        "amount_usd": amount_usd,
        "invoice_id": invoice_id,
        "invoice_url": invoice_url,
        "status": "waiting_payment"
    }


@app.get("/deposit-status/{deposit_id}")
async def deposit_status(deposit_id: str):
    deposit = deposits.get(deposit_id)
    if not deposit:
        raise HTTPException(status_code=404, detail="deposit not found")

    return {
        "success": True,
        "deposit_id": deposit_id,
        "status": deposit["status"],
        "data": deposit
    }


@app.post("/nowpayments-ipn")
async def nowpayments_ipn(request: Request):
    raw_body = await request.body()
    signature = request.headers.get("x-nowpayments-sig")

    if not signature:
        raise HTTPException(status_code=400, detail="missing signature header")

    if NOWPAY_IPN_SECRET:
        expected_sig = hmac.new(
            NOWPAY_IPN_SECRET.encode(),
            raw_body,
            hashlib.sha512
        ).hexdigest()

        if signature != expected_sig:
            raise HTTPException(status_code=403, detail="invalid IPN signature")

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="invalid json")

    order_id = payload.get("order_id")
    payment_status = payload.get("payment_status", "unknown")

    # Находим депозит по order_id
    found_deposit = None
    for dep_id, dep in deposits.items():
        if dep.get("order_id") == order_id:
            found_deposit = dep
            break

    if found_deposit is None:
        return {"ok": True, "warning": "deposit not found, but ipn accepted"}

    found_deposit["status"] = payment_status
    found_deposit["ipn_payload"] = payload

    return {"ok": True, "status": payment_status}