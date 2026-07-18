from analyzer import analyze_logs, extract_ips, extract_usernames, extract_timestamps
from report import save_report, view_reports
from monitor import monitor_log_file

RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
RESET = "\033[0m"

def analyze_file_once():
    file_path = input("Enter path to log file: ").strip()

    try:
        with open(file_path, "r") as file:
            logs = file.read()
    except FileNotFoundError:
        print(RED + "File not found. Try again." + RESET)
        return

    ips = extract_ips(logs)
    users = extract_usernames(logs)
    times = extract_timestamps(logs)

    ai_report = analyze_logs(logs)

    print("\n" + BLUE + "--- AI Security Report ---" + RESET + "\n")
    print(ai_report)

    print("\n" + BLUE + "--- Extracted Indicators ---" + RESET)
    if ips:
        print("IPs:", ", ".join(ips))
    if users:
        print("Users:", ", ".join(users))
    if times:
        print("Timestamps:", ", ".join(times))

    full_report = (
        f"{ai_report}\n\n"
        f"Extracted IPs: {ips}\n"
        f"Users: {users}\n"
        f"Timestamps: {times}"
    )

    saved_path = save_report(full_report, prefix="report")
    print(f"\nReport saved to: {GREEN}{saved_path}{RESET}")


def main():
    while True:
        print(BLUE + "\n=== AI Log Analyzer v4 ===" + RESET)
        print("1. Analyze a log file once")
        print("2. View saved reports")
        print("3. Real-time monitor a log file")
        print("4. Exit")

        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            analyze_file_once()
        elif choice == "2":
            view_reports()
        elif choice == "3":
            path = input("Enter path to log file to monitor: ").strip()
            monitor_log_file(path)
        elif choice == "4":
            print("Goodbye.")
            break
        else:
            print(RED + "Invalid choice. Please enter 1, 2, 3, or 4." + RESET)


if __name__ == "__main__":
    main()
