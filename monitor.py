import os
import time

RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
RESET = "\033[0m"

from report import save_report

def monitor_log_file(path):
    if not os.path.exists(path):
        print(RED + "Log file not found." + RESET)
        return

    print(BLUE + f"\n[+] Real-time monitoring: {path}" + RESET)
    print("Press CTRL+C to stop.\n")

    suspicious_keywords = ["failed password","invalid user","authentication failure","unauthorized","denied","connection refused","sudo","root","error"]

    alerts = []
    with open(path, "r") as f:
        f.seek(0, os.SEEK_END)
        try:
            while True:
                line = f.readline()
                if not line:
                    time.sleep(1)
                    continue
                lower = line.lower()
                if any(k in lower for k in suspicious_keywords):
                    msg = f"[ALERT] {line.strip()}"
                    print(RED + msg + RESET)
                    alerts.append(msg)
        except KeyboardInterrupt:
            print("\nStopping monitoring...")

    if alerts:
        content = "\n".join(alerts)
        saved_path = save_report(content, prefix="monitor")
        print(f"\nMonitoring alerts saved to: {GREEN}{saved_path}{RESET}")
    else:
        print("No suspicious activity detected during monitoring.")
