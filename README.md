# 🧠 Memory-Assisted Shaping

A ChatGPT Projects protocol for shaping one idea across a long conversation without losing decisions, gates, discarded paths, or source boundaries.

It keeps shaping notes separate from the final artifact. 🧩➡️📦

## 🚀 Use with ChatGPT Projects

Add the project files to ChatGPT Project Source.

Tell GPT:

> Use Memory-Assisted Shaping for this idea.

Then work normally.

Ask for a recap when state matters.  
Ask for a final artifact only when the shape is ready.

## 🌊 Why this exists

Long ChatGPT conversations drift. 🌀

Examples become decisions.  
Discarded paths return.  
Open questions disappear.  
The final output starts carrying process residue.

Memory-Assisted Shaping gives GPT a small continuity layer without turning the conversation into note management.

## ⚙️ Operating model

GPT shapes the idea before producing an artifact.

It tracks:

- ✅ decisions
- 🚧 open gates
- 🗑️ discarded paths
- 📚 source boundaries
- 🏁 artifact readiness

When continuity would degrade without retention, GPT may emit a minimal memory signal.

Python appends the signal.  
GPT does not manage or rewrite memory files.

The final artifact is produced only after explicit approval.

## 📁 Files

`protocol.md`  
The behavioral protocol GPT should follow while shaping the idea.

`note-io.md`  
The boundary between GPT and the internal note layer.

`notes.py`  
The small Python helper that appends internal notes.

During use, the tool may generate:

`session_meta.json`  
`session_notes.jsonl`  
`session_export.json`

Do not include generated session files in the clean source package.

## 🔁 Recap and final artifacts

Ask for a recap when you need to recover the current state.

Useful prompts:

- “Recap the internal notes.”
- “Show me the current shape of the idea.”
- “List decisions, open points, discarded paths, and artifact readiness.”
- “Are there any gates still open before we write the final artifact?”

The final artifact is the clean output you eventually ask for.

It should not contain raw notes, discarded paths, internal reasoning, or process trace unless you explicitly ask for an audit-style document.

---

<details>
<summary>🛠️ Technical details</summary>

## Project structure

Recommended repository layout:

```text
memory-assisted-shaping/
  README.md
  protocol.md
  note-io.md
  notes.py
```

Generated during use:

```text
session_meta.json
session_notes.jsonl
session_export.json
```

Generated files are session-specific and should not be committed as part of the clean base package.

## Memory model

The live memory model is append-only.

GPT does not own or rewrite the memory files.

GPT emits a minimal signal.  
Python timestamps it, assigns an ID, appends it to `session_notes.jsonl`, and returns a short receipt.

Live note signals are intentionally small:

```text
type
text
optional effect
```

Python adds:

```text
id
timestamp
session_id
sequence number
checksum
```

## Signal types

Allowed live signal types:

```text
mode
shape
gate
decision
discard
tension
source
artifact
```

These are not meant to describe everything in the conversation.

They exist only for moments that affect continuity: a change in direction, an important decision, an open decision point, a discarded path, a source boundary, or artifact readiness.

## Python usage

Run note commands with:

```bash
python3 -S
```

From the extracted package folder:

```bash
python3 -S ./notes.py init
```

Append a note:

```bash
python3 -S ./notes.py append --type decision --text "The final artifact is separate from shaping notes."
```

Append with an effect:

```bash
python3 -S ./notes.py append --type gate --text "Persistence model is deferred." --effect "Do not finalize the artifact until this is resolved."
```

View recent notes:

```bash
python3 -S ./notes.py tail --limit 5
```

Get a simple summary:

```bash
python3 -S ./notes.py summary
```

Export the session:

```bash
python3 -S ./notes.py export
```

## Storage behavior

By default, `notes.py` writes session files next to itself.

If the project is extracted as:

```text
/mnt/data/memory-assisted-shaping/
```

then the live note log will be:

```text
/mnt/data/memory-assisted-shaping/session_notes.jsonl
```

You can override the directory if needed:

```bash
python3 -S ./notes.py --dir /path/to/session append --type decision --text "..."
```

## Design boundaries

The note layer is not a user-facing document.

It is there to help GPT avoid drift during long shaping sessions.

The protocol keeps shaping separate from final artifact creation. 🧩➡️📦

A final artifact should be clean, standalone, and produced only after explicit approval.

</details>