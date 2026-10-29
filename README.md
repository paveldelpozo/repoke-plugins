# repoke plugins

Official plugins for [repoke](https://github.com/paveldelpozo/repoke): tools that update themselves without being package managers, which repoke then checks and upgrades like any other.

| Id | What it updates | Needs | Tested on |
|----|-----------------|-------|-----------|
| `omz` | oh-my-zsh, when its branch is behind the remote | git, zsh | macOS |
| `vscode` | VS Code extensions with a newer stable release; also `export` and `init` | code, python3 | macOS |
| `git` | Nothing to update: carries `.gitconfig` and `~/.config/git` in `export` (repoke 0.7+) | git | macOS, Debian |
| `zsh` | Nothing to update: carries `.zshrc` and the other startup files in `export` (repoke 0.7+) | zsh | macOS, Debian |
| `zinit` | zinit and the zsh plugins it cloned | git, zsh | Ubuntu 24.04 |
| `antidote` | antidote bundles with new commits, and antidote when it is a clone | git, zsh | Ubuntu 24.04 |
| `tpm` | tpm and the tmux plugins it cloned | git, tmux | Ubuntu 24.04 |
| `lazy` | Neovim plugins that `:Lazy update` would move | nvim, git | Ubuntu 24.04 |
| `vimplug` | vim-plug plugins behind their remote or wildcard tag | git, vim or nvim | Ubuntu 24.04 |
| `gcloud` | gcloud components; also `export` and `init`. SDKs from apt, dnf or snap are left to them | gcloud | Ubuntu 24.04 |

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

Every file is pinned in `index.toml` by its sha256 once it has been reviewed, and `repoke plugin install` refuses a file that doesn't match.

## Community plugins

Anyone can share a plugin: open a pull request that adds it as `community/<id>/repoke-<id>` (or `<id>.toml`) with its entry in `index.toml`, using `tier = "community"`, your GitHub login as `author` and no `sha256`, and say which machine and tool versions you tried it on. `repoke plugin search` lists community plugins after the official ones, sorted by votes, with their downloads.

To vote for a plugin, upvote its Discussion; comments there are the reviews.

## Maintaining the index

- `scripts/check.sh` checks every entry; it fails when a file changed since it was pinned.
- `scripts/publish.py <id>…`, once a change has been reviewed, pins its sha256, uploads that version to the `files` release (where GitHub counts the downloads) and points `url` at it. `--discussion` also opens the plugin's Discussion in the `Plugins` category.
- `scripts/stats.py` writes each plugin's downloads and votes into `index.toml`.
- `scripts/update-stats.sh` runs `stats.py` and pushes the new numbers; a daily launchd agent on the maintainer's Mac runs it.

## License

Licensed under either of [Apache License, Version 2.0](LICENSE-APACHE) or [MIT license](LICENSE-MIT), at your option.
