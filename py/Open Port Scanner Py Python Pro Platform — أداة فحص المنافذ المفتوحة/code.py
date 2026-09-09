import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

# =========================
# Colors
# =========================
RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
CYAN = "\033[1;36m"
WHITE = "\033[1;37m"
RESET = "\033[0m"

# =========================
# Banner
# =========================
print("=" * 60)
print(" Open Port Scanner Py Python Pro Platform")
print("=" * 60)

# =========================
# Target
# =========================
target = input("\nاكتب IP أو Domain: ").strip()

# منع إدخال Arguments مع الهدف
if " " in target:
    print(f"\n{RED}اكتب الـIP أو الـDomain فقط.{RESET}")
    print(f"{YELLOW}مثال: 1.1.1.1{RESET}")
    exit()

try:
    target_ip = socket.gethostbyname(target)
except socket.gaierror:
    print(f"\n{RED}تعذر العثور على الهدف.{RESET}")
    exit()

print(f"\n{CYAN}Target : {target}{RESET}")
print(f"{CYAN}IP     : {target_ip}{RESET}")

# =========================
# Scan Mode
# =========================
print("\n" + "=" * 60)
print(" اختر نوع الفحص | Select Scan Type")
print("=" * 60)

print("1 - فحص كل البورتات | Scan All Ports")
print("2 - فحص بورتات محددة | Scan Specific Ports")
print("3 - فحص نطاق محدد | Scan Port Range")

choice = input("\nاختيارك: ").strip()

# =========================
# Select Ports
# =========================
if choice == "1":

    ports = range(1, 65536)
    total_ports = 65535

elif choice == "2":

    ports_input = input(
        "\nاكتب أرقام البورتات مفصولة بفاصلة\n"
        "مثال: 21,22,80,443\n"
        "البورتات: "
    ).strip()

    try:
        ports = sorted(
            set(
                int(p.strip())
                for p in ports_input.split(",")
            )
        )

        for port in ports:
            if not 1 <= port <= 65535:
                raise ValueError

    except ValueError:
        print(f"{RED}يوجد رقم بورت غير صحيح.{RESET}")
        exit()

    total_ports = len(ports)

elif choice == "3":

    try:
        start_port = int(input("\nمنفذ البداية: "))
        end_port = int(input("منفذ النهاية: "))

        if not (
            1 <= start_port <= 65535
            and 1 <= end_port <= 65535
            and start_port <= end_port
        ):
            raise ValueError

    except ValueError:
        print(f"{RED}نطاق البورتات غير صحيح.{RESET}")
        exit()

    ports = range(start_port, end_port + 1)
    total_ports = end_port - start_port + 1

else:

    print(f"{RED}اختيار غير صحيح.{RESET}")
    exit()

# =========================
# Port Information
# =========================
def get_service_name(port):

    try:
        return socket.getservbyport(port, "tcp")
    except:
        return "Unknown"


def scan_port(port):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)

    try:

        result = sock.connect_ex((target_ip, port))

        if result == 0:

            service = get_service_name(port)

            # محاولة الحصول على Banner
            banner = ""

            try:
                sock.settimeout(1)

                if port in [80, 8080, 8000, 8888]:
                    request = (
                        f"HEAD / HTTP/1.0\r\n"
                        f"Host: {target}\r\n"
                        f"Connection: close\r\n\r\n"
                    )

                    sock.send(request.encode())

                    data = sock.recv(1024)

                    banner = data.decode(
                        errors="ignore"
                    ).replace("\r", " ").replace("\n", " ")[:120]

            except:
                pass

            return {
                "port": port,
                "status": "OPEN",
                "service": service,
                "banner": banner
            }

        return {
            "port": port,
            "status": "CLOSED",
            "service": get_service_name(port),
            "banner": ""
        }

    except:
        return {
            "port": port,
            "status": "CLOSED",
            "service": get_service_name(port),
            "banner": ""
        }

    finally:
        sock.close()


# =========================
# Start Scan
# =========================
print("\n" + "=" * 60)
print(f"بدء الفحص | Total Ports: {total_ports}")
print("=" * 60 + "\n")

open_ports = []
closed_count = 0
completed = 0

workers = 100

with ThreadPoolExecutor(max_workers=workers) as executor:

    futures = [
        executor.submit(scan_port, port)
        for port in ports
    ]

    for future in as_completed(futures):

        result = future.result()
        completed += 1

        port = result["port"]

        if result["status"] == "OPEN":

            open_ports.append(result)

            service = result["service"]
            banner = result["banner"]

            print(
                f"{GREEN}[OPEN] "
                f"Port: {port:<5} "
                f"| Service: {service}{RESET}"
            )

            if banner:
                print(
                    f"{CYAN}       Banner: {banner}{RESET}"
                )

        else:

            closed_count += 1

            print(
                f"{RED}[CLOSED] "
                f"Port: {port:<5}{RESET}"
            )

# ترتيب النتائج
open_ports.sort(key=lambda x: x["port"])

# =========================
# Final Results
# =========================
print("\n" + "=" * 60)
print(" Scan Finished | انتهى الفحص")
print("=" * 60)

print(f"\nإجمالي البورتات المفحوصة : {total_ports}")
print(f"{GREEN}البورتات المفتوحة         : {len(open_ports)}{RESET}")
print(f"{RED}البورتات المغلقة          : {closed_count}{RESET}")

# =========================
# Open Ports Details
# =========================
if open_ports:

    print("\n" + "=" * 60)
    print(" Open Ports Information")
    print("=" * 60)

    for item in open_ports:

        print(
            f"\n{GREEN}Port: {item['port']}{RESET}"
        )

        print(
            f"Service : {item['service']}"
        )

        if item["banner"]:
            print(
                f"Banner  : {item['banner']}"
            )
        else:
            print(
                "Banner  : Not Available"
            )

else:

    print(
        f"\n{YELLOW}لم يتم العثور على بورتات مفتوحة.{RESET}"
    )

print("\n" + "=" * 60)
