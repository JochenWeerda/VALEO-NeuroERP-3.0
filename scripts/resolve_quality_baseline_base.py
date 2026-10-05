"""Keep main-to-develop imports on the established main ratchet lineage.

Only a two-parent develop push whose first parent is the previous branch
head and whose second parent is already on origin/main qualifies. Changes
in the merge result are still checked against that incoming main commit.
PRs, direct pushes and unmerged topic imports keep their original base.
"""
import argparse
from pathlib import Path
import subprocess


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True, encoding='utf-8').strip()


def select_base(root, base, head, event, branch):
    before = git(root, 'rev-parse', '--verify', '--end-of-options', base + '^{commit}')
    target = git(root, 'rev-parse', '--verify', '--end-of-options', head + '^{commit}')
    parents = git(root, 'rev-list', '--parents', '-n', '1', target).split()[1:]
    if event != 'push' or branch != 'develop' or len(parents) != 2 or parents[0] != before:
        return before
    established = subprocess.run(['git', '-C', str(root), 'merge-base', '--is-ancestor', parents[1],
                                  'refs/remotes/origin/main'], capture_output=True)
    return parents[1] if established.returncode == 0 else before


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', required=True)
    parser.add_argument('--head', default='HEAD')
    parser.add_argument('--event', required=True)
    parser.add_argument('--branch', required=True)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print(select_base(args.root, args.base, args.head, args.event, args.branch))


if __name__ == '__main__':
    main()
