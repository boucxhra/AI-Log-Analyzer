import os
from datetime import datetime

def save_report(content, prefix="report"):
    if not os.path.exists("reports"):
        os.makedirs("reports")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"reports/{prefix}_{timestamp}.txt"
    with open(filename, "w") as f:
        f.write(content)
    return filename

def view_reports():
    if not os.path.exists("reports"):
        print("No reports folder found yet.")
        return
    files = sorted(os.listdir("reports"))
    if not files:
        print("No reports saved yet.")
        return
    print("\nSaved reports:")
    for i, f in enumerate(files, 1):
        print(f"{i}. {f}")
