import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mininet.log import setLogLevel
from topologies.simple import make_net

HTTP_GET = ("python3 -c \"import urllib.request as u; "
            "print(u.urlopen('http://{ip}', timeout=3).status)\" 2>&1")


def ping_ok(src, dst_ip):
    out = src.cmd(f"ping -c 3 -W 2 {dst_ip}")
    match = re.search(r"(\d+) received", out)
    return bool(match) and int(match.group(1)) > 0


def http_ok(src, dst_ip):
    return "200" in src.cmd(HTTP_GET.format(ip=dst_ip))


def main():
    setLogLevel("warning")
    net = make_net()
    net.start()
    net.waitConnected()
    time.sleep(1)

    h1, h2, h3 = net.get("h1", "h2", "h3")
    server = h3.popen("python3 -m http.server 80 --directory /tmp",
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    checks = [
        ("h1 -> h2 ping allowed",     ping_ok, (h1, "10.0.0.2"), True),
        ("h1 -> h3 ping allowed",     ping_ok, (h1, "10.0.0.3"), True),
        ("h2 -> h3 ping BLOCKED",     ping_ok, (h2, "10.0.0.3"), False),
        ("h1 -> h3 web (80) BLOCKED", http_ok, (h1, "10.0.0.3"), False),
        ("h2 -> h3 web (80) allowed", http_ok, (h2, "10.0.0.3"), True),
    ]

    failed = 0
    for name, check, args, expected in checks:
        result = check(*args)
        status = "PASS" if result == expected else "FAIL"
        if status == "FAIL":
            failed += 1
        print(f"[{status}] {name}")

    server.terminate()
    net.stop()
    print(f"\n{len(checks) - failed}/{len(checks)} checks passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()