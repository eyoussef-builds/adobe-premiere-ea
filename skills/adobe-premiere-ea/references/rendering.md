# Requested final video exports

Export only when requested. Preserve the editable Premiere project and original recording. For cuts-only sequences, keep the original framing, frame rate, color space and channel mapping. H.264/AAC MP4 with fast-start metadata is a practical local playback format. Choose compression for the source quality and available disk space rather than copying a fixed bitrate to every recording.

Prefer Premiere's exporter when the timeline contains effects, transitions, gain changes, speed changes, reframing or extra media. For verified pure source cuts, an FFmpeg render from the manifests can reproduce the edit efficiently. First compare every saved native sequence with its manifest using `verify_premiere.py`; never render a stale cut list over newer user edits. A native project, XML or successful render command alone does not establish that an exported video exists and plays correctly.

For reviewed multi-lesson screen recordings at uniform requested 1.1×, read [lesson-cuts-and-speed.md](lesson-cuts-and-speed.md) for the validated pitch-preserving render, retimed native-project checks and every-join speech review. That workflow is a tested exception for simple uniform speed; do not reuse the original-speed cache method below unchanged for retimed audio/video.

## Efficient cuts-only method

- Decode source audio once, preserving sample rate and channels. Slice sample-accurate source ranges into one continuous PCM track per option, then encode AAC once for that full track. Independently encoded AAC segments introduce encoder delay/padding and can accumulate gaps or drift when concatenated.
- Derive audio positions from source timestamps and stream offsets. The observed aligned 60 fps / 48 kHz recording has exactly 800 audio samples per video frame. This mapping is specific to those stream properties; fractional rates or offsets require an adapted mapping or native export.
- Encode each unique video source range once into an agent-owned cache, preserving exact frame counts. Use identical codec/profile/pixel/color parameters for all ranges. On macOS, VideoToolbox hardware H.264 can be substantially faster; access may require normal tool permission escalation. Do not change system settings to obtain it.
- Concatenate encoded video in manifest order without another video generation. Verify each range begins at its intended source frame and has `source_out - source_in` frames. Include exact range durations rather than relying on rounded container durations.
- For the tested 60 fps video-only cache, disabling B-frames makes one packet correspond to one displayed frame. With a 1/60000 time base, packet PTS/DTS and duration can be assigned as `N*1000`, `N*1000`, `1000` using FFmpeg's `setts` bitstream filter during assembly. Verify the output timestamps before relying on this approach; do not apply it blindly to reordered packets, different rates or codecs.
- Mux the assembled video and continuous audio, then apply fast-start metadata. Keep enough space for muxing and temporary files. Remove only agent-created caches after all deliverables pass verification; preserve user media, projects and prior work.

## Verify and deliver

Probe every actual MP4 for codec, dimensions, pixel format, frame rate, exact frame count, duration, sample rate and audio channels. Decode the entire file with errors treated as failures. Check monotonic, evenly spaced video timestamps and compare decoded audio with the expected continuous source slices, including windows around every join. AAC is lossy; use a meaningful correlation tolerance rather than byte equality.

Compare exported cut-boundary frames with their intended source frames to catch a wrong range, ordering error, dropped frame or framing change. Inspect representative start/middle/end frames in a contact sheet and sample playback. Record which checks ran; automated decode and correlation are not a full real-time creative listening pass.

Deliver direct links to all requested MP4s with durations, alongside the retained editable project. Update work status and export verification records. Do not label a project-only ZIP as a video package. A new video archive is optional and should not unnecessarily duplicate large files on a nearly full disk.
