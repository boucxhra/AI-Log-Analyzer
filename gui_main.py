import requests
import json
import re
import os
import time
from datetime import datetime
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox

API_KEY = "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"   # ← put your real key here
MODEL = "llama-3.3-70b-versatile"


def extract_ips(text):
    return re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text)


def extract_usernames(text):
    return re.findall(r"user\s+'?(\w+)'?", text, re.IGNORECASE)


def extract_timestamps(text):
    return re.findall(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", text)


def analyze_logs(log_text):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
You are a cybersecurity analyst. Analyze the logs and provide:

1. A short summary of what is happening.
2. A severity level (Critical, High, Medium, Low).
3. A severity score from 1 to 10.
4. Detected threat types.
5. Suspicious IP addresses.
6. Indicators of compromise.
7. Recommended actions.

Logs:
{log_text}
"""

    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    result = response.json()

    if "error" in result:
        return f"API Error: {result['error'].get('message', 'Unknown error')}"

    return result["choices"][0]["message"]["content"]


def save_report(content, prefix="report"):
    if not os.path.exists("reports"):
        os.makedirs("reports")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"reports/{prefix}_{timestamp}.txt"

    with open(filename, "w") as f:
        f.write(content)

    return filename


class LogAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Log Analyzer v5")
        self.root.geometry("900x600")

        self.monitoring = False
        self.monitor_thread = None

        # Top frame with buttons
        top_frame = tk.Frame(root)
        top_frame.pack(pady=10)

        self.btn_analyze = tk.Button(top_frame, text="Analyze Log File Once", command=self.analyze_once)
        self.btn_analyze.grid(row=0, column=0, padx=5)

        self.btn_monitor = tk.Button(top_frame, text="Real-Time Monitor Log File", command=self.start_monitor)
        self.btn_monitor.grid(row=0, column=1, padx=5)

        self.btn_stop_monitor = tk.Button(top_frame, text="Stop Monitoring", command=self.stop_monitor, state=tk.DISABLED)
        self.btn_stop_monitor.grid(row=0, column=2, padx=5)

        self.btn_view_reports = tk.Button(top_frame, text="View Reports Folder", command=self.open_reports_folder)
        self.btn_view_reports.grid(row=0, column=3, padx=5)

        # Text area
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Courier", 10))
        self.text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready.")
        status_bar = tk.Label(root, textvariable=self.status_var, anchor="w")
        status_bar.pack(fill=tk.X)

    def log(self, msg):
        self.text_area.insert(tk.END, msg + "\n")
        self.text_area.see(tk.END)

    def set_status(self, msg):
        self.status_var.set(msg)
        self.root.update_idletasks()

    def analyze_once(self):
        file_path = filedialog.askopenfilename(title="Select log file")
        if not file_path:
            return

        try:
            with open(file_path, "r") as f:
                logs = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file:\n{e}")
            return

        self.set_status("Analyzing with AI...")
        self.log(f"[+] Analyzing file: {file_path}")

        try:
            ai_report = analyze_logs(logs)
        except Exception as e:
            messagebox.showerror("Error", f"API call failed:\n{e}")
            self.set_status("Error during analysis.")
            return

        ips = extract_ips(logs)
        users = extract_usernames(logs)
        times = extract_timestamps(logs)

        full_report = (
            f"{ai_report}\n\n"
            f"Extracted IPs: {ips}\n"
            f"Users: {users}\n"
            f"Timestamps: {times}"
        )

        self.log("\n=== AI Security Report ===\n")
        self.log(full_report)

        saved_path = save_report(full_report, prefix="report")
        self.log(f"\n[+] Report saved to: {saved_path}")
        self.set_status("Analysis complete.")

    def monitor_worker(self, path):
        suspicious_keywords = [
            "failed password",
            "invalid user",
            "authentication failure",
            "unauthorized",
            "denied",
            "connection refused",
            "sudo",
            "root",
            "error"
        ]

        alerts = []
        try:
            with open(path, "r") as f:
                f.seek(0, os.SEEK_END)
                self.log(f"[+] Monitoring: {path}")
                self.set_status("Monitoring... (Stop with 'Stop Monitoring')")

                while self.monitoring:
                    line = f.readline()
                    if not line:
                        time.sleep(1)
                        continue

                    lower = line.lower()
                    if any(k in lower for k in suspicious_keywords):
                        msg = f"[ALERT] {line.strip()}"
                        alerts.append(msg)
                        self.log(msg)
        except Exception as e:
            self.log(f"[!] Error while monitoring: {e}")

        if alerts:
            content = "\n".join(alerts)
            saved_path = save_report(content, prefix="monitor")
            self.log(f"\n[+] Monitoring alerts saved to: {saved_path}")
        else:
            self.log("\n[+] No suspicious activity detected during monitoring.")

        self.set_status("Monitoring stopped.")
        self.btn_monitor.config(state=tk.NORMAL)
        self.btn_stop_monitor.config(state=tk.DISABLED)
        self.monitoring = False

    def start_monitor(self):
        file_path = filedialog.askopenfilename(title="Select log file to monitor")
        if not file_path:
            return

        if not os.path.exists(file_path):
            messagebox.showerror("Error", "File does not exist.")
            return

        if self.monitoring:
            messagebox.showinfo("Info", "Already monitoring.")
            return

        self.monitoring = True
        self.btn_monitor.config(state=tk.DISABLED)
        self.btn_stop_monitor.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)

        self.monitor_thread = threading.Thread(target=self.monitor_worker, args=(file_path,), daemon=True)
        self.monitor_thread.start()

    def stop_monitor(self):
        if self.monitoring:
            self.monitoring = False
            self.set_status("Stopping monitoring...")

    def open_reports_folder(self):
        if not os.path.exists("reports"):
            os.makedirs("reports")

        self.log("[+] Opening reports folder.")
        if os.name == "nt":
            os.startfile("reports")
        elif os.name == "posix":
            os.system("open reports" if "darwin" in os.sys.platform else "xdg-open reports")
        else:
            self.log("Please open the 'reports' folder manually.")


if __name__ == "__main__":
    root = tk.Tk()
    app = LogAnalyzerGUI(root)
    root.mainloop()
