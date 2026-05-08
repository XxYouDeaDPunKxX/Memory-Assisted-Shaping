# Memory-Assisted Shaping

A lightweight ChatGPT Projects protocol that keeps long idea-shaping sessions structurally coherent: GPT follows real gates and source boundaries, uses append-only internal notes to avoid drift, and produces clean final artifacts only after approval.

## Why this exists

Long ChatGPT conversations can drift.

An example starts to look like a decision.  
A discarded path comes back later.  
A rough idea turns into a half-spec before it is ready.  
The final output starts carrying pieces of the messy conversation.

Memory-Assisted Shaping gives GPT a small way to keep the thread while one idea is being shaped.

The notes are not something you maintain.  
They are internal signals GPT can write in the background so it does not lose important decisions, open points, discarded paths, or changes in direction.

The final artifact is separate.  
It is produced only when the idea is clear enough and you explicitly ask for it.

## The basic idea

Use it when one idea needs more than a few turns.

GPT first helps shape the idea:

- what the idea is becoming
- which decisions are already clear
- which points are still open
- which paths were discarded
- where the real decision points are
- what should stay out of the final output

When something important should not be lost, GPT can save a tiny internal note.

Those notes are added, not rewritten.

Later, you can ask GPT to recap them:

- “What have you noted so far?”
- “Show me the open points.”
- “What decisions are already clear?”
- “What did we discard?”
- “Are we ready to produce the final artifact?”

The notes help GPT recover the thread.  
They are not the final product.

## How to use it with ChatGPT Projects

1. Put the protocol files in the ChatGPT Project Source.
2. Tell GPT to use Memory-Assisted Shaping.
3. Work normally.
4. Ask for a recap whenever you want.
5. Ask for a final artifact only when the idea is ready.

## Files

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

## When to ask for a recap

You can ask at any time.

Useful prompts:

- “Recap the internal notes.”
- “Show me the current shape of the idea.”
- “List decisions, open points, discarded paths, and artifact readiness.”
- “Before we continue, reconstruct the state from the notes.”
- “Are there any gates still open before we write the final artifact?”

GPT should not read and rewrite the notes after every turn.  
The notes stay in the background until you ask for them, request a checkpoint, or prepare a final artifact.

## Final artifacts

The final artifact is the clean output you eventually ask for.

It can be a protocol, spec, brief, pitch, design document, implementation handoff, or any other output that fits the idea.

The artifact should not contain the messy shaping process.

It should not include raw notes, discarded paths, or internal reasoning unless you explicitly ask for an audit-style document.

---

<details>
<summary>Technical details</summary>

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

The protocol keeps shaping separate from final artifact creation.

A final artifact should be clean, standalone, and produced only after explicit approval.

</details>
