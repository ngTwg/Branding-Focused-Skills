#!/usr/bin/env python3
import os
import shutil
import sys
from pathlib import Path

GLOBAL_GEMINI_DIR = Path(__file__).parent.parent

def safe_print(*args, **kwargs):
    sep = kwargs.get('sep', ' ')
    end = kwargs.get('end', '\n')
    file = kwargs.get('file', sys.stdout)
    msg = sep.join(str(arg) for arg in args)
    try:
        file.write(msg + end)
        file.flush()
    except UnicodeEncodeError:
        fallback_msg = msg.encode('ascii', errors='replace').decode('ascii')
        try:
            file.write(fallback_msg + end)
            file.flush()
        except Exception:
            pass
    except Exception:
        pass

print = safe_print


STATUS = {
    "ok":      "[OK]",
    "copy":    "[COPY]",
    "create":  "[CREATE]",
    "done":    "[DONE]",
    "error":   "[ERROR]",
    "warn":    "[WARN]",
    "info":    "[INFO]",
    "init":    "[INIT]",
}

def init_project(target_dir_path: Path):
    print(f"{STATUS['init']} Initializing Antigravity Rules and Workspace at: {target_dir_path.resolve()}")
    
    # 1. Copy essential folders
    folders_to_copy = ["rules", "workflows", "memory"]
    for folder in folders_to_copy:
        src = GLOBAL_GEMINI_DIR / folder
        dest = target_dir_path / ".agents" / folder
        
        if not src.exists():
            print(f"{STATUS['warn']} Template folder not found: {src}")
            continue
            
        if not dest.exists():
            print(f"{STATUS['copy']} Copying folder {folder}...")
            shutil.copytree(src, dest, dirs_exist_ok=True)
            print(f"{STATUS['create']} Created: {dest}")
        else:
            print(f"{STATUS['info']} Folder already exists: {dest}")

    # 1.5 Auto-copy memory and workflow .md files into rules
    rules_dest = target_dir_path / ".agents" / "rules"
    if rules_dest.exists():
        for folder in ["memory", "workflows"]:
            src_folder = target_dir_path / ".agents" / folder
            if src_folder.exists():
                for md_file in src_folder.glob("*.md"):
                    dest_file = rules_dest / md_file.name
                    if not dest_file.exists():
                        shutil.copy2(md_file, dest_file)
                        print(f"{STATUS['copy']} Copied {folder}/{md_file.name} to rules/")
                    else:
                        print(f"{STATUS['info']} File {md_file.name} already in rules/")

    # 2. Copy core markdown files to .agents directory
    files_to_copy = [
        "GEMINI.md", 
        "PROJECT_MAP_TEMPLATE.md", 
        "INVARIANTS.md", 
        "KNOWN_FAILURES.md"
    ]
    
    (target_dir_path / ".agents").mkdir(parents=True, exist_ok=True)
    
    for file_name in files_to_copy:
        src = GLOBAL_GEMINI_DIR / file_name
        dest = target_dir_path / ".agents" / file_name
        
        if file_name == "PROJECT_MAP_TEMPLATE.md" and src.exists():
            dest = target_dir_path / ".agents" / "PROJECT_MAP.md"
            
        if not src.exists():
            print(f"{STATUS['warn']} Template file not found: {src}")
            continue
            
        if not dest.exists():
            shutil.copy2(src, dest)
            print(f"{STATUS['create']} Created: {dest}")
        else:
            print(f"{STATUS['info']} File already exists: {dest}")

    # 3. Create IDE integration files (.cursorrules, .clinerules, etc.)
    gemini_md_src = GLOBAL_GEMINI_DIR / "GEMINI.md"
    if gemini_md_src.exists():
        ide_rules_files = [".cursorrules", ".clinerules", ".windsurfrules"]
        for rules_file in ide_rules_files:
            dest = target_dir_path / rules_file
            if not dest.exists():
                shutil.copy2(gemini_md_src, dest)
                print(f"{STATUS['create']} Created IDE system rules link: {dest}")
            else:
                print(f"{STATUS['info']} IDE rules file already exists: {dest}")

    print(f"\n{STATUS['done']} Antigravity project initialization complete!")
    print("Agent will now automatically load all custom rules and behaviors for every request.")
    print(f"\n{STATUS['warn']} IDE rules files (.cursorrules, .clinerules, .windsurfrules) are COPIES, not symlinks.")
    print("Remember to re-run this script after updating GEMINI.md to sync your IDE rules.")

if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    init_project(target)

