# Adobe Premiere EA

Turn a local recording into reviewed speech cuts, separate transcripts, better take selections and editable Adobe Premiere sequences—with checks that distinguish a finished export from a project file.

An open agent skill for course recordings, screen lessons and talking-head videos. It packages practical editing instructions, eight Python helpers and nine focused workflow references. It is a community project, unaffiliated with Adobe, and is not a Premiere extension or an MCP server.

## What it helps an agent do

- Propose silence cuts while protecting speech starts and endings.
- Review failed/repeated takes without permanently deleting footage.
- Transcribe retained scenes separately, with source and timeline indexes.
- Build alternative scene orders from the available recorded words.
- Prepare lesson splits and requested speed changes, including 1.1× with preserved pitch.
- Import linked video/audio into Premiere and save a genuine editable `.prproj`.
- Verify actual MP4 exports, source mapping, audio and cut joins.
- Plan requested backdrop cleanup, browser demonstrations, Arabic typography and vertical reels.

The advanced production workflows are instructions to adapt, not one-command bundled renderers. No workflow guarantees perfect speech detection, transcription or foreground extraction.

## Give it to your agent

Copy this message into your coding agent:

```text
Get the Adobe Premiere EA skill from:
https://github.com/eyoussef-builds/adobe-premiere-ea

Read skills/adobe-premiere-ea/SKILL.md and install the complete skill folder
using your documented skill location, keeping scripts/ and references/.
If native skills are unavailable, read those files as task instructions.
Check that you can access my local video, run FFmpeg/Python and operate
Premiere before claiming you can deliver an editable native project.
Tell me any missing capability. Do not change unrelated settings.
```

Use a local agent session with access to your recording and Premiere. A cloud sandbox or ordinary chatbot cannot control your desktop merely because it has this repository's URL.

**[Installation and invocation for 15 agents →](docs/agent-installation.md)**

Includes Codex, Claude Code, OpenClaw, Hermes, Cursor, Grok Bot, OpenCode, GitHub Copilot, Gemini CLI, Windsurf, Cline, Roo Code, Aider, Amp and Goose. Native skill discovery and instruction-file fallbacks are clearly distinguished. These are documentation-based setup guides, not a claim that this package was executed end to end in all 15 products.

## Quick start

```sh
git clone https://github.com/eyoussef-builds/adobe-premiere-ea.git
cd adobe-premiere-ea
```

Install the whole `skills/adobe-premiere-ea/` folder in your agent's skill directory using the linked guide. No model weights, video files, credentials or Premiere license are included.

Then ask, using actual local paths:

```text
Use adobe-premiere-ea to review /path/to/recording.mov.
Put work in /path/to/output-folder. Propose cuts for abandoned takes and
unnecessary pauses, with original timestamps and reasons. Preserve words
and useful screen actions. Give me the plan before editing.
```

After reviewing the plan:

```text
Apply the agreed cuts. Export the lessons at exactly 1.1× with pitch preserved.
Save an editable Premiere project and original-speed backup sequences.
Review every cut join against source speech and check the actual exports.
Deliver the MP4s, .prproj, source-to-final reports and any unresolved notes.
```

More examples and helper commands: **[Usage and requirements](docs/usage.md)**.

## Requirements and limits

| Operation | Needs |
| --- | --- |
| Read/edit plans | Agent file access; supplied media or transcripts |
| Basic local pause analysis | Python 3.12, NumPy, PyTorch, Silero VAD, FFmpeg/FFprobe |
| XML, reports and transcript packaging | Python 3.12 standard library; FFprobe for sequence options |
| Bundled local ASR | Apple Silicon macOS, MLX packages and separately downloaded models |
| Native editable project | Installed/licensed Premiere and host-supported UI/API automation |
| Advanced speed/export/cleanup | Workflow adaptation and additional tools as described in references |

Basic helpers expect aligned, progressive, square-pixel CFR footage with mono/stereo audio. Native project verification targets the observed **Premiere 26** schema and original-speed sequences; other versions, effects and speed changes require adapted checks. Keep source media available for relinking.

Installing a skill grants no new permissions. Follow the host's normal approval and access rules. Local processing avoids uploading recordings to an ASR service, but the agent provider may still receive task text or tool outputs. Review private task artifacts before sharing them.

## Public-package privacy

This distribution contains reusable code and generalized instructions. It excludes private recordings, transcripts, client details, brand assets, room images, model caches, private URLs and workstation paths. The publisher's public GitHub handle appears intentionally for repository links and licensing. The original private skill and projects are separate.

Generated task reports can contain source paths and spoken personal information; they are not automatically safe to publish. See [privacy and maintenance](docs/privacy.md).

## Validation

```sh
python3 -m unittest discover -s tests -v
```

The synthetic smoke tests require FFmpeg/FFprobe and exercise XML/range invariants, option scope, audio slicing and transcript archive integrity. They do not run paid software, download models, certify speech decisions or validate all agent integrations.

MIT licensed. Adobe Premiere and third-party tools/models retain their own licenses.
