# Fixed-camera backdrop and object cleanup

Use only when requested. Keep the real room and protected foreground; background replacement and full-person extraction are separate work. The public bundle describes the method but includes no scene-specific cleanup renderer, masks, model weights or room assets.

Inspect frames covering largest gestures, blur and target-object occlusions. Recheck resolution, mirroring, crop, camera movement, lighting and backdrop motion. Rebuild or track masks for the current shot. A static plate is unsuitable for an uncorrected moving camera.

1. Preserve the selected edit and native project. Work from verified source ranges in a fresh folder.
2. Choose a clear reference frame. Make separate feathered masks for cloth and unwanted objects. Protect face, hair, body, hands, arms, microphone, chair and furniture that should remain. Use a generous union of observed motion, not one static body outline.
3. Smooth only permitted backdrop pixels with a low-contrast plate or gentle dark gradient. Retain natural tonal variation and feather boundaries. Restore confident foreground from original source pixels.
4. Fill unobstructed object areas with matching background. Around overlaps, a local background matting model, reference differences and hand context can aid segmentation. Recalibrate crops and thresholds for the shot; landmarks are hints, not ground truth.
5. Review blur separately. Subtracting bright background luminance from uncertain translucent foreground can cause dark holes. An estimated soft repair may look more natural but cannot recover provably exact obscured pixels. Disclose it and do not silently reshape a hand when exact preservation is required.
6. Remove detached remnants narrowly, protecting fingertips and small real objects. Component-size or skin-color thresholds do not generalize across resolution, exposure or skin tones.
7. Render with source color interpretation and consistent AV timing. Prefer one final video encode; preserve unchanged audio without reencoding when feasible.

Difference keys can mistake cloth movement for foreground; person matting can retain object ghosts or lose fast hands. More aggressive removal is not automatically cleaner. Map annotations through each clip's **source** frames, not unrelated timeline indices.

Optional implementation starting points: [BackgroundMattingV2](https://github.com/PeterL1n/BackgroundMattingV2) and [MediaPipe](https://github.com/google-ai-edge/mediapipe). Review their code/model licenses and host compatibility; they are separate dependencies, not bundled integrations.

Verify actual export duration/frame count, full AV decode, color, audio alignment and protected foreground. Review furniture edges, hair, fingertip gaps, fastest gestures and occlusions in motion. Compare before/after source-aligned frames, including unchanged regions. State uncertain intervals and whether a full playback review occurred. Deliver the preview and describe whether cleanup is baked into media or editable as native effects.
