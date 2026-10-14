# Non-destructive take selection

Apply when the user asks to compare repeated talking scenes and remove unfinished, awkward or unprofessional attempts from future work scope. Preserve source media, all transcripts and existing edits. Selection is a reversible editorial decision, not permanent deletion.

Use the verified clip map and reviewed transcripts. Assess a **logical take**, not just a VAD fragment: a short clip may supply the subject or finish a sentence in its neighbor. Natural continuations must stay together. An incomplete start followed by a restarted attempt is different from a sentence continuing across a genuine pause.

Keep complete takes with different useful wording on the same topic. Do not deduplicate by semantic similarity alone. For equivalent wording, choose a representative using available delivery/presentation evidence and preserve the alternate. Normal dialect, code switching, rhetorical emphasis or an uncertain ASR spelling is not sufficient evidence of an unprofessional performance.

Exclude clear abandoned starts, aborted words, missing completions, misspoken restarts, awkward invitations and correction-heavy attempts from active scope. If a long take contains useful material but requires a tightening edit, record it as recoverable outside the current clean-take scope. Do not pretend it is ready, or discard its existence. A short, complete pickup can remain as a contextual alternate when its intended use is clear.

Review recognition disagreements before treating them as stumbles: a recognizer can omit real repetitions or invent them. Inspect source presentation and audio when possible. Contact sheets and audio-level metrics support a sampled check; they do not prove full real-time audiovisual review or flawless delivery. Record the actual coverage honestly.

## Persist the scope

Keep original clip IDs and exact original source/Premiere ranges. Save:

- `active-scope.json`: source path, source manifest fingerprint, active clip numbers/ranges, grouped logical scenes, rationale and review basis.
- `excluded-scope.json`: every excluded original clip, reason, retained alternatives and original transcript/source references. Mark all recoverable.
- A complete TXT/CSV decision report accounting for every clip once, plus a repeated-scene comparison by topic.
- Optional active-only transcript copies and a small ZIP for the user; exclude source video, caches and model weights.

The sequence builder expects `active_clip_numbers` and `active_clips`, each containing `clip`, `source_in`, `source_out` and `text`, along with `source`. A useful scene schema is:

```json
{"scene": 1, "title": "Audience pitch A", "original_clip_numbers": [13, 14], "note": "Natural continuation; keep together"}
```

Validate active/excluded sets are disjoint, cover the original retained clips exactly once, and retain all frame ranges. Their duration sums must match the original cut manifest. Verify active transcript copies against originals. Record preservation hashes when claiming originals/projects remained unchanged.

Update the task's work-status record to point to the active manifest and use this set by default on subsequent work. Do not automatically add excluded takes back for a script merely because the wording is convenient. Restoration or repair needs the user's request or a clearly applicable new instruction. A take-selection-only request need not change Premiere.
