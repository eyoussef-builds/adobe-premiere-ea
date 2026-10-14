# Usage and dependencies

## Start with the task

Provide the source path, output folder, language, intended lesson boundaries (if known), desired speed and deliverables. Say whether you want a plan first. Notes can be approximate; the agent should check the actual audio before deciding boundaries.

Examples:

```text
Review this screen recording using adobe-premiere-ea. Find abandoned attempts
and long empty gaps, retain useful reading/typing time, and give me a cut plan
with source timestamps, discarded wording, retained restarts and reasons.
```

```text
Transcribe each retained talking clip separately. Preserve dialect, English
terms and false starts. Deliver one TXT per clip, a CSV index and ZIP.
Do not change the timeline or add subtitles.
```

```text
Compare repeated takes. Keep distinct complete alternatives and exclude
unfinished attempts from active scope. Preserve all originals and record
how to recover every exclusion.
```

```text
Build five distinct scene orders from the active takes: proof first,
opportunity first, method deep dive, focused pitch and speaker story.
Use only recorded words. Give me editable Premiere sequences and actual
MP4 exports; add no graphics, music or website changes.
```

```text
Smooth this fixed black backdrop and remove the small background object.
Protect hair, face, body, hands, arms, chair and microphone. Show a short
gesture-heavy preview first and disclose any estimated foreground repair.
```

## Basic helper setup

Install [FFmpeg/FFprobe](https://ffmpeg.org/download.html) from a trusted distribution and make both available on PATH. Use an isolated Python environment outside this source repository for working files/models:

```sh
python3.12 -m venv /path/to/video-task/.venv
/path/to/video-task/.venv/bin/python -m pip install numpy torch silero-vad
```

Inspect and record installed versions. Platform-specific PyTorch wheels may require its official installation instructions. No paid ASR API is required by the bundled local helpers.

From `skills/adobe-premiere-ea/`:

```sh
python scripts/detect_pauses.py --input /path/to/source.mov --output-dir /path/to/video-task/cuts --sequence-name "Reviewed Speech Cuts"
```

Review `cuts.json`, `raw_speech` and `higher_energy_removed_intervals_to_review` against audio and screen context. Detection is a proposal. After adjusting the manifest to preserve full words and useful actions:

```sh
python scripts/build_sequence.py --workdir /path/to/video-task/cuts
```

This creates XML, `Cut Report.txt`, `Cut Report.csv` and `verification.json`. Import the XML into Premiere, check playback/audio, and save a new `.prproj` before:

```sh
python scripts/verify_premiere.py --workdir /path/to/video-task/cuts --project /path/to/video-task/Edited.prproj
```

The verifier targets the observed Premiere 26 original-speed structure. It reads source/project files and writes task verification, failing on unexpected structures. It is not a retime/effects/creative-quality verifier.

## Helper coverage

| Helper | What it actually does |
| --- | --- |
| `detect_pauses.py` | Local VAD proposals, speech margins, frame ranges, source fingerprint |
| `build_sequence.py` | Linked FCP7 XML plus complete chronological source/timeline reports |
| `verify_premiere.py` | Read-only original-speed native project/source/range/channel checks; writes a report |
| `prepare_transcripts.py` | Source-aligned mono analysis audio and exact retained-clip sample map |
| `recognize_clips.py` | Resumable Qwen or Whisper local recognition on Apple Silicon via MLX |
| `compare_transcripts.py` | Grouped Whisper word mapping and independent text disagreement flags |
| `package_transcripts.py` | Reviewed per-clip TXT, CSV index and verified ZIP |
| `build_options.py` | Scope-enforced scene-order XML and per-option manifests/scripts/reports |

Run a helper's `--help` for arguments. Do not use Python optimization (`-O`); some invariants use assertions. Use fresh output folders because several report builders intentionally replace their own generated files. Scripts do not overwrite original video media.

The local recognizer requires Apple Silicon MLX packages and separately downloaded model directories. See [transcription reference](../skills/adobe-premiere-ea/references/transcription.md) for versions, provenance and examples. Install only STT dependencies needed by your chosen backend. Other operating systems need adapted recognition code; the rest of the workflow can still be useful.

## Advanced work and handoff

Read the relevant workflow reference before splitting lessons, retiming, rendering, backdrop cleanup or polished production. These workflows require task-specific adaptation: the repository does not include a universal native retime patcher, final renderer, cleanup model pipeline, browser recorder or full Premiere controller.

Maintain a manifest separating original source frame ranges from final timeline ranges. Verify every join on actual output speech, every lesson's opening/closing, exact requested speed/pitch, frame count, PTS, full AV decode and audio channel alignment. For uncertain words, preserve more context and record the uncertainty.

Deliver requested MP4s, an editable native project, reports and recoverable exclusions. Clearly identify externally rendered graphics or MP4s, baked overlays and any remaining missing media/tool capability. Keep source files available for the project to reopen.
