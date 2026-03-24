#!/usr/bin/env sh

if [ "${HUSKY-}" = "0" ]; then
  exit 0
fi

hook_dir="$(dirname -- "$0")"
repo_root="$(cd "$hook_dir/../.." && pwd)"

case ":$PATH:" in
  *":$repo_root/node_modules/.bin:"*) ;;
  *) PATH="$repo_root/node_modules/.bin:$PATH" ;;
esac

export PATH
