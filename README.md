# ChatGPT Plus 支付长链生成

基于 ChatGPT 官方支付接口生成 Stripe 长链，支持印尼 GoPay、美元、日元等多地区账单。

## 功能

- `index.html`：支付链接生成页面
- `otp.html`：验证码获取（演示）
- `server.py`：Flask 后端，转发到海外上游网关
- 容器化部署：Dockerfile + docker-compose

## 部署

```bash
cd deploy
docker-compose up -d --build
```

启动后访问：<http://服务器IP:8787/>

前置 nginx + HTTPS 可做反代到 `127.0.0.1:8787`。

## 环境变量

| 名称 | 默认值 | 说明 |
|---|---|---|
| `PORT` | `8787` | 监听端口 |
| `UPSTREAM` | `http://49.235.161.109:8766/api/generate` | 上游网关地址 |

## 请求示例

```bash
curl -X POST http://localhost:8787/api/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "token": "<access_token 或 session JSON>",
    "billing_country": "ID",
    "billing_currency": "IDR"
  }'
```

## 支持的账单国家

| 国家 | 货币 | 备注 |
|---|---|---|
| ID | IDR | 印度尼西亚，可得 GoPay |
| US | USD | 美国 |
| JP | JPY | 日本 |
| SG | SGD | 新加坡 |
| DE | EUR | 德国 |

## 注意

Access Token 等同账号凭据，**不要用重要账号测试**。
