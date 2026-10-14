# Premiere handoff

Use an available Premiere connector/API when suitable, otherwise computer use. Native macOS scripting/input synthesis is an alternative only when the current session explicitly authorizes it; this skill does not grant permissions.

## Import and save

Create a named project in the requested folder or a separate sequence in an existing project. Commit text edits and verify the filename: AX `setValue` once appeared successful while Premiere created `Untitled.prproj`. Clicking the field, selecting its contents, pasting and committing worked; Save As recovered the name.

Import the generated FCP 7 XML once. On macOS, opening the exact XML with the installed Premiere application through Launch Services successfully imported it into the active project. File > Import also works. Inspect the bin before retrying to avoid duplicate sequences. Open the imported sequence and save the `.prproj`.

## UI recovery observed in Premiere 26

- An app screenshot does not establish foreground focus for coordinate/keyboard input. Prefer AX elements and fresh state; guard foreground focus when using authorized native input.
- A native Import dialog remained open while the main-window AX tree and screenshot omitted it. Opening XML directly imported the sequence behind that dialog, so timeline clicks were blocked. A full native desktop capture exposed it; Cancel dismissed it. Check hidden modal windows before repeating input or restarting the app.
- Screenshot cropping and global desktop coordinates can differ. Use coordinates from the actual controlled surface, not a guessed offset.
- Sending `activate` directly to Premiere through AppleScript timed out. Launch Services/NSRunningApplication activation and System Events Accessibility actions avoided that AppleEvent dependency. System Events File > Save worked without broadcasting keys into another app.
- Re-check installed application metadata if a native bundle identifier is needed. The tested installation used `com.adobe.PremierePro.26`; do not hardcode that for other versions.

These are recovery options when the corresponding issue is observed, not mandatory actions. Do not modify privacy settings or global Premiere preferences without applicable authorization.

## Checks

Verify retained and removed ranges partition the original, video/audio source and timeline ranges match, and the timeline has no gaps/overlaps. Stereo must retain distinct original left/right channels with a stereo master at the original sample rate; inspect routing/mix if the importer changes interpretation. Mono remains mono.

Verify the saved `.prproj`, not just the generated XML. `verify_premiere.py` reads the gzip-compressed XML used by the tested Premiere 26 version, resolves the intended sequence's track groups, and fails on unfamiliar structures rather than silently accepting them. Also verify original-picture playback, the displayed duration, linked editing, and representative quiet/unvoiced speech boundaries. Structural checks do not prove perfect speech extraction.

Consult primary references only when needed:

- [Apple FCP 7 XML elements](https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/FinalCutPro_XML/Elements/Elements.html): source/timeline ranges, file IDs, audio-only `groupindex`, output channels.
- [Apple encoding examples](https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/FinalCutPro_XML/Basics/Basics.html): linked video/stereo audio.
- [Silero VAD](https://github.com/snakers4/silero-vad): local model implementation and parameters.
