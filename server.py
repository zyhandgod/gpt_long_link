"""
ChatGPT Plus 支付长链生成。

后端按油猴脚本同款 payload 直接请求 ChatGPT 官方 checkout 接口，避免中间网关改写参数。
"""
import json
import os
import pathlib

import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

ROOT = pathlib.Path(__file__).parent
app = Flask(__name__, static_folder=None)
CORS(app)

CHECKOUT_URL = os.environ.get(
    "CHECKOUT_URL",
    "https://chatgpt.com/backend-api/payments/checkout",
)
PAYLOADS = {
    ("ID", "IDR"): {
        "plan_name": "chatgptplusplan",
        "billing_details": {"country": "ID", "currency": "IDR"},
        "cancel_url": "https://chatgpt.com/#pricing",
        "promo_campaign": {
            "promo_campaign_id": "plus-1-month-free",
            "is_coupon_from_query_param": False,
        },
        "checkout_ui_mode": "hosted",
    },
    ("DE", "EUR"): {
        "plan_name": "chatgptplusplan",
        "billing_details": {"country": "DE", "currency": "EUR"},
        "cancel_url": "https://chatgpt.com/#pricing",
        "promo_campaign": {
            "promo_campaign_id": "plus-1-month-free",
            "is_coupon_from_query_param": False,
        },
        "checkout_ui_mode": "hosted",
    },
    ("FR", "EUR"): {
        "plan_name": "chatgptplusplan",
        "billing_details": {"country": "FR", "currency": "EUR"},
        "cancel_url": "https://chatgpt.com/#pricing",
        "promo_campaign": {
            "promo_campaign_id": "plus-1-month-free",
            "is_coupon_from_query_param": False,
        },
        "checkout_ui_mode": "hosted",
    },
    ("GB", "GBP"): {
        "plan_name": "chatgptplusplan",
        "billing_details": {"country": "GB", "currency": "GBP"},
        "cancel_url": "https://chatgpt.com/#pricing",
        "promo_campaign": {
            "promo_campaign_id": "plus-1-month-free",
            "is_coupon_from_query_param": False,
        },
        "checkout_ui_mode": "hosted",
    },
}


@app.route("/")
def index():
    return send_from_directory(ROOT, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    target = ROOT / filename
    if target.is_file():
        return send_from_directory(ROOT, filename)
    return ("Not Found", 404)


def extract_token(raw):
    if not isinstance(raw, str):
        return ""
    raw = raw.strip()
    if not raw:
        return ""
    try:
        data = json.loads(raw)
    except ValueError:
        return raw
    if isinstance(data, dict):
        return data.get("accessToken") or data.get("token") or raw
    return raw


def normalize_cookie(raw):
    if not isinstance(raw, str):
        return ""
    raw = raw.strip()
    if raw.lower().startswith("cookie:"):
        raw = raw.split(":", 1)[1].strip()
    return raw


def checkout_payload_from(body):
    payload = body.get("checkout_payload")
    if isinstance(payload, dict):
        return payload

    country = body.get("billing_country") or "ID"
    currency = body.get("billing_currency") or "IDR"
    return PAYLOADS.get((country, currency)) or {
        "plan_name": "chatgptplusplan",
        "billing_details": {"country": country, "currency": currency},
        "cancel_url": "https://chatgpt.com/#pricing",
        "promo_campaign": {
            "promo_campaign_id": "plus-1-month-free",
            "is_coupon_from_query_param": False,
        },
        "checkout_ui_mode": "hosted",
    }


@app.post("/api/generate")
def api_generate():
    body = request.get_json(silent=True) or {}
    token = extract_token(body.get("token", ""))
    if not token:
        return jsonify({"error": "缺少 Access Token"}), 400

    chatgpt_cookie = normalize_cookie(body.get("chatgpt_cookie", ""))
    checkout_payload = checkout_payload_from(body)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Origin": "https://chatgpt.com",
        "Referer": "https://chatgpt.com/",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/147.0.0.0 Safari/537.36"
        ),
    }
    if chatgpt_cookie:
        headers["Cookie"] = chatgpt_cookie

    try:
        resp = requests.post(
            CHECKOUT_URL,
            json=checkout_payload,
            headers=headers,
            timeout=40,
        )
    except requests.RequestException as e:
        return jsonify({"error": f"ChatGPT checkout 网络错误: {e}"}), 502

    try:
        data = resp.json()
    except ValueError:
        return jsonify({
            "error": "ChatGPT checkout 返回非 JSON",
            "status": resp.status_code,
            "content_type": resp.headers.get("content-type", ""),
            "raw": resp.text[:500],
            "hint": "油猴脚本会随 credentials: include 自动带上 ChatGPT Cookie；独立网页需要额外粘贴同浏览器的 Cookie。",
        }), 502

    if isinstance(data, dict):
        link = data.get("url") or data.get("stripe_hosted_url") or data.get("checkout_url") or data.get("link")
        if link:
            data["link"] = link
        data.setdefault("checkout_payload", checkout_payload)

    return jsonify(data), resp.status_code


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8787))
    print(f"→ http://127.0.0.1:{port}/")
    print(f"→ checkout: {CHECKOUT_URL}")
    app.run(host="0.0.0.0", port=port, debug=False)
