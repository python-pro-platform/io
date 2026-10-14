#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFi Password Dumper — Dotbhai Toolkit
يستخرج كل شبكات الواي فاي المحفوظة على الجهاز مع الباسورد بتاعها
يدعم: Windows / Linux / macOS
"""

import os
import re
import sys
import json
import platform
import subprocess
from datetime import datetime

OS_NAME = platform.system().lower()


# ═══════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════
def run(cmd, shell=False):
    try:
        out = subprocess.check_output(
            cmd, shell=shell, stderr=subprocess.DEVNULL, timeout=30
        )
        return out.decode("utf-8", errors="ignore")
    except Exception as e:
        return ""


def is_admin():
    if OS_NAME == "windows":
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    else:
        return os.geteuid() == 0


# ═══════════════════════════════════════════════════════════
# Windows
# ═══════════════════════════════════════════════════════════
def windows_profiles():
    """يرجّع قائمة أسماء كل الـ profiles المحفوظة."""
    out = run(["netsh", "wlan", "show", "profiles"])
    if not out:
        return []
    profiles = re.findall(r"All User Profile\s*:\s*(.+)", out)
    if not profiles:
        # fallback للمناطق العربية
        profiles = re.findall(r"ملف تعريف المستخدم.*?:\s*(.+)", out)
    return [p.strip() for p in profiles if p.strip()]


def windows_password(profile_name):
    """يجيب الباسورد بتاع profile واحد."""
    out = run(["netsh", "wlan", "show", "profile",
               f"name={profile_name}", "key=clear"])
    if not out:
        return None, None

    password = None
    auth = None
    cipher = None

    # باسورد
    m = re.search(r"Key Content\s*:\s*(.+)", out)
    if m:
        password = m.group(1).strip()
    else:
        # fallback عربي
        m = re.search(r"محتوى المفتاح\s*:\s*(.+)", out)
        if m:
            password = m.group(1).strip()

    # نوع المصادقة
    m = re.search(r"Authentication\s*:\s*(.+)", out)
    if m:
        auth = m.group(1).strip()
    else:
        m = re.search(r"المصادقة\s*:\s*(.+)", out)
        if m:
            auth = m.group(1).strip()

    # التشفير
    m = re.search(r"Cipher\s*:\s*(.+)", out)
    if m:
        cipher = m.group(1).strip()
    else:
        m = re.search(r"التشفير\s*:\s*(.+)", out)
        if m:
            cipher = m.group(1).strip()

    return password, {"auth": auth, "cipher": cipher}


def dump_windows():
    profiles = windows_profiles()
    results = []
    for p in profiles:
        pw, meta = windows_password(p)
        results.append({
            "ssid": p,
            "password": pw if pw else "<open / hidden>",
            "auth": (meta or {}).get("auth"),
            "cipher": (meta or {}).get("cipher"),
        })
    return results


# ═══════════════════════════════════════════════════════════
# Linux
# ═══════════════════════════════════════════════════════════
def dump_linux():
    """
    الطريقة الأساسية: NetworkManager يخزن كل حاجة في
    /etc/NetworkManager/system-connections/*.nmconnection
    (محتاج root).
    """
    results = []

    if not is_admin():
        print("  \033[93m[!]\033[0m لازم تشغّل بـ sudo عشان تقرأ ملفات NM.")
        return results

    paths = [
        "/etc/NetworkManager/system-connections/",
        "/etc/NetworkManager/system-connections-encrypted/",
    ]

    for base in paths:
        if not os.path.isdir(base):
            continue
        for fname in os.listdir(base):
            path = os.path.join(base, fname)
            if not os.path.isfile(path):
                continue
            try:
                with open(path, "r", errors="ignore") as f:
                    content = f.read()
            except Exception:
                continue

            ssid_m = re.search(r"^ssid=(.+)$", content, re.M)
            psk_m  = re.search(r"^psk=(.+)$", content, re.M)
            key_mgmt_m = re.search(r"^key-mgmt=(.+)$", content, re.M)

            ssid = ssid_m.group(1).strip() if ssid_m else fname.replace(".nmconnection", "")
            psk  = psk_m.group(1).strip() if psk_m else "<open / none>"

            results.append({
                "ssid": ssid,
                "password": psk,
                "key_mgmt": key_mgmt_m.group(1).strip() if key_mgmt_m else None,
                "source": path,
            })

    # wpa_supplicant config (احتياطي)
    wpa_path = "/etc/wpa_supplicant/wpa_supplicant.conf"
    if os.path.isfile(wpa_path):
        try:
            with open(wpa_path, "r", errors="ignore") as f:
                content = f.read()
            networks = re.findall(r"network\s*=\s*\{([^}]+)\}", content, re.S)
            for net in networks:
                s = re.search(r'ssid\s*=\s*"([^"]+)"', net)
                p = re.search(r'psk\s*=\s*"([^"]+)"', net)
                if s:
                    results.append({
                        "ssid": s.group(1),
                        "password": p.group(1) if p else "<open / none>",
                        "key_mgmt": "WPA-PSK",
                        "source": wpa_path,
                    })
        except Exception:
            pass

    return results


# ═══════════════════════════════════════════════════════════
# macOS
# ═══════════════════════════════════════════════════════════
def dump_macos():
    """
    يستخدم security + airport لإيجاد كل الشبكات والباسورد من الـ Keychain.
    محتاج sudo لتجاوز نافذة الإذن لكل شبكة.
    """
    results = []
    if not is_admin():
        print("  \033[93m[!]\033[0m على ماك لازم تشغّل بـ sudo عشان الـ keychain يطلع الباسورد بدون برومبت.")

    # نحاول نلاقي كل الشبكات من الـ preferred networks
    pref_out = run([
        "/usr/libexec/PlistBuddy", "-c", "Print",
        "/Library/Preferences/SystemConfiguration/preferences.plist"
    ])
    # ماك مودرن شال airport، فبنستخدم بديل
    out = run(["networksetup", "-listpreferredwirelessnetworks", "en0"])
    ssids = re.findall(r"^\t(.+)$", out, re.M)

    if not ssids:
        # نجرب الـ interface الأولاني
        out_if = run(["networksetup", "-listallhardwareports"])
        m = re.search(r"Wi-Fi.*?Device:\s*(\w+)", out_if, re.S)
        if m:
            iface = m.group(1)
            out = run(["networksetup", "-listpreferredwirelessnetworks", iface])
            ssids = re.findall(r"^\t(.+)$", out, re.M)

    for ssid in ssids:
        ssid = ssid.strip()
        pw = run([
            "security", "find-generic-password",
            "-D", "AirPort network password",
            "-a", ssid, "-w"
        ]).strip()
        results.append({
            "ssid": ssid,
            "password": pw if pw else "<not found>",
        })

    return results


# ═══════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════
def banner():
    print("\n\033[95m" + "═" * 66 + "\033[0m")
    print("  \033[1;93mWiFi Password Dumper — Dotbhai Toolkit\033[0m")
    print("\033[95m" + "═" * 66 + "\033[0m")
    print(f"  \033[96mSystem:\033[0m {platform.system()} {platform.release()}")
    print(f"  \033[96mAdmin :\033[0m {is_admin()}")
    print("\033[95m" + "═" * 66 + "\033[0m\n")


def pretty_print(results):
    if not results:
        print("  \033[91m[!]\033[0m مفيش شبكات محفوظة على الجهاز.\n")
        return

    print(f"\n  \033[93m── شبكات الواي فاي المحفوظة ({len(results)}) ──\033[0m\n")
    for i, r in enumerate(results, 1):
        print(f"  \033[96m[{i}]\033[0m SSID: \033[1;93m{r['ssid']}\033[0m")
        print(f"      Password: \033[1;92m{r.get('password')}\033[0m")
        for k in ("auth", "cipher", "key_mgmt", "source"):
            if r.get(k):
                print(f"      {k}: {r[k]}")
        print()


def save_json(results, path=None):
    if not path:
        path = f"wifi_dump_{int(datetime.now().timestamp())}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "scraped_at": datetime.utcnow().isoformat() + "Z",
            "system": platform.system(),
            "networks": results,
        }, f, ensure_ascii=False, indent=2)
    print(f"  \033[92m[+]\033[0m تم الحفظ في: \033[93m{path}\033[0m\n")


def save_txt(results, path=None):
    if not path:
        path = f"wifi_dump_{int(datetime.now().timestamp())}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# WiFi Dump — {datetime.now().isoformat()}\n")
        f.write(f"# System: {platform.system()}\n\n")
        for r in results:
            f.write(f"SSID     : {r['ssid']}\n")
            f.write(f"Password : {r.get('password')}\n")
            if r.get("auth"):
                f.write(f"Auth     : {r['auth']}\n")
            if r.get("cipher"):
                f.write(f"Cipher   : {r['cipher']}\n")
            f.write("-" * 50 + "\n")
    print(f"  \033[92m[+]\033[0m تم الحفظ في: \033[93m{path}\033[0m\n")


def main():
    banner()

    if OS_NAME == "windows":
        results = dump_windows()
    elif OS_NAME == "linux":
        results = dump_linux()
    elif OS_NAME == "darwin":
        results = dump_macos()
    else:
        print("  \033[91m[!]\033[0m نظام مش مدعوم.\n")
        return

    pretty_print(results)

    if results:
        save_json(results)
        save_txt(results)

    # ملخص نهائي
    print("\033[95m" + "═" * 66 + "\033[0m")
    print(f"  \033[1;92mتم سحب {len(results)} شبكة\033[0m")
    print("\033[95m" + "═" * 66 + "\033[0m\n")


if __name__ == "__main__":
    main()
