import random
import string
import os

print("=" * 55)
print("        Random Password Generator Tool")
print("        مولد كلمات المرور العشوائية")
print("=" * 55)

# اسم الملف
filename = input("\nاكتب اسم الملف بدون .txt: ").strip()

if not filename:
    print("اسم الملف لا يمكن أن يكون فارغًا.")
    exit()

filename += ".txt"

# طول الباسورد
while True:
    try:
        length = int(input("حدد طول كلمة المرور: "))
        if length <= 0:
            print("الطول يجب أن يكون أكبر من صفر.")
            continue
        break
    except ValueError:
        print("اكتب رقمًا صحيحًا.")

# اختيار نوع الأحرف
print("\nاختر محتوى كلمة المرور:")
print("1 - حروف فقط")
print("2 - أرقام فقط")
print("3 - رموز فقط")
print("4 - حروف + أرقام")
print("5 - حروف + رموز")
print("6 - أرقام + رموز")
print("7 - حروف + أرقام + رموز")

while True:
    choice = input("\nاختيارك: ").strip()

    if choice == "1":
        characters = string.ascii_letters
        break
    elif choice == "2":
        characters = string.digits
        break
    elif choice == "3":
        characters = string.punctuation
        break
    elif choice == "4":
        characters = string.ascii_letters + string.digits
        break
    elif choice == "5":
        characters = string.ascii_letters + string.punctuation
        break
    elif choice == "6":
        characters = string.digits + string.punctuation
        break
    elif choice == "7":
        characters = string.ascii_letters + string.digits + string.punctuation
        break
    else:
        print("اختيار غير صحيح.")

# عدد الباسوردات
while True:
    try:
        count = int(input("\nحدد عدد كلمات المرور: "))
        if count <= 0:
            print("العدد يجب أن يكون أكبر من صفر.")
            continue
        break
    except ValueError:
        print("اكتب رقمًا صحيحًا.")

print("\nجاري إنشاء كلمات المرور...")

passwords = set()

# توليد كلمات مرور بدون تكرار
while len(passwords) < count:
    password = ''.join(random.choices(characters, k=length))
    passwords.add(password)

# حفظ الملف
try:
    with open(filename, "w", encoding="utf-8") as file:
        for password in passwords:
            file.write(password + "\n")

    print("\n" + "=" * 55)
    print("تم إنشاء الملف بنجاح.")
    print(f"اسم الملف: {filename}")
    print(f"طول كلمة المرور: {length}")
    print(f"عدد كلمات المرور: {len(passwords)}")
    print("=" * 55)

except Exception as e:
    print(f"حدث خطأ أثناء حفظ الملف: {e}")
