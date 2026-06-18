#!/usr/bin/env python3
"""
Regression Gate Tool (regression_gate.py)
=========================================
Saves file checkpoints, runs tests, and automatically rolls back on failure
to enforce a strict regression guard.
"""

import os
import sys
import shutil
import subprocess
import argparse
import io
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding for emoji/unicode
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

GEMINI_ROOT = Path(os.environ.get("GEMINI_ROOT", r"C:\Users\lengo\.gemini"))
BACKUP_DIR = GEMINI_ROOT / "antigravity" / "backups"

# Tracked files we care about backing up
TRACKED_FILES = [
    "GEMINI.md",
    "PROJECT_MAP.md",
    "antigravity/skills/MASTER_ROUTER.md",
]

def create_checkpoint(name: str):
    """Save target files to a checkpoint directory."""
    checkpoint_path = BACKUP_DIR / f"checkpoint_{name}"
    checkpoint_path.mkdir(parents=True, exist_ok=True)
    
    print(f"[+] Creating checkpoint: {name}")
    for file_rel in TRACKED_FILES:
        src = GEMINI_ROOT / file_rel
        if src.exists():
            dest = checkpoint_path / file_rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            print(f"  - Backed up: {file_rel}")
            
    # Record metadata
    meta_file = checkpoint_path / "metadata.txt"
    with open(meta_file, "w", encoding="utf-8") as f:
        f.write(f"Name: {name}\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
    print(f"✅ Checkpoint '{name}' saved to {checkpoint_path}")

def rollback(name: str):
    """Restore target files from a checkpoint directory."""
    checkpoint_path = BACKUP_DIR / f"checkpoint_{name}"
    if not checkpoint_path.exists():
        print(f"❌ Error: Checkpoint '{name}' does not exist.")
        sys.exit(1)
        
    print(f"[!] Rolling back to checkpoint: {name}")
    for file_rel in TRACKED_FILES:
        src = checkpoint_path / file_rel
        if src.exists():
            dest = GEMINI_ROOT / file_rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            print(f"  - Restored: {file_rel}")
    print(f"✅ Rollback to '{name}' complete.")

def run_tests_and_validate() -> bool:
    """Run all tests. Return True if pass, False if fail."""
    print("[*] Running validation test suite...")
    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        result = subprocess.run(
            [sys.executable, "run_all_tests.py"],
            cwd=GEMINI_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error executing tests: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Regression Gate Tool")
    parser.add_argument("--checkpoint", type=str, help="Create a checkpoint with the specified name")
    parser.add_argument("--rollback", type=str, help="Rollback to the specified checkpoint name")
    parser.add_argument("--test-and-revert", type=str, help="Run tests; if failure occurs, automatically rollback to this checkpoint")
    args = parser.parse_args()
    
    if args.checkpoint:
        create_checkpoint(args.checkpoint)
    elif args.rollback:
        rollback(args.rollback)
    elif args.test_and_revert:
        checkpoint_name = args.test_and_revert
        success = run_tests_and_validate()
        if not success:
            print(f"\n⚠️  TEST SUITE FAILED. Triggering automatic rollback to checkpoint '{checkpoint_name}'...")
            rollback(checkpoint_name)
            sys.exit(1)
        else:
            print("\n✅ All tests passed. Changes are verified.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
