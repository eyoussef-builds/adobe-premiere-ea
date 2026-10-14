# Script-guided sequence options

Use when the user asks for alternative scene orders or video cuts based on scripts. Confirm scope from the actual request: a cuts-and-order-only task uses the original picture/audio, without new graphics, B-roll, music, backgrounds, captions, synthetic speech or website changes. Do not publish or add the options to a landing page unless asked. Save separate native Premiere sequences/projects while preserving prior edits.

## Plan from available speech

Read the active-scope manifest before planning. Match script beats to recorded wording; never manufacture a missing line or silently restore an excluded take. Keep clean continuations together. Record script gaps: unavailable benefits, live-session details, income promises, disclaimers and visual directions are not magically present in the footage. Similar wording is not always an exact equivalent—e.g., “there is no magic button” does not literally say “results are not guaranteed.”

Build genuinely distinct orders rather than shuffling the same paragraphs arbitrarily. Useful persuasive structures include:

- **Proof first:** tangible work → audience → credibility → specific examples → why a method → learning path → offer/support → CTA.
- **Opportunity first:** practical opportunity → system → experience/proof → method → offer → realistic expectations/CTA.
- **Method deep dive:** audience → experience/proof → objection → concrete idea/specification/tasks/tests/deployment example → resources → CTA.
- **Focused pitch:** compact proof/audience/credibility → essential method and beginner fit → offer → CTA.
- **Founder story:** relevant experience → actual products → visitor’s goal → method → resources/income paths/support → CTA.

Choose the count requested by the user and explain why each option exists. Keep proof early for a cold visitor when footage supports it. Put examples of the speaker's past client fees in that context; do not turn them into a viewer income promise. Omit unsupported attributed quotes or record their verification gap rather than presenting an unverified celebrity claim as authority. Do not add unrecorded disclaimers, prices or promises through generated speech or text in a cuts-only task.

Avoid multiple introductions, duplicate income figures or several CTAs inside one option merely because all the takes are good. It is acceptable for options to share footage. Within each option, every jump should preserve the sentence, referent, pronoun, tense and causal flow. Resolve “because,” “then,” “both,” “this project” and unfinished conditional statements in their new context. Revisit the order if the join relies on a removed premise.

## Build and verify

Use `scripts/build_options.py` with the verified cut manifest, approved active scope and an editorial plan. It enforces active clip membership, parent-contained integer-frame trims, no overlapping reused footage within an option, matched CFR rate, mono/stereo audio and linked A/V ranges. It writes one combined FCP7 XML, per-option manifests/scripts/CSV maps and a summary. It does **not** create a native Premiere project or certify creative quality.

```json
{
  "source": "/path/to/source.mov",
  "options": [{
    "slug": "01-proof-first",
    "name": "Option 01 - Proof First",
    "script_anchor": "User script 2",
    "recommended": true,
    "intent": "Explain the business/creative purpose.",
    "beats": [{"label": "Hook", "clips": [{"clip": 8}]}]
  }]
}
```

For a subclip, add integer `source_in`, `source_out` and the actual trimmed `text` to the clip entry. The source range must stay within its active parent. Use word timings as approximate navigation, then check the source boundary and spoken phrase. Re-recognition can catch stray syllables, but does not prove a flawless cut. If a precise trim is uncertain, retain the original complete phrase or choose a cleaner join. Do not use the entire parent transcript for a shorter source interval.

```sh
python scripts/build_options.py --manifest CUT_FOLDER/cuts.json --active-scope SELECTION_FOLDER/active-scope.json --plan PLAN.json --output-dir OPTIONS_FOLDER --ffprobe /absolute/ffprobe
```

Read [premiere-handoff.md](premiere-handoff.md) for application handoff. A separate copy of the verified original project can preserve the original sequence alongside the new options. Import the combined XML once into the intended active project, open the options and save a `.prproj`. Check the current active project title before import/save. The original source and original project must not be overwritten.

If a revised XML is needed after import, avoid blindly importing it again and creating duplicate names. Preserve a native backup of existing work first. Close/rebuild only an agent-created saved project when current UI and disk evidence establish that no unsaved/user changes will be lost. Never dismiss a save prompt to discard changes. Respect any automatic-approval rejection; resolve its stated risk with evidence or a safer approach before retrying.

Run the existing native verifier for every option:

```sh
python scripts/verify_premiere.py --workdir OPTIONS_FOLDER/01-proof-first --project OPTIONS_FOLDER/Options.prproj
```

Verify all intended native sequences exist exactly once, every V1/A1/A2 source/timeline range matches its manifest, media paths resolve to the original, source channels remain distinct and the sequence/master audio configuration is correct. Also check online picture, visible duration, waveforms, representative playback and joins. Structural verification is not a full listening pass or proof of persuasive impact. Leave the recommended option open and the others easy to find.

Deliver the native project, a concise comparison with exact durations and beat/order maps, each option's assembled transcript and script-gap notes. Render final videos only if requested. State the creative recommendation as a judgment, not a proven conversion result. Update work status and record what was actually tested; when asked, save reusable implementation here rather than hard-coded clip IDs or decisions from one recording.

## Observed Premiere 26 UI details

- In the Project search field, AX `setValue` focused/cleared the field without entering the supplied text. A normal click, select-all and paste entered it correctly; verify the filter visibly applied.
- Filter by an exact sequence name, then use a fresh screenshot to open its row. Clear the filter or use a common option-name prefix afterwards so the user can see all choices.
- Opening a sequence and checking the Program Monitor established its name and duration. Save native project changes separately from workspace/tab state.
