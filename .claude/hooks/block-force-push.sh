#!/usr/bin/env bash
# JARVIS policy: block force-push entirely in this repo.
#
# PreToolUse hook. Reads the hook payload (JSON) from stdin and inspects
# tool_input.command. If the command is a `git push` that uses
# --force / --force-with-lease / -f (in ANY argument position), it blocks
# the call with exit code 2 (which feeds stderr back to Claude).
#
# This closes the gap that glob-based deny rules cannot cover: a trailing
# flag like `git push origin main --force` slips past `Bash(git push --force *)`
# because the allow rule `Bash(git push origin *)` matches it first.
# Server-side GitHub branch protection is the other backstop layer.

input="$(cat)"
cmd="$(printf '%s' "$input" | jq -r '.tool_input.command // ""' 2>/dev/null)"

if printf '%s' "$cmd" | grep -Eq 'git[[:space:]]+push' \
   && printf '%s' "$cmd" | grep -Eq -- '--force-with-lease|--force|(^|[[:space:]])-f([[:space:]]|=|$)'; then
  echo "Blocked by JARVIS policy: force-push (--force / -f / --force-with-lease) is not allowed in this repo." >&2
  exit 2
fi

exit 0
