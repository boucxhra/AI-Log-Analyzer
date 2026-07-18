import time
from datetime import datetime
import random

LOG_FILE = "test.log"

failed_msgs = [
    "Failed password for invalid user test from 192.168.1.10 port 22 ssh2",
    "Authentication failure for user admin from 10.0.0.5",
    "Connection refused for user guest from 172.16.0.3",
]

normal_msgs = [
    "User alice logged in successfully",
    "Service nginx started",
    "Cron job executed successfully",
]

while True:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if random.random() < 0.5:
        msg = random.choice(failed_msgs)
    else:
        msg = random.choice(normal_msgs)

    line = f"{now} {msg}\n"

    with open(LOG_FILE, "a") as f:
        f.write(line)

    print("Wrote:", line.strip())
    time.sleep(2)
