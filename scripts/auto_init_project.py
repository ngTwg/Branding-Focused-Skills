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
    target_dir_path = target_dir_path.resolve()
    project_name = target_dir_path.name
    import datetime
    current_date = datetime.date.today().strftime("%Y-%m-%d")

    print(f"{STATUS['init']} Initializing Antigravity Rules and Workspace at: {target_dir_path}")
    
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
    rules_dest.mkdir(parents=True, exist_ok=True)
    
    for folder in ["memory", "workflows", "rules"]:
        src_folder = target_dir_path / ".agents" / folder
        if src_folder.exists() and src_folder != rules_dest:
            for md_file in src_folder.glob("*.md"):
                dest_file = rules_dest / md_file.name
                if not dest_file.exists():
                    shutil.copy2(md_file, dest_file)
                    print(f"{STATUS['copy']} Copied {folder}/{md_file.name} to rules/")

    # 2. Copy and Customize core markdown files to .agents directory
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
            # Copy template
            shutil.copy2(src, dest)
            print(f"{STATUS['create']} Created: {dest}")
            
            # Perform dynamic customization on PROJECT_MAP.md
            if "map" in dest.name.lower():
                try:
                    with open(dest, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Replace dynamic parameters
                    customized = (content
                        .replace("c:/Users/lengo/.gemini", str(target_dir_path.as_posix()))
                        .replace("c:\\Users\\lengo\\.gemini", str(target_dir_path))
                        .replace("2026-06-16", current_date)
                        .replace("Antigravity AI Skills", f"{project_name} AI Rules Workspace")
                    )
                    
                    with open(dest, "w", encoding="utf-8") as f:
                        f.write(customized)
                    print(f"{STATUS['ok']} Customized {dest.name} for project '{project_name}'")
                except Exception as e:
                    print(f"{STATUS['error']} Customizing {dest.name} failed: {e}")
        else:
            print(f"{STATUS['info']} File already exists: {dest}")

    # Copy customized core files directly to rules/
    for file_name in ["GEMINI.md", "INVARIANTS.md", "KNOWN_FAILURES.md", "PROJECT_MAP.md"]:
        agent_file = target_dir_path / ".agents" / file_name
        if agent_file.exists():
            shutil.copy2(agent_file, rules_dest / file_name)
            print(f"{STATUS['copy']} Synced {file_name} directly into rules/")

    # 3. Create IDE integration files (.cursorrules, .clinerules, etc.) using customized rules/GEMINI.md
    gemini_md_src = rules_dest / "GEMINI.md"
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

