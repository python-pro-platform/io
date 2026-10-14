#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram OSINT — Dotbhai Toolkit [FULL EDITION]
سحب كل المعلومات المتاحة عن أي حساب إنستجرام عام
"""

import re
import json
import sys
import time
import hashlib
from datetime import datetime
from urllib.parse import quote

import requests


# ═══════════════════════════════════════════════════════════
# ثوابت وإعدادات
# ═══════════════════════════════════════════════════════════
UA_DESKTOP = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/124.0.0.0 Safari/537.36")

UA_MOBILE  = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) "
              "AppleWebKit/605.1.15 (KHTML, like Gecko) "
              "Version/17.4 Mobile/15E148 Safari/604.1")

UA_ANDROID = ("Instagram 219.0.0.12.117 Android "
              "(30/11; 420dpi; 1080x2340; samsung; SM-G991B; o1s; exynos2100; en_US; 341542721)")

APP_ID     = "936619743392459"

BASE_HEADERS = {
    "User-Agent": UA_DESKTOP,
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
    "X-IG-App-ID": APP_ID,
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://www.instagram.com",
    "Referer": "https://www.instagram.com/",
    "X-ASBD-ID": "129477",
    "X-IG-WWW-Claim": "0",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}


# ═══════════════════════════════════════════════════════════
# أنماط الاستخراج
# ═══════════════════════════════════════════════════════════
EMAIL_RE    = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_RE    = re.compile(r"\+?\d[\d\s\-\(\)]{7,}\d")
URL_RE      = re.compile(r"https?://[^\s\"'<>\)]+")
HASHTAG_RE  = re.compile(r"#([\w\u0600-\u06FF]+)")
MENTION_RE  = re.compile(r"@([A-Za-z0-9._]+)")
CRYPTO_RE   = re.compile(r"\b(0x[a-fA-F0-9]{40}|bc1[a-z0-9]{25,62}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})\b")


# ═══════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════
def safe_get(url, headers=None, cookies=None, timeout=15):
    try:
        r = requests.get(url, headers=headers or BASE_HEADERS,
                         cookies=cookies, timeout=timeout, allow_redirects=True)
        return r
    except requests.RequestException as e:
        print(f"  \033[93m[!]\033[0m فشل الطلب: {e}")
        return None


def parse_count(text):
    if not text:
        return 0
    text = str(text).lower().replace(",", "").strip()
    try:
        if text.endswith("k"):
            return int(float(text[:-1]) * 1_000)
        if text.endswith("m"):
            return int(float(text[:-1]) * 1_000_000)
        if text.endswith("b"):
            return int(float(text[:-1]) * 1_000_000_000)
        return int(float(text))
    except ValueError:
        return 0


def ts_to_str(ts):
    if not ts:
        return None
    try:
        return datetime.utcfromtimestamp(int(ts)).isoformat() + "Z"
    except Exception:
        return str(ts)


def hash_id(value):
    """يعمل hash صغير للـ IDs لملفات الأمان."""
    if not value:
        return None
    return hashlib.md5(str(value).encode()).hexdigest()[:12]


def parse_username_input(raw):
    """يقبل يوزرنيم أو رابط كامل ويرجّع اليوزرنيم النظيف."""
    if not raw:
        return None
    raw = raw.strip()

    if "instagram.com" in raw.lower():
        m = re.search(r"instagram\.com/([^/?#]+)", raw, re.I)
        if m:
            username = m.group(1)
        else:
            return None
    else:
        username = raw.lstrip("@")

    username = username.strip().strip("/").split("?")[0].split("#")[0]

    if not re.match(r"^[A-Za-z0-9._]{1,30}$", username):
        return None

    reserved = {"p", "reel", "reels", "explore", "stories", "tv",
                "accounts", "direct", "web", "developer"}
    if username.lower() in reserved:
        return None

    return username


# ═══════════════════════════════════════════════════════════
# [1] web_profile_info — البيانات الأساسية
# ═══════════════════════════════════════════════════════════
def api_web_profile_info(username, cookies=None):
    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={quote(username)}"
    headers = {**BASE_HEADERS, "User-Agent": UA_MOBILE}
    r = safe_get(url, headers=headers, cookies=cookies)
    if not r or r.status_code != 200:
        return None
    try:
        return r.json()
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════
# [2] HTML scraping fallback
# ═══════════════════════════════════════════════════════════
def scrape_html(username, cookies=None):
    url = f"https://www.instagram.com/{quote(username)}/"
    headers = {**BASE_HEADERS, "User-Agent": UA_DESKTOP}
    r = safe_get(url, headers=headers, cookies=cookies)
    if not r or r.status_code != 200:
        return None

    html = r.text
    data = {
        "profile_url": url,
        "html_size": len(html),
    }

    m = re.search(r'<meta\s+property="og:image"\s+content="([^"]+)"', html)
    if m:
        data["profile_pic_hd"] = m.group(1).replace("&amp;", "&")

    m = re.search(r'<meta\s+property="og:description"\s+content="([^"]+)"', html)
    if m:
        desc = m.group(1).replace("&amp;", "&").replace("&#x27;", "'")
        data["og_description"] = desc
        fm = re.search(r"([\d.,KMB]+)\s+Followers", desc, re.I)
        if fm:
            data["followers"] = parse_count(fm.group(1))
        pm = re.search(r"([\d.,KMB]+)\s+Posts", desc, re.I)
        if pm:
            data["posts"] = parse_count(pm.group(1))
        fol = re.search(r"([\d.,KMB]+)\s+Following", desc, re.I)
        if fol:
            data["following"] = parse_count(fol.group(1))

    m = re.search(r"<title>([^<]+)</title>", html)
    if m:
        title = m.group(1)
        data["html_title"] = title
        nm = re.search(r"^(.+?)\s+\(@" + re.escape(username) + r"\)", title)
        if nm:
            data["full_name"] = nm.group(1).strip()

    m = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', html)
    if m:
        data["meta_description"] = m.group(1).replace("&amp;", "&")

    # استخراج JSON المدفون
    m = re.search(r'window\._sharedData\s*=\s*({.+?});</script>', html, re.S)
    if m:
        try:
            shared = json.loads(m.group(1))
            entry = shared.get("entry_data", {}).get("ProfilePage", [])
            if entry:
                u = entry[0].get("graphql", {}).get("user", {})
                if u:
                    data["_graphql_user"] = u
        except Exception:
            pass

    # محاولة استخراج الـ user id من الـ HTML
    m = re.search(r'"user_id":"(\d+)"', html)
    if m:
        data["user_id_from_html"] = m.group(1)
    else:
        m = re.search(r'"profile_id":"(\d+)"', html)
        if m:
            data["user_id_from_html"] = m.group(1)

    # الـ JSON المدفون في new IG (بيكون اسمه __additionalDataLoaded)
    m = re.search(r'window\.__additionalDataLoaded\s*\(\s*[^,]+,\s*({.+?})\s*\);\s*</script>', html, re.S)
    if m:
        try:
            loaded = json.loads(m.group(1))
            if "graphql" in loaded:
                data["_additional_graphql"] = loaded["graphql"]
        except Exception:
            pass

    return data


# ═══════════════════════════════════════════════════════════
# [3] من الجراف كيوري — بيانات موسّعة
# ═══════════════════════════════════════════════════════════
def api_graphql(username, cookies=None):
    """
    محاولة عبر GraphQL العام.
    """
    url = "https://www.instagram.com/graphql/query/"
    headers = {**BASE_HEADERS, "Content-Type": "application/x-www-form-urlencoded"}
    params = {
        "query_hash": "c9100bf9110dd6361671b264e3762a2a",
        "variables": json.dumps({"username": username, "first": 50})
    }
    r = safe_get(url + "?" + "&".join(f"{k}={quote(str(v))}" for k, v in params.items()),
                 headers=headers, cookies=cookies)
    if not r or r.status_code != 200:
        return None
    try:
        return r.json()
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════
# [4] البوستات
# ═══════════════════════════════════════════════════════════
def extract_posts(profile_json):
    if not profile_json:
        return None
    try:
        edges = (profile_json.get("data", {})
                    .get("user", {})
                    .get("edge_owner_to_timeline_media", {})
                    .get("edges", []))
        posts = []
        for e in edges:
            n = e.get("node", {})
            caption = ""
            cedges = n.get("edge_media_to_caption", {}).get("edges", [])
            if cedges:
                caption = cedges[0].get("node", {}).get("text", "")

            hashtags = HASHTAG_RE.findall(caption)
            mentions = MENTION_RE.findall(caption)

            posts.append({
                "shortcode": n.get("shortcode"),
                "url": f"https://www.instagram.com/p/{n.get('shortcode')}/" if n.get("shortcode") else None,
                "id": n.get("id"),
                "is_video": n.get("is_video", False),
                "is_pinned": n.get("pinned_for_users") not in (None, []) if "pinned_for_users" in n else False,
                "likes": n.get("edge_liked_by", {}).get("count", 0),
                "comments_count": n.get("edge_media_to_comment", {}).get("count", 0),
                "views": n.get("video_view_count"),
                "play_count": n.get("video_play_count"),
                "caption": caption,
                "hashtags": hashtags,
                "mentions": mentions,
                "location": (n.get("location") or {}).get("name") if n.get("location") else None,
                "taken_at": n.get("taken_at_timestamp"),
                "taken_at_str": ts_to_str(n.get("taken_at_timestamp")),
                "display_url": n.get("display_url"),
                "thumbnail": n.get("thumbnail_src"),
                "dimensions": n.get("dimensions"),
                "accessibility_caption": n.get("accessibility_caption"),
                "comments_disabled": n.get("comments_disabled", False),
            })
        return posts
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════
# [5] الـ highlights
# ═══════════════════════════════════════════════════════════
def extract_highlights(profile_json):
    if not profile_json:
        return None
    try:
        user = profile_json.get("data", {}).get("user", {})
        edges = user.get("edge_highlight_reels", {}).get("edges", [])
        highlights = []
        for e in edges:
            n = e.get("node", {})
            highlights.append({
                "id": n.get("id"),
                "title": n.get("title"),
                "cover": n.get("cover_media", {}).get("thumbnail_src") or n.get("cover_media_cropped_thumbnail", {}).get("url"),
                "count": n.get("edge_highlight_reels", {}).get("count") if "edge_highlight_reels" in n else None,
            })
        return highlights
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════
# [6] الحسابات المشابهة (Suggested)
# ═══════════════════════════════════════════════════════════
def api_suggested(user_id, cookies=None):
    if not user_id:
        return None
    url = f"https://i.instagram.com/api/v1/discover/chaining/?target_id={user_id}"
    headers = {**BASE_HEADERS, "User-Agent": UA_MOBILE}
    r = safe_get(url, headers=headers, cookies=cookies)
    if not r or r.status_code != 200:
        return None
    try:
        return r.json()
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════
# [7] العلاقة مع الحساب — mutual followers
# ═══════════════════════════════════════════════════════════
def api_mutual(user_id, cookies=None):
    if not user_id:
        return None
    url = f"https://i.instagram.com/api/v1/friendships/show/{user_id}/"
    headers = {**BASE_HEADERS, "User-Agent": UA_MOBILE}
    r = safe_get(url, headers=headers, cookies=cookies)
    if not r or r.status_code != 200:
        return None
    try:
        return r.json()
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════
# [8] معلومات الحساب عبر i.instagram — تفاصيل إضافية
# ═══════════════════════════════════════════════════════════
def api_user_info(username, cookies=None):
    url = f"https://i.instagram.com/api/v1/users/{quote(username)}/usernameinfo/"
    headers = {**BASE_HEADERS, "User-Agent": UA_MOBILE}
    r = safe_get(url, headers=headers, cookies=cookies)
    if not r or r.status_code != 200:
        return None
    try:
        return r.json()
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════
# [9] info عن الحساب عبر lookup
# ═══════════════════════════════════════════════════════════
def api_lookup(user_id, cookies=None):
    if not user_id:
        return None
    url = f"https://i.instagram.com/api/v1/users/{user_id}/info/"
    headers = {**BASE_HEADERS, "User-Agent": UA_MOBILE}
    r = safe_get(url, headers=headers, cookies=cookies)
    if not r or r.status_code != 200:
        return None
    try:
        return r.json()
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════
# [10] Story highlights via reels_media
# ═══════════════════════════════════════════════════════════
def api_reels_media(user_id, cookies=None):
    if not user_id:
        return None
    url = f"https://i.instagram.com/api/v1/feed/reels_media/?reel_ids={user_id}"
    headers = {**BASE_HEADERS, "User-Agent": UA_MOBILE}
    r = safe_get(url, headers=headers, cookies=cookies)
    if not r or r.status_code != 200:
        return None
    try:
        return r.json()
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════
# [11] استخراج PII من النصوص
# ═══════════════════════════════════════════════════════════
def extract_pii(bio, posts=None, external_url=None, extra_text=""):
    blob = " ".join(filter(None, [bio, external_url, extra_text]))
    if posts:
        for p in posts:
            blob += " " + (p.get("caption") or "")

    emails   = list(set(EMAIL_RE.findall(blob)))
    phones   = list(set(PHONE_RE.findall(blob)))
    urls     = list(set(URL_RE.findall(blob)))
    hashtags = list(set(HASHTAG_RE.findall(blob)))
    mentions = list(set(MENTION_RE.findall(blob)))
    crypto   = list(set(CRYPTO_RE.findall(blob)))

    phones = [p for p in phones if len(re.sub(r"\D", "", p)) >= 8]

    return {
        "emails":   emails,
        "phones":   phones,
        "urls":     urls,
        "hashtags": hashtags[:50],
        "mentions": mentions[:50],
        "crypto_wallets": crypto,
    }


# ═══════════════════════════════════════════════════════════
# [12] تحليل الـ bio links
# ═══════════════════════════════════════════════════════════
def expand_links(links):
    """يحاول يفتح كل لينك ويعرف عنوانه وهو بيودّي فين."""
    out = []
    for link in links:
        if not link:
            continue
        try:
            r = requests.head(link, timeout=8, allow_redirects=True,
                              headers={"User-Agent": UA_DESKTOP})
            out.append({
                "url": link,
                "final_url": r.url,
                "status": r.status_code,
                "server": r.headers.get("Server"),
                "content_type": r.headers.get("Content-Type"),
            })
        except Exception:
            out.append({"url": link, "error": "unreachable"})
    return out


# ═══════════════════════════════════════════════════════════
# [13] الإحصائيات المحسوبة
# ═══════════════════════════════════════════════════════════
def compute_stats(info, posts):
    if not posts:
        return {}
    likes    = [p["likes"] for p in posts if p.get("likes") is not None]
    comments = [p["comments_count"] for p in posts if p.get("comments_count") is not None]
    followers = info.get("followers", 0) or 0

    # أفضل بوست
    top_liked = max(posts, key=lambda p: p.get("likes", 0), default=None)
    top_commented = max(posts, key=lambda p: p.get("comments_count", 0), default=None)

    # توزيع حسب النوع
    videos = sum(1 for p in posts if p.get("is_video"))
    images = len(posts) - videos

    # توزيع الوقت
    hours = {}
    for p in posts:
        ts = p.get("taken_at")
        if ts:
            h = datetime.utcfromtimestamp(ts).hour
            hours[h] = hours.get(h, 0) + 1
    best_hour = max(hours, key=hours.get) if hours else None

    # معدل التفاعل
    engagement_rate = 0
    if followers and posts:
        total = sum(likes) + sum(comments)
        engagement_rate = round(total / followers * 100 / len(posts), 3)

    return {
        "avg_likes":    round(sum(likes) / len(likes), 1) if likes else 0,
        "avg_comments": round(sum(comments) / len(comments), 1) if comments else 0,
        "max_likes":    max(likes) if likes else 0,
        "max_comments": max(comments) if comments else 0,
        "min_likes":    min(likes) if likes else 0,
        "min_comments": min(comments) if comments else 0,
        "total_likes":  sum(likes),
        "total_comments": sum(comments),
        "posts_sampled": len(posts),
        "videos": videos,
        "images": images,
        "best_post_hour_utc": best_hour,
        "engagement_rate_pct": engagement_rate,
        "top_liked_post": {
            "url": top_liked.get("url"),
            "likes": top_liked.get("likes"),
        } if top_liked else None,
        "top_commented_post": {
            "url": top_commented.get("url"),
            "comments": top_commented.get("comments_count"),
        } if top_commented else None,
    }


# ═══════════════════════════════════════════════════════════
# [14] Harvest — تجميع كل شيء
# ═══════════════════════════════════════════════════════════
def harvest(username, cookies=None):
    print(f"\n\033[95m{'═' * 66}\033[0m")
    print(f"  \033[1;93mInstagram OSINT — @{username}\033[0m")
    print(f"\033[95m{'═' * 66}\033[0m\n")

    result = {
        "username": username,
        "scraped_at": datetime.utcnow().isoformat() + "Z",
        "sources_used": [],
    }

    # ── [1] web_profile_info ──
    print("  \033[96m[1/9]\033[0m web_profile_info API...")
    prof = api_web_profile_info(username, cookies)
    user = None
    if prof and prof.get("data", {}).get("user"):
        user = prof["data"]["user"]
        result["sources_used"].append("web_profile_info")
        print("       \033[92m✓\033[0m نجح")

    # ── [2] HTML ──
    print("  \033[96m[2/9]\033[0m HTML scraping...")
    html_data = scrape_html(username, cookies)
    if html_data:
        result["html_fallback"] = html_data
        result["sources_used"].append("html_scrape")
        print("       \033[92m✓\033[0m نجح")

    # فحص النتيجة
    if not user and not html_data:
        result["ok"] = False
        print("\n  \033[91m[!]\033[0m الحساب مش موجود أو محجوب أو rate limit.\n")
        return result

    result["ok"] = True

    # ── [3] تفاصيل موسّعة من web_profile_info ──
    if user:
        info = {
            "id":               user.get("id"),
            "id_hashed":        hash_id(user.get("id")),
            "username":         user.get("username"),
            "full_name":        user.get("full_name"),
            "biography":        user.get("biography"),
            "bio_hashtags":     HASHTAG_RE.findall(user.get("biography") or ""),
            "bio_mentions":     MENTION_RE.findall(user.get("biography") or ""),
            "bio_emails":       EMAIL_RE.findall(user.get("biography") or ""),
            "bio_phones":       PHONE_RE.findall(user.get("biography") or ""),
            "external_url":     user.get("external_url"),
            "external_url_lynx": user.get("external_url_linkshimmed"),
            "is_private":       user.get("is_private"),
            "is_verified":      user.get("is_verified"),
            "is_business":      user.get("is_business_account"),
            "is_professional":  user.get("is_professional_account"),
            "business_category": user.get("business_category_name") or user.get("category_name"),
            "business_email":   user.get("business_email"),
            "business_phone":   user.get("business_phone_number"),
            "business_address": user.get("business_address_json"),
            "business_contact": user.get("business_contact_method"),
            "pronouns":         user.get("pronouns"),
            "profile_pic_hd":   user.get("profile_pic_url_hd"),
            "profile_pic":      user.get("profile_pic_url"),
            "has_clips":        user.get("has_clips"),
            "has_channel":      user.get("has_channel"),
            "has_guides":       user.get("has_guides"),
            "hide_like_view":   user.get("hide_like_and_view_counts"),
            "country_block":    user.get("country_block"),
            "followers":        user.get("edge_followed_by", {}).get("count", 0),
            "following":        user.get("edge_follow", {}).get("count", 0),
            "posts_count":      user.get("edge_owner_to_timeline_media", {}).get("count", 0),
            "igtv_count":       user.get("edge_felix_video_timeline", {}).get("count", 0),
            "highlights_count": user.get("highlight_reel_count"),
            "mutual_followers": user.get("edge_mutual_followed_by", {}).get("count"),
            "followed_by_viewer": user.get("followed_by_viewer"),
            "follows_viewer":   user.get("follows_viewer"),
            "requested_by_viewer": user.get("requested_by_viewer"),
            "blocked_by_viewer": user.get("blocked_by_viewer"),
            "restricted_by_viewer": user.get("restricted_by_viewer"),
        }

        # bio links
        bio_links = user.get("bio_links") or []
        if bio_links:
            info["bio_links"] = [
                {"url": b.get("url"), "lynx_url": b.get("lynx_url"),
                 "link_type": b.get("link_type"), "title": b.get("title")}
                for b in bio_links
            ]

        # business details
        if user.get("business_address_json"):
            info["business_address"] = user.get("business_address_json")

        result["info"] = info

    # ── [4] البوستات ──
    print("  \033[96m[3/9]\033[0m سحب البوستات...")
    posts = extract_posts(prof)
    if posts:
        result["recent_posts"] = posts
        print(f"       \033[92m✓\033[0m {len(posts)} بوست")

    # ── [5] الـ highlights ──
    print("  \033[96m[4/9]\033[0m سحب الـ highlights...")
    highlights = extract_highlights(prof)
    if highlights:
        result["highlights"] = highlights
        print(f"       \033[92m✓\033[0m {len(highlights)} highlight")
    else:
        print("       \033[93m— مفيش\033[0m")

    # ── [6] الحسابات المشابهة ──
    user_id = None
    if user:
        user_id = user.get("id")
    elif html_data:
        user_id = html_data.get("user_id_from_html")

    if user_id:
        print("  \033[96m[5/9]\033[0m سحب الحسابات المقترحة...")
        suggested = api_suggested(user_id, cookies)
        if suggested and suggested.get("users"):
            result["suggested_users"] = [
                {
                    "id": u.get("pk") or u.get("pk_id"),
                    "username": u.get("username"),
                    "full_name": u.get("full_name"),
                    "is_private": u.get("is_private"),
                    "is_verified": u.get("is_verified"),
                    "profile_pic": u.get("profile_pic_url"),
                    "followed_by_viewer": u.get("followed_by_viewer"),
                }
                for u in suggested["users"][:30]
            ]
            print(f"       \033[92m✓\033[0m {len(result['suggested_users'])} حساب")

        # ── [7] العلاقة ──
        print("  \033[96m[6/9]\033[0m العلاقة مع الحساب...")
        mut = api_mutual(user_id, cookies)
        if mut and mut.get("status") == "ok":
            result["relationship"] = {
                "following": mut.get("following"),
                "followed_by": mut.get("followed_by"),
                "incoming_request": mut.get("incoming_request"),
                "outgoing_request": mut.get("outgoing_request"),
                "blocking": mut.get("blocking"),
                "muting": mut.get("muting"),
            }
            print("       \033[92m✓\033[0m نجح")

        # ── [8] reels_media ──
        print("  \033[96m[7/9]\033[0m Stories / Reels media...")
        reels = api_reels_media(user_id, cookies)
        if reels and reels.get("reels"):
            reels_data = reels["reels"].get(str(user_id), {})
            items = reels_data.get("items", [])
            result["stories"] = [
                {
                    "id": it.get("id"),
                    "taken_at": ts_to_str(it.get("taken_at")),
                    "media_type": it.get("media_type"),
                    "is_video": it.get("media_type") == 2,
                    "image_url": (it.get("image_versions2", {})
                                    .get("candidates", [{}])[0]
                                    .get("url")) if it.get("image_versions2") else None,
                    "video_url": (it.get("video_versions", [{}])[0]
                                    .get("url")) if it.get("video_versions") else None,
                    "expiring_at": ts_to_str(it.get("expiring_at")),
                }
                for it in items
            ]
            print(f"       \033[92m✓\033[0m {len(result['stories'])} story")

        # ── [9] user info تفصيلي ──
        print("  \033[96m[8/9]\033[0m تفاصيل الحساب من i.instagram...")
        uinfo = api_user_info(username, cookies)
        if uinfo and uinfo.get("user"):
            u = uinfo["user"]
            result["user_detail"] = {
                "pk": u.get("pk"),
                "username": u.get("username"),
                "full_name": u.get("full_name"),
                "biography": u.get("biography"),
                "external_url": u.get("external_url"),
                "is_private": u.get("is_private"),
                "is_verified": u.get("is_verified"),
                "is_business": u.get("is_business"),
                "account_type": u.get("account_type"),
                "category": u.get("category"),
                "should_show_category": u.get("should_show_category"),
                "contact_phone_number": u.get("contact_phone_number"),
                "public_email": u.get("public_email"),
                "public_phone_number": u.get("public_phone_number"),
                "public_phone_country_code": u.get("public_phone_country_code"),
                "address_street": u.get("address_street"),
                "city_id": u.get("city_id"),
                "city_name": u.get("city_name"),
                "zip": u.get("zip"),
                "latitude": u.get("latitude"),
                "longitude": u.get("longitude"),
                "follower_count": u.get("follower_count"),
                "following_count": u.get("following_count"),
                "media_count": u.get("media_count"),
                "total_igtv_videos": u.get("total_igtv_videos"),
                "total_clips_count": u.get("total_clips_count"),
                "has_igtv_series": u.get("has_igtv_series"),
                "is_eligible_for_creator_ai": u.get("is_eligible_for_creator_ai"),
                "creator_ai_countries": u.get("creator_ai_countries"),
                "is_memorialized": u.get("is_memorialized"),
                "is_new": u.get("is_new"),
                "is_whatsapp_linked": u.get("is_whatsapp_linked"),
                "profile_pic_url_hd": u.get("hd_profile_pic_url_info", {}).get("url") or u.get("profile_pic_url"),
                "profile_pic_url": u.get("profile_pic_url"),
                "pronouns": u.get("pronouns"),
                "has_anonymous_profile_picture": u.get("has_anonymous_profile_picture"),
                "has_highlight_reels": u.get("has_highlight_reels"),
                "has_guides": u.get("has_guides"),
                "show_ig_app_switcher_badge": u.get("show_ig_app_switcher_badge"),
                "show_text_post_app_badge": u.get("show_text_post_app_badge"),
                "is_interest_account": u.get("is_interest_account"),
                "is_eligible_for_content_scheduling": u.get("is_eligible_for_content_scheduling"),
                "latest_reel_media": u.get("latest_reel_media"),
                "reel_media_seen_at": u.get("reel_media_seen_at"),
            }
            print("       \033[92m✓\033[0m نجح")

    # ── الحسابات المجمعة ──
    print("  \033[96m[9/9]\033[0m تحليل واستخراج...")
    info = result.get("info", {})
    posts_list = result.get("recent_posts") or []
    extra_text = " ".join([
        info.get("business_email") or "",
        info.get("business_phone") or "",
        info.get("business_address") or "",
    ])
    bio = (info.get("biography") or
           result.get("html_fallback", {}).get("meta_description") or "")
    ext = info.get("external_url")

    result["extracted"] = extract_pii(bio, posts_list, ext, extra_text)

    # الحسابات المشابهة من HTML (احتياطي)
    if result.get("suggested_users"):
        result["extracted"]["suggested_usernames"] = [
            u["username"] for u in result["suggested_users"]
        ]

    result["stats"] = compute_stats(info, posts_list)

    # وسّع اللينكات
    all_links = list(set(
        result["extracted"].get("urls", []) +
        [b["url"] for b in info.get("bio_links", []) if b.get("url")]
    ))[:15]
    if all_links:
        result["expanded_links"] = expand_links(all_links)

    return result


# ═══════════════════════════════════════════════════════════
# الطباعة المنسّقة
# ═══════════════════════════════════════════════════════════
def pretty_print(result):
    info = result.get("info", {})
    stats = result.get("stats", {})
    ext = result.get("extracted", {})
    posts = result.get("recent_posts") or []
    detail = result.get("user_detail", {})

    def row(label, value):
        if value in (None, "", [], {}, False):
            return
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        print(f"  \033[96m{label:22}\033[0m {value}")

    # ═══ الهوية ═══
    print(f"\n\033[95m{'═' * 66}\033[0m")
    print(f"  \033[1;93mالنتيجة — @{result.get('username')}\033[0m")
    print(f"\033[95m{'═' * 66}\033[0m")

    print(f"\n  \033[93m── الهوية ──\033[0m")
    row("ID:", info.get("id"))
    row("ID (hashed):", info.get("id_hashed"))
    row("Username:", info.get("username"))
    row("Full Name:", info.get("full_name"))
    row("Pronouns:", info.get("pronouns"))
    row("Biography:", info.get("biography"))
    row("External URL:", info.get("external_url"))
    row("External URL (lynx):", info.get("external_url_lynx"))
    row("Profile Pic HD:", info.get("profile_pic_hd"))

    # ═══ الحالة ═══
    print(f"\n  \033[93m── الحالة ──\033[0m")
    row("Private:", info.get("is_private"))
    row("Verified:", info.get("is_verified"))
    row("Business:", info.get("is_business"))
    row("Professional:", info.get("is_professional"))
    row("Category:", info.get("business_category"))
    row("Country Block:", info.get("country_block"))
    row("Hide Likes:", info.get("hide_like_view"))
    row("Memorialized:", detail.get("is_memorialized"))

    # ═══ الأرقام ═══
    print(f"\n  \033[93m── الأرقام ──\033[0m")
    row("Followers:",  info.get("followers"))
    row("Following:",  info.get("following"))
    row("Posts:",      info.get("posts_count"))
    row("IGTV:",       info.get("igtv_count"))
    row("Highlights:", info.get("highlights_count"))
    row("Mutual Followers:", info.get("mutual_followers"))

    # ═══ Business ═══
    if detail.get("public_email") or detail.get("public_phone_number") or \
       info.get("business_email") or info.get("business_phone") or detail.get("city_name"):
        print(f"\n  \033[93m── معلومات Business ──\033[0m")
        row("Business Email:", info.get("business_email") or detail.get("public_email"))
        row("Business Phone:", info.get("business_phone") or detail.get("public_phone_number"))
        row("Phone Country:", detail.get("public_phone_country_code"))
        row("Category:", info.get("business_category") or detail.get("category"))
        row("Address:", detail.get("address_street"))
        row("City:", detail.get("city_name"))
        row("ZIP:", detail.get("zip"))
        row("Latitude:", detail.get("latitude"))
        row("Longitude:", detail.get("longitude"))

    # ═══ الإحصائيات ═══
    if stats:
        print(f"\n  \033[93m── الإحصائيات ──\033[0m")
        row("Avg Likes:",    stats.get("avg_likes"))
        row("Avg Comments:", stats.get("avg_comments"))
        row("Max Likes:",    stats.get("max_likes"))
        row("Max Comments:", stats.get("max_comments"))
        row("Min Likes:",    stats.get("min_likes"))
        row("Total Likes:",  stats.get("total_likes"))
        row("Total Comments:", stats.get("total_comments"))
        row("Videos/Images:", f"{stats.get('videos')}/{stats.get('images')}")
        row("Best Hour UTC:", stats.get("best_post_hour_utc"))
        row("Engagement %:", stats.get("engagement_rate_pct"))

        if stats.get("top_liked_post"):
            print(f"\n  \033[96mTop Liked Post:\033[0m {stats['top_liked_post'].get('url')} — {stats['top_liked_post'].get('likes')} likes")
        if stats.get("top_commented_post"):
            print(f"  \033[96mTop Commented Post:\033[0m {stats['top_commented_post'].get('url')} — {stats['top_commented_post'].get('comments')} comments")

    # ═══ استخراج PII ═══
    if ext:
        print(f"\n  \033[93m── استخراج (PII / روابط) ──\033[0m")
        for k in ("emails", "phones", "crypto_wallets", "hashtags", "mentions", "urls"):
            v = ext.get(k)
            if v:
                print(f"  \033[96m{k:14}\033[0m {', '.join(map(str, v[:15]))}")

    # ═══ bio links ═══
    if info.get("bio_links"):
        print(f"\n  \033[93m── روابط البايو ──\033[0m")
        for b in info["bio_links"]:
            print(f"  • {b.get('url')}")

    # ═══ البوستات ═══
    if posts:
        print(f"\n  \033[93m── آخر {min(len(posts), 8)} بوست ──\033[0m")
        for i, p in enumerate(posts[:8], 1):
            kind = "🎬" if p.get("is_video") else "🖼"
            caption = (p.get("caption") or "").split("\n")[0][:60]
            print(f"  {i}. {kind} {p['url']}")
            print(f"     ❤ {p['likes']}  💬 {p['comments_count']}  📅 {p['taken_at_str']}")
            if caption:
                print(f"     \"{caption}\"")

    # ═══ highlights ═══
    if result.get("highlights"):
        print(f"\n  \033[93m── Highlights ({len(result['highlights'])}) ──\033[0m")
        for h in result["highlights"][:10]:
            print(f"  • {h.get('title')}  →  {h.get('cover')}")

    # ═══ suggested users ═══
    if result.get("suggested_users"):
        print(f"\n  \033[93m── حسابات مشابهة ({len(result['suggested_users'])}) ──\033[0m")
        names = [u["username"] for u in result["suggested_users"][:20]]
        print(f"  {', '.join(names)}")

    # ═══ stories ═══
    if result.get("stories"):
        print(f"\n  \033[93m── Stories حالية ({len(result['stories'])}) ──\033[0m")
        for s in result["stories"][:6]:
            print(f"  • {s.get('image_url') or s.get('video_url')}  (expires {s.get('expiring_at')})")

    # ═══ expanded links ═══
    if result.get("expanded_links"):
        print(f"\n  \033[93m── تحليل الروابط ──\033[0m")
        for lk in result["expanded_links"][:8]:
            print(f"  • {lk.get('url')}")
            if lk.get("final_url"):
                print(f"     → {lk.get('final_url')}")
            if lk.get("server"):
                print(f"     server: {lk.get('server')}")

    # ═══ المصادر ═══
    if result.get("sources_used"):
        print(f"\n  \033[93m── المصادر ──\033[0m")
        print(f"  {', '.join(result['sources_used'])}")

    print(f"\n\033[95m{'═' * 66}\033[0m\n")


def save_json(result, path=None):
    if not path:
        path = f"insta_{result['username']}_{int(datetime.now().timestamp())}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"  \033[92m[+]\033[0m تم الحفظ في: \033[93m{path}\033[0m\n")


# ═══════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════
def main():
    print("\n\033[95m" + "═" * 66 + "\033[0m")
    print("  \033[1;93mInstagram OSINT — Dotbhai Toolkit [FULL]\033[0m")
    print("\033[95m" + "═" * 66 + "\033[0m")
    print("  اكتب يوزرنيم الحساب أو الرابط الكامل.")
    print("  \033[96mأمثلة:\033[0m cristiano  |  @cristiano  |  https://instagram.com/cristiano/")
    print("\033[95m" + "═" * 66 + "\033[0m\n")

    while True:
        raw = input("\033[93m>>\033[0m اليوزرنيم أو الرابط: ").strip()
        if not raw:
            print("  \033[91m[!]\033[0m ما كتبتش حاجة.\n")
            continue
        username = parse_username_input(raw)
        if username:
            print(f"  \033[92m[+]\033[0m اليوزرنيم: \033[1;93m@{username}\033[0m\n")
            break
        else:
            print("  \033[91m[!]\033[0m المدخل غير صالح.\n")

    print("\033[96m[?]\033[0m sessionid اختياري (Enter لو مش عايز):")
    sid_input = input("\033[93m>>\033[0m ").strip()
    cookies = {"sessionid": sid_input} if sid_input else None
    if cookies:
        print("  \033[92m[+]\033[0m تم تسجيل الـ session.\n")

    result = harvest(username, cookies)
    pretty_print(result)

    if result.get("ok"):
        save_json(result)
    else:
        print("  \033[91m[!]\033[0m ما قدرتش أسحب بيانات.\n")


if __name__ == "__main__":
    main()
