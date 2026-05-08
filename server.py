"""
ChatGPT Plus 支付长链生成 - 纯转发网关

转发到上游：http://49.235.161.109:8766/api/generate
上游已落地海外并处理好地区逻辑，能正确返回各区域的 Stripe 支付长链（含印尼 GoPay）。
"""
import os
import pathlib

import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

ROOT = pathlib.Path(__file__).parent
app = Flask(__name__, static_folder=None)
CORS(app)

UPSTREAM = os.environ.get("UPSTREAM", "http://49.235.161.109:8766/api/generate")


@app.route("/")
def index():
    return send_from_directory(ROOT, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    target = ROOT / filename
    if target.is_file():
        return send_from_directory(ROOT, filename)
    return ("Not Found", 404)


@app.post("/api/generate")
def api_generate():
    body = request.get_json(silent=True) or {}
    body.setdefault("proxy", "")

    try:
        resp = requests.post(
            UPSTREAM,
            json=body,
            headers={
                "Content-Type": "application/json",
                "Origin": "http://49.235.161.109:8766",
                "Referer": "http://49.235.161.109:8766/",
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/147.0.0.0 Safari/537.36"
                ),
            },
            timeout=40,
        )
    except requests.RequestException as e:
        return jsonify({"error": f"上游网络错误: {e}"}), 502

    try:
        data = resp.json()
    except ValueError:
        return jsonify({"error": "上游返回非 JSON", "raw": resp.text[:500]}), 502

    # 归一化：前端用 data.link
    if isinstance(data, dict):
        links = data.get("links") or {}
        link = (
            data.get("link")
            or links.get("stripe_external")
            or links.get("openai_full")
            or ""
        )
        if link:
            data["link"] = link

    return jsonify(data), resp.status_code


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8787))
    print(f"→ http://127.0.0.1:{port}/")
    print(f"→ 上游: {UPSTREAM}")
    app.run(host="0.0.0.0", port=port, debug=False)
