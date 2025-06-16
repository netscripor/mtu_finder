import platform
import subprocess
import sys

def is_ping_successful(ip: str, size: int) -> bool:
    system = platform.system()
    if system == "Windows":
        cmd = ["ping", ip, "-f", "-l", str(size), "-n", "1"]
    elif system in ["Linux", "Darwin"]:
        cmd = ["ping", "-M", "do", "-s", str(size), "-c", "1", ip]
    else:
        raise NotImplementedError("Unsupported OS")
    try:
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except Exception:
        return False

def find_max_mtu(ip: str, min_size: int = 1200, max_size: int = 1472) -> int | None:
    if not is_ping_successful(ip, min_size):
        return None

    low, high = min_size, max_size
    best = low
    while low <= high:
        mid = (low + high) // 2
        if is_ping_successful(ip, mid):
            best = mid
            low = mid + 1
        else:
            high = mid - 1
    return best

def classify_mtu(frame_size: int) -> str:
    if frame_size >= 1500:
        return "✅ Полноценный MTU"
    elif frame_size >= 1400:
        return "⚠️ Сниженный MTU — допустимо"
    elif frame_size >= 1300:
        return "⚠️ MTU ограничен — возможны проблемы (VPN/CDN)"
    else:
        return "❌ Критически малый MTU"

def main():
    if len(sys.argv) < 2:
        print("📦 Использование: python mtu_finder.py <ip1> [<ip2> ...]")
        sys.exit(1)

    print("🔍 MTU-проверка с флагом Don't Fragment:\\n")
    for ip in sys.argv[1:]:
        max_payload = find_max_mtu(ip)
        if max_payload is None:
            print(f"{ip:<20} → ❌ Хост недоступен или полностью режет пакеты (нет ответа на ping)")
            continue

        total_frame = max_payload + 28
        rating = classify_mtu(total_frame)
        print(f"{ip:<20} → Payload: {max_payload} байт  |  Frame: {total_frame} байт  → {rating}")

    print("ℹ️  Payload — полезная нагрузка без заголовков (ICMP/IP)")
    print("ℹ️  Frame — общий размер пакета, включая заголовки (MTU = payload + 28 байт)")

if __name__ == "__main__":
    main()
