# Install and use with 15 agents

Install the **complete** `skills/adobe-premiere-ea` directory, not only `SKILL.md`. Scripts and references are loaded as needed. Clone the repository first and run copy commands from its root. Commands below use a POSIX shell on macOS/Linux; Windows users can copy the same directory with Explorer or PowerShell. MLX recognition remains Apple Silicon only.

Before any copy, check whether that destination already contains `adobe-premiere-ea`. Preserve your existing version and deliberately merge/update it; the examples refuse an existing destination. Restart/reload the agent if discovery does not refresh. Installing in one location does not sync it to cloud/remote machines.

The setup locations below were checked against linked official documentation on 2026-10-14. They are **documentation-verified, not end-to-end tested in every harness**. Versions and managed policies can change discovery. Native skill support supplies instructions; actual editing still needs media access, Python/FFmpeg and Premiere control on the execution machine.

## 1. OpenAI Codex

Use the supported personal skill directory:

```sh
test ! -e "$HOME/.agents/skills/adobe-premiere-ea" && mkdir -p "$HOME/.agents/skills" && cp -R skills/adobe-premiere-ea "$HOME/.agents/skills/"
```

For a team/project, copy it into `.agents/skills/adobe-premiere-ea/` in that repository instead. Invoke `$adobe-premiere-ea`, or select it with `/skills` in CLI/IDE. In the desktop skill picker, select the installed skill. Alternatively ask `$skill-installer` to install `skills/adobe-premiere-ea` from this GitHub repository. Use a local session for local Premiere work; cloud sessions need their own accessible media/runtime. [Official skill documentation](https://developers.openai.com/codex/skills/).

## 2. Claude Code

```sh
test ! -e "$HOME/.claude/skills/adobe-premiere-ea" && mkdir -p "$HOME/.claude/skills" && cp -R skills/adobe-premiere-ea "$HOME/.claude/skills/"
```

Project alternative: `.claude/skills/adobe-premiere-ea/`. Invoke `/adobe-premiere-ea` followed by the task, or ask to use it by name. A personal local directory does not automatically install it into Claude web, Cowork or cloud sessions; follow those products' own account skill mechanisms. This guide targets local Claude Code with file/terminal access and separately available Premiere automation. [Official Claude Code skills](https://code.claude.com/docs/en/skills).

## 3. OpenClaw

From this repository, install the local skill directory into the active OpenClaw workspace:

```sh
openclaw skills install ./skills/adobe-premiere-ea --as adobe-premiere-ea
openclaw skills list
```

Inspect any install/trust warning; do not bypass it blindly. Manual alternative: copy the folder to `<active-workspace>/skills/adobe-premiere-ea/`. Ask: “Use the adobe-premiere-ea skill to review this recording.” Check eligibility with `openclaw skills check`. A remote Gateway or sandbox needs media and executable tools in its own execution environment; a path on your laptop is not sufficient. [Official skills guide](https://docs.openclaw.ai/skills), [CLI](https://docs.openclaw.ai/cli/skills).

## 4. Hermes Agent

Hermes documents installation directly from a GitHub skill subdirectory:

```sh
hermes skills install eyoussef-builds/adobe-premiere-ea/skills/adobe-premiere-ea
```

Inspect the community skill scan and verify the installed entry. Manual alternative for the default profile: copy the full directory into `~/.hermes/skills/adobe-premiere-ea/`; custom profiles may use another root. Ask Hermes to list available skills, then: “Use adobe-premiere-ea for this local recording.” If you instead use project discovery, follow Hermes' project trust flow. Keep its normal security checks enabled. [Official skills guide and GitHub install syntax](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/).

## 5. Cursor

```sh
test ! -e .cursor/skills/adobe-premiere-ea && mkdir -p .cursor/skills && cp -R skills/adobe-premiere-ea .cursor/skills/
```

Use this in the workspace where you will edit. Global alternative: `~/.cursor/skills/adobe-premiere-ea/`. In Agent chat type `/` and select `adobe-premiere-ea`, or ask to use it by name. Confirm its supporting references are actually read. Use local Agent for your local video; unsynced user skills and local disk paths do not automatically follow a Cloud Agent. [Official Cursor skills](https://cursor.com/docs/skills).

## 6. Grok Bot

Use an instruction-import workflow rather than assuming an undocumented filesystem skill directory. Send the public repository link and ask the Bot to read `skills/adobe-premiere-ea/SKILL.md` plus the needed references, retaining the helpers. Then ask it to save the adapted method as a skill called “Adobe Premiere EA.” Verify the saved entry in **Connect apps → Your plugins → Manage plugins and skills → Private skills**, and reference it with `/` in the desktop composer where available.

This is an adaptation using Grok Bot's documented reusable-skill feature, **not verified native import of this repository's SKILL.md format**. Its cloud computer does not thereby gain access to your local Premiere or local video. Use it for plans/code unless suitable access exists. [Official skills and routines](https://docs.x.ai/grok-bot/skills-routines-and-automations), [files and results](https://docs.x.ai/grok-bot/files-and-results).

## 7. OpenCode

```sh
test ! -e .opencode/skills/adobe-premiere-ea && mkdir -p .opencode/skills && cp -R skills/adobe-premiere-ea .opencode/skills/
```

Global alternative: `~/.config/opencode/skills/adobe-premiere-ea/`. Ask: “Load the adobe-premiere-ea skill and review this local video.” OpenCode exposes discovered skills through its skill tool; verify the name is present and read supporting files when needed. Ensure tool permissions allow the requested local work. [Official OpenCode skills](https://opencode.ai/docs/skills/).

## 8. GitHub Copilot

```sh
test ! -e .github/skills/adobe-premiere-ea && mkdir -p .github/skills && cp -R skills/adobe-premiere-ea .github/skills/
```

Use local IDE Agent mode or Copilot CLI and explicitly ask to use `adobe-premiere-ea`. Personal alternative: `~/.copilot/skills/adobe-premiere-ea/` where supported. Copilot's cloud agent can read repository skills but cannot reach your desktop Premiere automatically. Skill availability varies by product and organizational policy; check the skill is discovered in the specific client. [Official Copilot skills and locations](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills).

## 9. Gemini CLI

```sh
test ! -e "$HOME/.gemini/skills/adobe-premiere-ea" && mkdir -p "$HOME/.gemini/skills" && cp -R skills/adobe-premiere-ea "$HOME/.gemini/skills/"
```

Project alternative: `.gemini/skills/adobe-premiere-ea/`. Start Gemini CLI in the video workspace, inspect available skills with its skills controls, and ask: “Use adobe-premiere-ea to review this recording.” Keep activation/permission prompts in place. Its local terminal can support helper execution; Premiere interaction still needs a suitable authorized tool. [Official Gemini CLI Agent Skills](https://geminicli.com/docs/cli/skills/).

## 10. Windsurf / Cascade

```sh
test ! -e .windsurf/skills/adobe-premiere-ea && mkdir -p .windsurf/skills && cp -R skills/adobe-premiere-ea .windsurf/skills/
```

Ask Cascade to use `adobe-premiere-ea` and confirm discovery. Current official docs redirect to Devin Desktop and retain `.windsurf/skills/` as a legacy-compatible workspace location; the new preferred workspace root is `.devin/skills/`. A documented global location is `~/.codeium/windsurf/skills/`. Follow the location appropriate to your installed version. [Official Cascade skills documentation](https://docs.windsurf.com/windsurf/cascade/skills).

## 11. Cline

```sh
test ! -e .cline/skills/adobe-premiere-ea && mkdir -p .cline/skills && cp -R skills/adobe-premiere-ea .cline/skills/
```

Global alternative: `~/.cline/skills/adobe-premiere-ea/`. Check Cline's skill controls/settings if discovery is unavailable, then ask it to load `adobe-premiere-ea`. Use the mode with tools enabled for implementation, after any requested review plan. Linked supporting files are needed in addition to the entrypoint. [Official Cline skills](https://docs.cline.bot/customization/skills).

## 12. Roo Code

```sh
test ! -e .roo/skills/adobe-premiere-ea && mkdir -p .roo/skills && cp -R skills/adobe-premiere-ea .roo/skills/
```

Global alternative: `~/.roo/skills/adobe-premiere-ea/`. Ask Roo to load the named skill in a mode with the tools needed for the task. Roo also has mode-specific roots; use the generic root above unless you intentionally want mode scoping. Supporting reference files must be explicitly read as needed. [Official Roo skill tool documentation](https://roocodeinc.github.io/Roo-Code/advanced-usage/available-tools/skill/).

## 13. Aider

Use read-only context rather than claiming native skill discovery:

```sh
aider --read skills/adobe-premiere-ea/SKILL.md
```

Inside chat, add the specific relevant reference with `/read skills/adobe-premiere-ea/references/lesson-cuts-and-speed.md` (or another workflow). Ask Aider to implement task-specific tools using that workflow. Add supporting helper scripts as read-only context when needed. Run generated commands yourself or through Aider's supported command workflow. Aider is useful for scripts/manifests; this repository does not give it a native Premiere UI controller. [Official read-only context guidance](https://aider.chat/docs/usage/tips.html).

## 14. Amp

```sh
test ! -e .agents/skills/adobe-premiere-ea && mkdir -p .agents/skills && cp -R skills/adobe-premiere-ea .agents/skills/
```

Ask Amp to reload/list its skills and use `adobe-premiere-ea`. Current Amp also documents `amp skill add <source>` for installation and `amp skills list` for inspection. A project-local copy avoids assumptions about personal/workspace repositories. Use actual local tool/media access for editing. [Official Amp skills and discovery](https://ampcode.com/docs/customize/skills).

## 15. Goose

```sh
test ! -e .agents/skills/adobe-premiere-ea && mkdir -p .agents/skills && cp -R skills/adobe-premiere-ea .agents/skills/
```

Global alternative: `~/.agents/skills/adobe-premiere-ea/`. Keep the built-in Skills extension enabled. Use `/skills adobe-premiere-ea` or ask Goose to apply it; inspect with `goose skills list` in versions supporting that command. Its Developer/tool extensions must separately provide local execution and any Premiere interaction. [Official Goose skill guide source](https://github.com/aaif-goose/goose/blob/main/documentation/docs/guides/context-engineering/using-skills.md).

## Fallback for any other coding agent

Clone/download this repository into an accessible workspace and send:

```text
Read skills/adobe-premiere-ea/SKILL.md as the workflow for this task.
Load only the relevant linked references and inspect helpers before running.
Use my supplied source/output paths. Report unavailable tools accurately.
Review the recording and propose source-timestamped cuts first.
```

For chat-only agents, attach the entrypoint and relevant references if file reading is unavailable. That enables advice, not local media access or Premiere automation. Never solve missing capabilities by silently replacing an editable Premiere project with an XML file or a claimed export.
