#!/usr/bin/env python3
"""
Contract Test (contract_test.py)
================================
Validates output structure against schema versions and golden test definitions.
"""

import os
import sys
import json
import difflib
import argparse
from pathlib import Path

GEMINI_ROOT = Path(os.environ.get("GEMINI_ROOT", r"C:\Users\lengo\.gemini"))
CONTRACTS_DIR = GEMINI_ROOT / "contracts"
GOLDEN_DIR = CONTRACTS_DIR / "golden"

def validate_schema(schema_name: str, input_data: dict) -> bool:
    schema_path = CONTRACTS_DIR / f"{schema_name}.schema.json"
    if not schema_path.exists():
        print(f"[!] No schema contract found at: {schema_path}. Creating permissive base schema.")
        schema_path.parent.mkdir(parents=True, exist_ok=True)
        base_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "schema_version": {"type": "string"}
            },
            "required": ["schema_version"],
            "additionalProperties": True
        }
        with open(schema_path, "w", encoding="utf-8") as f:
            json.dump(base_schema, f, indent=2)
            
    try:
        import jsonschema
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
            
        # Ensure schema_version is present in input
        if "schema_version" not in input_data:
            print("[-] Schema validation failed: 'schema_version' is required in inputs.", file=sys.stderr)
            return False
            
        jsonschema.validate(instance=input_data, schema=schema)
        print(f"[+] Schema validation passed for: {schema_name} (v{input_data.get('schema_version')})")
        return True
    except ImportError:
        return isinstance(input_data, dict) and "schema_version" in input_data
    except Exception as e:
        print(f"[-] Schema validation failed: {e}", file=sys.stderr)
        return False

def check_golden_contract(schema_name: str, input_data: dict) -> bool:
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    golden_path = GOLDEN_DIR / f"{schema_name}.json"
    
    input_str = json.dumps(input_data, indent=2, sort_keys=True)
    
    if not golden_path.exists():
        print(f"[+] Initializing golden snapshot for: {schema_name}")
        with open(golden_path, "w", encoding="utf-8") as f:
            f.write(input_str)
        return True
        
    with open(golden_path, "r", encoding="utf-8") as f:
        golden_data = json.load(f)
        
    golden_str = json.dumps(golden_data, indent=2, sort_keys=True)
    
    if input_str == golden_str:
        print(f"[+] Golden snapshot matches for: {schema_name}")
        return True
        
    # Check if format changed but schema version was NOT bumped
    if input_data.get("schema_version") == golden_data.get("schema_version"):
        print("[-] Error: Schema structure changed but 'schema_version' was not bumped!", file=sys.stderr)
        diff = list(difflib.unified_diff(
            golden_str.splitlines(),
            input_str.splitlines(),
            fromfile="golden",
            tofile="current",
            lineterm=""
        ))
        print("\n".join(diff), file=sys.stderr)
        return False
        
    print(f"[+] Golden version bumped from v{golden_data.get('schema_version')} to v{input_data.get('schema_version')}.")
    return True

def main():
    parser = argparse.ArgumentParser(description="Golden Contract Validator")
    parser.add_argument("--schema", type=str, required=True, help="Contract schema name")
    parser.add_argument("--input", type=str, required=True, help="JSON path or raw JSON string")
    parser.add_argument("--update-golden", action="store_true", help="Overwrite golden with input")
    args = parser.parse_args()
    
    try:
        if os.path.exists(args.input):
            with open(args.input, "r", encoding="utf-8") as f:
                input_data = json.load(f)
        else:
            input_data = json.loads(args.input)
    except Exception as e:
        print(f"[-] Failed to parse input JSON: {e}", file=sys.stderr)
        sys.exit(1)
        
    if args.update_golden:
        golden_path = GOLDEN_DIR / f"{args.schema}.json"
        GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
        with open(golden_path, "w", encoding="utf-8") as f:
            json.dump(input_data, f, indent=2, sort_keys=True)
        print(f"[+] Golden snapshot updated.")
        sys.exit(0)
        
    schema_ok = validate_schema(args.schema, input_data)
    golden_ok = check_golden_contract(args.schema, input_data)
    
    sys.exit(0 if (schema_ok and golden_ok) else 1)

if __name__ == "__main__":
    main()
