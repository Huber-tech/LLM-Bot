# utils/cleanup_manager.py

import os
import time

def cleanup_old_logs(folder="logs", retention_days=10):
    now = time.time()
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        if os.path.isfile(path):
            if now - os.path.getmtime(path) > retention_days * 86400:
                os.remove(path)
