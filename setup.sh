#!/bin/sh
# Bootstrap deterministic repository checks. Run from the target repository root.
set -eu

if [ ! -d .git ]; then
  printf '%s\n' 'Run this from the root of a Git repository.' >&2
  exit 2
fi

if ! command -v uvx >/dev/null 2>&1; then
  printf '%s\n' 'uvx is required to run fym (install uv first).' >&2
  exit 2
fi

printf '\n%s\n' '== Fuck Your Markdown =='
if uvx --from fuck-your-markdown fym --hr; then
  printf '%s\n' 'fym: clean'
else
  printf '%s\n' 'fym: findings require conversion to executable checks.'
fi

printf '\n%s\n' '== Zanity =='
if ! command -v zanity >/dev/null 2>&1; then
  printf '%s\n' 'Installing Zanity from its official release installer.'
  curl -fsSL https://raw.githubusercontent.com/benomahony/zanity/main/install.sh | sh
  PATH="$HOME/.local/bin:$PATH"
  export PATH
fi
if ! command -v zanity >/dev/null 2>&1; then
  printf '%s\n' 'Zanity installation failed or binary is not on PATH.' >&2
  exit 1
fi
if [ ! -f zanity.toml ]; then
  zanity init
fi
if zanity check . --fail-on warning --strict; then
  printf '%s\n' 'zanity: clean'
else
  printf '%s\n' 'zanity: fix findings; try zanity check . --fix, then rerun.'
fi

printf '\n%s\n' '== Overwatch =='
if command -v claude >/dev/null 2>&1; then
  printf '%s\n' 'Claude Code detected. Install Overwatch inside Claude Code:'
  printf '%s\n' '  /plugin install overwatch --marketplace benomahony/overwatch'
elif command -v codex >/dev/null 2>&1; then
  printf '%s\n' 'Codex detected. Install and trust Overwatch hooks:'
  printf '%s\n' '  codex plugin marketplace add benomahony/overwatch'
  printf '%s\n' '  codex plugin add overwatch@overwatch'
elif command -v opencode >/dev/null 2>&1; then
  printf '%s\n' 'OpenCode detected. Install Overwatch using the documented plugin command.'
elif command -v pi >/dev/null 2>&1; then
  printf '%s\n' 'Pi detected. Install Overwatch:'
  printf '%s\n' '  pi install git:github.com/benomahony/overwatch'
else
  printf '%s\n' 'No supported agent CLI detected. See https://github.com/benomahony/overwatch#install'
fi
printf '%s\n' 'Overwatch auto-detects supported test runners; use .overwatch.json only if needed.'
printf '\n%s\n' 'Next: implement fym recommendations as checks, fix Zanity findings, add CI gates, and verify a deliberate failure is caught.'
