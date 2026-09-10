import socket
import concurrent.futures
import ipaddress
from colorama import Fore, Style, init

init(autoreset=True)


# ==============================
# SETTINGS
# ==============================

TIMEOUT = 0.35
THREADS = 100

COMMON_PORTS = [
    80,
    443,
    8080,
    8443,
    22,
    23,
    53,
    139,
    445,
    3389
]


# ==============================
# BANNER
# ==============================

def banner():

    print(Fore.CYAN + "=" * 65)

    print(
        Fore.YELLOW +
        "        NETWORK DEVICE SCANNER"
    )

    print(
        Fore.YELLOW +
        "        كاشف أجهزة الشبكة"
    )

    print(Fore.CYAN + "=" * 65)


# ==============================
# GET LOCAL IP
# ==============================

def get_local_ip():

    try:

        s = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        s.connect(("8.8.8.8", 80))

        ip = s.getsockname()[0]

        s.close()

        return ip

    except:

        return None


# ==============================
# CREATE /24 NETWORK
# ==============================

def get_network(ip):

    try:

        network = ipaddress.ip_network(
            ip + "/24",
            strict=False
        )

        return network

    except:

        return None


# ==============================
# CHECK HOST
# ==============================

def check_host(ip):

    ip = str(ip)

    for port in COMMON_PORTS:

        try:

            sock = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            sock.settimeout(TIMEOUT)

            result = sock.connect_ex(
                (ip, port)
            )

            sock.close()

            if result == 0:

                return {
                    "ip": ip,
                    "port": port,
                    "status": "ONLINE"
                }

        except:

            pass

    return None


# ==============================
# HOSTNAME
# ==============================

def get_hostname(ip):

    try:

        return socket.gethostbyaddr(ip)[0]

    except:

        return "Unknown"


# ==============================
# SCAN
# ==============================

def scan(network, local_ip):

    hosts = list(network.hosts())

    results = []

    print()
    print(
        Fore.YELLOW +
        f"[*] Hosts to scan: {len(hosts)}"
    )

    print(
        Fore.YELLOW +
        "[*] Starting TCP discovery..."
    )

    print()

    completed = 0

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=THREADS
    ) as executor:

        futures = {
            executor.submit(
                check_host,
                host
            ): host

            for host in hosts
        }

        for future in concurrent.futures.as_completed(
            futures
        ):

            completed += 1

            result = future.result()

            if result:

                ip = result["ip"]

                hostname = get_hostname(ip)

                result["hostname"] = hostname

                results.append(result)

                print(
                    Fore.GREEN +
                    f"[+] ONLINE  {ip}"
                    +
                    Fore.WHITE +
                    f"  Port: {result['port']}"
                    +
                    Fore.CYAN +
                    f"  Host: {hostname}"
                )

            elif completed % 25 == 0:

                print(
                    Fore.BLUE +
                    f"[*] Progress: "
                    f"{completed}/{len(hosts)}"
                )

    # Remove duplicates
    unique = {}

    for device in results:

        unique[device["ip"]] = device

    results = list(unique.values())

    return results


# ==============================
# RESULTS
# ==============================

def show_results(results, local_ip):

    print()
    print(
        Fore.CYAN +
        "=" * 65
    )

    print(
        Fore.GREEN +
        "                    RESULTS"
    )

    print(
        Fore.CYAN +
        "=" * 65
    )

    if not results:

        print(
            Fore.RED +
            "\n[!] No reachable devices detected."
        )

        print(
            Fore.YELLOW +
            "[!] This does NOT necessarily mean "
            "that no devices are connected."
        )

        print(
            Fore.YELLOW +
            "[!] Devices may block TCP probes."
        )

        return

    print()

    for number, device in enumerate(
        results,
        1
    ):

        ip = device["ip"]

        if ip == local_ip:

            color = Fore.MAGENTA

            tag = " [YOUR DEVICE]"

        else:

            color = Fore.WHITE

            tag = ""

        print(
            Fore.CYAN +
            "-" * 65
        )

        print(
            color +
            f"[{number}] IP       : "
            f"{ip}{tag}"
        )

        print(
            Fore.YELLOW +
            f"    Open Port: "
            f"{device['port']}"
        )

        print(
            Fore.GREEN +
            f"    Hostname : "
            f"{device['hostname']}"
        )

    print(
        Fore.CYAN +
        "-" * 65
    )

    print(
        Fore.GREEN +
        f"\n[+] Detected devices: "
        f"{len(results)}"
    )


# ==============================
# MAIN
# ==============================

def main():

    banner()

    local_ip = get_local_ip()

    if not local_ip:

        print(
            Fore.RED +
            "[!] Could not determine local IP."
        )

        return

    print(
        Fore.WHITE +
        "\n[+] Your IP: "
        +
        Fore.GREEN +
        local_ip
    )

    network = get_network(local_ip)

    if not network:

        print(
            Fore.RED +
            "[!] Could not determine network."
        )

        return

    print(
        Fore.WHITE +
        "[+] Network: "
        +
        Fore.GREEN +
        str(network)
    )

    results = scan(
        network,
        local_ip
    )

    show_results(
        results,
        local_ip
    )

    print(
        Fore.CYAN +
        "\n[+] Scan completed."
    )


# ==============================
# START
# ==============================

if __name__ == "__main__":

    main()
