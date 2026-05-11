// ==UserScript==
// @name         ChatGPT 长链生成器
// @namespace    https://chatgpt.com/
// @author       Miku-Y
// @version      1.0.2
// @description  在 ChatGPT 页面显示快捷支付和 Token 入口，并兼容当前站点的翻译告警。
// @downloadURL   https://gpt.mooizz.com/chatgpt-long-link.user.js
// @updateURL     https://gpt.mooizz.com/chatgpt-long-link.user.js
// @match        https://chatgpt.com/*
// @run-at       document-start
// @grant        none
// ==/UserScript==

(() => {
    "use strict";

    if (window.self !== window.top) return;
    if (location.hostname !== "chatgpt.com") {
        alert("请在 chatgpt.com 页面运行这个脚本。当前页面没有 ChatGPT 登录态，所以会 Failed to fetch。");
        window.open("https://chatgpt.com/", "_blank");
        return;
    }

    const CONTAINER_ID = "gopay-container";
    const TIP_ID = "gopay-checkout-tip";
    const STYLE_ID = "gopay-style";
    const COLLAPSED_KEY = "gopay-collapsed";
    const POSITION_KEY = "gopay-btn-pos";
    const BTN_ID = "gopay-checkout-button";
    const PAYPAL_BTN_ID = "gopay-paypal-button";
    const PAYPAL_EU_BTN_ID = "gopay-paypal-eu-button";
    const PAYPAL_UK_BTN_ID = "gopay-paypal-uk-button";
    const TOKEN_BTN_ID = "gopay-token-button";
    const I18N_KEY = "navigation.sidebarProfileCodexPlanName.plus";
    const I18N_WARNING_SNIPPET = `Missing message: "${I18N_KEY}"`;

    const CONTAINER_CSS = "position:fixed;right:22px;top:22px;z-index:2147483647;width:304px;max-width:calc(100vw - 24px);overflow:hidden;background:#f7f3eb;color:#181512;border-radius:24px;padding:0;box-shadow:0 26px 70px rgba(22,20,16,0.34),0 0 0 1px rgba(40,34,24,0.12);user-select:none;transition:box-shadow 0.25s ease,transform 0.25s ease;will-change:left,top;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;";
    const BTN_BASE = "width:100%;border:0;color:inherit;font:700 13px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;cursor:pointer;transition:transform 0.18s ease,box-shadow 0.18s ease,background 0.18s ease;white-space:nowrap;display:flex;align-items:center;text-align:left;";
    const TIP_CSS = "position:fixed;bottom:40px;left:50%;transform:translateX(-50%) translateY(100px);z-index:2147483648;padding:12px 28px;border-radius:50px;font:600 15px -apple-system,sans-serif;box-shadow:0 12px 40px rgba(0,0,0,0.5);color:#fff;opacity:0;pointer-events:none;transition:all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);";

    const STYLE = `
        #gopay-container * { box-sizing: border-box; }
        #gopay-container:hover { box-shadow: 0 32px 86px rgba(22,20,16,0.42),0 0 0 1px rgba(40,34,24,0.16); transform: translateY(-2px); }
        #gopay-container.gopay-collapsed { width: 168px; border-radius: 999px; padding: 0; background: #fff7e8; }
        #gopay-container.gopay-collapsed:hover { transform: translateY(-1px); }
        #gopay-container.gopay-collapsed #gopay-drag-handle,
        #gopay-container.gopay-collapsed .gopay-head,
        #gopay-container.gopay-collapsed .gopay-body { display: none; }
        #gopay-container:not(.gopay-collapsed) .gopay-mini { display: none; }
        #gopay-drag-handle { cursor: grab; height: 28px; display: flex; align-items: center; justify-content: center; background: #efe6d6; }
        #gopay-drag-handle::after { content: ""; display: block; width: 48px; height: 4px; background: rgba(77,63,36,0.22); border-radius: 999px; }
        .gopay-head { position: relative; padding: 18px 18px 16px; background: linear-gradient(135deg,#fff7e8 0%,#e5f7e9 100%); color: #181512; border-top: 1px solid rgba(255,255,255,0.7); }
        .gopay-head::after { content: ""; position: absolute; right: 18px; bottom: -18px; width: 84px; height: 84px; border-radius: 50%; background: radial-gradient(circle,#28c98b 0 24%,transparent 25% 100%); opacity: 0.28; pointer-events: none; }
        .gopay-kicker { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; color: rgba(24,21,18,0.5); font: 700 11px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; text-transform: uppercase; letter-spacing: 0; }
        .gopay-status { display: inline-flex; align-items: center; gap: 7px; min-width: 0; }
        .gopay-status-dot { width: 8px; height: 8px; border-radius: 50%; background: #28c98b; box-shadow: 0 0 0 4px rgba(40,201,139,0.14); }
        .gopay-status-dot.is-busy { background: #f59e0b; box-shadow: 0 0 0 4px rgba(245,158,11,0.16); }
        .gopay-status-dot.is-error { background: #ef4444; box-shadow: 0 0 0 4px rgba(239,68,68,0.16); }
        .gopay-status-dot.is-ok { background: #28c98b; box-shadow: 0 0 0 4px rgba(40,201,139,0.14); }
        .gopay-status-text { max-width: 118px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .gopay-tools { position: relative; z-index: 2; display: flex; justify-content: flex-end; gap: 6px; margin-bottom: 12px; }
        .gopay-tool { width: 28px; height: 28px; border: 0; border-radius: 999px; color: rgba(24,21,18,0.72); background: rgba(255,255,255,0.62); cursor: pointer; display: grid; place-items: center; font: 800 15px/1 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; transition: background 0.18s ease, transform 0.18s ease, color 0.18s ease; }
        .gopay-tool:hover { color: #061a12; background: #fffaf1; transform: translateY(-1px); }
        .gopay-title { position: relative; z-index: 1; margin: 0; color: #181512; font: 800 22px/1.12 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; letter-spacing: 0; }
        .gopay-subtitle { position: relative; z-index: 1; margin-top: 7px; color: rgba(24,21,18,0.58); font: 600 12px/1.35 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; }
        .gopay-body { padding: 14px; display: grid; gap: 10px; background: linear-gradient(180deg,#f7f3eb,#eee6d8); }
        .gopay-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
        .gopay-row { position: relative; min-width: 0; min-height: 52px; padding: 12px; border-radius: 16px; gap: 10px; background: #fffaf1; box-shadow: 0 1px 0 rgba(255,255,255,0.8) inset, 0 7px 18px rgba(77,63,36,0.1); }
        .gopay-row:hover { transform: translateY(-2px); box-shadow: 0 1px 0 rgba(255,255,255,0.9) inset, 0 13px 28px rgba(77,63,36,0.17); }
        .gopay-row:active { transform: scale(0.98); }
        .gopay-row:disabled { cursor: progress; }
        .gopay-primary { grid-column: 1 / -1; min-height: 78px; padding: 16px; color: #061a12; background: linear-gradient(135deg,#44e19e,#19b978); box-shadow: 0 16px 30px rgba(25,185,120,0.28), inset 0 1px 0 rgba(255,255,255,0.45); }
        .gopay-paypal { color: #13233f; background: linear-gradient(135deg,#dcecff,#b9d6ff); }
        .gopay-token { color: #20184b; background: linear-gradient(135deg,#ece6ff,#d6ccff); }
        .gopay-icon { width: 34px; height: 34px; flex: 0 0 auto; border-radius: 12px; display: grid; place-items: center; background: rgba(255,255,255,0.48); font-size: 17px; box-shadow: inset 0 0 0 1px rgba(255,255,255,0.42); }
        .gopay-primary .gopay-icon { width: 42px; height: 42px; border-radius: 15px; background: rgba(6,26,18,0.12); font-size: 20px; }
        .gopay-copy { min-width: 0; display: grid; gap: 2px; }
        .gopay-label { overflow: hidden; text-overflow: ellipsis; font-size: 13px; }
        .gopay-primary .gopay-label { font-size: 16px; }
        .gopay-meta { overflow: hidden; text-overflow: ellipsis; color: rgba(24,21,18,0.55); font: 650 11px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; }
        .gopay-mini { width: 100%; height: 48px; padding: 0 12px; border: 0; border-radius: 999px; background: linear-gradient(135deg,#fff7e8,#dff7e8); color: #181512; cursor: pointer; display: flex; align-items: center; gap: 9px; text-align: left; box-shadow: inset 0 1px 0 rgba(255,255,255,0.78); }
        .gopay-mini-icon { width: 30px; height: 30px; border-radius: 999px; display: grid; place-items: center; background: #19b978; color: #061a12; font-size: 15px; }
        .gopay-mini-copy { min-width: 0; display: grid; gap: 1px; }
        .gopay-mini-title { color: #181512; font: 800 12px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; white-space: nowrap; }
        .gopay-mini-state { color: rgba(24,21,18,0.58); font: 700 10px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        @media (max-width: 420px) { #gopay-container { right: 12px !important; top: 12px; width: calc(100vw - 24px); } .gopay-title { font-size: 20px; } }
    `;

    const PAYLOAD = {
        plan_name: "chatgptplusplan",
        billing_details: { country: "ID", currency: "IDR" },
        cancel_url: "https://chatgpt.com/#pricing",
        promo_campaign: { promo_campaign_id: "plus-1-month-free", is_coupon_from_query_param: false },
        checkout_ui_mode: "hosted",
    };
    const PAYLOAD_DE = {
        plan_name: "chatgptplusplan",
        billing_details: { country: "DE", currency: "EUR" },
        cancel_url: "https://chatgpt.com/#pricing",
        promo_campaign: { promo_campaign_id: "plus-1-month-free", is_coupon_from_query_param: false },
        checkout_ui_mode: "hosted",
    };
    const PAYLOAD_EU = {
        plan_name: "chatgptplusplan",
        billing_details: { country: "FR", currency: "EUR" },
        cancel_url: "https://chatgpt.com/#pricing",
        promo_campaign: { promo_campaign_id: "plus-1-month-free", is_coupon_from_query_param: false },
        checkout_ui_mode: "hosted",
    };
    const PAYLOAD_GB = {
        plan_name: "chatgptplusplan",
        billing_details: { country: "GB", currency: "GBP" },
        cancel_url: "https://chatgpt.com/#pricing",
        promo_campaign: { promo_campaign_id: "plus-1-month-free", is_coupon_from_query_param: false },
        checkout_ui_mode: "hosted",
    };

    let busy = false;
    let panelStatus = "就绪";

    const $ = (id) => document.getElementById(id);
    const mount = (el) => (document.body || document.documentElement).appendChild(el);
    const inCheckout = () => true;

    function silenceKnownIntlWarning() {
        const originalError = console.error;
        if (originalError.__gopayWrapped) return;

        const wrapped = function (...args) {
            const text = args.map((item) => {
                if (typeof item === "string") return item;
                if (item instanceof Error) return item.message;
                return "";
            }).join(" ");

            if (text.includes("@formatjs/intl Error MISSING_TRANSLATION") && text.includes(I18N_WARNING_SNIPPET)) {
                return;
            }

            return originalError.apply(this, args);
        };

        wrapped.__gopayWrapped = true;
        console.error = wrapped;
    }

    function fixTranslations() {
        try {
            const data = window.__NEXT_DATA__;
            const pageProps = data?.props?.pageProps;
            if (!pageProps) return;

            const candidates = [pageProps.messages, pageProps.localeMessages, pageProps.l10nMessages];
            for (const messages of candidates) {
                if (messages && typeof messages === "object" && !messages[I18N_KEY]) {
                    messages[I18N_KEY] = "Plus";
                }
            }
        } catch (_) {
            // noop
        }
    }

    function ensureStyle() {
        if ($(STYLE_ID)) return;
        const style = document.createElement("style");
        style.id = STYLE_ID;
        style.textContent = STYLE;
        (document.head || document.documentElement).appendChild(style);
    }

    function setPanelStatus(text, state = "ok") {
        panelStatus = text;
        const container = $(CONTAINER_ID);
        if (!container) return;

        const statusText = container.querySelector(".gopay-status-text");
        const miniState = container.querySelector(".gopay-mini-state");
        const dot = container.querySelector(".gopay-status-dot");

        if (statusText) statusText.textContent = text;
        if (miniState) miniState.textContent = text;
        if (dot) {
            dot.classList.remove("is-ok", "is-busy", "is-error");
            dot.classList.add(state === "busy" ? "is-busy" : state === "error" ? "is-error" : "is-ok");
        }
    }

    function setCollapsed(container, on) {
        container.classList.toggle("gopay-collapsed", on);
        localStorage.setItem(COLLAPSED_KEY, on ? "1" : "0");
    }

    function tip(text, error = false) {
        let el = $(TIP_ID);
        if (!el) {
            ensureStyle();
            el = document.createElement("div");
            el.id = TIP_ID;
            el.style.cssText = TIP_CSS;
            mount(el);
        }

        el.textContent = text;
        el.style.background = error
            ? "linear-gradient(135deg, #ef4444 0%, #991b1b 100%)"
            : "linear-gradient(135deg, #1f2937 0%, #111827 100%)";

        const hide = () => {
            el.style.opacity = "0";
            el.style.transform = "translateX(-50%) translateY(100px)";
        };
        const show = () => {
            el.style.opacity = "1";
            el.style.transform = "translateX(-50%) translateY(0)";
        };

        hide();
        void el.offsetWidth;
        show();

        if (!error) setTimeout(hide, 4000);
    }

    async function fetchJson(url, options) {
        const response = await fetch(url, options);
        const data = await response.json().catch(() => null);
        if (!response.ok) throw Object.assign(new Error(`HTTP ${response.status}`), { data });
        return data;
    }

    async function copyText(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (_) {
            try {
                const ta = document.createElement("textarea");
                ta.value = text;
                ta.style.cssText = "position:fixed;opacity:0;top:0;left:0;";
                document.body.appendChild(ta);
                ta.select();
                document.execCommand("copy");
                document.body.removeChild(ta);
                return true;
            } catch (_) {
                return false;
            }
        }
    }

    async function getToken() {
        setPanelStatus("获取 Token 中", "busy");
        tip("正在获取 AccessToken...");

        try {
            const data = await fetchJson("/api/auth/session", { credentials: "include" });
            const token = data?.accessToken;
            if (!token) throw new Error("获取失败，请确认 ChatGPT 已登录。");

            await copyText(token);
            setPanelStatus("Token 已复制", "ok");
            tip("AccessToken 已复制到剪贴板。");
        } catch (error) {
            console.error("[plus-link]", error);
            setPanelStatus("Token 获取失败", "error");
            tip(error.message || "获取失败", true);
        }
    }

    async function pay(button, payload, label) {
        if (busy) return;
        busy = true;

        const labelEl = button.querySelector(".gopay-label");
        const originalText = labelEl?.textContent || button.textContent;

        const setLoading = (on) => {
            button.disabled = on;
            if (labelEl) labelEl.textContent = on ? "正在跳转..." : originalText;
            button.style.opacity = on ? ".65" : "1";
        };

        setLoading(true);
        setPanelStatus(`${label} 生成中`, "busy");
        tip("正在生成支付链接...");

        try {
            const token = (await fetchJson("/api/auth/session", { credentials: "include" }))?.accessToken;
            if (!token) throw new Error("获取登录 Token 失败，请确认 ChatGPT 已登录。");

            const data = await fetchJson("https://chatgpt.com/backend-api/payments/checkout", {
                method: "POST",
                credentials: "include",
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });

            const hostedUrl = data?.url || data?.stripe_hosted_url || data?.checkout_url;
            if (!hostedUrl) throw new Error("未找到付款链接，请查看控制台原始响应。");

            console.log("[plus-link]", label, hostedUrl, data);
            setPanelStatus("链接生成成功", "ok");
            const copied = await copyText(hostedUrl);
            tip(copied ? "长链接已复制，正在跳转..." : "链接生成成功，正在跳转...");
            location.assign(hostedUrl);
        } catch (error) {
            console.error("[plus-link]", error);
            busy = false;
            setLoading(false);
            setPanelStatus("付款链接失败", "error");
            tip(error.message || "请求失败，请看控制台日志", true);
        }
    }

    function makeDraggable(el, handle) {
        const dragTarget = handle || el;
        let isDragging = false;
        let moved = false;
        let startX;
        let startY;
        let initialX;
        let initialY;

        const pos = JSON.parse(localStorage.getItem(POSITION_KEY) || "{}");
        if (pos.left !== undefined) {
            el.style.left = pos.left;
            el.style.right = "auto";
        }
        if (pos.top !== undefined) {
            el.style.top = pos.top;
        }

        dragTarget.addEventListener("mousedown", (e) => {
            if (e.target.tagName === "BUTTON" || e.target.closest("button") || e.target.closest("a")) return;
            isDragging = true;
            moved = false;
            startX = e.clientX;
            startY = e.clientY;
            initialX = el.offsetLeft;
            initialY = el.offsetTop;
            document.addEventListener("mousemove", onMove);
            document.addEventListener("mouseup", onEnd);
        });

        function onMove(e) {
            if (!isDragging) return;
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;

            if (Math.abs(dx) > 5 || Math.abs(dy) > 5) {
                moved = true;
                el.style.cursor = "grabbing";
            }

            el.style.left = `${initialX + dx}px`;
            el.style.top = `${initialY + dy}px`;
            el.style.right = "auto";
        }

        function onEnd() {
            if (!isDragging) return;
            isDragging = false;
            el.style.cursor = "default";
            document.removeEventListener("mousemove", onMove);
            document.removeEventListener("mouseup", onEnd);

            if (moved) {
                localStorage.setItem(POSITION_KEY, JSON.stringify({ left: el.style.left, top: el.style.top }));
            }

            setTimeout(() => {
                moved = false;
            }, 0);
        }

        el.querySelectorAll("button, a").forEach((node) => {
            node.addEventListener("click", (e) => {
                if (moved) {
                    e.stopImmediatePropagation();
                    e.preventDefault();
                }
            }, true);
        });
    }

    function makeRow(id, icon, label, meta, cls = "") {
        const btn = document.createElement("button");
        if (id) btn.id = id;
        btn.className = `gopay-row ${cls}`.trim();
        btn.type = "button";
        btn.style.cssText = BTN_BASE;
        btn.innerHTML = `<span class="gopay-icon">${icon}</span><span class="gopay-copy"><span class="gopay-label">${label}</span><span class="gopay-meta">${meta}</span></span>`;
        return btn;
    }

    function showButton() {
        if (!inCheckout() || $(CONTAINER_ID)) return;

        ensureStyle();
        fixTranslations();
        silenceKnownIntlWarning();

        const container = document.createElement("div");
        container.id = CONTAINER_ID;
        container.style.cssText = CONTAINER_CSS;

        const handle = document.createElement("div");
        handle.id = "gopay-drag-handle";

        const mini = document.createElement("button");
        mini.className = "gopay-mini";
        mini.type = "button";
        mini.innerHTML = `<span class="gopay-mini-icon">💸</span><span class="gopay-mini-copy"><span class="gopay-mini-title">快捷支付</span><span class="gopay-mini-state">${panelStatus}</span></span>`;
        mini.addEventListener("click", () => setCollapsed(container, false));

        const head = document.createElement("div");
        head.className = "gopay-head";
        head.innerHTML = `
            <div class="gopay-tools">
                <button class="gopay-tool" type="button" data-action="collapse" title="折叠">-</button>
                <button class="gopay-tool" type="button" data-action="close" title="关闭">×</button>
            </div>
            <div class="gopay-kicker"><span>Checkout Console</span><span class="gopay-status"><span class="gopay-status-text">${panelStatus}</span><span class="gopay-status-dot is-ok"></span></span></div>
            <div class="gopay-title">快捷支付中枢</div>
            <div class="gopay-subtitle">支付和 Token 集中处理</div>
        `;
        head.querySelector('[data-action="collapse"]').addEventListener("click", () => setCollapsed(container, true));
        head.querySelector('[data-action="close"]').addEventListener("click", () => setCollapsed(container, true));

        const body = document.createElement("div");
        body.className = "gopay-body";

        const actions = document.createElement("div");
        actions.className = "gopay-actions";

        const payBtn = makeRow(BTN_ID, "💸", "GoPay 支付", "印尼 IDR 方案", "gopay-primary");
        payBtn.addEventListener("click", () => pay(payBtn, PAYLOAD, "GoPay"));

        const paypalBtn = makeRow(PAYPAL_BTN_ID, "P", "PayPal", "德国 EUR", "gopay-paypal");
        paypalBtn.addEventListener("click", () => pay(paypalBtn, PAYLOAD_DE, "PayPal-DE"));

        const paypalEuBtn = makeRow(PAYPAL_EU_BTN_ID, "P", "PayPal", "欧区 EUR", "gopay-paypal");
        paypalEuBtn.addEventListener("click", () => pay(paypalEuBtn, PAYLOAD_EU, "PayPal-EU"));

        const paypalUkBtn = makeRow(PAYPAL_UK_BTN_ID, "P", "PayPal", "英国 GBP", "gopay-paypal");
        paypalUkBtn.addEventListener("click", () => pay(paypalUkBtn, PAYLOAD_GB, "PayPal-UK"));

        const tokenBtn = makeRow(TOKEN_BTN_ID, "🪪", "Token", "复制登录凭证", "gopay-token");
        tokenBtn.addEventListener("click", getToken);

        actions.appendChild(payBtn);
        actions.appendChild(paypalBtn);
        actions.appendChild(paypalEuBtn);
        actions.appendChild(paypalUkBtn);
        actions.appendChild(tokenBtn);

        body.appendChild(actions);
        container.appendChild(handle);
        container.appendChild(mini);
        container.appendChild(head);
        container.appendChild(body);

        setCollapsed(container, localStorage.getItem(COLLAPSED_KEY) === "1");

        const tryMount = () => {
            if (document.body) {
                if (!$(CONTAINER_ID)) {
                    document.body.appendChild(container);
                    makeDraggable(container, handle);
                    setPanelStatus(panelStatus, "ok");
                }
            } else {
                setTimeout(tryMount, 50);
            }
        };

        tryMount();
    }

    function sync() {
        fixTranslations();
        silenceKnownIntlWarning();

        if (!inCheckout()) {
            $(CONTAINER_ID)?.remove();
            $(TIP_ID)?.remove();
            return;
        }

        if (!$(CONTAINER_ID)) showButton();
    }

    for (const method of ["pushState", "replaceState"]) {
        const original = history[method];
        history[method] = function (...args) {
            const result = original.apply(this, args);
            sync();
            return result;
        };
    }

    window.addEventListener("popstate", sync);
    window.addEventListener("DOMContentLoaded", sync);

    let rafId = null;
    const observer = new MutationObserver(() => {
        if (rafId) return;
        rafId = requestAnimationFrame(() => {
            rafId = null;
            sync();
        });
    });

    observer.observe(document.documentElement, { childList: true, subtree: true });

    sync();
})();
