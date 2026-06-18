#!/usr/bin/env python3
"""
Trace Recorder & Test Packager (trace_recorder.py)
==================================================
Logs production traces and packages them as regression test fixtures.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

GEMINI_ROOT = Path(os.environ.get("GEMINI_ROOT", r"C:\Users\lengo\.gemini"))
TRACES_DIR = GEMINI_ROOT / "traces"
FIXTURES_DIR = GEMINI_ROOT / "tests" / "regression"

def log_trace(input_text: str, tool_calls: list, final_output: str, verdict: str = "success"):
    TRACES_DIR.mkdir(parents=True, exist_ok=True)
    trace_file = TRACES_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"
    
    trace_id = f"trace_{int(datetime.now(timezone.utc).timestamp())}"
    
    entry = {
        "trace_id": trace_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input": input_text,
        "tool_calls": tool_calls,
        "final_output": final_output,
        "verdict": verdict
    }
    
    with open(trace_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        
    print(f"[+] Trace logged: {trace_id} -> {trace_file}")
    return trace_id

def package_as_fixture(trace_id: str):
    found_trace = None
    
    # Scan all jsonl files in traces dir
    if TRACES_DIR.exists():
        for file in TRACES_DIR.glob("*.jsonl"):
            with open(file, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    data = json.loads(line)
                    if data.get("trace_id") == trace_id:
                        found_trace = data
                        break
            if found_trace:
                break
                
    if not found_trace:
        print(f"[-] Error: Trace {trace_id} not found.", file=sys.stderr)
        return False
        
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    fixture_file = FIXTURES_DIR / f"{trace_id}_fixture.json"
    
    with open(fixture_file, "w", encoding="utf-8") as f:
        json.dump(found_trace, f, indent=2, ensure_ascii=False)
        
    print(f"[+] Replay fixture generated at: {fixture_file}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Trace Recorder and Replay Fixture Generator")
    parser.add_argument("--log", action="store_true", help="Log a new trace from standard input")
    parser.add_argument("--package", type=str, help="Package trace ID as test fixture")
    args = parser.parse_args()
    
    if args.log:
        try:
            raw_data = sys.stdin.read()
            data = json.loads(raw_data)
            trace_id = log_trace(
                input_text=data.get("input", ""),
                tool_calls=data.get("tool_calls", []),
                final_output=data.get("final_output", ""),
                verdict=data.get("verdict", "success")
            )
            print(trace_id)
        except Exception as e:
            print(f"[-] Failed to parse trace input: {e}", file=sys.stderr)
            sys.exit(1)
            
    elif args.package:
        success = package_as_fixture(args.package)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
