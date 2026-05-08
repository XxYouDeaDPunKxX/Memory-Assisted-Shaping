# NOTE I/O CONTRACT

MODE: AI_ONLY
SCOPE: GPT_TO_PYTHON_APPEND_ONLY_MEMORY_SIGNALS
TARGET_READER: MODEL_EXECUTION
OUTPUT_TYPE: I/O_CONTRACT


---

## 1. PURPOSE

This contract defines the live boundary between model reasoning and Python memory persistence.

Emit minimal memory signals.
Python owns append-only persistence.
The live conversation must not become file management.

This contract does not define shaping behavior.
The shaping protocol governs behavior.
This contract defines only I/O.

---

## 2. EXECUTION RULE

Run all Python note commands with `python3 -S`.

Do not use plain `python3` for note persistence commands.

Keep note commands stdlib-only unless OP explicitly approves dependencies.

Default storage is the package directory that contains `notes.py`.

When the system is distributed as a zip, the extracted root folder is the local working container for the active shaping session.

`--dir` is an optional override, not a live requirement.

V0 assumes one active writer per package directory.

---

## 3. LIVE WRITE MODEL

During live shaping, the model may send a memory signal to Python only when the shaping protocol allows it.

Send the smallest useful signal.

Emit means command execution, not chat text.

When a live signal is required and Python execution is available, run:

`python3 -S ./notes.py append --type <type> --text "<text>"`

Use `--effect` only when the effect changes later shaping or synthesis.

Default payload:

- type
- text
- optional effect

Do not send full reasoning.
Do not send a schema-complete record.
Do not read the note file before appending.

---

## 4. SIGNAL TYPES

Allowed live signal types:

- mode
- shape
- gate
- decision
- discard
- tension
- source
- artifact

No other live signal type is valid in v0.

If the signal does not fit one of these types, do not append.
Continue shaping.

---

## 5. PYTHON RESPONSIBILITY

Python adds:

- id
- timestamp
- session_id
- sequence number
- optional checksum

Python appends the record to the live append log.

Python returns the storage path in the receipt.

Python does not infer meaning.
Python does not reshape content.
Python does not decide importance.
Python does not rewrite prior records during live append.

---

## 6. RECEIPT

Python returns a short receipt only.

Receipt shape:

- ok
- note_id
- sequence number
- path

Do not return the full log after append.
Do not summarize the log after append.
Do not expose receipt to OP unless useful or requested.

A minimal OP-facing marker is valid only after a successful append:

`Memory: <type> appended.`

If Python execution is unavailable, no append marker is valid.
State once that append-only memory is not active.

If append fails, surface the smallest persistence error needed to avoid fake persistence.

---

## 7. LIVE READ RESTRICTION

During live shaping, the model must not:

- read the live note log every turn
- rewrite the live note log
- normalize the live note log
- repair the live note log by inference
- treat the note log as a checklist
- let memory persistence interrupt OP-facing shaping

Live memory is write-only from the model perspective.

---

## 8. READBACK COMMANDS

Readback is allowed only when:

- OP requests recap
- OP requests export
- OP requests checkpoint
- re-entry requires state recovery
- synthesis preparation requires consolidated state

Readback commands must not run automatically every turn.

Readback order:

1. `summary`
2. `tail` when recent context is needed
3. `export` only for OP-requested export, handoff, or full consolidation

---

## 9. COMMAND SET V0

Minimum command set:

- init
- append
- tail
- summary
- export

During live shaping, use append by default.

Use tail, summary, or export only under the readback conditions above.

---

## 10. COMMAND SHAPES

From the extracted package root:

`python3 -S ./notes.py append --type <type> --text <text>`

Append command:

`python3 -S notes.py append --type <type> --text <text>`

Append with effect:

`python3 -S notes.py append --type <type> --text <text> --effect <effect>`

Initialize session:

`python3 -S notes.py init`

Tail recent notes:

`python3 -S notes.py tail --limit <n>`

Summary:

`python3 -S notes.py summary`

Export:

`python3 -S notes.py export`

Optional directory override:

`python3 -S notes.py --dir <session_dir> append --type <type> --text <text>`

---

## 11. FAILURE CONDITIONS

The I/O boundary fails if you:

- writes memory files directly
- reads memory files during live shaping without a readback condition
- sends schema-complete records during live append
- uses note persistence as a checklist
- asks Python to infer shaping meaning
- uses plain `python3` for memory persistence commands
- lets persistence work dominate OP-facing shaping
- claims append-only persistence when Python execution is unavailable
- outputs a live memory signal in chat instead of running append when append is required and Python is available

---

## 12. SUCCESS CONDITION

The boundary succeeds when:

- the model follows OP-facing shaping without file-management drift
- Python receives only minimal signals
- Python appends deterministically
- live memory remains write-only from the model perspective
- recap and export remain explicit operations
- later reinterpretation can recover useful continuity from minimal signals
