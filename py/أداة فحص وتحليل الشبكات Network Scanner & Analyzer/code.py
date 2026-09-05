import socket
from concurrent.futures import ThreadPoolExecutor

target = input("اكتب IP الجهاز المصرح لك بفحصه: ").strip()

ports = [
    21, 22, 23, 25, 53, 80,
    110, 135, 139, 143, 443,
    445, 3306, 3389, 8080
]

def scan_port(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)

        result = sock.connect_ex((target, port))
        sock.close()

        if result == 0:
            try:
                service = socket.getservbyport(port)
            except:
                service = "Unknown"

            print(f"[OPEN] Port {port} ({service})")

    except Exception:
        pass


print(f"\nScanning authorized target: {target}\n")

with ThreadPoolExecutor(max_workers=50) as executor:
    executor.map(scan_port, ports)

print("\nScan finished.")
