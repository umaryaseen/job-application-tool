#!/bin/sh
set -eu

repo_root=$(git rev-parse --show-toplevel) || {
    echo "hook setup: run this command inside the repository" >&2
    exit 2
}
cd "$repo_root"

expected='.githooks'
configured=$(git config --local --get core.hooksPath || true)
if [ -n "$configured" ] && [ "$configured" != "$expected" ]; then
    echo "hook setup: existing local core.hooksPath=$configured conflicts with $expected; unchanged" >&2
    exit 2
fi

hooks_dir=$(git rev-parse --git-path hooks)
if [ -z "$configured" ] && [ -e "$hooks_dir/pre-commit" ]; then
    echo "hook setup: existing $hooks_dir/pre-commit preserved; configure integration manually" >&2
    exit 2
fi

if [ ! -x "$expected/pre-commit" ]; then
    echo "hook setup: $expected/pre-commit is missing or not executable" >&2
    exit 2
fi

git config --local core.hooksPath "$expected"
echo "hook setup: enabled $expected (idempotent)"
