# Privacy and public-package maintenance

This repository is a sanitized distribution of reusable editing knowledge and helpers. Only the public publisher handle and repository links identify its publisher. It deliberately excludes private media, transcripts, personal names/contact data, client examples/fees, business URLs, brand assets, room images, local workstation paths, account data and model caches.

A public skill and a private editing task are different artifacts. Running this skill creates reports with source filenames, absolute source paths and spoken content. Those outputs may be personal or confidential. Keep them outside this repository and review any delivery archive before sharing it.

## Before a public update

1. Stage only intended text/code files. Inspect added files, diffs and all reachable commit history. A later deletion does not erase an earlier leaked commit.
2. Search for home/volume paths, names, email addresses, private domains, credentials, client information, unique recording filenames and hidden metadata. Automated scans are complementary to reading the content.
3. Exclude media, task reports, local images, `.env`, model weights, virtual environments and caches. `.gitignore` helps prevent accidents; it does not make already tracked files private.
4. Use intentional public commit attribution, such as an account's GitHub noreply address, rather than an unintended private email. Check GitHub upload attribution settings separately.
5. Validate relative references, CLI help and synthetic smoke tests. Do not reuse private recordings as public fixtures.
6. Publish only after reviewing the actual staged tree. Inspect the resulting public repository and owner/visibility.

The bundled helpers run local media processing, with initial dependency/model downloads as needed. No telemetry or recording-upload service is configured. The agent host may send prompts, excerpts or tool outputs to its model provider; consult its settings. The skill does not change that policy or grant additional access.

Third-party software/models retain their own licenses. Report issues with synthetic examples and sanitized logs, not private source projects or credentials.
