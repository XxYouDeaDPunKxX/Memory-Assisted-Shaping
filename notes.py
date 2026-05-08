#!/usr/bin/env python3
"""
Append-only memory signal tool for Memory-Assisted Shaping.

Run with:
  python3 -S notes.py <command>

This tool owns persistence.
It does not infer meaning.
It does not reshape content.
It does not rewrite prior live records.
"""

import argparse
import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path


ALLOWED_TYPES = {
    "mode",
    "shape",
    "gate",
    "decision",
    "discard",
    "tension",
    "source",
    "artifact",
}

DEFAULT_LOG_NAME = "session_notes.jsonl"
DEFAULT_META_NAME = "session_meta.json"
DEFAULT_EXPORT_NAME = "session_export.json"


class NotesError(Exception):
    pass


class StrictArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise NotesError(message)


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def json_dump(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def json_line(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n"


def default_base_dir():
    return Path(__file__).resolve().parent


def resolve_base_dir(path_value):
    return Path(path_value).resolve() if path_value else default_base_dir()


def meta_path(base_dir):
    return base_dir / DEFAULT_META_NAME


def log_path(base_dir):
    return base_dir / DEFAULT_LOG_NAME


def export_path(base_dir):
    return base_dir / DEFAULT_EXPORT_NAME


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise NotesError(f"missing file: {path}")
    except json.JSONDecodeError as exc:
        raise NotesError(f"invalid JSON in {path}: {exc}")


def write_json_atomic(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        handle.write(json_dump(value))
        handle.flush()
        os.fsync(handle.fileno())
    tmp.replace(path)


def ensure_session(base_dir):
    base_dir.mkdir(parents=True, exist_ok=True)
    mpath = meta_path(base_dir)
    lpath = log_path(base_dir)

    if mpath.exists():
        meta = load_json(mpath)
        if not isinstance(meta.get("session_id"), str) or not meta["session_id"]:
            raise NotesError("session_meta.json missing session_id")
    else:
        meta = {
            "schema_version": "shaping-memory-session-meta.v0",
            "session_id": str(uuid.uuid4()),
            "created_at": utc_now(),
            "log_file": str(lpath),
        }
        write_json_atomic(mpath, meta)

    if not lpath.exists():
        lpath.write_text("", encoding="utf-8")

    return meta, lpath


def read_records(lpath):
    if not lpath.exists():
        return []

    records = []
    with lpath.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            raw = line.strip()
            if raw == "":
                continue
            try:
                record = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise NotesError(f"invalid JSONL at line {line_no}: {exc}")
            if not isinstance(record, dict):
                raise NotesError(f"invalid JSONL at line {line_no}: record must be object")
            records.append(record)
    return records


def validate_type(value):
    if value not in ALLOWED_TYPES:
        allowed = ", ".join(sorted(ALLOWED_TYPES))
        raise NotesError(f"invalid type {value!r}; allowed: {allowed}")


def validate_text(value, field_name):
    if not isinstance(value, str) or value.strip() == "":
        raise NotesError(f"{field_name} must be a non-empty string")
    return value.strip()


def record_checksum(record):
    payload = dict(record)
    payload.pop("checksum", None)
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def command_init(args):
    base_dir = resolve_base_dir(args.dir)
    meta, lpath = ensure_session(base_dir)
    return {
        "ok": True,
        "command": "init",
        "session_id": meta["session_id"],
        "path": str(lpath),
    }


def command_append(args):
    base_dir = resolve_base_dir(args.dir)
    meta, lpath = ensure_session(base_dir)

    validate_type(args.type)
    text = validate_text(args.text, "text")
    effect = args.effect.strip() if isinstance(args.effect, str) and args.effect.strip() else None

    records = read_records(lpath)
    sequence = len(records) + 1
    note_id = f"n{sequence:05d}"

    record = {
        "id": note_id,
        "ts": utc_now(),
        "session_id": meta["session_id"],
        "seq": sequence,
        "type": args.type,
        "text": text,
    }
    if effect is not None:
        record["effect"] = effect

    record["checksum"] = record_checksum(record)

    with lpath.open("a", encoding="utf-8") as handle:
        handle.write(json_line(record))
        handle.flush()
        os.fsync(handle.fileno())

    return {
        "ok": True,
        "command": "append",
        "note_id": note_id,
        "seq": sequence,
        "path": str(lpath),
    }


def command_tail(args):
    base_dir = resolve_base_dir(args.dir)
    _meta, lpath = ensure_session(base_dir)
    limit = args.limit
    if limit < 1:
        raise NotesError("limit must be >= 1")
    records = read_records(lpath)
    return {
        "ok": True,
        "command": "tail",
        "count": min(limit, len(records)),
        "path": str(lpath),
        "records": records[-limit:],
    }


def command_summary(args):
    base_dir = resolve_base_dir(args.dir)
    meta, lpath = ensure_session(base_dir)
    records = read_records(lpath)

    by_type = {key: 0 for key in sorted(ALLOWED_TYPES)}
    for record in records:
        rtype = record.get("type")
        if rtype in by_type:
            by_type[rtype] += 1

    last = records[-1] if records else None

    return {
        "ok": True,
        "command": "summary",
        "session_id": meta["session_id"],
        "path": str(lpath),
        "total": len(records),
        "by_type": by_type,
        "last_note_id": last.get("id") if last else None,
        "last_type": last.get("type") if last else None,
    }


def command_export(args):
    base_dir = resolve_base_dir(args.dir)
    meta, lpath = ensure_session(base_dir)
    records = read_records(lpath)

    out_path = Path(args.output).resolve() if args.output else export_path(base_dir)
    export = {
        "schema_version": "shaping-memory-export.v0",
        "exported_at": utc_now(),
        "session": meta,
        "record_count": len(records),
        "records": records,
    }
    write_json_atomic(out_path, export)

    return {
        "ok": True,
        "command": "export",
        "record_count": len(records),
        "path": str(out_path),
    }


def build_parser():
    parser = StrictArgumentParser(description="Append-only shaping memory signal tool")
    parser.add_argument("--dir", default=None, help="Base directory for session files; defaults to the package directory containing notes.py")

    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.set_defaults(func=command_init)

    append = sub.add_parser("append")
    append.add_argument("--type", required=True, choices=sorted(ALLOWED_TYPES))
    append.add_argument("--text", required=True)
    append.add_argument("--effect", default=None)
    append.set_defaults(func=command_append)

    tail = sub.add_parser("tail")
    tail.add_argument("--limit", type=int, default=5)
    tail.set_defaults(func=command_tail)

    summary = sub.add_parser("summary")
    summary.set_defaults(func=command_summary)

    export = sub.add_parser("export")
    export.add_argument("--output", default=None)
    export.set_defaults(func=command_export)

    return parser


def main(argv=None):
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        result = args.func(args)
    except NotesError as exc:
        result = {
            "ok": False,
            "error": str(exc),
        }
        print(json_dump(result), end="")
        return 2
    except Exception as exc:
        result = {
            "ok": False,
            "error": f"unexpected_error: {exc}",
        }
        print(json_dump(result), end="")
        return 1

    print(json_dump(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
