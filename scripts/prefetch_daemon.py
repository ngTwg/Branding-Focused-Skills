import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

PROJECT_DIR = os.getcwd()
CONTEXT_READY_FILE = r"C:\Users\lengo\.gemini\memory\context-ready.md"

class AnticipatoryPrefetcher(FileSystemEventHandler):
    def on_modified(self, event):
        filepath = event.src_path
        
        # Bỏ qua file rác
        if not filepath.endswith(('.c', '.cpp', '.py', '.ioc', '.h')): return

        # ==========================================
        # MARKOV CHAIN / HEURISTIC PREDICTION MOCKUP
        # ==========================================
        context_data = ""
        filename = os.path.basename(filepath)

        if filename.endswith('.ioc'):
            context_data = """## [PRE-FETCHED CONTEXT] 
- **Trigger**: Sửa file STM32Cube `.ioc`. 
- **Prediction**: User chuẩn bị gen code HAL. 
- **Loaded Memory**: Lưu ý RAM constraint (từ Causal Graph). Nạp sẵn datasheet phần cứng liên quan."""
        
        elif "crypto" in filename or "pqc" in filename:
            context_data = """## [PRE-FETCHED CONTEXT] 
- **Trigger**: Viết thuật toán mã hóa. 
- **Prediction**: Nguy cơ Memory Leak / Tràn RAM. 
- **Loaded Memory**: Load best practices về cấp phát động bộ nhớ trong C/C++ từ Global Preferences."""

        if context_data:
            with open(CONTEXT_READY_FILE, "w", encoding="utf-8") as f:
                f.write(context_data)
            print(f"[+] Anticipatory Context Updated for: {filename}")

if __name__ == "__main__":
    print("[*] Starting Anticipatory Pre-fetching Daemon...")
    observer = Observer()
    observer.schedule(AnticipatoryPrefetcher(), PROJECT_DIR, recursive=True)
    observer.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
