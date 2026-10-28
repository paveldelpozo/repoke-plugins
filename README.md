# repoke plugins

Official plugins for [repoke](https://github.com/paveldelpozo/repoke): tools that update themselves without being package managers, which repoke then checks and upgrades like any other.

| Id | What it updates | Needs | Tested on |
|----|-----------------|-------|-----------|
| `omz` | oh-my-zsh, when its branch is behind the remote | git, zsh | macOS |
| `vscode` | VS Code extensions with a newer stable release; also `export` and `init` | code, python3 | macOS |

## Install

```sh
repoke plugin search          # what is available
repoke plugin install vscode  # shows the code, asks, then copies it into ~/.local/bin
repoke plugin remove vscode
```

Executable plugins go to `~/.local/bin`, which has to be on your PATH. You can also copy a file from `plugins/` by hand.

A plugin runs with your user's permissions. `repoke plugin install` shows its code before installing it; read it.

## Writing one

The protocol and the TOML format are in [repoke's docs/plugins.md](https://github.com/paveldelpozo/repoke/blob/main/docs/plugins.md). A plugin here:

- lives in `plugins/<id>/` and is listed in `index.toml`;
- needs nothing beyond what `requires` says, and checks for it in `detect`;
- never prompts, and keeps `describe` instant;
- passes `scripts/check.sh` and has been run against the real tool, noted in the table above.

Planned: tpm (tmux), zinit and antidote (zsh), lazy.nvim and vim-plug, gcloud components. Pull requests are welcome once each has been tried on a machine that has the tool.

## License

Licensed under either of [Apache License, Version 2.0](LICENSE-APACHE) or [MIT license](LICENSE-MIT), at your option.
