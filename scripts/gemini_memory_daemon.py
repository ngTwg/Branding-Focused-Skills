"""
Gemini Implicit Feedback Daemon (v2.0)
======================================
Background daemon that monitors file changes, detects implicit user preferences
by analyzing diffs between AI-generated and user-edited code, and proposes
memory updates following the False Memory Guard protocol.

Features:
  - Multi-project monitoring via YAML config
  - Structured JSON logging with rotation
  - 3-strike dedup: same preference must appear 3+ times before proposal
  - Dry-run mode for safe testing
  - Graceful shutdown with signal handling
  - Windows Task Scheduler integration via --install/--uninstall

Usage:
  python gemini_memory_daemon.py                    # Run with defaults
  python gemini_memory_daemon.py --dry-run           # Test without writing
  python gemini_memory_daemon.py --config path.yaml  # Custom config
  python gemini_memory_daemon.py --install            # Install as Windows Task
  python gemini_memory_daemon.py --uninstall          # Remove Windows Task

Architecture:
  FileSystemObserver -> DebouncedHandler -> DiffAnalyzer -> LLM Extractor
                                                        -> DeduplicationGuard
                                                        -> ProposalWriter
"""

import os
import sys
import time
import json
import signal
import hashlib
import difflib
import logging
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from threading import Timer, Event, Lock
from logging.handlers import RotatingFileHandler

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ============================================================================
# CONSTANTS
# ============================================================================
GEMINI_ROOT = Path(os.environ.get("GEMINI_ROOT", r"C:\Users\lengo\.gemini"))
DEFAULT_CONFIG_PATH = GEMINI_ROOT / "config" / "daemon-config.yaml"
DEFAULT_LOG_DIR = GEMINI_ROOT / "logs"
GLOBAL_MEMORY_FILE = GEMINI_ROOT / "memory" / "preferences.md"
PENDING_PROPOSALS_FILE = GEMINI_ROOT / "memory" / "vault" / "pending-proposals.json"
TASK_NAME = "GeminiImplicitMemoryDaemon"

WATCHED_EXTENSIONS = (
    '.py', '.c', '.cpp', '.h', '.hpp', '.js', '.ts', '.jsx', '.tsx',
    '.md', '.yaml', '.yml', '.json', '.ioc', '.ld', '.s', '.rs', '.go',
)

IGNORED_DIRS = {
    '.git', 'node_modules', '.venv', '__pycache__', '.next', 'dist',
    'build', '.cache', '.hypothesis', 'antigravity-browser-profile',
}

# ============================================================================
# LOGGING SETUP
# ============================================================================
def setup_logging(log_dir: Path, dry_run: bool = False) -> logging.Logger:
    """Configure structured JSON logging with rotation."""
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("gemini_daemon")
    logger.setLevel(logging.DEBUG)

    # Rotating file handler (5MB x 3 backups)
    file_handler = RotatingFileHandler(
        log_dir / "daemon.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # JSON-ish structured format
    class StructuredFormatter(logging.Formatter):
        def format(self, record):
            entry = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "module": record.module,
                "msg": record.getMessage(),
            }
            if hasattr(record, "extra_data"):
                entry["data"] = record.extra_data
            return json.dumps(entry, ensure_ascii=False)

    file_handler.setFormatter(StructuredFormatter())

    # Human-readable console format
    prefix = "[DRY-RUN] " if dry_run else ""
    console_fmt = logging.Formatter(f"{prefix}[%(asctime)s] %(levelname)s: %(message)s", "%H:%M:%S")
    console_handler.setFormatter(console_fmt)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


# ============================================================================
# CONFIGURATION
# ============================================================================
def load_config(config_path: Path) -> dict:
    """Load daemon configuration from YAML, or return sensible defaults."""
    defaults = {
        "debounce_seconds": 30,
        "watched_projects": [str(GEMINI_ROOT)],
        "min_diff_lines": 3,
        "dedup_threshold": 3,  # Must see preference 3x before proposing
        "llm_model": "gemini-2.0-flash",
        "llm_timeout": 30,
    }
    if config_path.exists():
        try:
            import yaml
            with open(config_path, "r", encoding="utf-8") as f:
                user_cfg = yaml.safe_load(f) or {}
            defaults.update(user_cfg)
        except ImportError:
            # Fallback: read as simple key=value if no PyYAML
            pass
    return defaults


# ============================================================================
# DEDUPLICATION GUARD (3-Strike Rule)
# ============================================================================
class DeduplicationGuard:
    """
    Ensures the same preference is observed at least N times (default 3)
    before it gets proposed as a memory update. Prevents one-off edits
    from polluting the memory bank.
    """

    def __init__(self, threshold: int = 3, state_file: Path = None):
        self.threshold = threshold
        self.state_file = state_file or (GEMINI_ROOT / "memory" / "vault" / "dedup-state.json")
        self.lock = Lock()
        self.counts: dict[str, dict] = self._load_state()

    def _load_state(self) -> dict:
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return {}

    def _save_state(self):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.counts, f, indent=2, ensure_ascii=False)

    def _hash_preference(self, category: str, preference: str) -> str:
        raw = f"{category.lower().strip()}::{preference.lower().strip()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def should_propose(self, category: str, preference: str) -> bool:
        """
        Record an observation of a preference. Returns True only when
        the observation count reaches the threshold.
        """
        with self.lock:
            key = self._hash_preference(category, preference)
            if key not in self.counts:
                self.counts[key] = {
                    "category": category,
                    "preference": preference,
                    "count": 0,
                    "first_seen": datetime.now(timezone.utc).isoformat(),
                    "last_seen": None,
                    "proposed": False,
                }

            entry = self.counts[key]
            entry["count"] += 1
            entry["last_seen"] = datetime.now(timezone.utc).isoformat()

            if entry["count"] >= self.threshold and not entry["proposed"]:
                entry["proposed"] = True
                self._save_state()
                return True

            self._save_state()
            return False

    def get_status(self) -> list[dict]:
        """Return all tracked preferences with their counts."""
        with self.lock:
            return [
                {
                    "category": v["category"],
                    "preference": v["preference"],
                    "count": v["count"],
                    "threshold": self.threshold,
                    "proposed": v["proposed"],
                }
                for v in self.counts.values()
            ]


# ============================================================================
# IMPLICIT PREFERENCE EXTRACTOR
# ============================================================================
class ImplicitPreferenceExtractor:
    """
    Analyzes file diffs to extract implicit user preferences using LLM.
    Maintains shadow copies for accurate before/after comparison.
    """

    def __init__(self, config: dict, dedup: DeduplicationGuard,
                 logger: logging.Logger, dry_run: bool = False):
        self.config = config
        self.dedup = dedup
        self.logger = logger
        self.dry_run = dry_run
        self.shadow_copies: dict[str, str] = {}
        self._llm_model = None

    def _get_llm(self):
        """Lazy-load LLM model to avoid import cost at startup."""
        if self._llm_model is None:
            try:
                import google.generativeai as genai
                from dotenv import load_dotenv
                load_dotenv(GEMINI_ROOT / ".env")
                api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
                if not api_key:
                    self.logger.error("No GEMINI_API_KEY or GOOGLE_API_KEY found in environment")
                    return None
                genai.configure(api_key=api_key)
                self._llm_model = genai.GenerativeModel(self.config.get("llm_model", "gemini-2.0-flash"))
            except Exception as e:
                self.logger.error(f"Failed to initialize LLM: {e}")
                return None
        return self._llm_model

    def init_shadow_copies(self, project_dirs: list[str]):
        """Pre-load shadow copies for existing files (cold start)."""
        count = 0
        for project_dir in project_dirs:
            for root, dirs, files in os.walk(project_dir):
                # Prune ignored dirs in-place
                dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
                for fname in files:
                    if fname.endswith(WATCHED_EXTENSIONS):
                        fpath = os.path.join(root, fname)
                        self._update_shadow(fpath)
                        count += 1
        self.logger.info(f"Initialized shadow copies for {count} files")

    def _update_shadow(self, filepath: str):
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                self.shadow_copies[filepath] = f.read()
        except OSError:
            pass

    def analyze_change(self, filepath: str):
        """Core analysis pipeline: diff -> LLM extract -> dedup -> propose."""
        if filepath not in self.shadow_copies:
            self._update_shadow(filepath)
            return

        old_content = self.shadow_copies[filepath]
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                new_content = f.read()
        except OSError:
            return

        if old_content == new_content:
            return

        # Generate unified diff
        diff_lines = list(difflib.unified_diff(
            old_content.splitlines(),
            new_content.splitlines(),
            fromfile="ai_version",
            tofile="user_version",
            lineterm="",
        ))

        # Update shadow
        self.shadow_copies[filepath] = new_content

        # Skip trivial changes
        meaningful_changes = [l for l in diff_lines if l.startswith(('+', '-')) and not l.startswith(('+++', '---'))]
        if len(meaningful_changes) < self.config.get("min_diff_lines", 3):
            return

        diff_text = "\n".join(diff_lines)
        self.logger.info(f"Analyzing change: {filepath} ({len(meaningful_changes)} changed lines)")
        self._extract_and_propose(diff_text, filepath)

    def _extract_and_propose(self, diff_text: str, filepath: str):
        """Call LLM to extract preference, then run through dedup guard."""
        model = self._get_llm()
        if model is None:
            self.logger.warning("LLM unavailable — skipping extraction")
            return

        prompt = f"""You are an implicit preference extraction engine.
Analyze this code diff where 'ai_version' is the AI-generated code and 'user_version' 
is the code after the user manually edited it.

Your task: Identify IMPLICIT PREFERENCES — what the user consistently prefers.
Examples: library choices, naming conventions, architecture patterns, code style.

Diff from file: {Path(filepath).name}
```diff
{diff_text[:3000]}
```

If NO clear preference exists (just bug fixes, logic changes), return exactly:
{{"is_preference": false}}

If a CLEAR preference exists, return:
{{
  "is_preference": true,
  "category": "Architecture|Library|CodingStyle|Naming|ErrorHandling|Performance|Other",
  "preference": "Concise bullet-point description of the preference",
  "confidence": 0.0 to 1.0,
  "evidence": "Brief explanation of why you think this is a preference"
}}

Return ONLY valid JSON. No markdown fences."""

        try:
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.1, "max_output_tokens": 500},
            )
            raw = response.text.strip().strip("`").replace("json\n", "").replace("json\r\n", "")
            result = json.loads(raw)

            if not result.get("is_preference"):
                self.logger.debug(f"No preference detected in {filepath}")
                return

            category = result.get("category", "Unknown")
            preference = result.get("preference", "")
            confidence = result.get("confidence", 0.5)
            evidence = result.get("evidence", "")

            self.logger.info(
                f"Preference detected [{category}] (conf={confidence:.2f}): {preference}",
            )

            # Deduplication gate
            if self.dedup.should_propose(category, preference):
                self._write_proposal(category, preference, confidence, evidence, filepath)
            else:
                status = next(
                    (s for s in self.dedup.get_status()
                     if s["preference"] == preference),
                    None,
                )
                count = status["count"] if status else "?"
                threshold = status["threshold"] if status else "?"
                self.logger.info(
                    f"Dedup gate: {count}/{threshold} observations — not yet ready to propose"
                )

        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            self.logger.debug(f"LLM parse error (non-critical): {e}")
        except Exception as e:
            self.logger.warning(f"LLM call failed: {e}")

    def _write_proposal(self, category: str, preference: str,
                        confidence: float, evidence: str, source_file: str):
        """Write a pending proposal following False Memory Guard protocol."""
        proposal = {
            "id": hashlib.sha256(f"{category}:{preference}".encode()).hexdigest()[:12],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "target": "Global",
            "category": category,
            "preference": preference,
            "confidence": confidence,
            "evidence": evidence,
            "source_file": str(source_file),
            "status": "pending_approval",
        }

        if self.dry_run:
            self.logger.info(f"[DRY-RUN] Would propose: {json.dumps(proposal, ensure_ascii=False)}")
            return

        # Append to pending proposals file
        proposals = []
        if PENDING_PROPOSALS_FILE.exists():
            try:
                with open(PENDING_PROPOSALS_FILE, "r", encoding="utf-8") as f:
                    proposals = json.load(f)
            except (json.JSONDecodeError, OSError):
                proposals = []

        proposals.append(proposal)
        PENDING_PROPOSALS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PENDING_PROPOSALS_FILE, "w", encoding="utf-8") as f:
            json.dump(proposals, f, indent=2, ensure_ascii=False)

        self.logger.info(
            f"[PROPOSED MEMORY UPDATE] Target: Global | "
            f"Detected: {preference} | "
            f"Category: {category} | "
            f"Evidence: {evidence} | "
            f"Confidence: {confidence:.2f} | "
            f"Saved to: {PENDING_PROPOSALS_FILE}"
        )


# ============================================================================
# DEBOUNCED FILE SYSTEM HANDLER
# ============================================================================
class DebouncedHandler(FileSystemEventHandler):
    """
    Watches filesystem events with debouncing to avoid analyzing
    files while the user is still typing.
    """

    def __init__(self, extractor: ImplicitPreferenceExtractor,
                 debounce_sec: float, logger: logging.Logger):
        self.extractor = extractor
        self.debounce_sec = debounce_sec
        self.logger = logger
        self.timers: dict[str, Timer] = {}
        self.lock = Lock()

    def on_modified(self, event):
        if event.is_directory:
            return

        filepath = event.src_path

        # Filter by extension
        if not filepath.endswith(WATCHED_EXTENSIONS):
            return

        # Filter by ignored directories
        path_parts = Path(filepath).parts
        if any(part in IGNORED_DIRS for part in path_parts):
            return

        with self.lock:
            # Cancel existing timer for this file
            if filepath in self.timers:
                self.timers[filepath].cancel()

            # Set new debounced timer
            timer = Timer(
                self.debounce_sec,
                self.extractor.analyze_change,
                args=[filepath],
            )
            timer.daemon = True
            self.timers[filepath] = timer
            timer.start()


# ============================================================================
# WINDOWS TASK SCHEDULER INTEGRATION
# ============================================================================
def install_task_scheduler():
    """Register daemon as a Windows Task Scheduler task (runs at logon)."""
    python_exe = sys.executable
    script_path = os.path.abspath(__file__)

    cmd = (
        f'schtasks /create /tn "{TASK_NAME}" /tr '
        f'"\"{python_exe}\" \"{script_path}\"" '
        f'/sc onlogon /rl highest /f'
    )
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"[+] Task '{TASK_NAME}' installed successfully.")
        print(f"    Python: {python_exe}")
        print(f"    Script: {script_path}")
        print(f"    Trigger: On Logon")
    except subprocess.CalledProcessError as e:
        print(f"[-] Failed to install task: {e}")
        print("    Try running as Administrator.")
        sys.exit(1)


def uninstall_task_scheduler():
    """Remove the daemon from Windows Task Scheduler."""
    cmd = f'schtasks /delete /tn "{TASK_NAME}" /f'
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"[+] Task '{TASK_NAME}' removed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[-] Failed to remove task: {e}")
        sys.exit(1)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Gemini Implicit Feedback Daemon v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH,
                        help="Path to daemon config YAML")
    parser.add_argument("--dry-run", action="store_true",
                        help="Analyze without writing proposals")
    parser.add_argument("--install", action="store_true",
                        help="Install as Windows Task Scheduler task")
    parser.add_argument("--uninstall", action="store_true",
                        help="Remove from Windows Task Scheduler")
    parser.add_argument("--status", action="store_true",
                        help="Show dedup guard status and pending proposals")
    args = parser.parse_args()

    if args.install:
        install_task_scheduler()
        return

    if args.uninstall:
        uninstall_task_scheduler()
        return

    # Load configuration
    config = load_config(args.config)

    # Setup logging
    logger = setup_logging(DEFAULT_LOG_DIR, dry_run=args.dry_run)

    if args.status:
        dedup = DeduplicationGuard(threshold=config.get("dedup_threshold", 3))
        print("\n=== Deduplication Guard Status ===")
        for entry in dedup.get_status():
            status = "✅ PROPOSED" if entry["proposed"] else f"⏳ {entry['count']}/{entry['threshold']}"
            print(f"  [{entry['category']}] {entry['preference']} — {status}")

        if PENDING_PROPOSALS_FILE.exists():
            with open(PENDING_PROPOSALS_FILE, "r", encoding="utf-8") as f:
                proposals = json.load(f)
            print(f"\n=== Pending Proposals ({len(proposals)}) ===")
            for p in proposals:
                print(f"  [{p['category']}] {p['preference']} (conf={p['confidence']:.2f})")
        return

    # Initialize components
    dedup = DeduplicationGuard(threshold=config.get("dedup_threshold", 3))
    extractor = ImplicitPreferenceExtractor(config, dedup, logger, dry_run=args.dry_run)

    project_dirs = config.get("watched_projects", [str(GEMINI_ROOT)])
    logger.info(f"Gemini Implicit Feedback Daemon v2.0 starting...")
    logger.info(f"Mode: {'DRY-RUN' if args.dry_run else 'LIVE'}")
    logger.info(f"Monitoring {len(project_dirs)} project(s): {project_dirs}")
    logger.info(f"Debounce: {config.get('debounce_seconds', 30)}s")
    logger.info(f"Dedup threshold: {config.get('dedup_threshold', 3)} observations")
    logger.info(f"Target memory: {GLOBAL_MEMORY_FILE}")

    # Initialize shadow copies
    extractor.init_shadow_copies(project_dirs)

    # Setup filesystem observers
    handler = DebouncedHandler(extractor, config.get("debounce_seconds", 30), logger)
    observers = []
    for project_dir in project_dirs:
        if not os.path.isdir(project_dir):
            logger.warning(f"Project dir not found, skipping: {project_dir}")
            continue
        obs = Observer()
        obs.schedule(handler, project_dir, recursive=True)
        obs.start()
        observers.append(obs)
        logger.info(f"Watching: {project_dir}")

    if not observers:
        logger.error("No valid project directories to watch. Exiting.")
        sys.exit(1)

    # Graceful shutdown handler
    shutdown_event = Event()

    def signal_handler(signum, frame):
        logger.info("Shutdown signal received. Stopping gracefully...")
        shutdown_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Main loop
    try:
        while not shutdown_event.is_set():
            shutdown_event.wait(timeout=1.0)
    finally:
        for obs in observers:
            obs.stop()
        for obs in observers:
            obs.join(timeout=5.0)
        logger.info("Daemon stopped cleanly.")


if __name__ == "__main__":
    main()
