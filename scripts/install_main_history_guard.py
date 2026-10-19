"""Install the shared main guard without replacing existing Husky hooks."""
from __future__ import annotations
import argparse
from pathlib import Path
import subprocess


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()


def install(repo: Path, template: bytes, *, check: bool = False) -> bool:
    worktree=Path(git(repo,'rev-parse','--show-toplevel')).resolve()
    common=Path(git(repo,'rev-parse','--path-format=absolute','--git-common-dir')).resolve()
    owner=common.parent if common.name=='.git' else worktree
    result=subprocess.run(['git','-C',str(repo),'config','--get','core.hooksPath'],capture_output=True,text=True)
    configured=result.stdout.strip() if result.returncode==0 else ''
    hooks=(Path(configured) if Path(configured).is_absolute() else owner/configured) if configured else common/'hooks'
    hooks=hooks.resolve()
    if not (hooks.is_relative_to(owner) or hooks.is_relative_to(common)):
        raise RuntimeError('External shared hooks directory requires explicit integration')
    target=hooks/'reference-transaction'
    if target.exists() and target.read_bytes()!=template:
        raise RuntimeError('Existing reference-transaction hook preserved; explicit integration required')
    if check:
        return target.is_file() and target.read_bytes()==template and Path(configured).is_absolute()
    hooks.mkdir(parents=True,exist_ok=True)
    target.write_bytes(template)
    target.chmod(0o755)
    # Pin the same existing directory so GIT_WORK_TREE overrides cannot skip it.
    subprocess.run(['git','-C',str(repo),'config','--local','core.hooksPath',hooks.as_posix()],check=True)
    return install(repo,template,check=True)


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args();repo=Path.cwd()
    template=subprocess.check_output(['git','show','HEAD:.husky/reference-transaction'],cwd=repo)
    if not install(repo,template,check=args.check):
        print('Main history guard is not installed; run this installer without --check')
        return 1
    print('Main history guard active; existing hook directory preserved')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
