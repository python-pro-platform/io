import os
import shutil

# المجلد الذي تريد ترتيبه
folder = os.path.expanduser("~/storage/downloads")

# تصنيفات الملفات
categories = {
    "صور": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    "فيديوهات": [".mp4", ".mkv", ".avi", ".mov"],
    "موسيقى": [".mp3", ".wav", ".m4a", ".flac"],
    "مستندات": [".pdf", ".doc", ".docx", ".txt"],
    "ملفات_مضغوطة": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "برامج": [".apk", ".exe"],
}

def get_category(filename):
    extension = os.path.splitext(filename)[1].lower()

    for category, extensions in categories.items():
        if extension in extensions:
            return category

    return "أخرى"


def organize():
    if not os.path.exists(folder):
        print("❌ مجلد Downloads غير موجود")
        print("شغّل:")
        print("termux-setup-storage")
        return

    count = 0

    for filename in os.listdir(folder):
        source = os.path.join(folder, filename)

        # تجاهل المجلدات
        if not os.path.isfile(source):
            continue

        category = get_category(filename)
        destination_folder = os.path.join(folder, category)

        os.makedirs(destination_folder, exist_ok=True)

        destination = os.path.join(destination_folder, filename)

        # لو الملف موجود بالفعل
        if os.path.exists(destination):
            name, ext = os.path.splitext(filename)
            destination = os.path.join(
                destination_folder,
                name + "_copy" + ext
            )

        shutil.move(source, destination)
        print(f"✓ {filename} → {category}")
        count += 1

    print(f"\nتم ترتيب {count} ملف.")


organize()
