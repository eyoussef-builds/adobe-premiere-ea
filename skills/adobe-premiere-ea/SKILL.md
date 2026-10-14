---
name: adobe-premiere-ea
description: Edit course and talking-head recordings for Adobe Premiere with reviewed speech cuts, transcripts, reversible take selection, scene orders, and verified exports. Use for editable Premiere video work, including screen-recorded lessons at requested speed with preserved pitch.
---

# Adobe Premiere EA

Deliver an editable `.prproj` referencing the original media, source-to-timeline reports, and actual video exports when requested. FCP7 XML is an interchange file, not a completed native project. This skill supplies instructions and helpers; the host must provide file/terminal access and a suitable way to operate Premiere.

## Choose the workflow

- Screen-recorded lessons, failed takes, lesson boundaries or speed changes: read [lesson-cuts-and-speed.md](references/lesson-cuts-and-speed.md).
- Separate talking-clip transcripts: read [transcription.md](references/transcription.md). Transcription alone does not authorize recutting or captions.
- Compare repeated takes without deleting media: read [take-selection.md](references/take-selection.md).
- Alternative script-guided scene orders: read [sequence-options.md](references/sequence-options.md).
- Final playable videos: read [rendering.md](references/rendering.md).
- Wrinkle smoothing or small objects on a fixed backdrop: read [room-background-cleanup.md](references/room-background-cleanup.md).
- Requested graphics, website demonstrations, camera moves or Arabic typography: read [course-production-style.md](references/course-production-style.md).
- Requested vertical excerpts and word captions: read [vertical-reels.md](references/vertical-reels.md).
- Application import, native project saving and structural checks: read [premiere-handoff.md](references/premiere-handoff.md).

Read only the references needed for the task. Advanced references describe methods to adapt; bundled scripts do not implement every operation automatically.

## Scope and defaults

Preserve originals and prior projects. Use the user's output folder and a fresh task subfolder. Preserve framing, source audio channels and speed for cuts-only requests. At a requested speed, maintain pitch and check the saved exact speed. Add graphics, background cleanup, captions, sound or publishing only within the current request.

Begin with local voice activity detection (VAD), not amplitude alone. Adjustable pause-cut defaults are **0.50 s minimum pause**, **0.20 s speech tail** and **0.15 s speech lead**. Review quiet speech, suspicious removals and joins. A silent screen action may need to remain visible. VAD and recognition cannot guarantee that every word is preserved.

Treat user timestamps as approximate navigation unless explicitly exact. Where a user requests a plan first, review and propose before editing; once authorized, complete the agreed work without asking again for routine implementation choices.

## Prepare basic cuts

Use Python 3.12 in an isolated environment, NumPy, PyTorch, Silero VAD, and FFmpeg/FFprobe on PATH. Do not install unrelated packages globally. Run these commands from this skill directory, substituting actual absolute input/output paths:

```sh
python scripts/detect_pauses.py --input /path/to/source.mov --output-dir /path/to/task --sequence-name "Source - Speech Cuts"
python scripts/build_sequence.py --workdir /path/to/task
```

Detection writes proposals to `cuts.json`; review and adjust before building the sequence. Helpers support aligned mono/stereo CFR footage at integer or standard NTSC rates. Matching reported frame rates alone do not prove CFR: inspect packet timing for uncertain footage. Adapt VFR, interlaced, rotated, offset or multichannel media rather than silently forcing these assumptions.

Frame ranges are start-inclusive/end-exclusive. TXT/CSV reports cover original chronology and edited timeline. Distinguish milliseconds (`HH:MM:SS.mmm`) from nominal non-drop-frame labels (`HH:MM:SS:FF`).

Import the XML, open the correct sequence and save a real Premiere project. Check online picture, duration, linked edits and audio routing. For the tested Premiere 26 original-speed schema:

```sh
python scripts/verify_premiere.py --workdir /path/to/task --project /path/to/task/Edited.prproj
```

This checks saved source/timeline ranges and source channels. It reads the project without changing it and writes a verification report. It does not validate speech, speed changes, arbitrary effects or unfamiliar Premiere schemas. Use adapted checks and actual native audio exports where appropriate.

Deliver project/report links, real clip/pause counts and durations, plus requested MP4s. State what was verified and any uncertainty; do not claim perfect transcription, full listening coverage or native editable graphics without evidence.
