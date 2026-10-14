# Separate transcripts for retained clips

Use current verified `cuts.json`, keeping clip IDs and frame ranges fixed. Inspect the saved sequence if the user edited it since the manifest. Transcription alone does not authorize timeline changes or captions. Helpers expect one aligned source, original-speed clips and a contiguous chronological timeline; adapt multi-source, VFR, offsets and speed changes.

Transcribe as spoken, including dialect, code switching, repetitions, false starts and incomplete attempts. Do not summarize, translate, silently correct claims or substitute expected script wording. Normalize spelling only when it preserves the spoken words.

## Local preparation

Use a fresh output folder and isolated environment. `prepare_transcripts.py` extracts mono PCM16 16 kHz analysis audio, concatenates retained intervals and saves an exact sample/frame map. A supplied WAV must begin at original source time zero with matching alignment.

The bundled recognizer uses **MLX on Apple Silicon macOS**; it is not a Windows/Linux backend. A tested configuration used Python 3.12, mlx 0.32.3, mlx-whisper 0.4.3, mlx-audio 0.5.8 and transformers 4.57.6, plus NumPy, SoundFile and CFFI. These record a working combination, not a requirement to downgrade a working installation. On other platforms use a suitable local backend and retain equivalent mapping/provenance.

Public model examples:

- `mlx-community/Qwen3-ASR-1.7B-4bit`, revision `78a389c776a5483b2d0d4ea5494e11012e0d6159`.
- `mlx-community/whisper-large-v3-mlx-8bit`, revision `04ca5b03c22d72ddf4f4b2d808a28bf9902fb71a`.

Download from the model's official Hugging Face repository, verify required weights/config/tokenizer files and license, and record revision. Weights are not bundled. First download needs network; recognition uses local model paths with offline mode. Check memory and disk first; quantized models can avoid severe swap pressure. Run larger passes sequentially on constrained hosts.

From this skill directory, replace path placeholders:

```sh
python scripts/prepare_transcripts.py --manifest /path/to/cuts/cuts.json --output-dir /path/to/transcripts
python scripts/recognize_clips.py --workdir /path/to/transcripts --backend qwen --model /path/to/qwen-model --run qwen-clips --language Arabic
python scripts/recognize_clips.py --workdir /path/to/transcripts --backend whisper --model /path/to/whisper-model --run large-v3-8bit --language ar --group-seconds 120
python scripts/compare_transcripts.py --workdir /path/to/transcripts --primary-run qwen-clips --comparison-run large-v3-8bit
```

Change language for other recordings. Qwen runs per clip; Whisper groups by bounded duration for context. Test with `--max-items 1`, then resume only when input/map/model/settings match. A long individual clip may need further acoustic chunking. Confirm full result coverage; started processes do not prove completion.

Use `--clips 1,2` for focused individual checks; the comparison helper maps grouped Whisper word results, so individual check outputs need separate review. Do not assume a successful ASR pass provides accurate forced alignment. The inspected MLX Whisper version did not implement beam search; avoid `beam_size` unless supported in your installed version.

## Review and package

Compare all clips, focusing on technical terms, names, numbers, omitted repetitions, dense/zero-duration timings and short sounds. Confidence is evidence, not proof; high-confidence hallucinations exist. Check disagreements against original audio and independent recognition. Use supplied or verified spelling for clearly spoken names; never infer speech from biography or scripts.

Mark unresolved wording explicitly, such as `[unclear]` or a language-appropriate equivalent. Preserve aborted words and tiny clips in the index. Create `reviewed-corrections.json` with every clip number:

```json
{
  "1": {"text": "The reviewed words as spoken.", "reason": "Material corrections and evidence.", "uncertainties": []},
  "2": {"text": "[unclear]", "reason": "Recognition disagreement.", "uncertainties": ["Needs source-audio review."]}
}
```

```sh
python scripts/package_transcripts.py --workdir /path/to/transcripts --reviewed /path/to/transcripts/reviewed-corrections.json
```

Deliver separate `clips/clip-NNN.txt`, `Clip Index.csv`, `All Talking Clips.txt` and `Talking Clip Transcripts.zip`. Check exact clip count, nonempty text, source/timeline ranges, ZIP integrity and uncertainties. Reports distinguish nominal NDF frame labels from real-time milliseconds. Outputs contain the user's transcript and local source paths: keep task artifacts private unless publication is explicitly requested. Exclude audio, model caches and unrelated files from transcript archives. State recognition/review coverage honestly.
