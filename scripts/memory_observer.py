#!/usr/bin/env python3
"""
Antigravity Memory Observer — CLI for recording observations and summaries.
==========================================================================
Provides the agent with a simple CLI to record what happened during a task.

Usage:
    python memory_observer.py observe --project my-app --type bugfix --title "Fixed auth" --narrative "..."
    python memory_observer.py summarize --project my-app --request "Fix auth" --completed "Done" --learned "..."
    python memory_observer.py status
    python memory_observer.py history --project my-app --limit 10
"""

import argparse
import json
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

# Add parent to path for sibling import
sys.path.insert(0, str(Path(__file__).parent))
from memory_db import MemoryDB


def _epoch_to_readable(epoch_ms: int) -> str:
    dt = datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def _relative_time(epoch_ms: int) -> str:
    delta = (time.time() * 1000 - epoch_ms) / 1000
    if delta < 60:
        return f"{int(delta)}s ago"
    if delta < 3600:
        return f"{int(delta / 60)}m ago"
    if delta < 86400:
        return f"{int(delta / 3600)}h ago"
    return f"{int(delta / 86400)}d ago"


def cmd_observe(args):
    db = MemoryDB()
    project_id = db.get_or_create_project(args.project, root_path=args.root_path)

    session_id = None
    if args.session:
        session_id = args.session
    else:
        session_id = db.get_active_session(project_id)

    facts = [f.strip() for f in args.facts.split(",")] if args.facts else []
    concepts = [c.strip() for c in args.concepts.split(",")] if args.concepts else []
    files_read = [f.strip() for f in args.files_read.split(",")] if args.files_read else []
    files_modified = [f.strip() for f in args.files_modified.split(",")] if args.files_modified else []

    obs_id = db.create_observation(
        project_id=project_id,
        kind=args.kind,
        type_=args.type,
        title=args.title,
        subtitle=args.subtitle,
        narrative=args.narrative,
        facts=facts,
        concepts=concepts,
        files_read=files_read,
        files_modified=files_modified,
        session_id=session_id,
    )
    print(f"[CREATE] Observation #{obs_id} recorded")
    print(f"  Project: {args.project} | Type: {args.type} | Title: {args.title}")
    db.close()


def cmd_summarize(args):
    db = MemoryDB()
    project_id = db.get_or_create_project(args.project, root_path=args.root_path)

    session_id = None
    if args.session:
        session_id = args.session
    else:
        session_id = db.get_active_session(project_id)

    summary_id = db.create_summary(
        project_id=project_id,
        request=args.request,
        investigated=args.investigated,
        learned=args.learned,
        completed=args.completed,
        next_steps=args.next_steps,
        session_id=session_id,
    )

    if session_id:
        db.end_session(session_id, status="completed")
        print(f"[DONE] Session {session_id} completed")

    print(f"[CREATE] Summary #{summary_id} recorded")
    print(f"  Request: {args.request}")
    print(f"  Completed: {args.completed}")
    if args.learned:
        print(f"  Learned: {args.learned}")
    db.close()


def cmd_session(args):
    db = MemoryDB()
    project_id = db.get_or_create_project(args.project, root_path=args.root_path)

    if args.action == "start":
        session_id = db.start_session(project_id, title=args.title)
        print(f"[CREATE] Session {session_id} started for project '{args.project}'")
    elif args.action == "end":
        session_id = args.session_id or db.get_active_session(project_id)
        if session_id:
            db.end_session(session_id, status=args.status or "completed")
            print(f"[DONE] Session {session_id} ended with status: {args.status or 'completed'}")
        else:
            print("[WARN] No active session found for this project")
    db.close()


def cmd_history(args):
    db = MemoryDB()
    project_id = db.get_or_create_project(args.project)
    observations = db.list_observations(
        project_id, limit=args.limit, kind=args.kind, type_=args.obs_type
    )

    if not observations:
        print(f"No observations found for project '{args.project}'")
        db.close()
        return

    print(f"\n{'ID':>6} | {'Time':>8} | {'Kind':>12} | {'Type':>12} | Title")
    print("-" * 80)
    for obs in observations:
        rel = _relative_time(obs["created_at"])
        title = (obs["title"] or "")[:40]
        print(f"{obs['id']:>6} | {rel:>8} | {obs['kind']:>12} | {obs['type']:>12} | {title}")

    print(f"\nShowing {len(observations)} observations")
    db.close()


def cmd_status(args):
    db = MemoryDB()
    stats = db.stats()
    print(json.dumps(stats, indent=2))
    db.close()


def cmd_get(args):
    db = MemoryDB()
    ids = [int(x) for x in args.ids]
    observations = db.get_observations(ids)

    if not observations:
        print("No observations found for the given IDs")
        db.close()
        return

    for obs in observations:
        print(f"\n{'='*60}")
        print(f"Observation #{obs['id']} | {obs['kind']} / {obs['type']}")
        print(f"Created: {_epoch_to_readable(obs['created_at'])}")
        if obs["title"]:
            print(f"Title: {obs['title']}")
        if obs["subtitle"]:
            print(f"Subtitle: {obs['subtitle']}")
        if obs["narrative"]:
            print(f"\nNarrative:\n  {obs['narrative']}")
        if obs["facts"]:
            print(f"\nFacts:")
            for fact in obs["facts"]:
                print(f"  - {fact}")
        if obs["concepts"]:
            print(f"Concepts: {', '.join(obs['concepts'])}")
        if obs["files_modified"]:
            print(f"Files modified: {', '.join(obs['files_modified'])}")
        if obs["files_read"]:
            print(f"Files read: {', '.join(obs['files_read'])}")

    print(f"\n{'='*60}")
    db.close()


def main():
    parser = argparse.ArgumentParser(
        description="Antigravity Memory Observer — Record observations and summaries"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # observe
    p_obs = sub.add_parser("observe", help="Record an observation")
    p_obs.add_argument("--project", required=True, help="Project name")
    p_obs.add_argument("--root-path", help="Project root path (for auto-detection)")
    p_obs.add_argument("--kind", default="observation",
                       choices=["observation", "summary", "decision", "preference", "manual"],
                       help="Observation kind")
    p_obs.add_argument("--type", required=True,
                       help="Type: bugfix, feature, discovery, refactor, decision, config, test, docs")
    p_obs.add_argument("--title", required=True, help="Short title")
    p_obs.add_argument("--subtitle", help="Subtitle / one-liner")
    p_obs.add_argument("--narrative", help="Detailed description")
    p_obs.add_argument("--facts", help="Comma-separated facts")
    p_obs.add_argument("--concepts", help="Comma-separated concepts/tags")
    p_obs.add_argument("--files-read", help="Comma-separated files read")
    p_obs.add_argument("--files-modified", help="Comma-separated files modified")
    p_obs.add_argument("--session", help="Session ID (auto-detected if not provided)")

    # summarize
    p_sum = sub.add_parser("summarize", help="Record a session summary")
    p_sum.add_argument("--project", required=True, help="Project name")
    p_sum.add_argument("--root-path", help="Project root path")
    p_sum.add_argument("--request", help="What user asked for")
    p_sum.add_argument("--investigated", help="What was investigated")
    p_sum.add_argument("--learned", help="What was learned")
    p_sum.add_argument("--completed", help="What was completed")
    p_sum.add_argument("--next-steps", help="Recommended next steps")
    p_sum.add_argument("--session", help="Session ID (auto-detected if not provided)")

    # session
    p_sess = sub.add_parser("session", help="Manage sessions")
    p_sess.add_argument("action", choices=["start", "end"], help="Start or end a session")
    p_sess.add_argument("--project", required=True, help="Project name")
    p_sess.add_argument("--root-path", help="Project root path")
    p_sess.add_argument("--title", help="Session title")
    p_sess.add_argument("--session-id", help="Session ID (for end)")
    p_sess.add_argument("--status", help="End status", default="completed")

    # history
    p_hist = sub.add_parser("history", help="List recent observations")
    p_hist.add_argument("--project", required=True, help="Project name")
    p_hist.add_argument("--limit", type=int, default=20, help="Max results")
    p_hist.add_argument("--kind", help="Filter by kind")
    p_hist.add_argument("--obs-type", help="Filter by type")

    # get
    p_get = sub.add_parser("get", help="Get full observation details by IDs")
    p_get.add_argument("ids", nargs="+", help="Observation IDs")

    # status
    sub.add_parser("status", help="Show database statistics")

    args = parser.parse_args()

    commands = {
        "observe": cmd_observe,
        "summarize": cmd_summarize,
        "session": cmd_session,
        "history": cmd_history,
        "get": cmd_get,
        "status": cmd_status,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
