#!/usr/bin/env python3
"""
Planner Engine (planner.py)
==========================
Defines plan steps (Read -> Analyze -> Edit -> Test), maintains assumption logs,
and enforces goal registry validations to prevent Goal Drift.
"""

import os
import sys
import json
import argparse
from pathlib import Path

GEMINI_ROOT = Path(os.environ.get("GEMINI_ROOT", r"C:\Users\lengo\.gemini"))
GOAL_REGISTRY = GEMINI_ROOT / ".gemini" / "goal_registry.json"
ASSUMPTION_LOG = GEMINI_ROOT / "ASSUMPTION_LOG.md"

def load_goal_registry() -> dict:
    if GOAL_REGISTRY.exists():
        try:
            with open(GOAL_REGISTRY, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"primary_objective": "", "current_step": "init", "steps": []}

def save_goal_registry(data: dict):
    GOAL_REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    with open(GOAL_REGISTRY, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def log_assumption(assumption: str, rationale: str):
    exists = ASSUMPTION_LOG.exists()
    with open(ASSUMPTION_LOG, "a", encoding="utf-8") as f:
        if not exists:
            f.write("# Assumption Log\n\n")
        f.write(f"- **Assumption**: {assumption}\n  - **Rationale**: {rationale}\n\n")
    print(f"[+] Assumption logged: {assumption}")

def check_goal_drift(current_task: str) -> bool:
    data = load_goal_registry()
    primary = data.get("primary_objective")
    if not primary:
        print("[!] No primary goal registered.")
        return False
    # Quick simple check to see if current task drifts from primary
    primary_words = set(primary.lower().split())
    task_words = set(current_task.lower().split())
    intersection = primary_words.intersection(task_words)
    if len(intersection) == 0:
        print(f"[WARN: GOAL DRIFT DETECTED] Current step '{current_task}' has drifted from objective: '{primary}'")
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description="Planning & Alignment Subsystem")
    parser.add_argument("--set-goal", type=str, help="Set the primary objective of the session")
    parser.add_argument("--check-drift", type=str, help="Validate if active task matches the registered goal")
    parser.add_argument("--assume", type=str, help="Log a framework/system assumption")
    parser.add_argument("--rationale", type=str, default="None", help="Rationale for logged assumption")
    args = parser.parse_args()

    if args.set_goal:
        save_goal_registry({
            "primary_objective": args.set_goal,
            "current_step": "init",
            "steps": ["Read", "Analyze", "Edit", "Test"]
        })
        print(f"[+] Objective registered: {args.set_goal}")
        sys.exit(0)

    if args.check_drift:
        drift = check_goal_drift(args.check_drift)
        sys.exit(1 if drift else 0)

    if args.assume:
        log_assumption(args.assume, args.rationale)
        sys.exit(0)

    parser.print_help()

if __name__ == "__main__":
    main()
