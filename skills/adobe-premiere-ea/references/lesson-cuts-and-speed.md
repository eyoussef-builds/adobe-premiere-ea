# Screen-recorded lessons and pitch-preserving speed

Use for reviewed failed-take removal, pause tightening, lesson splitting and requested speed changes. This is an adaptation guide, not a bundled universal lesson renderer or Premiere project patcher.

## Review before cutting

Probe duration, exact rational frame rate, frame count, dimensions, color interpretation, audio channels/sample rate, stream offsets and disk space. Fingerprint the source. Never assume a new recording is 1080p60 or stereo 48 kHz.

Read [transcription.md](transcription.md). Prepare continuous analysis audio from source time zero. Transcribe the complete recording in bounded chunks with source offsets and a coverage ledger. Use independent recognition passes, then focused checks around user notes, disagreements and lesson boundaries. Preserve literal false starts in raw evidence: recognition can silently merge restarts or invent words. Word timestamps are approximate navigation, not authoritative cut positions.

For each proposed removal, record discarded wording, the complete retained restart, source range, reason and uncertainty. Interpret obvious reversed timestamp typos from neighboring context and record the correction. Preserve useful complete alternatives and uncertain speech. Do not manufacture missing clean takes.

Inspect screen context. Silent scrolling, typing, reading or file loading may explain the narration. Shorten waits while retaining the action and a readable destination hold. A lesson title can appear before the prior narration finishes: split by completed speech and the next opening, not a slide alone. Preserve final farewells and quiet endings.

## Protect complete words

Use VAD, waveform/energy and phrase context together. Conservative 0.25 s handles on each speech side are a useful lesson starting point. Calibrate against quiet/unvoiced endings; do not treat a fixed RMS threshold as proof of silence. Preserve deliberate pauses and screen reading time.

Find phrase boundaries, not just between-syllable gaps. Prefer complete clauses over splicing technical-word fragments. Build original-speed join previews with about 3–4 s outgoing and 4–6 s incoming context. Review every manual join against the original; listen when available and extend uncertain excerpts. Move a boundary or retain the full phrase when a syllable or grammatical premise is missing. ASR spelling cannot certify pronunciation.

Quantize a removal `[a,b)` at frame rate F as `[ceil(a*F), floor(b*F))`. Merge overlaps, subtract protected screen holds, and compute retained intervals. Verify retained and removed ranges partition the source exactly once. Keep exclusions reversible.

## Exact uniform speed

Keep source frames separate from original-speed and final timeline frames. Each clip needs source in/out, original timeline in/out, speed and retimed in/out; ends are exclusive. Use rational speed and a consistent rounding convention.

For requested 1.1×, retain source selection and compute boundaries from cumulative retained frames:

```text
retimed_in  = round(timeline_in / 1.1)
retimed_out = round(timeline_out / 1.1)
final_frames = round(total_retained_frames / 1.1)
```

Cumulative rounding avoids drift from rounding each length independently. Check adjacency, positive lengths and final duration. Maintain pitch; changing sample rate alone raises pitch. Uniform 1.1× does not authorize extra fast navigation sections.

## Native editable project

Read [premiere-handoff.md](premiere-handoff.md). Import original-speed cuts and retain both final-speed sequences and 100% backup sequences. Test speed behavior on a short AV clip in the installed Premiere version.

In a Premiere 26 test, an FCP7 `timeremap` import at 110% unexpectedly changed source OutPoint; importing at 1× then applying native speed preserved selection. GUI speed entry can also save a nearby duration-rounded value. Verify actual saved speed, source endpoints and output duration.

Prefer native controls or a supported API. If adapting native project internals, close and snapshot the agent-created project first, verify its version/schema, and touch only the intended new sequences. Do not patch an open project or overwrite newer user edits. On unfamiliar structures, stop that method and use supported controls.

Version-specific Premiere 26 observations to validate, not blindly apply:

- Resolve sequence track groups → track items → SubClip → VideoClip/AudioClip. Preserve `Clip/InPoint` and `Clip/OutPoint` source ticks.
- Premiere ticks are 254016000000/s. Derive ticks/frame and ticks/sample from actual rates; at 60 fps these are 4233600000/frame and at 48 kHz 5292000/sample.
- Timeline TrackItem Start/End reflect cumulative retiming; `Clip/PlaybackSpeed` is 1.1 for this request.
- AudioClip `Clip/MaintainAudioPitch=true` and AudioClip-root `AudioTimeScalerSettings={"m":2,"mp":true,"p":0,"t":0,"v":1}` were required in the tested schema. The scaler is not a track-item child.
- Compare integer ticks exactly. Check source identity, ranges, links, channels, pitch, speed, backups and no gaps. Default-valued parameters may be omitted; inspect keyframes/defaults before failing a check.

Separate imported mono tracks can sum through stereo routing. Compare an actual short native WAV export with the expected audio. Hard pan or pan-law compensation depends on that exact track layout; no universal gain correction applies.

Reopen in Premiere, inspect every lesson, save through the application and reverify the saved file. The bundled original-speed verifier is insufficient for retimed sequences; adapt it. Clear temporary In/Out marks and QA sequences in the delivery project. Restore video-export settings after audio-only checks.

## Efficient uniform-speed export

Prefer Premiere for complex effects/retiming. A manifest-driven FFmpeg/PyAV renderer can implement simple reviewed cuts at uniform speed; identify it accurately as an external render. The public bundle does not include a universal implementation. Invalidate caches when source, manifest or settings change.

Process one lesson at a time. Decode audio by PTS, preserving every retained sample and both channels. Seek earlier than needed and slice by timestamps. A PyAV seek to zero skipped the initial decoded audio frame in one source; decode from the beginning when necessary and verify coverage.

Concatenate retained PCM continuously, then apply tempo once. One tested filter pattern was `apad=pad_dur=0.25,atempo=1.1,apad,atrim=end_sample=N`, where N derives from final frames, output fps and sample rate. At 60 fps/48 kHz, N is final_frames×800; other rate pairs need rational accounting. Encode AAC once to avoid accumulated per-segment delay. Verify the final word is complete.

Preserve source YUV/color interpretation. For simple frame-dropping speed-up, use each retimed clip's cumulative output length and a validated source-frame mapping such as `min(source_out-1, source_in+floor(k*1.1))`. Decode from a preceding keyframe and confirm exact source indices. This samples pictures while continuous time-stretched audio carries the speech.

Choose compression by screen-text legibility and size; do not copy an arbitrary bitrate or force Rec.709 tags onto unknown footage.

## Verify actual delivery

For each actual MP4, probe format, rate, frame count, duration and audio configuration; fully decode AV with failures treated as errors. Check video PTS spacing. PTS=DTS is expected only for formats without reordered pictures.

Compare first/middle/last frames of every retained clip with the intended source mapping. Compare decoded audio with expected continuous pitch-preserved PCM channel by channel, overall and around every join. Handle silent windows without dividing by zero; investigate failures rather than loosening gates.

Extract checks from the compressed output around every join (about 4 s before/6 s after), plus opening/closing speech (about 14 s). Review against retained source speech, extending excerpts that themselves cut a word. Correct and rerender affected lessons if necessary.

Verify source hash and saved project against current manifests. Deliver MP4s, native project, source-to-final TXT/CSV reports, recoverable exclusions and a truthful verification record. Automated checks complement speech review; they are not a 100% semantic guarantee or proof of a full human listening pass.
